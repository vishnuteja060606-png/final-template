# Code Standards

## 1. Purpose

These standards keep the AI Content Creator Marketplace **simple, consistent, testable, secure, and fast to develop**.

The project is a hackathon MVP, so code quality means:

- clear code,
- predictable behavior,
- easy automated testing,
- minimal duplication,
- easy debugging,
- easy SQLite → MySQL migration,
- no unnecessary architecture.

Do not add complexity merely to make the code look enterprise-grade.

---

## 2. General Rules

### 2.1 Prefer Readability

Prefer code that another developer can understand quickly.

Good:

```python
creator = creator_service.get_by_id(creator_id)
```

Avoid unnecessarily clever abstractions when a straightforward function is clearer.

### 2.2 Keep Functions Small

A function should generally do one logical job.

Avoid functions that simultaneously:

- validate input,
- query several unrelated tables,
- upload files,
- call Groq,
- transform data,
- and render a response.

Split responsibilities when the function becomes difficult to test or understand.

### 2.3 Avoid Premature Abstraction

Do not create:

- generic base classes without a real use case,
- unused interfaces,
- speculative repositories,
- unnecessary factories,
- unnecessary dependency-injection frameworks.

Create an abstraction when it protects a real boundary, such as file storage or an external AI provider.

---

## 3. Python Standards

Use modern Python with type hints.

Prefer:

```python
def get_creator(creator_id: int) -> Creator | None:
    ...
```

over:

```python
def get_creator(creator_id):
    ...
```

Use clear names:

```python
creator_profile
portfolio_item
search_filters
company_id
```

Avoid:

```python
cp
pi
data2
temp
x
```

unless the scope is extremely small and obvious.

---

## 4. Formatting and Imports

Follow standard Python formatting conventions.

Recommended:

- PEP 8 style.
- Consistent 4-space indentation.
- One import style throughout the project.
- Standard library imports first.
- Third-party imports second.
- Local imports last.

Example:

```python
from pathlib import Path

from fastapi import APIRouter, Depends

from app.services.creator_service import CreatorService
```

Keep imports explicit and avoid wildcard imports.

---

## 5. Type Hints

Use type hints for:

- service functions,
- repository functions,
- public utility functions,
- API dependencies,
- important data transformations.

Use Pydantic models for structured API data instead of passing arbitrary dictionaries through multiple layers.

Avoid excessive typing complexity.

The goal is useful type safety, not type-system experimentation.

---

## 6. Naming Conventions

### Python

Use `snake_case`:

```python
creator_profile
search_creators
portfolio_item
```

### Classes

Use `PascalCase`:

```python
CreatorProfile
PortfolioItem
SearchService
AIService
```

### Constants

Use uppercase:

```python
MAX_UPLOAD_SIZE
ALLOWED_FILE_TYPES
```

### Database Tables

Use a consistent naming convention.

Do not change table naming conventions midway through the project.

---

## 7. FastAPI/API Standards

Routes should be thin.

Prefer:

```python
@router.post("/creators")
def create_creator(
    payload: CreatorCreate,
    service: CreatorService = Depends(get_creator_service),
):
    return service.create(payload)
```

Avoid putting large business workflows directly inside route functions.

### API Responsibilities

Routes should handle:

1. request parsing,
2. validation,
3. authentication/authorization dependencies,
4. calling the service,
5. converting the result into the response.

Services should handle business logic.

Repositories should handle persistence.

---

## 8. HTTP Status Codes

Use predictable status codes.

Typical usage:

- `200` — successful read/update/action.
- `201` — successful creation.
- `204` — successful deletion with no response body.
- `400` — invalid request.
- `401` — unauthenticated.
- `403` — authenticated but not authorized.
- `404` — resource not found.
- `409` — conflict.
- `422` — validation error where appropriate.
- `500` — unexpected server failure.

Do not return `200` for every failure.

---

## 9. Error Handling

Errors should be controlled and understandable.

Do:

```python
if creator is None:
    raise HTTPException(
        status_code=404,
        detail="Creator profile not found",
    )
```

Do not expose:

- stack traces,
- database connection strings,
- API keys,
- internal filesystem paths,
- implementation details.

Unexpected exceptions should be logged server-side and converted into safe responses.

Do not use broad exception handling unless there is a clear recovery or logging purpose.

Avoid:

```python
try:
    ...
except Exception:
    pass
```

