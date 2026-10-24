# Team Shared Contract & Architecture (5-Member Parallel Workflow)

This document is the **immutable contract** between all 5 developers and their Antigravity AI agents.
It defines database schemas, Pydantic contracts, abstract service interfaces, API routes, and branch boundaries so all team members can build in parallel with **zero merge conflicts**.

---

## 👥 1. 5-Member Role & Ownership Matrix

| Member | Branch Name | Agent Playbook | Target Files to Implement | Abstract Interface Contract |
| :--- | :--- | :--- | :--- | :--- |
| **Member 1** (Architect & Lead) | `member-1/core-contracts` | `AGENT_ROLE_1_CORE.md` | `app/db/database.py`, `app/db/seed.py`, `app/models/sidecar.py`, `app/templates/base.html` | DB migrations, sidecar schemas, role-based navbar, authentication |
| **Member 2** (Creator Profiles & Portfolios) | `member-2/creator-portfolios` | `AGENT_ROLE_2_CREATOR.md` | `app/models/creator.py`, `app/models/portfolio.py`, `app/models/connection.py`, `app/services/creator_service.py`, `app/services/connection_service.py`, `app/api/creators.py`, `app/api/connections.py` | Mandatory 2 uploads rule, pinning best works (max 3), creator connections, profile view counters |
| **Member 3** (Company Reviews & Currency) | `member-3/company-reviews-currency` | `AGENT_ROLE_3_COMPANY.md` | `app/models/company.py`, `app/models/review.py`, `app/services/company_service.py`, `app/services/review_service.py`, `app/api/companies.py`, `app/api/reviews.py`, `app/static/js/main.js` | Distinct company profile, company reviews & ratings for creators, primary INR (₹) & USD ($) converter |
| **Member 4** (Semantic Search & NER) | `member-4/semantic-search-ner` | `AGENT_ROLE_4_SEARCH_NER.md` | `app/services/embedding_service.py`, `app/services/ner_service.py`, `app/services/hybrid_search_service.py` | `BaseEmbeddingService`, `BaseNERService`, FastEmbed ONNX vectors, canonical dictionary, RRF search |
| **Member 5** (Ranking Engine & AI Briefs UI) | `member-5/ranking-rag-ui` | `AGENT_ROLE_5_RANKING_UI.md` | `app/services/ranking_service.py`, `app/services/rag_service.py`, `app/templates/ai/brief_builder.html`, `app/templates/jobs/` | `BaseRankingService`, `BaseRAGService`, equal 20% 5-factor ranking engine, Groq RAG brief builder |

---

## 🔒 2. Golden Rules for Zero-Conflict Development

1. **Only edit your assigned target files**. Never edit another member's target files without explicit coordination.
2. **Never change Pydantic schemas** in `app/schemas/advanced.py` without team consensus.
3. **Always use Mock Stubs on Day 1**. If your backend ML code is not done, your mock stub in `app/services/stubs/` allows other members to test UI and APIs immediately.
4. **All monetary rates and budgets must be stored in INR (₹)**. Frontend components use `data-inr="<amount>"` for dynamic USD conversion.
5. **Verify with test suite before committing**:
   ```bash
   python -m pytest
   ```

---

## 📐 3. Data Model Specifications

### A. Creator Profile (`app/models/creator.py`)
- `status`: `"draft"` (if `< 2` uploads) vs `"published"` (if `>= 2` uploads). Mandatory 2 uploads rule.
- `views_count`: Total profile visits (session de-duplicated).
- `hourly_rate_inr`: Base hourly rate in Indian Rupees (₹).
- `tools_models`: Comma-separated AI tools used (e.g. `Runway Gen-3, Midjourney v6, ComfyUI, Flux.1`).
- `specifications`: JSON-encoded production specs (`resolution`, `max_fps`, `aspect_ratios`, `hardware`, `lora_training`).
- `social_links`: JSON-encoded social links (`twitter`, `instagram`, `youtube`, `artstation`, `github`, `linkedin`, `website`).

### B. Company Profile (`app/models/company.py`)
- `company_name`: Official business name.
- `industry`: Sector focus (e.g. `Athletic Apparel`, `Advertising & VFX`).
- `logo_url`: High-resolution logo URL.
- `location`: Company headquarters / remote base.
- `social_links`: JSON-encoded links (`linkedin`, `twitter`, `website`).

