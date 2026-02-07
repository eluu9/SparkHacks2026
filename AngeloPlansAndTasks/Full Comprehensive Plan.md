# Full Comprehensive Plan

Below is a concrete plan for **Angelo (Person 3: LLM + “brains” layer)** that matches the **Prompt.md overview**: (1) clarification gate → (2) kit JSON generation (no exact SKUs) → (3) query generation + fingerprints → all with **structured JSON + schema validation**, and designed so each piece is **testable in isolation**.

---

## **0) Goal and boundaries (what Angelo owns)**

**Owns:**

- llm_service.py provider interface + one working provider (env-configured).
- planner_service.py (clarify gate + task interpretation).
- kit_service.py (kit JSON generation + schema validation).
- “kit → search query” transforms: clean query, expanded query, strict match fingerprint.

**Does not own:**

- Retailer adapters, search execution, matching/price logic (Person 4).
- UI/Jinja templates (Person 2).
- Auth/session/DB plumbing (Person 1), except **document shapes** for conversations + kits the LLM layer consumes/produces.

---

## **1) Contracts first (schemas + typed DTOs)**

### **1.1 JSON Schemas (hard requirements from Prompt.md)**

Create/finish these schema files (already in tree):

- app/schemas/llm_clarify_gate.schema.json
- app/schemas/kit.schema.json

Add (or extend) a schema for query generation outputs:

- app/schemas/search_candidate.schema.json (or rename to item_queries.schema.json)

**Rule:** Every LLM response must validate against a schema before being used.

### **1.2 Python DTO layer (for unit tests and internal clarity)**

Add lightweight dataclasses/Pydantic models that mirror the schemas:

- app/services/dtos.py (or keep in each service)

These DTOs let you test logic without Flask, Mongo, or an actual LLM call.

---

## **2) LLM provider architecture (fully mockable)**

### **2.1**

### **LLMProvider**

### **interface (core)**

In app/services/llm_service.py:

- class LLMProvider(Protocol):
    - generate_json(system_prompt: str, user_prompt: str, schema: dict, temperature: float=0.2) -> dict
- class OpenAIProvider(LLMProvider) (or any working provider via env vars)
- class MockProvider(LLMProvider) for tests (returns fixtures)

**Design rule:** planner_service and kit_service accept a provider instance via dependency injection so unit tests can run with MockProvider.

### **2.2 Prompt templates (versioned)**

Create:

- app/services/prompts/clarify_gate.md
- app/services/prompts/kit_builder.md
- app/services/prompts/query_generator.md

Each prompt file should:

- Describe required JSON shape
- Include strict “no extra keys” instruction (if you enforce)
- Include “do not output SKUs” rule from Prompt.md

---

## **3) Planner service: Clarification Gate (Step 1 in Prompt.md)**

### **3.1 Input → output**

**Inputs:**

- user_prompt: str
- conversation_history: list[{"role","content","ts"}] (from conversations collection)
- optional user_preferences (budget/brands), if available

**Outputs (schema-enforced):**

- need_clarification: bool
- questions: [1..3] if true
- else: task_interpretation with:
    - domain, goals, assumptions, constraints, safety_considerations, regulatory_or_best_practice_notes

### **3.2 Logic**

- The *only* logic in Python is orchestration + schema validation:
    - Build system+user prompt
    - Call provider
    - Validate JSON
    - Return structured result

### **3.3 Tests (no Flask, no DB)**

File: tests/test_planner_gate.py

- **Fixture tests**: feed canned prompts + mocked provider outputs.
- Validate:
    - questions count is 1–3 if clarification
    - no searching occurs here (unit scope: confirm planner doesn’t call search service)
    - schema validation rejects malformed outputs

---

## **4) Kit service: Purchase kit JSON generation (Step 2 in Prompt.md)**

### **4.1 Required output characteristics (from Prompt.md)**

Kit JSON must contain:

- kit_title, summary, sections[] with required section names and item fields:
    - item_key, name, description, sku_type, specs_to_search, quantity_suggestion, priority, safety_notes, compatibility_notes, query_terms, identifier_hints

**Rules to encode in prompts + validations:**

- No exact SKUs as primary mechanism
- Include “Frequently Forgotten Items”
- Reasonable item counts per section

