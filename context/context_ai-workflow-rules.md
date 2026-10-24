# AI Workflow Rules

## 1. Project Mission

Build a hackathon-ready AI Content Creator Marketplace that reliably demonstrates the core workflow:

1. Creators create profiles and showcase AI-generated work.
2. Brands/companies publish AI-content creator project or job requirements.
3. Users discover and filter relevant creators or companies.
4. Users inspect detailed profiles, portfolios, and requirements.
5. Optional AI features improve the workflow without becoming a dependency.

The project must prioritize **working core functionality, automated-test reliability, simple architecture, and a polished user experience** over unnecessary complexity.

The hackathon problem statement emphasizes creator profiles/AI portfolios, structured briefs, discovery/filtering, usability, and presentation. The project's implementation should directly support those evaluation areas. fileciteturn0file0L55-L65

---

## 2. Core Development Principles

### 2.1 Inspect Before Changing

Before modifying existing code:

- Inspect the relevant files, routes, models, templates, services, and tests.
- Understand existing conventions before introducing a new pattern.
- Reuse existing utilities/components when practical.
- Do not rewrite working modules merely to make them stylistically different.
- Keep changes focused on the requested feature.

### 2.2 Prefer Simple, Testable Solutions

Use the simplest implementation that satisfies the requirement.

Prefer:

- Python services/functions with clear inputs and outputs.
- Small FastAPI-style route handlers/controllers.
- SQLAlchemy or an equivalent database abstraction that keeps SQLite/MySQL migration straightforward.
- Server-side validation plus client-side usability validation.
- Deterministic search/filter behavior for the core marketplace.
- Optional AI/RAG layers behind clearly separated services.

Do not introduce microservices, queues, vector databases, complex agent frameworks, or other infrastructure unless they provide clear value for the MVP.

### 2.3 Core Features Must Not Depend on AI

The marketplace must remain usable when:

- `GROQ_API_KEY` is missing.
- Groq is temporarily unavailable.
- RAG dependencies fail.
- An embedding/vector search service is unavailable.

AI-assisted functionality is an enhancement. Core profile creation, portfolio management, job/brief creation, search, filtering, and profile viewing must work without an LLM.

---

## 3. Feature Priority

Implement features in this order:

### P0 — Required for MVP

- Authentication/role handling as required by the application.
- Creator profile creation/editing.
- Portfolio item creation/editing/deletion.
- Portfolio file upload and metadata.
- Rich portfolio metadata:
  - title
  - description
  - file type
  - media/content type
  - aspect ratio/format
  - tools/models
  - skills
  - specialization
  - workflow information
  - relevant tags
- Brand/company profile or account information.
- Brand/company project/job/brief creation and management.
- Creator discovery.
- Company/job discovery where applicable.
- Search and structured filters.
- Empty-state handling.
- Creator profile and portfolio detail pages.
- Automated tests for important business logic and API behavior.

### P1 — High-value Enhancements

- Combined/multi-filter search.
- Relevance ranking.
- Search normalization.
- Similarity matching.
- Better portfolio previews.
- Saved/favorite items if useful to the demo.

### P2 — Bonus

- LangChain/RAG-based similarity search.
- Groq AI Builder for turning rough ideas into detailed structured briefs.
- Retrieval of relevant user/profile preferences for AI generation.
- Creator verification/trust signals.

The original challenge explicitly identifies creator verification and an AI-assisted brief builder as bonus features. fileciteturn0file0L45-L53

---

## 4. AI and RAG Rules

### 4.1 Groq

- Read the API key only from environment configuration.
- Never hard-code API keys.
- Never commit secrets to source control.
- Wrap Groq calls in a dedicated service/module.
- Use timeouts and controlled error handling.
- Validate structured AI output before storing or displaying it.
- Treat generated content as user-editable suggestions, not authoritative database facts.

### 4.2 RAG

RAG should be introduced only after deterministic search works.

Recommended progression:

1. Normalize and index structured fields.
2. Implement exact/filtered database search.
3. Add text relevance search.
4. Add embeddings/similarity only if required.
5. Add LangChain orchestration only where it simplifies the implementation.
6. Always retain a deterministic fallback.

RAG retrieval must respect user-visible filters and permissions. Never retrieve private data merely because it is semantically similar.

### 4.3 AI Builder

The AI Builder should:

1. Accept a rough idea.
2. Retrieve relevant allowed user preferences/profile information.
3. Generate a structured draft.
4. Validate the generated structure.
5. Present it as editable fields.
6. Allow the user to accept or modify it.
7. Never silently publish generated content.

---

## 5. Database Rules

Design database code so SQLite can later move to MySQL with minimal application changes.

Rules:

