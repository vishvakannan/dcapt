-- Priority score computation. See reference/scoring-spec.md — this file must match it exactly.
--
-- Design note: the score depends on scored_entry_cobenefits / scored_entry_collaborating_departments /
-- scored_entry_funding_sources, which can only be written AFTER the parent scored_entries row exists
-- (their FK requires it). So this can't be a single BEFORE INSERT trigger. Instead:
--   1. compute_priority_score(id) reads the current state of a row + its join tables and updates
--      that row's component columns and priority_score.
--   2. AFTER triggers on scored_entries and on each join table call it whenever anything relevant changes.
--   3. create_scored_entry(...) is the RPC the app actually calls: it writes the row, the join rows,
--      and returns the fully-scored result from ONE atomic call, so the client never sees a
--      partially-scored intermediate state.

create or replace function qualitative_score(p_value text)
returns numeric language sql immutable as $$
  select case p_value
    when 'Very High' then 10.0
    when 'High'       then 8.0
    when 'Medium'      then 5.0
    when 'Low'          then 2.0
    when 'Very Low'      then 0.0
    when 'None'           then 0.0
    else 0.0
  end;
$$;

create or replace function scale_band_score(p_band text)
returns numeric language sql immutable as $$
  select case p_band
    when 'Hamlet'    then 2.0
    when 'Panchayat' then 4.0
    when 'Block'     then 6.0
    when 'MultiBlock' then 8.0
    when 'District'  then 10.0
    else 0.0
  end;
$$;

create or replace function cost_band_score(p_band text)
returns numeric language sql immutable as $$
  select case p_band
    when 'VeryLow'  then 10.0
    when 'Low'       then 7.5
    when 'Medium'     then 5.0
    when 'High'        then 2.5
    when 'VeryHigh'     then 0.0
    else 0.0
  end;
$$;

create or replace function timeframe_band_score(p_band text)
returns numeric language sql immutable as $$
  select case p_band
    when 'Under3mo' then 10.0
    when '3to6mo'    then 7.5
    when '6to12mo'    then 5.0
    when '1to2yr'      then 2.5
    when 'Over2yr'      then 0.0
    else 0.0
  end;
$$;

create or replace function collaboration_score(p_count int)
returns numeric language sql immutable as $$
  select case
    when p_count <= 0 then 10.0
    when p_count = 1  then 7.0
    when p_count = 2  then 5.0
    when p_count = 3  then 3.0
    else 1.0
  end;
$$;

create or replace function funding_score(p_scored_entry_id uuid)
returns numeric language sql stable as $$
  select least(10.0, coalesce(max(fs.tier_score), 0.0) + greatest(0, count(*) - 1))
  from scored_entry_funding_sources sefs
  join funding_sources fs on fs.id = sefs.funding_source_id
  where sefs.scored_entry_id = p_scored_entry_id;
$$;

create or replace function cobenefit_score(p_scored_entry_id uuid)
returns numeric language sql stable as $$
  select case when (select count(*) from cobenefit_items) = 0 then 0.0
    else (
      select count(*)::numeric from scored_entry_cobenefits
      where scored_entry_id = p_scored_entry_id
    ) / (select count(*)::numeric from cobenefit_items) * 10.0
  end;
$$;

create or replace function compute_priority_score(p_id uuid)
returns void language plpgsql as $$
declare
  r scored_entries%rowtype;
  v_collab numeric;
  v_funding numeric;
  v_capacity numeric;
  v_cobenefit numeric;
  v_scale numeric;
  v_cost numeric;
  v_timeframe numeric;
  v_hazard numeric;
  v_weight_sum numeric;
  v_score numeric;
