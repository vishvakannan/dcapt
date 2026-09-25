-- DCAPT schema: reference hierarchies, scoring config, and the scored_entries fact table.
-- See reference/scoring-spec.md for the formula this schema exists to support.

create extension if not exists "pgcrypto";

-- ---------------------------------------------------------------------------
-- Reference hierarchy 1: Risk -> Strategy -> Intervention
-- ---------------------------------------------------------------------------

create table climate_risks (
  id uuid primary key default gen_random_uuid(),
  name text not null unique,
  description text,
  sort_order int not null default 0,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table climate_strategies (
  id uuid primary key default gen_random_uuid(),
  risk_id uuid not null references climate_risks(id) on delete cascade,
  name text not null,
  description text,
  sort_order int not null default 0,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (risk_id, name)
);

create table interventions (
  id uuid primary key default gen_random_uuid(),
  strategy_id uuid not null references climate_strategies(id) on delete cascade,
  name text not null,
  description text,
  sort_order int not null default 0,
  is_active boolean not null default true,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (strategy_id, name)
);

-- ---------------------------------------------------------------------------
-- Reference hierarchy 2: Department -> Scheme
-- ---------------------------------------------------------------------------

create table departments (
  id uuid primary key default gen_random_uuid(),
  name text not null unique,
  sort_order int not null default 0,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table schemes (
  id uuid primary key default gen_random_uuid(),
  department_id uuid not null references departments(id) on delete cascade,
  name text not null,
  description text,
  sort_order int not null default 0,
  is_active boolean not null default true,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (department_id, name)
);

-- ---------------------------------------------------------------------------
-- Co-benefit checklist
-- ---------------------------------------------------------------------------

create table cobenefit_categories (
  id uuid primary key default gen_random_uuid(),
  name text not null unique,
  sort_order int not null default 0
);

create table cobenefit_items (
  id uuid primary key default gen_random_uuid(),
  category_id uuid not null references cobenefit_categories(id) on delete cascade,
  label text not null,
  sort_order int not null default 0,
  unique (category_id, label)
);

-- ---------------------------------------------------------------------------
-- Funding source tiers
-- ---------------------------------------------------------------------------

create table funding_sources (
  id uuid primary key default gen_random_uuid(),
  name text not null unique,
  tier_score numeric(4,2) not null,
  sort_order int not null default 0
);

-- ---------------------------------------------------------------------------
-- Scoring weights — all default to 1 (plain average); tune later with no deploy
-- ---------------------------------------------------------------------------

create table scoring_weights (
  component text primary key
    check (component in ('hazard','capacity','cobenefit','scale','cost','timeframe')),
  weight numeric(5,2) not null default 1
);

-- ---------------------------------------------------------------------------
-- Fixed enum bands, shared by check constraints below
-- ---------------------------------------------------------------------------
-- severity scale:  'Very High' | 'High' | 'Medium' | 'Low' | 'Very Low' | 'None'
-- scale bands:      'Hamlet' | 'Panchayat' | 'Block' | 'MultiBlock' | 'District'
-- cost bands:        'VeryLow' | 'Low' | 'Medium' | 'High' | 'VeryHigh'
-- timeframe bands:  'Under3mo' | '3to6mo' | '6to12mo' | '1to2yr' | 'Over2yr'

-- ---------------------------------------------------------------------------
-- scored_entries — the fact table
-- ---------------------------------------------------------------------------

create table scored_entries (
  id uuid primary key default gen_random_uuid(),
  author_id uuid references auth.users(id),   -- nullable: unused under single-shared-login v1,
                                               -- reserved for a future per-user auth model
  district text not null,
  sector text not null,
  climate_risk_id uuid not null references climate_risks(id),
  climate_strategy_id uuid not null references climate_strategies(id),
  intervention_id uuid not null references interventions(id),
  intervention_detail text,
  department_id uuid not null references departments(id),
  scheme_id uuid references schemes(id),
  hazard_severity text not null
    check (hazard_severity in ('Very High','High','Medium','Low','Very Low','None')),
  scale_band text not null
    check (scale_band in ('Hamlet','Panchayat','Block','MultiBlock','District')),
  cost_band text not null
    check (cost_band in ('VeryLow','Low','Medium','High','VeryHigh')),
  timeframe_band text not null
    check (timeframe_band in ('Under3mo','3to6mo','6to12mo','1to2yr','Over2yr')),
  scheme_alignment_pct numeric(5,2) not null default 0
    check (scheme_alignment_pct between 0 and 100),
  hazard_component numeric(4,2),
  collaboration_component numeric(4,2),
  funding_component numeric(4,2),
  capacity_component numeric(4,2),
  cobenefit_component numeric(4,2),
  scale_component numeric(4,2),
  cost_component numeric(4,2),
  timeframe_component numeric(4,2),
  priority_score numeric(4,2),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create index scored_entries_district_dept_idx on scored_entries (district, department_id);

-- ---------------------------------------------------------------------------
-- Join tables for the scored_entries multi-selects
-- ---------------------------------------------------------------------------

create table scored_entry_cobenefits (
  scored_entry_id uuid not null references scored_entries(id) on delete cascade,
  cobenefit_item_id uuid not null references cobenefit_items(id),
  primary key (scored_entry_id, cobenefit_item_id)
);

create table scored_entry_collaborating_departments (
  scored_entry_id uuid not null references scored_entries(id) on delete cascade,
  department_id uuid not null references departments(id),
  primary key (scored_entry_id, department_id)
);

create table scored_entry_funding_sources (
  scored_entry_id uuid not null references scored_entries(id) on delete cascade,
  funding_source_id uuid not null references funding_sources(id),
  primary key (scored_entry_id, funding_source_id)
);

-- ---------------------------------------------------------------------------
-- Ranking view — computed live, never stored: any sibling row changing shifts
-- these, which a per-row insert/update trigger cannot maintain correctly.
-- ---------------------------------------------------------------------------

create view scored_entries_ranked as
select *,
  rank() over (partition by district, department_id order by priority_score desc) as dept_rank,
  rank() over (partition by district order by priority_score desc) as overall_rank
from scored_entries;
