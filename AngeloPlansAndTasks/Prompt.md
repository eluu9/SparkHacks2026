# Prompt

Below is a “single paste” comprehensive prompt you can give to an AI coder to generate the full Flask + MongoDB AI shopping web app (frontend + backend) with multi-retailer search using **free APIs only**, smart clarifying questions, kit-building, and **exact-item** price comparison (via UPC/GTIN/MPN + normalization).

You can paste it as-is into another model.

---

## **Comprehensive Build Prompt: “AI Shopping Kit Builder” (Flask + MongoDB)**

You are an expert full-stack engineer and product designer. Build a production-ready **AI shopping web application** using:

- **Flask** for backend and server-rendered frontend (Jinja templates) *or* Flask API + minimal JS (your choice, but keep it simple).
- **MongoDB** for user accounts, sessions/tokens, saved kits, item comparisons, and search logs.
- A **pluggable LLM provider** (implement an interface; include at least one working provider using environment variables).
- Multi-retailer search via **free APIs only** (no paid keys required). Do **not** scrape websites. If a retailer has no free API, skip them. Use public/free sources.
- A workflow that accepts **one short user prompt** (examples: “I need to replace a bathroom exhaust fan.” “We’re setting up a small workshop.” “I need a new laptop.”) and then the AI does the rest.

### **Core Product Behavior**

### **Input**

User provides one natural-language prompt describing what they need.

### **Output (what user sees)**

The app produces:

1. **A complete purchase kit** organized into sections:
    - 🛠️ Essential Items
    - 🔒 Safety / PPE (recommended)
    - ✨ Optional Upgrades
    - 💵 Budget-Friendly Alternatives
    - 📦 Frequently Forgotten Items
2. For each item, provide **cart-ready format without exact SKU scraping**:
    - Item name
    - Short description
    - **Recommended “SKU type” / category** (NOT exact SKUs)
    - Key specs to search for (dimensions, ratings, compatibility)
    - Suggested quantity
3. **Price comparison** feature:
    - Attempt to find the **lowest price for the same exact item** across supported retailers.
    - “Same exact item” must be determined by strong identifiers first (UPC/GTIN/EAN, MPN, model number). If missing, fall back to high-confidence normalization + fuzzy match with strict thresholds and clearly label uncertainty.
4. **Comparison mode**:
    - Users can ask “Aluminum vs steel ladders?” “PVC vs copper?” “Which gloves for battery acid?”
    - AI outputs:
        - Comparison table
        - Recommendation
        - Safety notes
        - Cost considerations
        - Durability/compatibility notes
5. **Clarifying questions only when needed**:
    - If task is underspecified, ask **1–3 short 1-sentence clarifiers** max, and do not search until answered.
    - Examples: “Indoor or outdoor use?” “Light/medium/heavy duty?” “What size bathroom (sq ft)?” “Windows/Mac?” “Budget range?”

### **Architectural Requirements**

### **Pages / UX**

- Landing page with a single prompt box + examples.
- Results page showing the kit sections with expandable item details.
- “Price Compare” view per item (table of sources, price, shipping if available, link).
- “Ask a follow-up” box that continues the conversation (stored context).
- Saved kits page (“My Kits”).
- Login/register pages.

Keep UI clean and accessible:

- High contrast, readable typography.
- Works on mobile.
- Clear section headers and collapsible cards.

### **Backend Structure**

Implement a clean modular layout:

- app.py / create_app() factory
- routes/ (auth, kit, compare, api)
- services/
    - llm_service.py (provider interface)
    - planner_service.py (intent + clarification detection)
    - kit_service.py (kit schema generation + validation)
    - search_service.py (multi-source product search)
    - match_service.py (exact-item matching + confidence)
    - price_service.py (price comparisons + caching)
- models/ or db/ for Mongo helpers
- templates/ and static/ (minimal JS only if needed)

### **MongoDB Collections (minimum)**

Define schema-like structures (Mongo is flexible, but standardize documents):

1. users
    - _id, email, password_hash, created_at
    - optional: preferences (brands, shipping, budget)
2. sessions (or use Flask-Login + server sessions)
3. conversations
    - _id, user_id, messages [{role, content, ts}], state (e.g., awaiting_clarification)
4. kits
    - _id, user_id, prompt, clarifications, kit_json, created_at, updated_at
5. items
    - normalized catalog entries generated from kit items (optional but helpful)
6. search_results_cache
    - keyed by query + source + locale; TTL index
7. price_comparisons
    - per item: candidates, match reasons, confidence, selected_lowest

Add proper indexes (email unique, TTL cache, user_id lookups).

### **LLM Behavior Design**

You must implement **structured outputs** from the LLM to avoid messy parsing. Use JSON schema enforcement in code (Pydantic or jsonschema).

### **Step 1: Task Understanding + Clarification Gate**

Given the user prompt and conversation history, the LLM must output either:

- need_clarification: true + questions: [...] (1–3)
    
    OR
    
- need_clarification: false + a structured “task interpretation”.

Interpretation must include:

- domain (home repair, workshop, electronics, etc.)
- goals
- assumptions
- constraints (budget, environment, skill level, compatibility)
- safety_considerations (PPE, hazards)
- regulatory_or_best_practice_notes (generalized, non-legal disclaimers)

### **Step 2: Generate Purchase Kit (No exact SKUs)**

