# Architecture

## 1. Architecture Goal

Use a **simple modular monolith** that is fast to build, easy to test, and easy to deploy.

The application should have one Python backend, one web frontend, one relational database, and optional AI/search services.

Do not split the MVP into microservices.

### Primary stack

- Backend: Python + FastAPI
- ORM: SQLAlchemy
- Database: SQLite initially
- Future database: MySQL
- Frontend: HTML + CSS + JavaScript
- UI framework: Bootstrap
- AI provider: Groq API
- Optional AI orchestration/retrieval: LangChain
- File storage: local filesystem for development, replaceable storage adapter for deployment
- Testing: pytest + FastAPI test client
- Configuration: environment variables
- Deployment: keep backend/frontend structure simple enough for common cloud deployment

---

## 2. High-Level Architecture

```text
Browser
  |
  | HTTP / HTML / JSON
  v
FastAPI Application
  |
  +--------------------+
  |                    |
  v                    v
Web/UI Layer       API Layer
  |                    |
  +---------+----------+
            |
            v
       Service Layer
            |
      +-----+-------------------+
      |             |           |
      v             v           v
  Repository    File Service   AI Service
      |             |           |
      v             v           v
 SQLAlchemy     File Storage  Groq API
      |
      v
 SQLite / MySQL

Optional:
Service Layer -> Search/RAG Service -> Embeddings/Vector Store
```

The key rule is that **core marketplace functionality does not depend on the AI/RAG branch**.

---

## 3. Recommended Project Structure

Use a structure similar to:

```text
project/
├── app/
│   ├── main.py
│   ├── config.py
│   │
│   ├── api/
│   │   ├── auth.py
│   │   ├── creators.py
│   │   ├── portfolios.py
│   │   ├── companies.py
│   │   ├── jobs.py
│   │   ├── search.py
│   │   └── ai.py
│   │
│   ├── models/
│   │   ├── user.py
│   │   ├── creator.py
│   │   ├── portfolio.py
│   │   ├── company.py
│   │   ├── job.py
│   │   └── common.py
│   │
│   ├── schemas/
│   │   ├── auth.py
│   │   ├── creator.py
│   │   ├── portfolio.py
│   │   ├── company.py
│   │   ├── job.py
│   │   ├── search.py
│   │   └── ai.py
│   │
│   ├── services/
│   │   ├── creator_service.py
│   │   ├── portfolio_service.py
│   │   ├── company_service.py
│   │   ├── job_service.py
│   │   ├── search_service.py
│   │   ├── file_service.py
│   │   └── ai_service.py
│   │
│   ├── repositories/
│   │   ├── creator_repository.py
│   │   ├── portfolio_repository.py
│   │   ├── company_repository.py
│   │   └── job_repository.py
│   │
│   ├── db/
│   │   ├── database.py
│   │   └── migrations/
│   │
│   ├── search/
│   │   ├── keyword_search.py
│   │   ├── similarity.py
│   │   └── rag.py
│   │
│   ├── templates/
│   └── static/
│
├── tests/
├── uploads/
├── .env.example
├── requirements.txt
└── README.md
```

The exact module names may change as implementation evolves. Do not create empty abstractions merely to match this tree.

---

## 4. Application Layers

### 4.1 API/Web Layer

Responsible for:

- HTTP routes.
- Request parsing.
- Authentication dependency checks.
- Input/output schema validation.
- HTTP status codes.
- Rendering templates where server-rendered pages are used.

Routes should not contain large blocks of business logic.

### 4.2 Service Layer

Responsible for:

- Business rules.
- Creating/updating marketplace entities.
- Search/filter orchestration.
- Permission-aware operations.
- File metadata coordination.
- Calling optional AI services.
- Coordinating repositories.

This is the main application logic layer.

### 4.3 Repository/Data Layer

Responsible for:

- Database queries.
- Persistence.
- Filtering primitives.
- Fetching related records.

Keep database-specific details here where practical.

### 4.4 Model Layer

SQLAlchemy models represent persistent entities and relationships.

Keep models focused on:

- fields,
- relationships,
- database constraints,
- indexes.

Do not put large application workflows inside ORM models.

