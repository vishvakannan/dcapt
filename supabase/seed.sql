-- Loads reference/*.csv into the reference hierarchy tables. Run automatically by
-- `supabase db reset`, or manually with: psql "$DATABASE_URL" -f supabase/seed.sql
-- Must be invoked from the repo root so the relative \copy paths below resolve.
--
-- Uses staging tables rather than hand-written INSERTs so reference/*.csv stays the one
-- source of truth for this data — nothing here should ever need to be edited by hand;
-- edit the CSVs (or the app's admin screens, once they exist) instead.

begin;

create temporary table _staging_nests (
  id serial primary key,
  climate_risk text,
  climate_strategy text,
  intervention text
);
\copy _staging_nests (climate_risk, climate_strategy, intervention) from 'reference/nests_export.csv' with (format csv, header true)

create temporary table _staging_schemes (
  id serial primary key,
  department text,
  scheme text
);
\copy _staging_schemes (department, scheme) from 'reference/schemes_master.csv' with (format csv, header true)

create temporary table _staging_cobenefits (
  id serial primary key,
  category text,
  item text
);
\copy _staging_cobenefits (category, item) from 'reference/cobenefits.csv' with (format csv, header true)

-- Risks: distinct, ordered by first appearance in the CSV
insert into climate_risks (name, sort_order)
select climate_risk, min(id)
from _staging_nests
group by climate_risk
on conflict (name) do nothing;

-- Strategies: distinct (risk, strategy) pairs, ordered by first appearance
insert into climate_strategies (risk_id, name, sort_order)
select r.id, s.climate_strategy, min(s.id)
from _staging_nests s
join climate_risks r on r.name = s.climate_risk
group by r.id, s.climate_strategy
on conflict (risk_id, name) do nothing;

-- Interventions: one row per staging row
insert into interventions (strategy_id, name, sort_order)
select cs.id, s.intervention, s.id
from _staging_nests s
join climate_risks r on r.name = s.climate_risk
join climate_strategies cs on cs.risk_id = r.id and cs.name = s.climate_strategy
on conflict (strategy_id, name) do nothing;

-- Departments: distinct, ordered by first appearance
insert into departments (name, sort_order)
select department, min(id)
from _staging_schemes
group by department
on conflict (name) do nothing;

-- Schemes: one row per staging row
insert into schemes (department_id, name, sort_order)
select d.id, s.scheme, s.id
from _staging_schemes s
join departments d on d.name = s.department
on conflict (department_id, name) do nothing;

-- Co-benefit categories: distinct, ordered by first appearance
insert into cobenefit_categories (name, sort_order)
select category, min(id)
from _staging_cobenefits
group by category
on conflict (name) do nothing;

-- Co-benefit items: one row per staging row
insert into cobenefit_items (category_id, label, sort_order)
select c.id, s.item, s.id
from _staging_cobenefits s
join cobenefit_categories c on c.name = s.category
on conflict (category_id, label) do nothing;

commit;
