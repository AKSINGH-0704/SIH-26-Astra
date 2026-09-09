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
