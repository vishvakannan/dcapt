# DCAPT priority scoring — source of truth

This is the canonical definition of the DCAPT priority score. `supabase/migrations/`'s
`compute_priority_score()` trigger function and `app/lib/scoring.ts`'s client-side preview
must both implement exactly this. If they ever diverge, this file is right and they are wrong.

## Formula

```
priority_score = Σ(weight_i × component_i) / Σ(weight_i)
```

Six components, each 0–10. Weights come from the `scoring_weights` table (component text primary
key, weight numeric) and are **all seeded to 1** — i.e. currently a plain average — but are stored
data, not constants in code, so they can be tuned later from Supabase Studio with no deploy.

## Components

### hazard_component

Direct lookup of the user-selected Hazard Severity:

| Value | Score |
|---|---|
| Very High | 10 |
| High | 8 |
| Medium | 5 |
| Low | 2 |
| Very Low / None | 0 |

### capacity_component = average(collaboration_score, funding_score)

Technical Complexity and Infrastructure Maturity (used in the original Streamlit prototype) are
**not** inputs here — dropped entirely, not folded in elsewhere.

**collaboration_score** — tiered, inverse to the count of collaborating departments (more
coordination required = slower = lower score):

| Collaborating departments | Score |
|---|---|
| 0 (sole department) | 10 |
| 1 | 7 |
| 2 | 5 |
| 3 | 3 |
| 4+ | 1 |

**funding_score** — user multi-selects one or more applicable funding sources from a fixed,
editable tier list (`funding_sources` table):

| Funding source | Tier score |
|---|---|
| Scheme (tied) | 10 |
| Scheme (untied) | 10 |
| Other district funds | 7.5 |
| State funding | 5 |
| Grants / Loans | 2.5 |
| CSR / other private finance | 1 |

Combination math:
```
funding_score = min(10, max(tier score of selected sources) + 1 × (count of additional distinct sources selected))
```

This is also where the prototype's old 0–100% "Convergence" (scheme-alignment) slider now lives —
folded into funding_score rather than kept as a separate top-level component.

### cobenefit_component

```
cobenefit_component = (count of checked items in scored_entry_cobenefits / count of all cobenefit_items) × 10
```

Checklist categories (`cobenefit_categories` → `cobenefit_items`): Social, Economic, Environmental,
Mitigation, Avoided Losses.

### scale_component — population/area reached

| Band | Score |
|---|---|
| Hamlet / Village | 2 |
| Panchayat / cluster of villages | 4 |
| Block level | 6 |
| Multiple blocks | 8 |
| District-wide | 10 |

### cost_component — cost-effectiveness

```
cost_component = average(scale_component, cost_tier_score)
```

Approximated as an average of reach (scale_component) and affordability, rather than a literal
cost ÷ impact ratio — no calibration data exists yet to set a meaningful ratio threshold.
`cost_tier_score` from the user-selected cost band, cheaper = higher score:

| Band | Score |
|---|---|
| Very Low (<₹1L) | 10 |
| Low (₹1–10L) | 7.5 |
| Medium (₹10–50L) | 5 |
| High (₹50L–2Cr) | 2.5 |
| Very High (>₹2Cr) | 0 |

### timeframe_component — implementation speed

| Band | Score |
|---|---|
| <3 months | 10 |
| 3–6 months | 7.5 |
| 6–12 months | 5 |
| 1–2 years | 2.5 |
| >2 years | 0 |

## Interpretation bands

| priority_score | Meaning |
|---|---|
| ≥ 7.5 | High priority — "No Regret" |
| 5.0–7.4 | Medium priority — Strategic |
| < 5.0 | Low priority — Re-evaluate |

## Ranking (not part of the score itself)

Ranks are computed live via a view, not stored, since any sibling row changing shifts them:

```sql
create view scored_entries_ranked as
select *,
  rank() over (partition by district, department_id order by priority_score desc) as dept_rank,
  rank() over (partition by district order by priority_score desc) as overall_rank
from scored_entries;
```

`dept_rank` — standing among entries for the same district *and* department.
`overall_rank` — standing across every department within that same district.

## Why this differs from the original Streamlit prototype

The prototype's formula (Hazard/Capacity/CoBenefit/Convergence, simple average of 4) was the
starting point, then reworked directly with the project owner:

- Capacity dropped Technical Complexity + Infrastructure Maturity, replaced by collaboration
  overhead and funding-source quality.
- Convergence (0–100% scheme-alignment slider) was absorbed into the new Funding Sources tier
  rather than kept separate.
- Scale, Cost, and Timeframe were added — none exist in the prototype.
- The whole thing became a weighted average (all weights = 1 today) instead of a fixed simple
  average, so future tuning doesn't require touching code.