### **4.2 Post-processing (deterministic, testable)**

After schema validation, add **deterministic cleanup**:

- Ensure every item has a stable item_key (slug/uuid). If missing, generate one.
- Normalize section names to canonical set:
    - Essential Items, Safety / PPE, Optional Upgrades, Budget-Friendly Alternatives, Frequently Forgotten Items
- Deduplicate items across sections by normalized (sku_type + core name) to reduce repeats.

### **4.3 Tests**

File: tests/test_schemas.py + tests/test_kit_service.py (add)

- Schema validation: good fixture passes; malformed fails.
- Deterministic cleanup: stable keys, canonical sections, dedupe behavior.

---

## **5) Query generation: kit items → search queries + fingerprints (Step 3)**

### **5.1 Deterministic transform first, LLM optional**

**Prefer deterministic generation** from item fields:

- clean_query = "{brand?} {name} {top specs}" (brand optional unless hinted)
- expanded_query = add synonyms from query_terms + key specs
- strict_match_fingerprint:
    - include normalized brand, mpn, model, upc if present
    - include must-have specs (e.g., “CFM”, “size”, “voltage”) derived from specs_to_search

If you still want LLM help, do it as an optional second pass:

- LLM suggests better query phrasing but must validate against schema.

### **5.2 Output shape**

Per item:

- item_key
- clean_query
- expanded_query
- strict_match_fingerprint: {brand?, mpn?, model?, upc?, must_have_tokens[]}

### **5.3 Tests**

File: tests/test_query_generation.py (add)

- Given a kit fixture, verify:
    - queries are non-empty
    - fingerprints prefer identifiers if present
    - must-have tokens include critical specs when present

---

## **6) Conversation/state hooks (minimal, but testable)**

Prompt.md requires state machine:

- NEW_PROMPT → AWAITING_CLARIFICATION → READY_TO_BUILD_KIT → KIT_READY → PRICE_COMPARE_READY

Angelo’s layer should expose **pure functions** that help Person 1 implement state:

- planner_decide_state(gate_output) -> state
- should_ask_clarifiers(gate_output) -> bool
- merge_clarifications(previous_prompt, answers) -> enriched_prompt (simple concatenation + structure)

**Tests:** tests/test_state_helpers.py (add)

---

## **7) Test harness and fixtures (so everything is individually testable)**

### **7.1 Fixtures folder**

Add:

- tests/fixtures/prompts/ (example user prompts)
- tests/fixtures/llm_outputs/ (valid/invalid JSON for:
    - clarify gate
    - kit builder
    - query generator)

### **7.2 MockProvider modes**

MockProvider supports:

- “return fixture by test name”
- “return invalid JSON” (to test schema failure path)
- “return missing keys” (to test strictness)

### **7.3 CI-friendly tests**

All Angelo tests must run without:

- Mongo running
- network access
- real API keys

---

## **8) Milestones (sequenced to unblock others)**

**Milestone A (Day 1):** Schemas + DTOs + MockProvider

- Everyone can start integrating immediately with stable contracts.

**Milestone B (Day 1–2):** Planner clarify gate end-to-end (mocked)

- Backend can wire the “ask clarifiers” UI path.

**Milestone C (Day 2):** Kit generation end-to-end (mocked) + cleanup

- UI can render kits reliably with stable keys/sections.

**Milestone D (Day 2–3):** Query generation + fingerprints + tests

- Person 4 can plug search + matching using deterministic fingerprints.

**Milestone E (Day 3):** Real provider integration + “golden” regression fixtures

- Keep a small set of “golden” outputs to detect prompt drift.

---

## **9) Deliverables Angelo should commit**

- app/services/llm_service.py (provider + mock)
- app/services/planner_service.py
- app/services/kit_service.py
- app/services/query_service.py (or part of kit_service)
- app/services/prompts/*.md
- Schema tweaks in app/schemas/*
- Tests:
    - tests/test_planner_gate.py
    - tests/test_kit_service.py
    - tests/test_query_generation.py
    - tests/test_schemas.py
    - fixtures under tests/fixtures/*

This structure matches Prompt.md’s required workflow (clarify → kit JSON → query/fingerprint), keeps outputs schema-valid, and makes each unit independently testable without any external dependencies.