### 4.5 Schema Layer

Pydantic schemas define:

- request validation,
- response structures,
- AI output structures,
- API contracts.

Never trust raw request dictionaries throughout the application.

---

## 5. Core Domain Model

The minimum domain should contain these concepts.

### User

Represents authentication/account identity.

Important attributes may include:

- id
- email
- password/auth identifier
- role
- created_at
- updated_at

Roles should distinguish at least:

- creator
- company/brand

### CreatorProfile

Represents the public professional identity of an AI content creator.

Possible fields:

- id
- user_id
- display_name
- headline
- bio
- specialization
- skills
- tools/models
- workflow
- experience
- location/availability if required
- profile metadata
- created_at
- updated_at

For searchable multi-value attributes, use a consistent relational or normalized representation rather than storing arbitrary Python objects in the database.

### PortfolioItem

Represents one creator work.

Possible fields:

- id
- creator_id
- title
- description
- file_path/storage_key
- original_filename
- mime_type
- file_size
- content_type
- aspect_ratio
- format
- tools/models
- skills
- tags
- workflow
- created_at
- updated_at

A portfolio item should remain useful for both human evaluation and search.

The hackathon specifically expects portfolios to communicate tools/models, skills, specialization, and workflow information. fileciteturn0file0L21-L28

### CompanyProfile

Represents a brand/company/agency.

Possible fields:

- id
- user_id
- company_name
- description
- industry
- website
- location
- requirements/profile metadata
- created_at
- updated_at

### Job / CreativeBrief

Represents a company's project or requirement for AI content creators.

Possible fields:

- id
- company_id
- title
- description
- campaign_requirements
- content_type
- style
- aspect_ratio
- format
- commercial_use
- required_tools
- required_skills
- specialization
- budget/engagement details if included
- status
- created_at
- updated_at

The brief model should preserve the challenge's required campaign, content type, style, format/aspect ratio, and commercial-use concepts. fileciteturn0file0L29-L36

---

## 6. Entity Relationships

```text
User
 ├── 1:1 CreatorProfile
 │       └── 1:N PortfolioItem
 │
 └── 1:1 CompanyProfile
         └── 1:N Job/CreativeBrief

CreatorProfile
 └── PortfolioItem[]
```

Additional many-to-many tables can be introduced for skills, tools, tags, or other normalized searchable data if the implementation requires them.

Do not over-normalize early.

A practical hackathon implementation may begin with normalized association tables for the most important searchable values and add more only when necessary.

---

## 7. Portfolio File Architecture

Separate **file storage** from **portfolio metadata**.

```text
PortfolioItem
    |
    +-- database metadata
    |
    +-- storage_key/file_path
             |
             v
        File Storage
```

The database should not be responsible for storing large uploaded media unless there is a strong reason.

Create a `FileService` abstraction so the implementation can move from:

```text
LocalStorage
```

to:

```text
Cloud/ObjectStorage
```

without changing portfolio business logic.

For MVP development:

```text
uploads/
  creators/
    <creator_id>/
      <safe-generated-name>
```

Never use the raw user filename as the storage path.

---

## 8. Search Architecture

Search should be implemented in layers.

### Level 1 — Structured Filtering

Use database queries for exact/structured filters:

- skills
- specialization
- tools/models
- content type
- aspect ratio/format
- tags
- company/job attributes

This is the authoritative MVP search.

### Level 2 — Keyword Relevance

Normalize and search text fields such as:

- creator bio
- portfolio descriptions
- workflow
- skills
- tools
- job descriptions
- campaign requirements

### Level 3 — Similarity/RAG

Optional:

```text
User Query
    |
    v
Search Service
    |
    +--> Structured Filters
    |
    +--> Keyword Search
    |
    +--> Similarity Retrieval
              |
              v
         Relevant Records
              |
              v
        Ranking/Response
```

Semantic search should enhance discovery, not bypass explicit filters.

If the similarity system fails:

```text
Similarity failure
       |
       v
Structured + keyword search
```

The user should still receive useful results.

---

## 9. AI Builder Architecture

The optional AI Builder should be isolated from normal marketplace operations.