### C. Creator Review (`app/models/review.py`)
- `creator_id`: Foreign key to `creator_profiles.id`.
- `company_id`: Foreign key to `company_profiles.id`.
- `rating`: Integer from 1 to 5 stars.
- `project_title`: Campaign / brief title.
- `comment`: Detailed performance feedback.
- `tools_used`: AI tools utilized.
- `is_verified_engagement`: Boolean flag for platform-verified contracts.

### D. Creator Connection (`app/models/connection.py`)
- `requester_id`: Foreign key to `creator_profiles.id`.
- `receiver_id`: Foreign key to `creator_profiles.id`.
- `status`: `"pending"`, `"accepted"`, `"rejected"`.
- Unique pair constraint on `(requester_id, receiver_id)`.

### E. Portfolio Item (`app/models/portfolio.py`)
- `is_pinned`: Boolean flag (max 3 pinned items per creator).
- `pin_order`: Priority sort integer (1, 2, 3).
- `views_count`: Item impressions count.

### F. Creative Brief / Job (`app/models/job.py`)
- `budget_inr`: Primary budget in INR (₹).
- `budget_range`: Formatted display range (e.g. `"₹3,50,000 - ₹5,00,000"`).
- `commercial_use`: Commercial buyout terms (e.g. `"Full Commercial Buyout"`).

---

## ⚡ 4. Core Algorithms & Techniques Specification

### 1. Semantic Search (`BaseEmbeddingService`)
- **Technology**: FastEmbed (`BAAI/bge-small-en-v1.5` via ONNX).
- **Zero Cost / Zero GPU**: Local in-process embeddings.
- **Sidecar Storage**: `embedding_records` table storing JSON float vectors.
- **Metric**: Cosine similarity via NumPy dot product.

### 2. Named Entity Recognition (`BaseNERService`)
- **Canonical Dictionaries**: `CANONICAL_TOOLS`, `CANONICAL_FORMATS`, `CANONICAL_LICENSES`.
- **Extraction**: Fast regex pattern matching with Groq `llama-3.3-70b-versatile` structured JSON fallback.
- **Provenance Tagging**: Flag entities as `'creator_claim'`, `'platform_verified'`, or `'brief_requirement'`.

### 3. Hybrid Search with Reciprocal Rank Fusion (`HybridSearchService`)
- Combines Keyword Search (SQL `LIKE` on title, tools, skills) + Vector Similarity.
- **Fusion Formula**:
  $$RRF\_Score(d) = \frac{1}{60 + rank_{keyword}(d)} + \frac{1}{60 + rank_{vector}(d)}$$

### 4. Creator-Brief Ranking Engine (`DeterministicRankingService`)
- **Stage 1 (Hard Gate)**: Excludes creators lacking required aspect ratio or commercial buyout rights.
- **Stage 2 (5 Equal 20% Signals)**:
  $$\text{Score} = 0.20 \times S_{\text{semantic}} + 0.20 \times S_{\text{tools}} + 0.20 \times S_{\text{reviews}} + 0.20 \times S_{\text{verification}} + 0.20 \times S_{\text{views}}$$
- Transparent explainability endpoint: `GET /api/v2/creators/{id}/explain-match/{job_id}`.

---

## 🌐 5. API Endpoints Contract

### Creator Endpoints
- `GET /api/creators/me`: Authenticated creator profile.
- `GET /api/creators/{id}`: Public creator profile (increments views).
- `PUT /api/creators/{id}`: Update profile & specifications.
- `POST /api/creators/portfolio/{item_id}/pin`: Pin / unpin work (enforces max 3).

### Company Reviews Endpoints
- `POST /creators/{id}/reviews`: Company submits 1-5 star review.
- `GET /creators/{id}/reviews`: List all reviews & average rating.

### Creator Connections Endpoints
- `POST /api/creators/{id}/connect`: Send connection request.
- `POST /api/connections/{id}/status`: Accept or reject request.
- `GET /api/creators/{id}/connections`: List creator's connections.

### AI Search & Algorithms Endpoints
- `POST /api/v2/search/semantic`: Natural language semantic query.
- `POST /api/v2/search/hybrid`: Hybrid keyword + vector search with aspect ratio filters.
- `POST /api/v2/ner/extract`: Extract AI tools, specs, and formats from raw text.
- `POST /api/v2/rankings/creators-for-brief`: Leaderboard ranked creators for a brief.
- `POST /api/v2/briefs/ai-generate`: Groq RAG AI Brief Builder.
