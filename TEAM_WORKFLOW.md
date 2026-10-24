# Team Parallel Development Guide (5-Member Zero-Conflict Workflow)

Welcome to the **Synapse AI Content Creator Marketplace** parallel sprint!
This project template is engineered for **5 developers working simultaneously with Antigravity AI agents** without merge conflicts.

---

## 🚀 1. Fast Onboarding: How Each Member Starts

When you clone this repository, run the role setup script:
```bash
python setup_role.py --role <1|2|3|4|5>
```

This will automatically:
1. Create and switch to your dedicated git branch (`member-<N>/...`).
2. Display your mission and isolated target files.
3. Provide the exact prompt to pass to your Antigravity agent.

---

## 👥 2. 5-Member Role & Ownership Matrix

| Member | Branch Name | Agent Playbook | Target Files to Implement | Abstract Interface Contract |
| :--- | :--- | :--- | :--- | :--- |
| **Member 1** (Architect & Lead) | `member-1/core-contracts` | `AGENT_ROLE_1_CORE.md` | `app/db/database.py`, `app/db/seed.py`, `app/models/sidecar.py`, `app/templates/base.html` | DB migrations, sidecar schemas, role-based navbar, authentication |
| **Member 2** (Creator Profiles & Portfolios) | `member-2/creator-portfolios` | `AGENT_ROLE_2_CREATOR.md` | `app/models/creator.py`, `app/models/portfolio.py`, `app/models/connection.py`, `app/services/creator_service.py`, `app/services/connection_service.py`, `app/api/creators.py`, `app/api/connections.py` | Mandatory 2 uploads rule, pinning best works (max 3), creator connections, profile view counters |
| **Member 3** (Company Reviews & Currency) | `member-3/company-reviews-currency` | `AGENT_ROLE_3_COMPANY.md` | `app/models/company.py`, `app/models/review.py`, `app/services/company_service.py`, `app/services/review_service.py`, `app/api/companies.py`, `app/api/reviews.py`, `app/static/js/main.js` | Distinct company profile, company reviews & ratings for creators, primary INR (₹) & USD ($) converter |
| **Member 4** (Semantic Search & NER) | `member-4/semantic-search-ner` | `AGENT_ROLE_4_SEARCH_NER.md` | `app/services/embedding_service.py`, `app/services/ner_service.py`, `app/services/hybrid_search_service.py` | `BaseEmbeddingService`, `BaseNERService`, FastEmbed ONNX vectors, canonical dictionary, RRF search |
| **Member 5** (Ranking Engine & AI Briefs UI) | `member-5/ranking-rag-ui` | `AGENT_ROLE_5_RANKING_UI.md` | `app/services/ranking_service.py`, `app/services/rag_service.py`, `app/templates/ai/brief_builder.html`, `app/templates/jobs/` | `BaseRankingService`, `BaseRAGService`, equal 20% 5-factor ranking engine, Groq RAG brief builder |

---

## 🛠️ 3. Member Implementation Summaries

### 👨‍💻 Member 1: Core Architecture & Lead
- **Files**: `app/db/database.py`, `app/db/seed.py`, `app/models/sidecar.py`, `app/templates/base.html`.
- **Tasks**: Enforce role-based navbar (creators don't see Discover Creators; companies don't see Brands & Companies). Maintain auto-migrations and realistic seeds.

### 👨‍💻 Member 2: Creator Profiles, Portfolios & Connections
- **Files**: `app/models/creator.py`, `app/models/portfolio.py`, `app/models/connection.py`, `app/services/creator_service.py`, `app/services/connection_service.py`.
- **Tasks**: Enforce mandatory 2 portfolio uploads rule (draft vs published status). Implement pinning best works (max 3). Implement mutual creator connections and view counters.

### 👨‍💻 Member 3: Company Profiles, Reviews & Currency
- **Files**: `app/models/company.py`, `app/models/review.py`, `app/services/review_service.py`, `app/static/js/main.js`.
- **Tasks**: Implement distinct company profile (logo, location, social links). Implement 1-5 star company reviews for creators. Maintain primary INR (₹) rates and global navbar toggle for USD ($).

### 👨‍💻 Member 4: Semantic Search & Canonical NER Engine
- **Files**: `app/services/embedding_service.py`, `app/services/ner_service.py`, `app/services/hybrid_search_service.py`.
- **Tasks**: Implement FastEmbed ONNX local vector embeddings (`bge-small-en-v1.5`). Maintain canonical tool dictionary & regex/LLM extraction. Implement Reciprocal Rank Fusion (RRF) for hybrid search.

### 👨‍💻 Member 5: Ranking Engine & AI Brief Builder UI
- **Files**: `app/services/ranking_service.py`, `app/services/rag_service.py`, `app/templates/ai/brief_builder.html`.
- **Tasks**: Implement the 5-factor ranking engine with equal 20% weights:
  $$\text{Score} = 0.20 \times S_{\text{semantic}} + 0.20 \times S_{\text{tools}} + 0.20 \times S_{\text{reviews}} + 0.20 \times S_{\text{verification}} + 0.20 \times S_{\text{views}}$$
  Implement Groq RAG brief builder with grounded citations and UI match explainer modals.

---

## 🧪 4. Testing Your Implementation

Before submitting any Pull Request, verify all tests pass:
```bash
python -m pytest
```

---

## 🔒 5. Golden Rules for Parallel Work
1. **Never edit files outside your assigned module** without coordinating with Member 1.
2. **Never change the Pydantic schemas** in `app/schemas/advanced.py` without team consensus.
3. **Commit often** to your assigned branch (`member-<N>/...`).
4. **All embeddings run locally via FastEmbed** (zero cost, no GPU required).