- Use an ORM/database abstraction rather than SQLite-specific SQL throughout the application.
- Avoid SQLite-only features unless there is a clear migration path.
- Keep models relational and normalized.
- Store file metadata in the database; do not depend on database BLOBs for large portfolio files unless explicitly required.
- Keep upload/storage paths separate from business records.
- Use migrations for schema changes.
- Avoid destructive schema changes during normal feature work.
- Use foreign keys and indexes for commonly filtered fields.
- Use UTC timestamps consistently.

Important searchable fields should have appropriate indexes where practical, especially role/type, specialization, content type, and other frequently filtered attributes.

---

## 6. File Upload Rules

Portfolio uploads must support the project's accepted file types without assuming every file is an image or video.

For every portfolio item:

- Preserve the original filename safely.
- Determine and store a trustworthy file/MIME type.
- Store file size.
- Store content/media type.
- Store aspect ratio when applicable.
- Store description and searchable metadata.
- Validate upload size and allowed types.
- Prevent path traversal and unsafe filenames.
- Never execute uploaded files.
- Separate storage concerns from portfolio metadata.

If preview generation is not practical for a file type, provide a safe metadata/download representation rather than breaking the portfolio page.

---

## 7. Search and Filtering Rules

Search must be useful even without AI.

Normalize user input by:

- trimming whitespace,
- handling case differences,
- avoiding accidental duplicate filters,
- safely handling empty values.

Core search should support meaningful creator/company/job attributes such as:

- skills
- specialization
- tools/models
- content type
- format/aspect ratio
- tags
- location or availability if included in the product
- project/job type
- relevant profile attributes

Multiple filters should combine predictably.

Never return a server error simply because no records match. Show a clear empty state with the active filters and an easy way to reset them.

If semantic/RAG search is enabled, use it to improve ranking rather than replacing transparent structured filtering.

---

## 8. API and Backend Rules

- Validate request data at the API boundary.
- Return predictable status codes.
- Return consistent error structures.
- Do not expose stack traces to users.
- Keep route handlers thin; put business logic in services.
- Keep database access in a clear repository/data-access layer where useful.
- Do not duplicate business rules across routes.
- Enforce authorization on the server, not only in the UI.
- Prevent users from editing another user's private data.
- Keep public profile/portfolio data separate from private account data.

Every important endpoint should have at least one automated success-path test and tests for important validation/authorization failures.

---

## 9. Frontend/UI Rules

Use HTML/CSS/JavaScript with Bootstrap or another lightweight, well-supported UI layer.

UI goals:

- Clean.
- Responsive.
- Easy to understand.
- Fast to navigate.
- Strong empty/error/loading states.
- Consistent forms and buttons.
- Clear creator portfolio presentation.
- Clear job/brief presentation.
- Accessible labels and controls.

Do not over-design the UI at the expense of completing the marketplace workflow.

Every major user action should provide visible feedback.

---

## 10. Testing Rules

Automated testing is a first-class requirement because the first-round evaluation uses automated tests.

Tests should cover at minimum:

- database/model creation,
- creator profile CRUD,
- portfolio CRUD,
- portfolio metadata validation,
- upload validation,
- company/job/brief CRUD,
- search,
- filters,
- combined filters,
- empty search results,
- authorization boundaries,
- AI service failure fallback,
- structured AI output validation.

Tests must not require a live Groq API key unless the test is explicitly marked as an integration test.

Mock external AI calls in normal unit/API tests.

Prefer deterministic fixtures and isolated test databases.

---

## 11. Security Rules

Never:

- hard-code secrets,
- commit `.env` files containing credentials,
- trust client-side authorization,
- directly interpolate user input into SQL,
- expose private records through search,
- execute uploaded files,
- trust an AI-generated field without validation.

Use environment variables for:

- `GROQ_API_KEY`
- database configuration
- secret/session configuration
- deployment-specific storage configuration.

Validate and sanitize all user-controlled input.

---

## 12. Scope Control

When time is limited:

**Finish P0 before P1. Finish P1 before P2.**

Do not spend hackathon time on:

- unnecessary microservices,
- complex DevOps,
- custom model training,
- elaborate agent architectures,
- payment systems,
- production-grade marketplace economics,
- features not visible in the evaluation flow.

A small complete feature is better than a sophisticated incomplete feature.

---

## 13. Definition of Done

A feature is done only when:

- The happy path works.
- Validation works.
- Authorization is considered.
- Error/empty states are handled.
- Data persists correctly.
- The feature is testable.
- The UI gives clear feedback.
- No secrets are introduced.
- Existing functionality still works.
- The implementation remains compatible with the planned SQLite → MySQL migration.

For AI features, additionally:

- The feature has a deterministic fallback where practical.
- External failures do not crash the marketplace.
- AI output is validated.
- Users can edit generated content before it becomes application data.
