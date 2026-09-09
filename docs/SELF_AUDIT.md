# Self-audit log

One entry per completed slice, answering the gate in CLAUDE.md section 13. An
answer of "no" or "not sure" is the next thing fixed, not a footnote.

---

## Slice 1 - monorepo scaffold, domain model, config, provenance, deployment baseline

**Date:** 2026-09-09
**Commit:** `chore: scaffold ASTRA monorepo, domain model and deployment baseline`

### What actually works end to end

The API serves the model configuration, the formula registry, the provenance
registry, the layer catalogue, the fixture integrity gate result and the baseline
scenario. The web app renders all of it live from the API, with generated
TypeScript types. Nothing on that screen is typed into the frontend by hand.

### Gate answers

| # | Question | Answer |
|---|---|---|
| 1 | Is any part of this an LLM guessing, dressed as a computed score? | No. There is no LLM call in the codebase yet, and the LLM adapter, when it lands, is narration only. `/health` reports `llm_mode: template` because no key is configured, and everything works. |
| 2 | Can every number on screen be traced in one hop to a documented formula and its inputs? | Yes. Every number rendered is a config constant, and each carries key, value, unit, provenance class, description and (where standard-derived) citation. The formula registry is served alongside, and a test asserts every formula's declared config keys resolve to real constants. |
| 3 | Is anything animated or displayed that is not backed by a real backend event or value? | No. There is no animation. Every panel renders API data; when the API is unreachable the page says so rather than showing placeholder figures. |
| 4 | Is any DEMO_CONFIG constant presented as if it were a government rule? | No. 90 of 97 constants are marked `DEMO_CONFIG` with a chip; the 7 standard-derived ones carry their Sphere / PMAY-G / NDMA citation inline. A test refuses to construct a non-DEMO constant without a citation. |
| 5 | Does the provenance panel honestly distinguish real / derived / synthetic per layer, without blending? | Yes. Per-class counts are separate, never summed into one "data sources" figure. The registry currently holds only the two datasets that genuinely exist; real datasets land in Slice 2 and are registered then, not promised now. |
| 6 | Are the same figures identical across every screen that shows them? | Yes, structurally: there is one API, one generated type package, and no client-side arithmetic. |
| 7 | Does the opening 20 seconds avoid looking like a generic dashboard? | Partially. The visual foundation (palette, tabular figures, wordmark, dense panels, no KPI card wall) is in place, but the cold open and Command Centre are Slice 12 and Slice 3. The root route redirects to the screen that is genuinely built rather than showing an empty dashboard. |
| 8 | Does every recommendation screen make it unambiguous that the SDMA decides? | Yes for what exists. The decision-authority notice and the synthetic-scenario disclaimer are served by the API and rendered on the page. There are no recommendation screens yet. |
| 9 | Does the demo run start to finish with the network off and no LLM key? | Yes for this slice. No runtime external call exists: the frontend talks only to the API, and the API reads only local files. Fonts are self-hosted by the build. |
| 10 | Can the optimiser breach capacity? | Not applicable yet. Slice 7. |
| 11 | Is there any feature that looks impressive but changes no decision? | The layer catalogue lists 17 layers of which 0 are available. That is a roadmap, not a capability, and it is labelled "Not yet built" on every card. Kept because it makes the honest build state visible; it will become the real layer control in Slice 3. |
| 12 | Would this survive "walk me through exactly how you got this number", live? | Yes for the constants and formulas on screen. Computed values start in Slice 3. |

### Red-team finding

**The weakest point in this slice is that the layer catalogue and the formula
registry describe engines that do not exist yet.** A hostile reader could call
that a promise dressed as a feature. Two things were done about it: every layer
carries an `available` flag that is `false` and renders as "Not yet built", and
the integrity gate refuses to let a layer be marked available while its datasets
are absent from the provenance registry - enforced by
`_validate_layers` and covered by a test. The catalogue therefore cannot lie in a
later slice either.

