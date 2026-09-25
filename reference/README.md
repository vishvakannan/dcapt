# reference/ — salvaged domain data + spec

Content only, never code. Seeded into Supabase by `supabase/seed/`. See `scoring-spec.md` for the
priority formula.

| File | Source | Status |
|---|---|---|
| `nests_export.csv` | Live Google Sheet "Nests" tab, Risk/Strategy/Intervention block, forward-filled, one incomplete row excluded (see below) | Current — matches the live sheet as of this migration |
| `schemes_master.csv` | Live Google Sheet "Nests" tab, Department/Scheme block, forward-filled | **Provisional.** Most scheme names are still generic placeholders ("RD scheme", "WRD scheme", "PWD scheme", …) rather than real scheme names — the sheet was never fully filled in for this block. **TODO: reconstruct this file from actual government policy notes/scheme documentation before treating it as final.** A separate, unrelated file (`current_scheme_master_list.csv`, in the old local project folder, not migrated here) has real scheme names like MGNREGS/PMKSY/AMRUT but uses a completely different department taxonomy — it is not a valid cross-check source for this file and should not be merged in mechanically. |
| `cobenefits.csv` | Streamlit prototype's `CO_BENEFITS_MAP` (content only, not the Python dict) | Current |

## Known gap excluded from nests_export.csv

The live sheet's row for climate risk "Wild fire" has no Strategy/Intervention of its own filled
in. Under the sheet's cascading-dropdown fill-down convention, leaving it in would have silently
inherited the Land Slide row's Strategy/Intervention ("Reduce soil erosion and run-off" / "Bunding/
Stone Bunding...") — a spreadsheet artifact, not real content. It was excluded rather than
migrated as a fabricated entry. Wild Fire currently has **zero** defined interventions and needs
real content added via the app's admin "add new entry" screen once Phase 2 ships.
