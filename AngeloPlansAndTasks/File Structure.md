# File Structure

ai-shopping-kit-builder/
├── [README.md](http://readme.md/)
├── .gitignore
├── .env.example
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── [wsgi.py](http://wsgi.py/)
├── scripts/
│   ├── seed_demo.py
│   └── create_indexes.py
├── app/
│   ├── **init**.py
│   ├── [config.py](http://config.py/)
│   ├── [extensions.py](http://extensions.py/)
│   ├── utils/
│   │   ├── **init**.py
│   │   ├── [logging.py](http://logging.py/)
│   │   ├── [security.py](http://security.py/)
│   │   ├── [validators.py](http://validators.py/)
│   │   ├── [normalization.py](http://normalization.py/)
│   │   └── [ids.py](http://ids.py/)
│   ├── db/
│   │   ├── **init**.py
│   │   ├── [mongo.py](http://mongo.py/)
│   │   └── repositories/
│   │       ├── **init**.py
│   │       ├── users_repo.py
│   │       ├── sessions_repo.py
│   │       ├── conversations_repo.py
│   │       ├── kits_repo.py
│   │       ├── cache_repo.py
│   │       └── comparisons_repo.py
│   ├── schemas/
│   │   ├── **init**.py
│   │   ├── llm_clarify_gate.schema.json
│   │   ├── kit.schema.json
│   │   ├── search_candidate.schema.json
│   │   └── price_comparison.schema.json
│   ├── routes/
│   │   ├── **init**.py
│   │   ├── [auth.py](http://auth.py/)
│   │   ├── [kit.py](http://kit.py/)
│   │   ├── [compare.py](http://compare.py/)
│   │   └── [api.py](http://api.py/)
│   ├── services/
│   │   ├── **init**.py
│   │   ├── llm_service.py
│   │   ├── planner_service.py
│   │   ├── kit_service.py
│   │   ├── search_service.py
│   │   ├── match_service.py
│   │   ├── price_service.py
│   │   └── conversation_service.py
│   ├── adapters/
│   │   ├── **init**.py
│   │   ├── base_adapter.py
│   │   ├── enabled_sources.py
│   │   └── sources/
│   │       ├── **init**.py
│   │       ├── example_free_source.py
│   │       └── open_data_source_optional.py
│   ├── templates/
│   │   ├── base.html
│   │   ├── landing.html
│   │   ├── login.html
│   │   ├── register.html
│   │   ├── kits.html
│   │   ├── kit_result.html
│   │   ├── clarify.html
│   │   ├── compare_item.html
│   │   ├── retailers.html
│   │   └── error.html
│   └── static/
│       ├── css/
│       │   └── styles.css
│       ├── js/
│       │   └── ui.js
│       └── img/
│           └── logo.svg
├── tests/
│   ├── **init**.py
│   ├── test_matcher.py
│   ├── test_schemas.py
│   ├── test_normalization.py
│   └── test_planner_gate.py
└── docs/
├── UX_NOTES.md
├── API_SOURCES.md
└── DATA_MODEL.md