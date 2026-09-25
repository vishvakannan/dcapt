# DCAPT — District Climate Action Prioritisation Tool

Ranks climate-adaptation interventions for Tamil Nadu districts. Formerly a Google Sheet with
cascading dropdowns; now a shared Expo (web + iOS + Android) app backed by Supabase, so multiple
district officials work from one live database instead of a spreadsheet passed around a team.

See [CLAUDE.md](./CLAUDE.md) or [AGENTS.md](./AGENTS.md) for the technical overview, and
[reference/scoring-spec.md](./reference/scoring-spec.md) for the full prioritisation formula.

## Structure

- `app/` — the Expo Router application (web, iOS, Android from one codebase)
- `supabase/` — Postgres schema, RLS policies, scoring engine, and seed data loader
- `reference/` — salvaged reference data and the scoring spec, migrated from the original
  Google Sheet and Streamlit prototype

## Quickstart

```
supabase start
supabase db reset
cd app && npm install && npx expo start
```

## History

The original prototype (a Streamlit app) is preserved at the `legacy-streamlit-snapshot` git
tag, not in the active tree — see `git show legacy-streamlit-snapshot:dcapt/app.py`.