LLM outputs a JSON object:

```
{
  "kit_title": "…",
  "summary": "…",
  "sections": [
    {
      "name": "Essential Items",
      "items": [
        {
          "item_key": "slug_or_uuid",
          "name": "…",
          "description": "…",
          "sku_type": "category/type only",
          "specs_to_search": ["…", "…"],
          "quantity_suggestion": "…",
          "priority": "essential|recommended|optional",
          "safety_notes": ["…"],
          "compatibility_notes": ["…"],
          "query_terms": ["…"],
          "identifier_hints": {
            "mpn": null,
            "model": null,
            "upc": null
          }
        }
      ]
    }
  ]
}
```

Rules:

- Provide realistic quantities.
- Include “frequently forgotten items”.
- Include at least 3–8 essentials, 2–6 PPE, 2–6 optional upgrades, 2–6 budget alternatives, 3–10 forgotten items depending on task complexity.
- Do not invent standards citations. Use general best practices language.

### **Step 3: Turn Kit Items into Search Queries**

For each item produce:

- a “clean query string”
- an expanded query with synonyms and specs
- a “strict match fingerprint” (for exact match attempts) based on model/MPN/UPC when possible

### **Multi-Retailer Search (Free APIs Only)**

Implement product search adapters. Use whichever free sources are available **without paid keys**. Prefer:

- Public/free product data sources (e.g., Open Food Facts is food-only; only use if relevant).
- Marketplace or affiliate APIs that have free tiers **without requiring paid approval** (if truly free for dev use).
- If a source requires approval/payment, exclude it.

Implementation requirements:

- Each adapter returns normalized product candidates:
    - title, price, currency, availability (if any), url, image, brand, model, mpn, upc/ean, seller/source, shipping_cost (if any), raw payload.
- Add rate limiting and caching (Mongo TTL).
- If no APIs return results, the UI must gracefully show: “No free API sources returned matches; refine query or add identifiers.”

### **Exact-Item Price Comparison Logic**

Implement a deterministic matcher that ranks candidates:

1. **Strong match**: UPC/GTIN exact match
2. **Medium match**: MPN + brand exact (normalized)
3. **Model number + brand** exact-ish (normalized)
4. **Fallback**: title similarity + key specs overlap with strict thresholds

Output:

- confidence from 0–1
- match_reason list
- Highlight if it’s not exact (confidence < threshold)

Then select the lowest total price:

- price + shipping (if shipping available; else price only)
- show disclaimer if shipping unknown

### **Conversation / State Machine**

Implement a minimal conversation state:

- NEW_PROMPT
- AWAITING_CLARIFICATION
- READY_TO_BUILD_KIT
- KIT_READY
- PRICE_COMPARE_READY

Flow:

1. User prompt → LLM “clarify gate”
2. If clarifications needed → show questions, store state
3. After user answers → build kit → display
4. User can click “Compare Prices” per item → run search + matching → display
5. User can ask follow-up questions; preserve context in conversations

### **Security and Ops**

- Password hashing (bcrypt/argon2).
- Session management (Flask-Login or secure signed cookies).
- CSRF protection for forms.
- Input validation and output escaping.
- Environment variables for secrets.
- Provide .env.example.
- Provide a Dockerfile and docker-compose.yml for Flask + Mongo.
- Provide a requirements.txt.
- Logging with request IDs.
- Basic error pages.

### **Deliverables (You must output all of these)**

1. Complete repository-style code listing with file tree.
2. Full code for each file.
3. Setup instructions:
    - local venv run
    - docker compose run
4. Example screenshots description (text only) of key pages.
5. A small suite of tests:
    - unit tests for matcher
    - unit tests for schema validation
6. Seed data script (optional) for demo user + demo kit.

### **Constraints / Non-negotiables**

- Do not scrape retailer pages.
- Do not output exact SKUs as the primary mechanism. The kit must be **SKU-type + specs**.
- Ask clarifying questions before searching if needed.
- Price comparison must attempt to find the **same exact item**, not “similar”.
- Use free APIs only; if uncertain, implement adapter stubs with clear TODOs and show how to add sources later.
- Keep the UI simple and functional.

### **Implementation Hint: Provide Two Modes**

- **General Kit Mode** (no exact identifiers required)
- **Exact Match Mode** (user optionally provides brand/model/UPC to lock exact matching)

### **Include These Example Prompts in the UI**

- “I need to replace a bathroom exhaust fan.”
- “We’re setting up a small workshop.”
- “I want gloves for handling chemicals.”
- “We need mounts for LED high bays.”
- “Buying tools for HVAC installation. Help?”
- “I need a new laptop.”

### **Final Output Format**

Start with:

- Project summary
- File tree

Then provide each file in a separate code block with its path as a header.

---

## **Optional Add-on (If time): “Retailers” Page**

A page listing currently enabled free API sources, their rate limits, and coverage.

---

If you follow the above, produce the complete app.

---

### **Notes you can keep (for the AI coder)**

- Use JSON schema validation to enforce LLM outputs.
- Build robust normalization functions for brand/model/MPN parsing.
- Caching avoids rate limit issues and speeds demos.

---

If you want, I can also tailor this prompt to a specific LLM (OpenAI / local model) and pick a concrete set of free sources you’re okay with, but the prompt above is designed to work even when free-source availability is limited.