Secondary finding: the fixture gate currently passes trivially because there are
no fixtures. That is honest but weak, so the gate was written and tested against
deliberately broken fixtures (out-of-bbox coordinates, duplicate IDs, malformed
JSON, households exceeding population) rather than against an empty directory.
Six tests fail the gate on purpose.

### Verification

- 56 backend tests pass (`pytest`, `apps/api`).
- `ruff check apps/api scripts` clean.
- Fixture integrity gate passes standalone and on API startup.
- `tsc --noEmit` clean; `next build` succeeds.
- Page verified rendering live API values in a production build, not dev mode.

---

## Slice 2 - study area, real open data, derived surfaces and the calibrated synthetic layer

**Date:** 2026-09-09
**Commit:** `feat(data): establish Chamoli study area, provenance registry and validated demo dataset`

### What actually works end to end

Six real open datasets are vendored for the Alaknanda corridor. Fourteen terrain
and hydrology surfaces are computed from the real DEM by standard published
methods. Twelve habitations and six candidate sites are generated from those
surfaces, validated by the blocking integrity gate, served by the API and
rendered on a shaded-relief plate of the corridor with a panel that states, side
by side, what was measured and what was assumed.

### Gate answers

| # | Question | Answer |
|---|---|---|
| 1 | Is any part of this an LLM guessing, dressed as a computed score? | No. There is still no LLM call in the codebase. Every surface is a documented geomorphometric computation; every generated attribute is either read off a real raster or comes from a named DEMO_CONFIG assumption. |
| 2 | Can every number on screen be traced in one hop? | Yes. Each derived layer carries its method (Horn 1981, Riley 1999, Priority-Flood, D8, Renno/Nobre HAND) and its observed range, served from the build manifest. Habitation attributes trace to either a raster sample or a named constant. |
| 3 | Is anything displayed that is not backed by a real value? | No. The terrain plate is a render of the vendored DEM; the markers are drawn at the coordinates in the fixtures. Nothing is drawn that the API did not return. |
| 4 | Is any DEMO_CONFIG constant presented as a government rule? | No. The 18 generation constants are chipped DEMO_CONFIG in the transparency panel, and the study-area screen carries an explicit "what was assumed, not measured" list. |
| 5 | Does the provenance panel distinguish real / derived / synthetic without blending? | Yes. Ten datasets: six REAL_OPEN with source URLs and licences, two SYNTHETIC_CALIBRATED, two DEMO_CONFIG. Counts are reported per class, never summed. |
| 6 | Are the same figures identical across screens? | Yes. Totals are computed once in the API and rendered as received. |
| 7 | Does the opening avoid looking like a generic dashboard? | Improving. The root now opens on the corridor itself - real shaded relief with the settlements on it. The cinematic cold open is still Slice 12. |
| 8 | Is it unambiguous that the SDMA decides? | Yes for what exists. The synthetic-scenario disclaimer and the tenure limitation are served by the API and shown at the top of the study-area screen. |
| 9 | Does it run with the network off? | Yes, and this is now tested. `scripts/ingest.py` is the only code that touches the network; every connector's `load` path reads the vendored artifact and raises if it is absent, and a test asserts a connector without its artifact fails rather than fetching. |
| 10 | Can the optimiser breach capacity? | Not applicable yet. Slice 7. |
| 11 | Any feature that looks impressive but changes no decision? | The waterway-distance surface is computed but nothing reads it yet; it is retained because the flood sub-model in Slice 3 consumes it directly. If Slice 3 does not use it, it comes out. |
| 12 | Would this survive "walk me through exactly how you got this number"? | Yes for terrain and hydrology: the methods are named, cited, unit-tested against analytically known cases, and the surfaces reproduce from the DEM in about 20 seconds. |

### Red-team finding

