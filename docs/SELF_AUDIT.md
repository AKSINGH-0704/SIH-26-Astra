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

---

## Slice 5 - suitability gates, usable area, multi-constraint carrying capacity and bottleneck analysis

**Date:** 2026-09-10
**Commit:** `feat(capacity): multi-constraint carrying-capacity engine with bottleneck analysis`

### What actually works end to end

Every candidate site is now put through five binary suitability gates, measured
for buildable ground on the real land-cover, slope and drainage surfaces, and
assessed for capacity service by service against the published per-person norms.
The effective capacity of a site is the minimum across its services, the
bottleneck is the argmin, and the marginal intervention table says what one unit
of each intervention would unlock and which service would bind next. The
Relocation Sites screen renders all of it: sites ordered availability-first, the
binding service drawn in red as the shortest bar on the screen, the projected
next constraint outlined in amber when an intervention row is hovered, every gate
with its observed value against its threshold, and the tenure limitation stated
before anyone asks for it.

The corridor answer is a real and uncomfortable one: 3 of 6 sites clear every
gate, giving 2,467 people of effective capacity against 2,519 residents assessed
- 52 short - and the marginal table shows exactly which single intervention
closes the gap.

### Gate answers

| # | Question | Answer |
|---|---|---|
| 1 | Is any part of this an LLM guessing, dressed as a computed score? | No. Every capacity figure is `supply / norm` or `supply x norm` against a cited Sphere / PMAY-G constant. The one ML component refines land cover and nothing else. |
| 2 | Can every number on screen be traced in one hop? | Yes. Each service row carries its supply, its norm, the norm's unit, provenance and citation. Effective capacity is the smallest of them; the panel names which. |
| 3 | Is anything displayed that is not backed by a real value? | No. The marginal headline sentence is assembled from `capacity_before`, `capacity_after`, `capacity_gain` and `next_bottleneck` returned by the API - it is a rendering of computed numbers, not prose about them. The hover projection uses the same fields and says explicitly that the bars still show today's assessment. |
| 4 | Is any DEMO_CONFIG constant presented as a government rule? | No. The water, sanitation, health and site-area norms are cited to Sphere; the gate thresholds, the intervention unit sizes and the measurement radius are `DEMO_CONFIG` and appear in `GET /model/config` as such. |
| 5 | Does the provenance panel distinguish real / derived / synthetic without blending? | Yes. Usable area is marked `REAL_OPEN` because it is measured on WorldCover and the Copernicus DEM; the service supplies are `SYNTHETIC_CALIBRATED` and carry that on each row. |
| 6 | Are the same figures identical across screens? | Yes. Population assessed on this screen is the same sum the Priority screen ranks, both from the same fixtures through the same API. |
| 7 | Does the opening avoid looking like a generic dashboard? | The Sites screen is a diagnostic, not a KPI wall: four figures, then the bottleneck bars. The cold open itself is Slice 12. |
| 8 | Is it unambiguous that the SDMA decides? | Yes, and this screen carries the sharpest limitation in the product: ASTRA does not verify land ownership, tenure or encumbrance. It is stated in the header, not buried in a tooltip. |
| 9 | Does it run with the network off? | Yes. The Sentinel-2 composite, the WorldCover clip and the trained refinement raster are all vendored; nothing is fetched at request time. |
| 10 | Can the optimiser breach capacity? | Not yet applicable, but this slice sets the constraint it will be held to: a site failing any gate is excluded from the district total and is marked "not available for allocation", and a test asserts the total excludes it. |
| 11 | Any feature that looks impressive but changes no decision? | The hover projection was one, and was fixed rather than kept - see below. |
| 12 | Would this survive "walk me through exactly how you got this number"? | Yes. Panduri Terrace: 5.24 ha of buildable footprint / 45 m2 per person = 1,164 land capacity; water supply / 15 L/person/day = 812; 812 is the smallest, so effective capacity is 812 and water binds. One borewell at 15,000 L/day raises it to 1,164, at which point land binds. |

### Red-team finding

**The weakest point was the intervention hover, and it was a fabricated-feature
problem hiding inside honest data.** Hovering an intervention row re-coloured the
capacity bars to highlight `next_bottleneck` in the same red used for the current
bottleneck - while the bar lengths, being the present per-service capacities, did
not move. The screen was therefore asserting "this service binds capacity" about
a service that does not, using values that describe a different scenario. Every
number was real; the composition of them was not. Fixed by giving the projected
constraint its own visual language (amber, dashed outline, distinct from red) and
adding a caption that states the projection in full and ends with "Bars show the
assessment as it stands today". This is exactly the class of failure section 2.3
forbids, and it survived one review before being caught.