Silent failures are especially dangerous in the marketplace search and upload workflows.

---

## 10. Pydantic Schemas

Use separate schemas when request and response requirements differ.

Example:

```text
CreatorCreate
CreatorUpdate
CreatorResponse
```

Do not automatically expose ORM models as public API contracts.

Validate:

- required fields,
- lengths,
- allowed values,
- file metadata,
- filter parameters,
- AI-generated structured output.

---

## 11. SQLAlchemy/Database Standards

Keep database access portable.

Prefer ORM/query APIs over raw SQLite-specific SQL.

Avoid:

```sql
PRAGMA ...
```

or other SQLite-specific logic in business code unless it is isolated and documented.

Use relationships and foreign keys consistently.

Use indexes for fields frequently involved in:

- search,
- filtering,
- joins,
- ownership checks.

Do not add indexes blindly.

---

## 12. Database Transactions

Operations that modify multiple related records should use a transaction.

Example:

```text
Create portfolio item
      +
Save metadata
      +
Associate creator
```

should not leave partially-created records when one step fails.

Commit at the appropriate service/repository boundary.

Avoid scattered commits throughout a single business operation.

---

## 13. Database Migrations

Schema changes must be migration-friendly.

Do not manually modify the production database schema during normal feature development.

Use a migration system such as Alembic when the project structure is ready.

Every schema change should consider:

- existing records,
- nullable/default values,
- indexes,
- foreign keys,
- SQLite compatibility,
- future MySQL compatibility.

---

## 14. Search Code Standards

Search code must distinguish between:

### Structured filters

Examples:

```text
skill = "video generation"
specialization = "AI filmmaking"
content_type = "video"
```

### Free-text search

Examples:

```text
"cinematic product ads with Runway"
```

### Semantic search

Optional similarity/RAG retrieval.

Keep these mechanisms separable.

Do not make a database query impossible to understand because it attempts to implement the entire AI search system in one function.

---

## 15. Search Normalization

Normalize user search input consistently.

At minimum:

```python
query = query.strip()
```

For case-insensitive comparisons, use the database/query strategy consistently.

Avoid inconsistent behavior such as:

```text
Runway
runway
RUNWAY
```

producing completely different results when they should represent the same filter.

---

## 16. Empty Search Results

An empty result is valid application behavior.

Do not raise an exception simply because:

```python
results == []
```

Instead return a valid empty result structure and let the UI display an appropriate message.

Example:

```json
{
  "items": [],
  "total": 0,
  "message": "No creators matched your filters."
}
```

The exact API contract may differ, but the principle must remain.

---

## 17. File Upload Standards

Treat every uploaded file as untrusted input.

Validate:

- file size,
- MIME type,
- extension where appropriate,
- filename,
- storage path.

Generate safe storage names.

Do not use:

```python
Path(upload.filename)
```

as the final storage location without sanitization.

Prefer generated identifiers:

```text
<portfolio_id>-<random-safe-name>
```

Store metadata in the database.

Never execute uploaded files.

---

## 18. Portfolio Metadata

A portfolio item should contain enough information for both humans and search.

Important fields include:

- title,
- description,
- file type,
- content type,
- aspect ratio,
- format,
- tools/models,
- skills,
- specialization,
- tags,
- workflow information.

Do not make every metadata field mandatory if it does not make sense for the uploaded work.

For example, an arbitrary document may not have a meaningful visual aspect ratio.

---

## 19. Frontend Standards

Use semantic HTML where practical.

Prefer:

```html
<label for="title">Title</label>
<input id="title" name="title" ...>
```

over unlabeled inputs.

Use Bootstrap consistently rather than mixing several UI frameworks.

Keep custom CSS focused on:

- branding,
- layout adjustments,
- components not covered by Bootstrap,
- marketplace-specific visual design.

Avoid large inline style blocks.

---

## 20. JavaScript Standards

Keep JavaScript modular and focused.

Avoid putting all application logic in one giant script.

Use clear names:

```javascript
loadCreators()
applyFilters()
submitPortfolio()
```

Handle:

- loading states,
- errors,
- empty results,
- successful operations.

Do not silently ignore failed API requests.

---

## 21. Templates

Keep templates responsible for presentation.

Avoid embedding substantial business logic in HTML/Jinja templates.

Prefer:

```text
Route -> Service -> Data
                    |
                    v
                 Template
```

rather than implementing database queries or complex business rules inside templates.