**The sharpest attack on this slice is the demographic composition.** CLAUDE.md
asks for proportions calibrated to Census/SECC district figures. The Census
district tables are not available through any endpoint reachable without
credentials, and the accessible mirrors are unverifiable third-party copies. Two
options were available: cite a mirror and hope, or state the truth. ASTRA states
the truth - the demographic shares are ASTRA assumptions for a Himalayan hill
district, they appear as DEMO_CONFIG constants with that wording, and the
study-area screen lists them under "what was assumed, not measured" before anyone
asks. Everything that *could* be grounded in real data is: placement, elevation
band, slope, buildable land cover, road access, and settlement size integrated
from the WorldPop population surface. The weight-sensitivity analysis in Slice 10
is what turns this from a weakness into an answer.

Secondary finding: the historical inventory holds 251 incidents across the
Uttarakhand-Himalaya window but only 23 inside the study bbox. That is a thin
positive set for a ROC-AUC back-test. It is recorded here now so Slice 10 reports
the sample size alongside the figure rather than quietly presenting an AUC
computed on 23 points as if it were robust.

### Verification

- 102 backend tests pass, including terrain maths checked against analytically
  known answers (45-degree plane, pit filling, HAND on a uniform slope).
- `ruff check apps/api scripts` clean.
- Integrity gate: PASS, 6 checks, 18 fixture records, 10 datasets.
- Determinism: regenerating the fixtures from the same surfaces reproduces every
  record exactly.
- `tsc --noEmit` and ESLint clean; `next build` succeeds; study-area page verified
  against a production build serving live API data.

---

## Slice 3 - multi-hazard susceptibility engine, analytical red zones and the map surface

**Date:** 2026-09-09
**Commit:** `feat(hazard): multi-hazard susceptibility engine and analytical red-zone mapping`

### What actually works end to end

Three hazard sub-models score a 387 x 432 grid of 100 m cells over the corridor
by weighted overlay of normalised factors computed from the real DEM, land
cover, road network, incident inventory and rainfall archive. The composite
preserves dominance rather than averaging it away. The classified surface is
cleaned to a minimum mapping unit, grown by the configured buffer and published
as 335 non-overlapping zone polygons, each carrying its area, dominant hazard,
hazard mix, mean and maximum composite, intersected population, evidence
confidence and rule version. The Risk Explorer renders all of it on MapLibre and
deck.gl, and clicking anywhere returns the full factor decomposition.

### Gate answers

| # | Question | Answer |
|---|---|---|
| 1 | Is any part of this an LLM guessing, dressed as a computed score? | No. Still no LLM anywhere in the codebase. Every score is `100 x sum(w_f x n_f)` over surfaces derived from real data. |
| 2 | Can every number on screen be traced in one hop? | Yes, and it is now demonstrable: click any cell and the panel lists, per hazard, each factor's measured value, normalised value, weight and contribution, with the formula ID, formula version, engine version and config version underneath. A test asserts the published contributions sum to the published score. |
| 3 | Is anything displayed that is not backed by a real value? | No. The basemap is a render of the vendored DEM, the overlay is the computed composite, the polygons are the computed zones, the markers are fixture coordinates. There is no animation. |
| 4 | Is any DEMO_CONFIG constant presented as a government rule? | No. The zone thresholds are stated on screen with the percentile of the corridor distribution they sit at, and chipped DEMO_CONFIG in the transparency panel. |
| 5 | Does the provenance panel distinguish real / derived / synthetic without blending? | Yes. Every factor carries its own provenance class through to the decomposition panel. |
| 6 | Are the same figures identical across screens? | Yes. Zone summary, class shares and habitation composites are computed once in the engine and rendered as received. |
| 7 | Does the opening avoid looking like a generic dashboard? | Yes. The root opens on the map, dominated by real terrain with the classified surface over it. The cinematic cold open is still Slice 12. |
| 8 | Is it unambiguous that the SDMA decides? | Yes. Every zone feature carries `classification_label: ASTRA analytical classification`, the zones response carries the decision-authority line, and the panel footer states both it and the synthetic-scenario disclaimer. |
| 9 | Does it run with the network off? | Yes. MapLibre uses no token and no external tiles: basemap, hazard overlay, zone geometry and roads are all served by the ASTRA API from local files, and the style declares no sprite or glyph server. |
| 10 | Can the optimiser breach capacity? | Not applicable yet. Slice 7. |
| 11 | Any feature that looks impressive but changes no decision? | The waterway-distance surface from Slice 2 is still unused: the flood sub-model ended up using HAND and channel distance from the DEM-derived network, which is better evidence than mapped-waterway distance. It stays for the route work in Slice 6 and comes out if unused there. |
| 12 | Would this survive "walk me through exactly how you got this number"? | This is the slice where that question gets answered on screen. Composite 94.9 at Rauligaon: Flood 79.4, driven by height above drainage 7.33 m normalised to 0.897 at weight 0.42, contributing 0.377; plus Cloudburst 61.9 as the second hazard at lambda 0.25. |