Two further findings from the same pass:

**The site list was ordered by effective capacity alone, which put a site failing
a hard gate at the top with the largest number on the screen.** A gate failure is
binary - the site is not available at any capacity - so ranking it above the
sites that are available inverted the decision the screen exists to support.
Sites now sort availability-first, gate-failed rows are dimmed and state which
gate they fail, and the detail panel opens with "Not available for allocation".

**The API declared none of the dependencies it actually imports.**
`pyproject.toml` listed FastAPI, Pydantic and uvicorn while the analytical core
has imported numpy, scipy, rasterio, shapely and pyproj since Slice 2. Every
local run worked because the development environment had them; a clean CI
checkout or a Docker build would not have. They are now declared as runtime
dependencies, with the fetch-and-build tooling (`requests`, `pillow`,
`scikit-learn`) in a separate `data` extra, since none of it runs at request
time.

**Standing limitation, recorded rather than hidden:** access capacity is a route
throughput question and the route engine is Slice 6. Rather than assume access is
unconstrained, every site reports it as a pending constraint with the reason, and
a test asserts no `ACCESS` service capacity is ever scored before that engine
exists.

### Verification

- 222 backend tests pass, 33 of them new: per-service arithmetic against hand
  calculation, the norm and citation on every row, argmin selection including a
  deliberate tie, theoretical-vs-effective separation, intervention gain for a
  binding and a non-binding service, intervention ranking, the marginal sentence
  assembled from computed fields, all five gates passing and failing at their
  thresholds, the three-condition usable-area intersection, contiguous-patch
  selection including an unusable centre, no-coverage reported as no coverage
  rather than zero area, refinement agreement driving confidence, and against the
  real corridor: effective never exceeding theoretical, the binding service being
  the lowest, availability-first ordering, district totals excluding gate
  failures, access declared pending, and determinism across two runs.
- `ruff` clean, fixture gate PASS (18 records, 11 datasets), OpenAPI exported and
  TypeScript contracts regenerated, `tsc --noEmit` clean, ESLint clean,
  `next build` succeeds, and the Sites screen was driven in a real browser -
  selection, hover projection and gate-failure states - with zero console errors.

---

## Slice 6 - route reliability, survivability and closure analysis

**Date:** 2026-09-10
**Commit:** `feat(routes): route reliability and survivability analysis`

### What actually works end to end

The OpenStreetMap extract is now a routed graph: 392 tagged road ways split at
their shared OSM nodes into 529 segments, each carrying a class-derived speed, a
bridge flag and hazard exposure sampled from the composite surface along its own
length. Every one of the 72 habitation-to-site pairs is routed twice, and each
route reports travel time, distance, reliability, hazard-exposed length, longest
continuous exposure, bridges crossed and the named stretches of road that decide
whether the journey happens. The Access & Routes screen draws the network
coloured by segment failure probability, draws the selected route, fits the
camera to it, and lets an official close any segment and re-route the whole
corridor against the open network.

Slice 5's one declared gap is closed: ACCESS is now a scored capacity row on
every site, supplied by this engine, and the pending-constraint notice is gone.

The corridor's answer is again a real one. Forty-eight of 72 routes clear the
60% reliability threshold; eleven of twelve habitations can reach a site that is
both suitable and reliably reachable, and one - Bhairaunkhal - cannot, which is
intelligence rather than a missing result. Closing a single 69 m bridge on the
Joshimath-Malari road changes 36 routes, drops 13 below the threshold and leaves
six habitations with nowhere suitable they can reach.

### Gate answers

