# Angelo's TODO List — LLM + "Brains" Layer

> Generated from Full Comprehensive Plan.md  
> Owner: Angelo (Person 3)  
> Scope: LLM service, planner/clarify gate, kit generation, query generation, schemas, tests

---

## Milestone A — Schemas + DTOs + MockProvider (Day 1)

- [ ] **A1.** Create `app/schemas/llm_clarify_gate.schema.json` — define JSON schema for clarify gate output (`need_clarification`, `questions`, `task_interpretation` with domain/goals/assumptions/constraints/safety/regulatory fields)
- [ ] **A2.** Create `app/schemas/kit.schema.json` — define JSON schema for kit output (`kit_title`, `summary`, `sections[]` with all required item fields: `item_key`, `name`, `description`, `sku_type`, `specs_to_search`, `quantity_suggestion`, `priority`, `safety_notes`, `compatibility_notes`, `query_terms`, `identifier_hints`)
- [ ] **A3.** Create/extend `app/schemas/search_candidate.schema.json` (or `item_queries.schema.json`) — schema for query generation outputs (`item_key`, `clean_query`, `expanded_query`, `strict_match_fingerprint`)
- [ ] **A4.** Create `app/services/dtos.py` — lightweight dataclasses/Pydantic models mirroring the schemas (no Flask/Mongo dependency)
- [ ] **A5.** Create `app/services/llm_service.py` — define `LLMProvider` protocol with `generate_json(system_prompt, user_prompt, schema, temperature) -> dict`
- [ ] **A6.** Implement `OpenAIProvider(LLMProvider)` in `llm_service.py` — working provider configured via env vars
- [ ] **A7.** Implement `MockProvider(LLMProvider)` in `llm_service.py` — returns test fixtures, supports modes: "return fixture by test name", "return invalid JSON", "return missing keys"
- [ ] **A8.** Create test fixtures directory structure: `tests/fixtures/prompts/`, `tests/fixtures/llm_outputs/` with valid and invalid JSON samples for clarify gate, kit builder, and query generator

---

## Milestone B — Planner / Clarify Gate (Day 1–2)

- [ ] **B1.** Create prompt template `app/services/prompts/clarify_gate.md` — describe required JSON shape, strict rules, "no extra keys", include conversation history format
- [ ] **B2.** Implement `app/services/planner_service.py` — orchestration: build system+user prompt → call provider → validate JSON against schema → return structured result
  - Input: `user_prompt`, `conversation_history`, optional `user_preferences`
  - Output: `{need_clarification, questions}` OR `{need_clarification: false, task_interpretation}`
- [ ] **B3.** Implement state helper pure functions in planner_service (or separate module):
  - `planner_decide_state(gate_output) -> state`
  - `should_ask_clarifiers(gate_output) -> bool`
  - `merge_clarifications(previous_prompt, answers) -> enriched_prompt`
- [ ] **B4.** Write `tests/test_planner_gate.py`:
  - Feed canned prompts + mocked provider outputs
  - Validate questions count is 1–3 when clarification needed
  - Confirm planner doesn't call search service (unit scope)
  - Schema validation rejects malformed outputs
- [ ] **B5.** Write `tests/test_state_helpers.py`:
  - Test `planner_decide_state` returns correct states (NEW_PROMPT, AWAITING_CLARIFICATION, READY_TO_BUILD_KIT, etc.)
  - Test `should_ask_clarifiers` logic
  - Test `merge_clarifications` produces well-structured enriched prompt

---

## Milestone C — Kit Generation (Day 2)

- [ ] **C1.** Create prompt template `app/services/prompts/kit_builder.md` — required JSON shape, "no exact SKUs" rule, section names, item count guidelines, "frequently forgotten items" requirement
- [ ] **C2.** Implement `app/services/kit_service.py` — call LLM with task interpretation → validate kit JSON against schema → run deterministic post-processing
- [ ] **C3.** Implement deterministic post-processing in kit_service:
  - Ensure every item has a stable `item_key` (slug/uuid); generate if missing
  - Normalize section names to canonical set: Essential Items, Safety / PPE, Optional Upgrades, Budget-Friendly Alternatives, Frequently Forgotten Items
  - Deduplicate items across sections by normalized (sku_type + core name)
- [ ] **C4.** Write `tests/test_schemas.py`:
  - Schema validation: good fixture passes, malformed fails (for both clarify gate and kit schemas)
- [ ] **C5.** Write `tests/test_kit_service.py`:
  - Test stable key generation
  - Test canonical section normalization
  - Test deduplication behavior
  - Test full kit generation with MockProvider

---

## Milestone D — Query Generation + Fingerprints (Day 2–3)

- [ ] **D1.** Create prompt template `app/services/prompts/query_generator.md` (optional, for LLM-assisted query refinement)
- [ ] **D2.** Implement `app/services/query_service.py` (or integrate into kit_service) — deterministic query generation from item fields:
  - `clean_query` = `"{brand?} {name} {top specs}"`
  - `expanded_query` = add synonyms from `query_terms` + key specs
  - `strict_match_fingerprint` = `{brand?, mpn?, model?, upc?, must_have_tokens[]}`
- [ ] **D3.** Implement optional LLM second pass for better query phrasing (validate against schema)
- [ ] **D4.** Write `tests/test_query_generation.py`:
  - Given a kit fixture, verify queries are non-empty
  - Verify fingerprints prefer identifiers when present
  - Verify `must_have_tokens` include critical specs when present
  - Validate output against `search_candidate.schema.json`

---

## Milestone E — Real Provider Integration + Regression (Day 3)

- [ ] **E1.** Test `OpenAIProvider` end-to-end with real API key (manual/CI-optional)
- [ ] **E2.** Create "golden" regression fixtures — small set of known-good LLM outputs to detect prompt drift
- [ ] **E3.** Add regression test that compares real provider output structure against golden fixtures (optional CI, requires key)
- [ ] **E4.** Verify all tests run without Mongo, network access, or real API keys (CI-friendly)

---

## Cross-Cutting / Ongoing

- [ ] **X1.** Ensure all LLM prompt templates include "do not output exact SKUs" instruction
- [ ] **X2.** Ensure all provider calls have proper error handling (timeouts, malformed responses, rate limits)
- [ ] **X3.** Add logging with request IDs to all service calls
- [ ] **X4.** Document schema decisions in `docs/DATA_MODEL.md` (coordinate with Person 1)
- [ ] **X5.** Coordinate with Person 4 on query/fingerprint format for search + matching integration
- [ ] **X6.** Coordinate with Person 2 on kit JSON structure for UI rendering

---

## Files Angelo Must Commit

| File | Milestone |
|------|-----------|
| `app/schemas/llm_clarify_gate.schema.json` | A |
| `app/schemas/kit.schema.json` | A |
| `app/schemas/search_candidate.schema.json` | A |
| `app/services/dtos.py` | A |
| `app/services/llm_service.py` | A |
| `app/services/planner_service.py` | B |
| `app/services/kit_service.py` | C |
| `app/services/query_service.py` | D |
| `app/services/prompts/clarify_gate.md` | B |
| `app/services/prompts/kit_builder.md` | C |
| `app/services/prompts/query_generator.md` | D |
| `tests/test_planner_gate.py` | B |
| `tests/test_state_helpers.py` | B |
| `tests/test_schemas.py` | C |
| `tests/test_kit_service.py` | C |
| `tests/test_query_generation.py` | D |
| `tests/fixtures/prompts/*` | A |
| `tests/fixtures/llm_outputs/*` | A |