### Red-team finding

**The first version of this slice reported each habitation's hazard as the
maximum composite within 300 m, and every settlement came out between 97 and
100.** That is technically defensible and practically useless: it destroyed the
ability to rank, which is the entire point of the product. The habitation score
is now the composite at the settlement's own cell, with the footprint mean and
maximum reported alongside as the spread around it. The corrected spread is 34
to 95 across the twelve habitations, with three different dominant hazards.

Second finding from the same pass: the initial thresholds put 10% of the corridor
in Critical and produced a single 190 km2 polygon - a "zone" too coarse for
anyone to act on. Thresholds now sit near the 95th, 82nd and 57th percentiles of
the corridor's own composite distribution, which is stated in the constant
descriptions and rendered on screen. A calibration choice, labelled as ASTRA's
choice wherever it appears.

Third: two factors CLAUDE.md lists - fault/lineament proximity for landslides and
historical inundation overlap for floods - have no obtainable open dataset for
this corridor. They were removed from the weight sets and the remaining weights
renormalised, with a comment in the config saying why. A neutral placeholder
constant would have looked like evidence and would not have been one.

### Verification

- 144 backend tests pass, 32 of them new: normalisation ramps against hand
  arithmetic, weighted overlay against a hand-computed expected score, the
  dominance-preserving composite against its own formula, exact behaviour at
  every classification threshold, confidence bounded and independent of the
  score, kernel density conserving total weight, single-cell speckle rejected by
  the minimum mapping unit, and zone classes proven non-overlapping.
- API tests assert that published factor contributions sum to the published
  score, that the composite equals the dominance formula, and that zone
  population totals agree with the habitation layer.
- `ruff` clean, integrity gate PASS, `tsc --noEmit` clean, ESLint clean,
  `next build` succeeds.
- The Risk Explorer was driven in a real browser against a production build: the
  map renders, layers toggle, opacity works, clicking a habitation returns its
  decomposition. Zero console errors.

---

## Slice 4 - exposure, vulnerability, history and phased relocation prioritisation

**Date:** 2026-09-10
**Commit:** `feat(priority): exposure, vulnerability and phased relocation prioritisation`

### What actually works end to end

Every habitation now carries four separately computed quantities - hazard over
its footprint, exposure, vulnerability and recency-weighted incident history -
combined into a priority score by declared weights, and assigned to Immediate,
Short-term or Medium-term by documented thresholds plus override rules that name
themselves when they fire. The Habitation Priority screen shows the ranked list
grouped by phase, colours the map by phase, and opens a reasoning drawer that
reproduces the whole calculation, component by component and factor by factor.

### Gate answers