| # | Question | Answer |
|---|---|---|
| 1 | Is any part of this an LLM guessing, dressed as a computed score? | No. Reliability is a product over segments, each segment's failure probability a documented function of its exposed length and its bridge flag. |
| 2 | Can every number on screen be traced in one hop? | Yes. The route panel lists each point of failure with its own probability and the reason it qualifies, and a test asserts the route reliability equals the product of the published per-leg figures. |
| 3 | Is anything displayed that is not backed by a real value? | No. Segment colours come from the computed `p_fail`; the route line is the geometry the router returned; the closure table is two real assessments compared. |
| 4 | Is any DEMO_CONFIG constant presented as a government rule? | No. Every speed, coefficient and threshold is `DEMO_CONFIG` and served on the assessment with its description. |
| 5 | Does the provenance panel distinguish real / derived / synthetic? | Yes. The road geometry is `REAL_OPEN` OpenStreetMap; the routes computed from it are `DERIVED`, and each route reports what share of it ASTRA actually scored. |
| 6 | Are the same figures identical across screens? | Yes, and one bug here was exactly that - see below. The habitation list, the header totals and the site options are now all read from one assessment object. |
| 7 | Does the opening avoid looking like a generic dashboard? | The screen is map-dominant with a ranked list and a reasoning panel. The cold open is Slice 12. |
| 8 | Is it unambiguous that the SDMA decides? | Yes; the decision-authority line closes the panel, and the closure tool is explicitly a what-if against the open network. |
| 9 | Does it run with the network off? | Yes. The graph is built from the vendored Overpass extract; nothing is fetched at request time. |
| 10 | Can the optimiser breach capacity or use an unusable route? | Not yet applicable, but the constraint it will be held to now exists: a pair below the reliability threshold is `feasible: false`, not merely expensive, and the optimiser slice must consume that. |
| 11 | Any feature that looks impressive but changes no decision? | The fastest-versus-safest contrast came close - see below. It is kept because it is correct and because the reason it rarely fires is itself the finding. |
| 12 | Would this survive "walk me through exactly how you got this number"? | Yes. Simalkot to Sarauli Bench: 23.7 km over 12 segments, 92 min at class speeds, reliability 0.81 as the product of twelve survival probabilities, the two worst being 7,575 m of the Joshimath-Malari road at exposure 0.81 (5.2%) and 4,738 m of the Joshimath-Auli road at 0.79 (4.2%), neither with any way around it. |

### Red-team finding

**The first version of the failure model made a route's survivability a property
of OpenStreetMap's mapping habits rather than of the road.** Failure probability
was a flat per-segment value, so the same stretch of road reported different
reliability depending on how many junctions happened to be mapped along it - and
this corridor has ways running 20 km without one beside ways of 2 m. Fixed by
scaling hazard failure with *exposed length*: `1 - (1 - c) ** (mean exposure x
length / reference)`. A test now asserts directly that one segment and the same
road split into four give identical reliability. The same fix removed a second
distortion, where taking the maximum exposure over a 20 km way saturated every
long road at the worst cell it touched, so the model stopped discriminating
between them.

**The stated SAFEST objective is not a shortest-path problem, and pretending it
was produced a safest route that was less reliable than the fastest one.**
`time x (1 + alpha x risk)` is a property of the finished route; minimising it
edge by edge is not the same thing, and at alpha 20 one pair came back with a
"safest" route seven minutes slower and four points *less* reliable. The engine
now generates three candidate paths - quickest, most reliable, and the
edge-weighted compromise - and scores each against the stated objective, which
costs three Dijkstra runs and guarantees the safest route is never worse. A test
asserts that across the whole corridor.

**Unscored road was being treated as safe road.** The Overpass extract runs past
the study bounding box, and segments outside the scored hazard surface came back
with exposure 0.0 - which the router read as a perfectly safe road and therefore
preferred. Segments with no coverage at all are now dropped from the graph and
counted (`unscored_segments`), and every route reports the share of its length
that was actually scored, with the caveat on screen when it is below 100%.

**One screen was showing two different assessments at once.** After a closure was
evaluated, the habitation list drew its "route blocked" badge from the
closed-network result while the reliability figure beside it still came from the
baseline. Both are true; on the same row they contradict each other. The header
totals, the list and the site options now all read one assessment object, and the
route panel is labelled "open network" while a closure is active.

**Calibration recorded rather than hidden.** The route constants inherited from
Slice 1 were written for a per-segment model and produced a corridor in which no
route at all cleared the threshold. They were re-set for the length-scaled model:
1.5% failure per kilometre of fully exposed road, 1% per bridge structure. These
are planning-horizon figures - whether a road is usable across the weeks a phased
relocation runs - and the descriptions say so. They were chosen so the model
discriminates rather than saturates, which is legitimate calibration and exactly
the kind of choice the Slice 10 sensitivity analysis has to test rather than
accept.

**A finding worth stating plainly:** the fastest and safest routes are the same
road for every pair in this corridor, and that is not a shortcoming of the
router. The valley network has 15 independent loops across 529 segments, and 76%
of segments have no alternative at all - removing one disconnects the network.
There is rarely a second road to choose. The screen says this in its own computed
numbers rather than leaving a feature looking broken, and a test asserts the
claim so it cannot quietly stop being true.

### Verification

