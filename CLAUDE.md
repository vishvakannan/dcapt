# DCAPT — District Climate Action Prioritisation Tool

Ranks climate-adaptation interventions for Tamil Nadu districts. Was a Google Sheet with
cascading dropdowns (Apps Script); is becoming a shared web + mobile app so multiple officials
get one live source of truth across devices instead of passing a spreadsheet around.

## Stack

| Layer | Choice |
|---|---|
| Frontend | Expo + Expo Router + TypeScript — one codebase, web + iOS + Android |
| Backend | Supabase — Postgres + Auth. Chosen over Firestore because the reference data is a strict relational hierarchy (FKs enforce an Intervention can't exist without a valid Strategy) |
| Auth | Single shared login (v1) — mirrors how the Sheet is used today. RLS still checks `authenticated`, not a specific user, so per-user roles can be added later without a schema rewrite |
| Native builds | EAS Build |

## Key directories

- `app/` — the Expo Router app. `app/lib/supabase.ts` is the Supabase client; `app/lib/scoring.ts` is a client-side score PREVIEW only — the stored `priority_score` is always server-computed, never trust a client-submitted one.
- `supabase/migrations/` — schema, RLS policies, and the scoring engine (`00002_scoring.sql`). This is the actual source of truth for the database; read it before assuming anything about the schema.
- `supabase/seed.sql` — loads `reference/*.csv` into the database. Run via `supabase db reset`.
- `reference/` — salvaged domain **data and spec only, never code**. `scoring-spec.md` is the canonical formula definition; `nests_export.csv` / `schemes_master.csv` / `cobenefits.csv` are the reference hierarchy content. See `reference/README.md` for provenance and known gaps — `schemes_master.csv` in particular is marked **provisional**, pending reconstruction from real government policy notes.

## Run it

```
supabase start          # local Postgres + Studio
supabase db reset        # applies migrations then supabase/seed.sql
cd app && npm install && npx expo start
```

## Don't

- Don't resurrect the `legacy-streamlit-snapshot` git tag's code as a pattern — it's the old
  Streamlit prototype, preserved for history only. It has two known bugs (a duplicate
  `TN_SCHEMES_MAP` definition that silently shadowed the richer one; a `train_model.py` that
  imports a function never defined) and used a different, since-reworked scoring formula.
- Don't hardcode reference data (risks, strategies, interventions, departments, schemes,
  co-benefit items, funding tiers, scoring weights) in application code — it all lives in
  Supabase tables specifically so it's editable without a deploy.
- Don't compute `priority_score` anywhere but `compute_priority_score()` in
  `supabase/migrations/00002_scoring.sql`. If the formula needs to change, change
  `reference/scoring-spec.md` first, then that function, then the client preview in
  `app/lib/scoring.ts` — in that order, since the spec is the source of truth.