---

## 22. Authentication and Authorization

Authorization checks must happen server-side.

For ownership checks:

```python
if portfolio.creator_id != current_user.creator_id:
    raise ForbiddenError(...)
```

Do not assume that hiding an edit button prevents unauthorized access.

Never trust a user-supplied ID merely because it came from the frontend.

---

## 23. Secrets and Configuration

Never hard-code:

- Groq API keys,
- passwords,
- session secrets,
- production database credentials,
- storage credentials.

Use environment variables.

Maintain:

```text
.env
.env.example
```

`.env` must not be committed.

`.env.example` should contain placeholder values only.

Example:

```text
GROQ_API_KEY=
DATABASE_URL=sqlite:///./app.db
SECRET_KEY=change-me
```

---

## 24. Groq/AI Code Standards

Keep Groq integration inside an AI service.

Example boundary:

```text
API
 |
AIService
 |
GroqClient
```

The rest of the application should not directly depend on Groq SDK calls.

AI calls must:

- have controlled timeouts,
- handle provider failures,
- validate responses,
- avoid logging secrets,
- avoid assuming the model always returns valid JSON.

---

## 25. AI Output Validation

Never directly persist arbitrary LLM output.

Use:

```text
LLM output
    ↓
Parse
    ↓
Validate with Pydantic
    ↓
Normalize
    ↓
User review
    ↓
Persist
```

If validation fails, return a recoverable error or fall back to the manual workflow.

---

## 26. RAG/LangChain Standards

LangChain is optional, not foundational.

Do not make ordinary CRUD depend on LangChain.

Keep retrieval code behind a search/RAG service boundary:

```python
search_service.search(...)
```

rather than exposing LangChain objects throughout the application.

If RAG fails:

```text
RAG unavailable
      ↓
keyword/structured search
```

The marketplace must continue functioning.

---

## 27. Testing Standards

Every important feature should have tests.

Prioritize:

1. Service/business logic tests.
2. API tests.
3. Validation tests.
4. Authorization tests.
5. Search/filter tests.
6. File validation tests.
7. AI parsing/fallback tests.

Use mocked Groq responses in normal tests.

Tests must not require:

- a real Groq API key,
- a production database,
- external network access,
- a cloud storage account.

Integration tests may explicitly test those dependencies separately.

---

## 28. Test Naming

Use descriptive test names.

Good:

```python
def test_creator_can_update_own_profile():
    ...
```

```python
def test_creator_cannot_update_another_creators_portfolio():
    ...
```

```python
def test_search_returns_empty_list_when_no_creator_matches():
    ...
```

Avoid:

```python
def test_creator_1():
    ...
```

---

## 29. Logging

Log useful diagnostic events, such as:

- failed AI requests,
- unexpected application errors,
- upload failures,
- important background operations if introduced.

Do not log:

- passwords,
- API keys,
- session secrets,
- private user content unnecessarily.

Use appropriate log levels.

---

## 30. Comments and Documentation

Write comments for **why**, not obvious **what**.

Bad:

```python
# Increment i
i += 1
```

Good:

```python
# Preserve deterministic ordering so search results remain stable between requests.
```

Document non-obvious architectural decisions.

Do not write comments that become false as soon as implementation changes.

---

## 31. Git Standards

Use small, meaningful commits.

Examples:

```text
feat: add creator profile CRUD
feat: add portfolio upload metadata
feat: add creator search filters
test: add portfolio authorization tests
fix: handle empty creator search results
feat: add groq brief builder
```

Avoid giant commits containing unrelated changes.

Do not commit:

- `.env`,
- database secrets,
- generated credentials,
- large temporary files,
- unnecessary build artifacts.

---

## 32. Definition of Code Quality

Before considering code complete, ask:

- Is the behavior easy to understand?
- Is the business logic in the correct layer?
- Is it testable?
- Is input validated?
- Is authorization enforced?
- Are failures handled?
- Is SQLite/MySQL portability preserved?
- Are external AI dependencies isolated?
- Is there unnecessary complexity?
- Would another developer be able to debug this quickly?

If the answer is yes, the code is likely appropriate for this hackathon project.

---

## 33. Priority Rule

When speed and complexity conflict:

> **Choose the simplest implementation that preserves correctness, testability, security, and the core user experience.**

Do not sacrifice core marketplace reliability for an impressive but fragile technical implementation.