- 274 backend tests pass, 41 of them new: travel time against class speeds, the
  failure formula against its documented form, bridge risk as an independent
  factor, compounding rather than doubling with length, split-invariance of route
  reliability, the reliability product, infeasibility below the threshold with a
  stated reason, the off-network walk, the safest route taking a detour and never
  being less reliable, the trade-off sentence carrying its own numbers, closures
  forcing a detour and reporting no path rather than a slow one, continuous
  versus cumulative hazard exposure, points of failure ranked and marked where no
  alternative exists, and against the real corridor: every pair evaluated, every
  site snapped to the main network rather than an isolated stub, both feasible
  and infeasible pairs present, geometry drawn in travel order to within 2% of
  the reported distance, closing the busiest bridge degrading real routes,
  determinism across two runs, and access capacity equal to route count times its
  norm.
- `ruff` clean, fixture gate PASS, OpenAPI exported and TypeScript contracts
  regenerated, `tsc --noEmit` clean, ESLint clean, `next build` succeeds, and the
  Risk, Priority, Sites and Routes screens were all driven in a real browser -
  including selecting a habitation, routing it, closing a point of failure and
  evaluating the impact - with zero console errors.

---

## Slice 7 - constrained relocation optimisation with counterfactual explanations

**Date:** 2026-09-10
**Commit:** `feat(optimizer): constrained relocation optimisation with counterfactual explanations`

### What actually works end to end

Every earlier engine now feeds one decision. OR-Tools CP-SAT assigns people from
habitations to sites, in phases, subject to site effective capacity, a phase
capacity ramp, per-phase travel ceilings, route reliability above the threshold,
suitability gates and a household-integrity floor - all of them hard, none of
them penalties. It minimises a weighted sum of unmet demand scaled by priority,
travel burden, route risk, site overload, livelihood disruption, community
fragmentation and phase delay, and every term is served on the response with the
constant that produced it.

Livelihood disruption is computed, not a kilometre rule: routed commute back to
the habitation's own livelihood centre, the weakest road class on that link, that
link's reliability, and routed travel time from the site to the nearest trunk
road. The four components and their arithmetic are on the assignment panel.

"Why not that site" re-solves with the assignment forced and reports what
happened - either the named hard constraint that removes it, or the objective
delta and who loses their place. Forcing Panduri Sera's 258 residents onto
Sarauli Bench returns "feasible but worse by 8,299 on the objective", with the
before and after objective values, from an actual second solve.

The corridor's plan places 1,144 of 2,519 residents across two sites, and the
reason for the rest is on screen with the constraint named for each habitation.
The headline finding is the one an SDMA can act on: **1,188 assessed places at
Sarauli Bench are unused and only twelve of the 1,375 people still waiting can
reach them.** The binding constraint on this district's relocation plan is the
road, not the site.

### Gate answers

| # | Question | Answer |
|---|---|---|
| 1 | Is any part of this an LLM guessing, dressed as a computed score? | No. The plan is a CP-SAT solution; the explanations are re-solves and constraint records. The one narrative sentence on the screen is assembled from the plan's own totals. |
| 2 | Can every number on screen be traced in one hop? | Yes. Each assignment carries its route, its reliability, its objective contribution and the four-row livelihood table whose contributions sum to the figure above them. The objective is broken out term by term. |
| 3 | Is anything displayed that is not backed by a real value? | No. Assignment lines on the map are the route geometry the solver planned against, not straight lines between centroids. The solver status, wall-clock time and objective are the solver's own. |
| 4 | Is any DEMO_CONFIG constant presented as a government rule? | No. All seven objective weights, the capacity ramp shares, the travel ceilings and the household floor are `DEMO_CONFIG` and served on the plan response. |
| 5 | Does the provenance panel distinguish real / derived / synthetic? | Yes. Livelihood factors are `DERIVED`; the routes they are measured on are derived from `REAL_OPEN` OSM geometry; the populations moved are `SYNTHETIC_CALIBRATED`. |
| 6 | Are the same figures identical across screens? | Yes. Site effective capacity on the plan matches the Sites screen; route reliability matches the Routes screen; both come from the same engines through the same API. |
| 7 | Does the opening avoid looking like a generic dashboard? | The plan screen is map-dominant with a movement list and a reasoning panel. The cold open is Slice 12. |
| 8 | Is it unambiguous that the SDMA decides? | Yes; the decision-authority line closes the panel, and approval and override are Slice 11. |
| 9 | Does it run with the network off? | Yes. CP-SAT is a local library and every input is vendored. |
| 10 | **Can the optimiser output an assignment that breaches capacity, an unusable route or an unsuitable site?** | **No, and it is proved rather than asserted.** `validate()` runs after every solve including the fallback and raises on a capacity breach, a phase-ceiling breach, an assignment that was never an allowed option, one below the household floor, or people who do not add up. Three tests forge each of those plans and assert the exception; a fourth re-checks the real corridor plan against the capacity engine and the route engine directly. |
| 11 | Any feature that looks impressive but changes no decision? | The greedy fallback changes no decision by design - it is demo insurance. It is labelled `FALLBACK` in the response, in the status chip and in a note, and a test asserts it is never better than the solver. |
| 12 | Would this survive "walk me through exactly how you got this number"? | Yes. Panduri Sera to Panduri Terrace, 258 residents: 12.2 km routed over 33 min at 89% reliability; livelihood disruption 0.710 = 0.40x(100.9/90 capped at 1.0) + 0.20x0.70 + 0.20x(1-0.49) + 0.20x(20.5/60). It is in the short-term phase because that is where the phasing engine put Panduri Sera, and it goes to S-05 rather than S-06 because forcing S-06 costs 8,299 more on the objective. |