begin
  select * into r from scored_entries where id = p_id;
  if not found then
    return;
  end if;

  v_hazard    := qualitative_score(r.hazard_severity);
  v_collab    := collaboration_score((
    select count(*)::int from scored_entry_collaborating_departments where scored_entry_id = p_id
  ));
  v_funding   := funding_score(p_id);
  v_capacity  := (v_collab + v_funding) / 2.0;
  v_cobenefit := cobenefit_score(p_id);
  v_scale     := scale_band_score(r.scale_band);
  v_cost      := (v_scale + cost_band_score(r.cost_band)) / 2.0;
  v_timeframe := timeframe_band_score(r.timeframe_band);

  select
    coalesce(sum(weight) filter (where component = 'hazard'), 1)
      * v_hazard
    + coalesce(sum(weight) filter (where component = 'capacity'), 1) * v_capacity
    + coalesce(sum(weight) filter (where component = 'cobenefit'), 1) * v_cobenefit
    + coalesce(sum(weight) filter (where component = 'scale'), 1) * v_scale
    + coalesce(sum(weight) filter (where component = 'cost'), 1) * v_cost
    + coalesce(sum(weight) filter (where component = 'timeframe'), 1) * v_timeframe,
    sum(weight)
  into v_score, v_weight_sum
  from scoring_weights;

  update scored_entries set
    hazard_component = round(v_hazard, 2),
    collaboration_component = round(v_collab, 2),
    funding_component = round(v_funding, 2),
    capacity_component = round(v_capacity, 2),
    cobenefit_component = round(v_cobenefit, 2),
    scale_component = round(v_scale, 2),
    cost_component = round(v_cost, 2),
    timeframe_component = round(v_timeframe, 2),
    priority_score = round(v_score / nullif(v_weight_sum, 0), 2),
    updated_at = now()
  where id = p_id;
end;
$$;

-- Keep scores correct if the base row's direct fields change.
create or replace function trg_scored_entries_recompute()
returns trigger language plpgsql as $$
begin
  perform compute_priority_score(new.id);
  return new;
end;
$$;

create trigger scored_entries_recompute
  after insert or update of hazard_severity, scale_band, cost_band, timeframe_band
  on scored_entries
  for each row execute function trg_scored_entries_recompute();

-- Keep scores correct if any join-table row changes (the multi-selects).
create or replace function trg_join_table_recompute()
returns trigger language plpgsql as $$
begin
  if tg_op = 'DELETE' then
    perform compute_priority_score(old.scored_entry_id);
    return old;
  else
    perform compute_priority_score(new.scored_entry_id);
    return new;
  end if;
end;
$$;

create trigger scored_entry_cobenefits_recompute
  after insert or delete on scored_entry_cobenefits
  for each row execute function trg_join_table_recompute();

create trigger scored_entry_collaborating_departments_recompute
  after insert or delete on scored_entry_collaborating_departments
  for each row execute function trg_join_table_recompute();

create trigger scored_entry_funding_sources_recompute
  after insert or delete on scored_entry_funding_sources
  for each row execute function trg_join_table_recompute();

-- ---------------------------------------------------------------------------
-- The app's actual write path: one atomic call in, one fully-scored row out.
-- ---------------------------------------------------------------------------

create or replace function create_scored_entry(
  p_district text,
  p_sector text,
  p_climate_risk_id uuid,
  p_climate_strategy_id uuid,
  p_intervention_id uuid,
  p_intervention_detail text,
  p_department_id uuid,
  p_scheme_id uuid,
  p_hazard_severity text,
  p_scale_band text,
  p_cost_band text,
  p_timeframe_band text,
  p_collaborating_department_ids uuid[],
  p_funding_source_ids uuid[],
  p_cobenefit_item_ids uuid[]
) returns scored_entries language plpgsql as $$
declare
  v_id uuid;
  v_result scored_entries%rowtype;
begin
  insert into scored_entries (
    author_id, district, sector, climate_risk_id, climate_strategy_id, intervention_id,
    intervention_detail, department_id, scheme_id, hazard_severity, scale_band, cost_band, timeframe_band
  ) values (
    auth.uid(), p_district, p_sector, p_climate_risk_id, p_climate_strategy_id, p_intervention_id,
    p_intervention_detail, p_department_id, p_scheme_id, p_hazard_severity, p_scale_band, p_cost_band, p_timeframe_band
  ) returning id into v_id;

  insert into scored_entry_collaborating_departments (scored_entry_id, department_id)
    select v_id, dept_id from unnest(p_collaborating_department_ids) as dept_id;

  insert into scored_entry_funding_sources (scored_entry_id, funding_source_id)
    select v_id, fs_id from unnest(p_funding_source_ids) as fs_id;

  insert into scored_entry_cobenefits (scored_entry_id, cobenefit_item_id)
    select v_id, cb_id from unnest(p_cobenefit_item_ids) as cb_id;

  perform compute_priority_score(v_id);

  select * into v_result from scored_entries where id = v_id;
  return v_result;
end;
$$;
