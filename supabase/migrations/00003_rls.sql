-- Row-Level Security. v1 auth model is a single shared login (see plan) — every policy just
-- requires 'authenticated', with no per-row ownership logic yet. scored_entries.author_id and
-- these broad 'authenticated' checks are deliberately structured so a future per-user/role model
-- can be layered on later without a schema rewrite.

alter table climate_risks enable row level security;
alter table climate_strategies enable row level security;
alter table interventions enable row level security;
alter table departments enable row level security;
alter table schemes enable row level security;
alter table cobenefit_categories enable row level security;
alter table cobenefit_items enable row level security;
alter table funding_sources enable row level security;
alter table scoring_weights enable row level security;
alter table scored_entries enable row level security;
alter table scored_entry_cobenefits enable row level security;
alter table scored_entry_collaborating_departments enable row level security;
alter table scored_entry_funding_sources enable row level security;

-- Reference + config tables: any authenticated user can read and write (mirrors what the Apps
-- Script "Add new entry" sidebar allowed on the Sheets side — no separate admin role yet).
do $$
declare
  t text;
begin
  foreach t in array array[
    'climate_risks','climate_strategies','interventions',
    'departments','schemes',
    'cobenefit_categories','cobenefit_items',
    'funding_sources','scoring_weights'
  ] loop
    execute format(
      'create policy %I_authenticated_all on %I for all to authenticated using (true) with check (true)',
      t, t
    );
  end loop;
end $$;

-- scored_entries and its join tables: any authenticated user can read and write everything
-- (matches how the shared Google Sheet works today — everyone sees everyone's entries).
create policy scored_entries_authenticated_all on scored_entries
  for all to authenticated using (true) with check (true);

create policy scored_entry_cobenefits_authenticated_all on scored_entry_cobenefits
  for all to authenticated using (true) with check (true);

create policy scored_entry_collaborating_departments_authenticated_all on scored_entry_collaborating_departments
  for all to authenticated using (true) with check (true);

create policy scored_entry_funding_sources_authenticated_all on scored_entry_funding_sources
  for all to authenticated using (true) with check (true);