### Red-team finding

**The map was being destroyed and rebuilt on every render, and it took a
disappearing camera to notice.** `RiskMap` created its MapLibre instance in an
effect whose dependency list included the `onSelectPoint` callback - and every
caller passes an inline arrow, so the dependency changed on every render, the
cleanup ran `map.remove()`, and a fresh map was built. It was invisible until the
counterfactual panel appeared and the camera silently jumped back to the whole
corridor. The callback is now read through a ref and the creation effect depends
only on the things that genuinely define the map. This was costing a full WebGL
teardown per keystroke of state on three screens.

Three modelling findings, all caught by looking at what the plan actually said:

**The site overload penalty was acting as a hard cap.** At the inherited value of
400 per person, overloading a site cost more than the priority-weighted penalty
for leaving someone unmoved, so the solver preferred to strand residents in a red
zone rather than use the last 15% of a site. That is not a plan an SDMA could
defend. Reduced to 60 with the reasoning written into the constant, and a test
asserts that a site's last places are used rather than people being left behind.

**Habitations were locked to a single phase, which made 'Immediate' a label
rather than a plan.** Engine 3 assigns a habitation its phase; the first version
of this engine treated that as its only phase, so a village of 487 people had to
move entirely within the immediate ramp or not at all, and a site 63 minutes away
was rejected outright rather than becoming a short-term destination. A phase is
now the *earliest* phase, and a village may move in stages - which is what a
phased relocation is. Fragmentation still charges splits between places, not
between phases, because a village moved to one site over two phases is not a
divided community.

**Then the opposite problem: nothing made the solver prefer moving people
sooner.** With phases open, the cost of moving a habitation now and in the medium
term were identical, and the solver picked whichever the search reached first.
Adding a delay penalty fixed the ordering - and at the first value tried, 120 per
person per phase, it also cut coverage by a hundred people, because a late move
stopped being worth making at all. That is the wrong trade: delay should
discipline *when* people move, never *whether*. Set to 25, with a test that
asserts the number of people placed is identical with the delay penalty at zero.

**Standing limitation, recorded:** the market-access component of livelihood
disruption uses routed travel time to the nearest trunk road as a proxy for where
a district's markets, banks and offices are. That is a real measurement of a real
thing, but it is a proxy, and the constant says so.

### Verification

- 324 backend tests pass, 50 of them new: capacity, phase-ramp and travel-ceiling
  constraints; priority winning contested capacity; cheaper routes and less
  disruptive destinations preferred; the household floor; staged moves to one
  site counting as one destination; splits happening when they place more people;
  reproducibility across runs; the delay penalty ordering without shrinking the
  plan; three forged plans rejected by post-solve validation; the fallback
  labelling itself and never beating the solver; livelihood disruption as a
  weighted sum, at zero for a perfect destination, worse on a worse road class at
  the same travel time, at maximum for an unreachable livelihood centre, and
  demonstrably not a distance rule; and on the real corridor: every resident
  accounted for, every rejected pairing naming its constraint, unmet demand
  explained rather than counted, stranded capacity measured against who can reach
  it, blocked habitations flagged, and counterfactuals for both a blocked and an
  allowed site.
- `ruff` clean, fixture gate PASS, OpenAPI exported and TypeScript contracts
  regenerated, `tsc --noEmit` clean, ESLint clean, `next build` succeeds, and the
  Plan screen was driven in a real browser - selecting a movement, watching the
  camera hold, and running a counterfactual re-solve - with zero console errors.
