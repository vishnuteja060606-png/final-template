# Synapse — AI Content Creator Marketplace (v2.0)

[![Python](https://img.shields.io/badge/Python-3.13+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0+-D71F00?logo=sqlalchemy&logoColor=white)](https://www.sqlalchemy.org/)
[![Tests](https://img.shields.io/badge/Tests-63%20Passed-success)](#automated-testing)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

An AI-native creative talent marketplace connecting specialized **AI content creators** (filmmakers, animators, prompt engineers, and generative media specialists) with **brands, creative agencies, and enterprises**.

Built specifically for parallel feature engineering with **Antigravity AI agents** across a 5-member development team.

---

## 🌟 Reviewer-Requested Upgrades & New Features

1. **Company Reviews for Creators**:
   - Registered companies and brands can submit structured 1–5 star performance reviews directly on creator profiles.
   - Evaluates creative adherence, prompt turnaround speed, visual quality, and AI tools used.
   - Reviews are highlighted on creator profiles and factored directly into the Creator Ranking Algorithm.

2. **Distinct Creator and Company Profile Architectures**:
   - **Creator Profiles**: Profile photo, location, full social media links (Twitter, Instagram, YouTube, ArtStation, GitHub, LinkedIn, Website), hourly rate in INR (₹), and an **AI Specs & Toolchain** card detailing max resolution (4K), framerate (60fps), aspect ratios (9:16 vertical, 16:9), LoRA fine-tuning, and hardware rigs.
   - **Company Profiles**: Company logo, industry, headquarters, website, social links (LinkedIn, Twitter), active briefs posted, and past reviews given to creators.

3. **Mandatory 2 Portfolio Uploads Rule**:
   - Creator profiles automatically begin in **Draft Mode** (hidden from public discovery and search) until at least 2 portfolio works are uploaded.
   - Once 2 works are uploaded, the profile automatically transitions to **Published & Discoverable**.
   - Dashboard displays a clear guided progress banner (`{count}/2 Uploads`).

4. **Pin Best Work (Featured Spotlight)**:
   - Creators can pin up to 3 of their finest portfolio items.
   - Pinned items are spotlighted with a golden ⭐ ribbon at the very top of their portfolio showcase.

5. **Creator-to-Creator Professional Connections**:
   - Mutual professional networking system (`Connect` -> `Accept` -> `Connected`).
   - Profile displays total connections count and connected peers list.

6. **Impression & View Tracking**:
   - Track total profile views ("👁️ 1,840 Views") and individual portfolio views with session-based de-duplication to prevent artificial refresh spam.

7. **Role-Based Dynamic Navigation**:
   - Logged-in Creators **never see** "Discover Creators" in the navbar.
   - Logged-in Companies **never see** "Brands & Companies" in the navbar.
   - Visitors and public guests see complete exploratory navigation.

8. **Primary Currency in Indian Rupees (₹) with Dynamic USD ($) Switcher**:
   - All rates and brief budgets are natively stored and calculated in INR (₹).
   - Global persistent header switcher `[ ₹ INR | $ USD ]` automatically converts and formats every rate across cards, modals, and lists using real-time or configured exchange rates (1 USD = ₹85.0).

---

## 🧠 Core AI Algorithms & Techniques

1. **Semantic Search via FastEmbed**:
   - Local ONNX CPU sentence embeddings (`bge-small-en-v1.5`) requiring zero GPU, zero API keys, and zero cost.
   - Cosine similarity matching between natural language queries and creator/brief vectors.

2. **Named Entity Recognition (NER)**:
   - Canonical alias dictionaries (`CANONICAL_TOOLS`, `CANONICAL_FORMATS`, `CANONICAL_LICENSES`).
   - Provenance tagging: differentiates `'creator_claim'`, `'platform_verified'`, and `'brief_requirement'`.
   - Regex extraction with structured Groq LLM fallback.

3. **Hybrid Job Search with Reciprocal Rank Fusion (RRF)**:
   - Merges keyword BM25/LIKE scores and semantic vector ranks:
     $$RRF\_Score(d) = \frac{1}{60 + rank_{keyword}(d)} + \frac{1}{60 + rank_{vector}(d)}$$
   - Respects hard filters: aspect ratio, required toolchains, and INR budget constraints.

4. **Creator Ranking Algorithm (5 Equal 20% Signals)**:
   $$\text{Score} = 0.20 \times S_{\text{semantic}} + 0.20 \times S_{\text{tools}} + 0.20 \times S_{\text{reviews}} + 0.20 \times S_{\text{verification}} + 0.20 \times S_{\text{views}}$$
   - Transparent score explanation endpoint: `/api/v2/creators/{id}/explain-match/{job_id}`.

5. **AI-Assisted Brief Builder (Groq RAG + Safe Fallback)**:
   - Converts unstructured campaign ideas into structured briefs with grounded citations to catalog standards.

---

## 👥 5-Member Parallel Development Workflow

To ensure all 5 team members develop simultaneously with **zero merge conflicts**, the project follows a contract-first architecture backed by automated role onboarding:

```bash
# Onboard your branch & role
python setup_role.py --role <1|2|3|4|5>
```

| Member | Branch Name | Agent Playbook | Target Scope |
| :--- | :--- | :--- | :--- |
| **Member 1** | `member-1/core-contracts` | `AGENT_ROLE_1_CORE.md` | Core DB, Sidecars, Role-based Nav, Auth & Deployments |
| **Member 2** | `member-2/creator-portfolios` | `AGENT_ROLE_2_CREATOR.md` | Creator Profiles, 2 Uploads Rule, Pins, Connections & Views |
| **Member 3** | `member-3/company-reviews-currency` | `AGENT_ROLE_3_COMPANY.md` | Company Profiles, Review System & INR/USD Currency Switcher |
| **Member 4** | `member-4/semantic-search-ner` | `AGENT_ROLE_4_SEARCH_NER.md` | FastEmbed Local Vectors, Canonical NER & Hybrid RRF Search |
| **Member 5** | `member-5/ranking-rag-ui` | `AGENT_ROLE_5_RANKING_UI.md` | 5-Factor Ranking Engine, AI Brief Builder & UI Integration |

Refer to [TEAM_CONTRACT.md](TEAM_CONTRACT.md) for immutable API schemas and database contracts.

---

## 🚀 Quick Start & Local Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Initialize Database & Seed Demo Data
```bash
python -m app.db.seed
```
This populates realistic Indian and global AI filmmakers, animators, ₹ budgets, company reviews, connections, and sample video media.

### 3. Run the Development Server
```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

- **Web Application**: [http://127.0.0.1:8000](http://127.0.0.1:8000)
- **Interactive Swagger Docs**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## 🧪 Automated Testing

Run the comprehensive pytest suite covering all modules, reviewer features, and algorithms:
```bash
python -m pytest -v
```

All 63 automated tests pass with 100% test pass rate!