```text
User rough idea
      |
      v
AI Builder API
      |
      v
Preference/Profile Retrieval
      |
      v
Optional RAG Context
      |
      v
Groq Service
      |
      v
Structured AI Response
      |
      v
Pydantic Validation
      |
      v
Editable Brief Form
      |
      v
User Confirmation
      |
      v
Job/CreativeBrief persistence
```

Important rule:

**AI generates a draft; the application owns the final data.**

If Groq is unavailable:

```text
AI unavailable
      |
      v
Show normal manual brief form
```

No marketplace-critical route should crash because the AI provider is unavailable.

---

## 10. Authentication and Authorization

Authentication should be centralized.

A route should be able to determine:

```text
current_user
current_role
```

Authorization belongs on the backend.

Examples:

- Creator can edit their own creator profile.
- Creator can manage their own portfolio.
- Company can edit its own company profile.
- Company can manage its own jobs/briefs.
- Public users may view public profiles if the product allows it.
- One user must not modify another user's records by changing an ID in the request.

Do not rely only on hiding buttons in the frontend.

---

## 11. Request Flow

### Creator Portfolio Flow

```text
Browser
  -> Portfolio form
  -> API
  -> Validation
  -> Authorization
  -> Portfolio Service
  -> File Service
  -> Repository
  -> Database
  -> Response
```

### Company Job Flow

```text
Browser
  -> Job form
  -> API
  -> Validation
  -> Authorization
  -> Job Service
  -> Repository
  -> Database
  -> Response
```

### Creator Search Flow

```text
Browser
  -> Search parameters
  -> Search API
  -> Search Service
       -> Structured filters
       -> Keyword search
       -> Optional similarity
  -> Ranked results
  -> Browser
```

---

## 12. Database Portability

The application starts with SQLite but must remain MySQL-friendly.

Use:

```text
Application
   |
 SQLAlchemy
   |
 +--------+
 |        |
SQLite   MySQL
```

Avoid putting SQLite-specific SQL throughout the code.

Database configuration must come from environment variables.

Example concept:

```text
DATABASE_URL=sqlite:///./app.db
```

Later:

```text
DATABASE_URL=mysql+pymysql://...
```

Application services should not need to change when the database changes.

---

## 13. Testing Architecture

Use tests at multiple levels.

### Unit Tests

Test:

- search normalization,
- filtering logic,
- validation,
- ranking,
- AI response parsing,
- file metadata validation.

### API Tests

Test:

- profile endpoints,
- portfolio endpoints,
- company endpoints,
- job endpoints,
- search endpoints,
- authentication/authorization behavior.

### Integration Tests

Test:

- database persistence,
- upload flow,
- AI service integration separately,
- optional RAG integration separately.

External APIs should be mocked in normal automated tests.

The architecture must make the deterministic core easy to test without Groq or external services.

---

## 14. Failure Boundaries

External dependencies must fail locally.

### Groq failure

Only AI functionality should be affected.

### RAG/vector search failure

Fallback to structured/keyword search.

### File preview failure

Show metadata instead of breaking the portfolio page.

### Database error

Return a controlled application error and log diagnostic information server-side.

### Invalid upload

Reject before persistence.

---

## 15. Deployment Principle

Keep deployment simple.

The deployed system should conceptually contain:

```text
Web Client
    |
    v
Python/FastAPI App
    |
    +--> Relational DB
    |
    +--> File Storage
    |
    +--> Groq API (optional)
```

Do not require a cluster, message broker, or multiple backend services for the MVP.

The architecture should make it possible to demonstrate the complete marketplace flow reliably during a hackathon presentation.

---

## 16. Architecture Decision Rules

When choosing between two implementations:

1. Prefer the simpler one.
2. Prefer the one easier to test.
3. Prefer standard Python/FastAPI/SQLAlchemy patterns.
4. Prefer database-portable solutions.
5. Keep AI optional.
6. Avoid new infrastructure unless it solves a demonstrated problem.
7. Keep business logic independent of UI.
8. Keep external integrations behind adapters/services.
9. Optimize for a complete working demo before advanced optimization.
10. Preserve a deterministic fallback for every non-essential AI capability.