| # | Question | Answer |
|---|---|---|
| 1 | Is any part of this an LLM guessing, dressed as a computed score? | No. Four weighted components, each decomposed into named factors with measured values. |
| 2 | Can every number on screen be traced in one hop? | Yes. The drawer shows priority = sum of four contributions, then each component's own factor table with measured, normalised, weight and contribution. Tests assert the published score equals the sum of the published contributions to within 0.02. |
| 3 | Is anything displayed that is not backed by a real value? | No. Phase colours on the map come from the computed phase; the override chip appears only when a rule actually fired. |
| 4 | Is any DEMO_CONFIG constant presented as a government rule? | No. Tier thresholds are described in the config as a policy choice about how much a district can act on at once, and that framing is on screen. |
| 5 | Does the provenance panel distinguish real / derived / synthetic without blending? | Yes, and it now matters: exposure and vulnerability factors are marked SYNTHETIC_CALIBRATED, history REAL_OPEN, hazard DERIVED. The habitation confidence is explicitly lower than the terrain confidence because of that mix. |
| 6 | Are the same figures identical across screens? | Yes. Habitation hazard composite matches between the Risk Explorer and the Priority screen because both render the same engine output. |
| 7 | Does the opening avoid looking like a generic dashboard? | Yes. Both built screens are map-dominant with a reasoning panel, not a KPI wall. |
| 8 | Is it unambiguous that the SDMA decides? | Yes. The decision-authority line, the scenario disclaimer and the history caveat sit in the drawer footer, and "priority is a ranking score, not a probability" is at the top of the list. |
| 9 | Does it run with the network off? | Yes; nothing new reaches outside. |
| 10 | Can the optimiser breach capacity? | Not applicable yet - and this slice is careful about that. `CAPACITY_BLOCKED` exists in the vocabulary but is never assigned, because no capacity engine has run. Every row instead lists the checks still pending: matched capacity (Engine 4) and route reliability (Engine 5). |
| 11 | Any feature that looks impressive but changes no decision? | No new ones. The waterway-distance surface is still on notice for Slice 6. |
| 12 | Would this survive "walk me through exactly how you got this number"? | Yes. Devgarh Tok, priority 61.1: hazard 0.875 x 0.35 = 0.306, exposure 0.146 x 0.25 = 0.036, vulnerability 0.558 x 0.25 = 0.139, history 0.859 x 0.15 = 0.129. Escalated to Immediate by the named Critical-zone vulnerability override, not by its score. |

### Red-team finding

**The first run of this engine ranked every habitation between 27 and 40, with
nothing reaching Immediate or Short-term, and the cause was a real modelling
error rather than a threshold problem.** Vulnerability was computed as a weighted
average of demographic shares, which lands near 0.2 for any realistic settlement
because those shares are individually small - so a component carrying a declared
weight of 0.25 was contributing about a fifth of that in practice, while hazard
(naturally 0.5-0.9) dominated. The components were on incomparable scales and the
configuration was quietly not doing what it said.

The fix is a stated reference profile: vulnerability is scaled against the score
of an acutely vulnerable settlement (25% elderly, 15% under five, 6% disability,
5% medically dependent, 70% low-income households, 100% weak construction), each
element a DEMO_CONFIG constant. Vulnerability now spans 0.51-0.58 across the
corridor and its weight carries what the config says it carries. A test asserts
that the reference profile scores 1.0 and that a resilient settlement scores
below 0.25.

Two related findings from the same pass. The history factor was dead - a
five-year decay constant against an inventory whose most recent record is nine
years old left every habitation at 0.00-0.05, discarding the one genuinely real
evidence layer in the priority score; the constant is now ten years, with the
reasoning in its description. And the confidence component named
`evidence_recency` was actually measuring how much incident evidence exists
nearby, so it was renamed `evidence_support` to say what it measures.

Standing weakness, recorded rather than hidden: the tier thresholds were revised
after seeing the score distribution. That is legitimate calibration - the
thresholds are a policy statement about how much a district can move at once, and
they are labelled as such - but it is exactly the kind of choice that the weight
sensitivity analysis in Slice 10 has to test rather than assert.

### Verification

- 184 backend tests pass, 40 of them new: exposure against fixed references and
  its saturation point, vulnerability against the reference profile in both
  directions, history decay and radius cut-off, the priority sum against hand
  arithmetic, exact behaviour at all three tier thresholds, both override rules
  firing only inside a Critical zone, and both being named when they fire.
- API tests assert the components arrive separately, that published contributions
  reproduce the published score, that phase totals account for every resident,
  and that pending constraint checks are declared on every row.
- `ruff` clean, gate PASS, `tsc --noEmit` clean, ESLint clean, `next build`
  succeeds, screen driven in a real browser with zero console errors.
