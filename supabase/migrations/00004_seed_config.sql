-- Small fixed config tables — literal seed data, no CSV pipeline needed.
-- The larger reference hierarchies (climate_risks/strategies/interventions, departments/schemes,
-- cobenefit_categories/items) are seeded from reference/*.csv by supabase/seed/load_reference.sql instead.

insert into funding_sources (name, tier_score, sort_order) values
  ('Scheme (tied)', 10, 1),
  ('Scheme (untied)', 10, 2),
  ('Other district funds', 7.5, 3),
  ('State funding', 5, 4),
  ('Grants / Loans', 2.5, 5),
  ('CSR / other private finance', 1, 6);

insert into scoring_weights (component, weight) values
  ('hazard', 1),
  ('capacity', 1),
  ('cobenefit', 1),
  ('scale', 1),
  ('cost', 1),
  ('timeframe', 1);
