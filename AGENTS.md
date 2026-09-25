# DCAPT — agent instructions

District Climate Action Prioritisation Tool: ranks climate-adaptation interventions for Tamil
Nadu districts. Migrating from a Google Sheet (cascading dropdowns + Apps Script) to a shared
Expo + Supabase app so multiple officials share one live database across web, iOS and Android.

## Stack

- Frontend: Expo + Expo Router + TypeScript (`app/`)
- Backend: Supabase — Postgres + Auth (`supabase/`)
- Auth: single shared login for now (no per-user roles yet — see CLAUDE.md for why)
- Native builds: EAS Build

## Directories

- `app/` — the application. `app/lib/supabase.ts` (client init), `app/lib/scoring.ts` (client
  preview of the score — display only, never authoritative).
- `supabase/migrations/` — schema, RLS, and the scoring engine. Read this before making any
  assumption about the data model.
- `supabase/seed.sql` — loads `reference/*.csv` into the database (`supabase db reset` runs it).
- `reference/` — salvaged data and formula spec, never code. `scoring-spec.md` is canonical for
  the priority formula.

## Run / test

```
supabase start
supabase db reset
cd app && npm install && npx expo start
```

## Constraints

- Reference data (risk/strategy/intervention, department/scheme, co-benefit items, funding
  tiers, scoring weights) lives in Supabase tables, not hardcoded in application code.
- The stored `priority_score` is always computed server-side by
  `compute_priority_score()` in `supabase/migrations/00002_scoring.sql`. A client-computed
  score is a preview only.
- `reference/scoring-spec.md` is the source of truth for the formula. If it and the trigger
  function ever disagree, the spec file is right.
- `schemes_master.csv` is provisional (placeholder scheme names) — see `reference/README.md`.
- Do not port logic from the `legacy-streamlit-snapshot` git tag; it's a superseded prototype
  with known bugs, kept only for history.
