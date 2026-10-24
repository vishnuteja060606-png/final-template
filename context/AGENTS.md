# AGENTS.md

# AI Content Creator Marketplace — Agent Instructions

## 1. Project Overview

This repository contains the **AI Content Creator Marketplace**, a hackathon prototype designed to connect AI content creators with brands, companies, and creative agencies.

The platform should allow:

- AI creators to create professional profiles.
- Creators to showcase AI-generated portfolio work.
- Creators to describe their skills, specialization, tools/models, and workflows.
- Brands/companies to create structured creative briefs/projects.
- Brands/companies to discover creators through search and filtering.
- Users to evaluate creator portfolios and relevant metadata.
- Companies to select/contact suitable creators.
- Optional AI functionality to help generate better creative briefs.

The project must prioritize a **working, testable core marketplace workflow** over unnecessary complexity.

The core workflow must work without AI.

---

# 2. Primary Objective

Build a reliable hackathon MVP that demonstrates:

```text
Creator Profile
      ↓
Portfolio
      ↓
Portfolio Metadata
      ↓
Company Creative Brief
      ↓
Creator Search
      ↓
Filtering
      ↓
Creator Evaluation
      ↓
Creator Selection / Engagement
```

The application should clearly demonstrate how an AI-native creator marketplace solves the problem of discovering suitable AI creative talent.

---

# 3. Source Problem Requirements

The platform should support the core requirements of the challenge:

- Creator profiles
- AI-focused portfolios
- Skills
- Specializations
- Tools/models
- Workflow information
- Structured creative briefs
- Campaign requirements
- Content type
- Style
- Format
- Aspect ratio
- Commercial-use requirements
- Creator search
- Filtering
- Creator evaluation

Optional/bonus functionality includes:

- Creator verification signals
- AI-assisted brief generation

These requirements are the basis for implementation priorities.

---

# 4. Technology Stack

Use the following stack unless there is a strong technical reason not to.

## Backend

- Python
- FastAPI

## Database

- SQLite for development and hackathon deployment
- SQLAlchemy ORM
- Design models so migration to MySQL is straightforward

## Frontend

- HTML
- CSS
- JavaScript
- Bootstrap

Do not introduce React, Vue, Angular, or another frontend framework unless explicitly requested.

## AI

- Groq API

Optional:

- LangChain
- RAG
- Vector/similarity search

AI functionality must remain optional for the core workflow.

---

# 5. Architecture

Use a **modular monolith**.

Do not create microservices unless explicitly required.

Preferred architecture:

```text
Browser
   ↓
HTML / Bootstrap / JavaScript
   ↓
FastAPI Routes
   ↓
Service Layer
   ↓
Repository / Data Access
   ↓
SQLAlchemy
   ↓
SQLite
```

Optional AI:

```text
FastAPI
   ↓
AI Service
   ↓
Groq
```

Optional semantic search:

```text
Search Request
      ↓
Structured Search
      ↓
Optional Semantic Search
      ↓
Ranked Results
```

The application should remain understandable to a hackathon developer.

---

# 6. Agent Operating Principles

Agents working on this repository must follow these principles.

## 6.1 Inspect Before Changing

Before modifying existing code:

1. Inspect the relevant files.
2. Understand existing architecture.
3. Identify related models/routes/services/templates.
4. Reuse existing patterns where possible.
5. Make the smallest reasonable change.

Do not blindly overwrite working code.

---

## 6.2 Preserve Existing Functionality

When adding a feature:

- Do not unnecessarily rewrite unrelated code.
- Do not remove working functionality.
- Do not change APIs without checking existing consumers.
- Do not break existing database relationships.
- Do not change UI behavior without considering existing pages.

A feature is not complete if it breaks an existing core workflow.

---

# 7. Feature Priority

Every feature must be classified as:

## P0 — Core

Required for the MVP.

Examples:

- Authentication
- Creator profiles
- Portfolio creation
- Portfolio metadata
- File uploads
- Company profiles
- Creative briefs/projects
- Creator discovery
- Search
- Filtering
- Creator profile viewing
- Creator selection/engagement

## P1 — Important

Useful for a strong hackathon submission.

Examples:

- Better search ranking
- Rich portfolio previews
- Project discovery
- Creator/project matching
- Profile completion
- Improved dashboard UX
- Better validation
- Verification signals

## P2 — Optional

Only implement after P0/P1 functionality is stable.

Examples:

- RAG
- Semantic search
- AI-assisted brief generation
- Advanced recommendation systems
- Complex analytics
- Additional marketplace features

Do not implement P2 features while P0 functionality is broken.

---

# 8. Core Functionality Must Not Depend on AI

The following must work without Groq, LangChain, or an LLM:

- Creator profile creation
- Portfolio creation
- Portfolio metadata
- File upload
- Company profile creation
- Project/brief creation
- Search
- Filtering
- Creator profile viewing
- Project discovery
- Creator selection

AI failures must never make the marketplace unusable.

---

# 9. AI Integration Rules

When implementing Groq:

- Read the API key from environment variables.
- Never hardcode API keys.
- Never expose the API key to frontend JavaScript.
- Handle API failures gracefully.
- Add timeouts where appropriate.
- Validate generated output.
- Allow users to edit generated content.
- Never automatically publish AI-generated content.

Expected flow:

```text
User Input
   ↓
FastAPI
   ↓
AI Service
   ↓
Groq
   ↓
Structured Result
   ↓
User Review
   ↓
User Confirmation
   ↓
Save
```

---

# 10. AI Brief Builder

The AI Brief Builder is an optional enhancement.

Its purpose is to convert a rough project idea into a structured creative brief.

Example:

```text
Input:

"I need a cinematic AI video campaign
for a new sports shoe."

Output:

Title
Description
Content Type
Style
Format
Aspect Ratio
Commercial Use
Required Skills
Potential Tools
Creative Requirements
```

The user must be able to:

- Review
- Edit
- Regenerate
- Reject
- Save

AI output must not directly become a published project.

---

# 11. RAG / Semantic Search Rules

If RAG or semantic search is implemented:

- It must be an enhancement.
- Deterministic search must continue to work.
- Structured filters must remain available.
- Do not make the user understand vector databases or embeddings.
- Do not use semantic search where simple database filtering is sufficient.
- Avoid unnecessary infrastructure.

Preferred search strategy:

```text
User Query
    ↓
Normalize Query
    ↓
Structured Filters
    ↓
Keyword Search
    ↓
Optional Semantic Matching
    ↓
Ranking
    ↓
Results
```

---

# 12. Database Rules

Use SQLAlchemy for database access.

Do not scatter raw SQL throughout route handlers.

Preferred:

```text
Route
  ↓
Service
  ↓
Repository
  ↓
SQLAlchemy
```

Database models should remain portable between SQLite and MySQL.

Avoid SQLite-specific behavior unless absolutely necessary.

Do not rely on SQLite-specific data types that make migration difficult.

---

# 13. Core Data Models

The implementation should support concepts equivalent to:

## User

Stores authentication/account information.

Possible fields:

- id
- email
- password hash
- role
- created_at
- updated_at

Roles:

```text
CREATOR
COMPANY
ADMIN
```

Only implement ADMIN functionality if actually required.

---

## CreatorProfile

Possible fields:

- user_id
- display_name
- headline
- bio
- specialization
- skills
- tools/models
- workflow
- profile image
- verification status where supported

---

## PortfolioItem

Possible fields:

- creator_id
- title
- description
- file path/storage reference
- file type
- content type
- format
- aspect ratio
- specialization
- skills
- tools/models
- workflow
- created_at

Portfolio metadata should be searchable.

---

## CompanyProfile

Possible fields:

- user_id
- company name
- industry
- description
- website
- tags

---

## Project / CreativeBrief

Possible fields:

- company_id
- title
- description
- campaign requirements
- content type
- style
- format
- aspect ratio
- commercial use requirements
- required skills
- preferred tools/models
- specialization
- status
- created_at
- updated_at

---

# 14. Relationships

Expected relationships:

```text
User
 ├── CreatorProfile
 │      └── PortfolioItems
 │
 └── CompanyProfile
        └── Projects / CreativeBriefs
```

Creator selection/engagement should use explicit relationships rather than storing arbitrary IDs in unrelated tables.

---

# 15. API Rules

FastAPI endpoints should:

- Use appropriate HTTP methods.
- Validate request data.
- Validate authorization.
- Return predictable responses.
- Use appropriate status codes.
- Avoid exposing internal exceptions.

Typical structure:

```text
GET    /api/creators
GET    /api/creators/{id}
POST   /api/creators
PUT    /api/creators/{id}

GET    /api/portfolio
POST   /api/portfolio
GET    /api/portfolio/{id}
PUT    /api/portfolio/{id}
DELETE /api/portfolio/{id}

GET    /api/projects
POST   /api/projects
GET    /api/projects/{id}
PUT    /api/projects/{id}

POST   /api/ai/brief
POST   /api/engagements
```

Actual routes should follow the existing project implementation if already established.

Do not create duplicate endpoints for the same functionality.

---

# 16. Authentication

Authentication must be handled server-side.

Never trust:

```text
role=creator
```

from the browser as proof of authorization.

Every protected backend operation must verify:

1. User identity
2. User role
3. Resource ownership where applicable

Examples:

A creator should be able to edit their own profile.

A company should not be able to edit another company's project.

A company should not be able to edit a creator's profile.

---

# 17. Password Security

Never store plaintext passwords.

Use a proper password hashing mechanism.

Never log:

- Passwords
- Password hashes
- API keys
- Authentication tokens
- Sensitive credentials

---

# 18. File Upload Rules

Portfolio uploads are core functionality.

Uploads must:

- Validate file type.
- Validate file size.
- Generate safe storage names.
- Prevent path traversal.
- Avoid trusting the original filename.
- Store metadata separately from storage paths.
- Return safe references to the frontend.

Never construct storage paths directly from untrusted user input.

Bad:

```python
path = upload_dir / filename
```

Prefer a generated safe filename.

---

# 19. Portfolio Metadata

Portfolio metadata is important for discovery.

Do not treat a portfolio upload as merely:

```text
file + title
```

Where applicable, support:

- Title
- Description
- Content type
- Format
- Aspect ratio
- Skills
- Specialization
- Tools/models
- Workflow

This metadata should be available to search/filter functionality.

---

# 20. Search Rules

Search should be deterministic and testable.

Search may consider:

- Creator name
- Skills
- Specialization
- Tools/models
- Portfolio title
- Portfolio description
- Content type
- Format
- Aspect ratio

Filters should be combinable.

Example:

```text
Skill = AI Video
AND
Tool = Runway
AND
Aspect Ratio = 16:9
AND
Specialization = Advertising
```

Do not implement search as a fake frontend-only filter.

Filtering must be backed by real application data.

---

# 21. Search UX

Search should support:

```text
Search creators...
```

with filters for:

- Skills
- Specialization
- Tools/models
- Content type
- Format
- Aspect ratio

Search results should display enough information for users to understand relevance.

---

# 22. Pagination

Do not load unlimited records.

Use pagination or reasonable limits for:

- Creator search
- Project search
- Portfolio listings

The UI should clearly indicate result counts where useful.

---

# 23. Frontend Rules

Use:

- Semantic HTML
- Bootstrap
- Small reusable components/templates
- Custom CSS only where needed
- Vanilla JavaScript where sufficient

Avoid introducing unnecessary frontend dependencies.

---

# 24. UI Priorities

The UI should prioritize:

1. Creator portfolio presentation
2. Creator discovery
3. Search/filtering
4. Structured project creation
5. Creator profile evaluation
6. Clear dashboard actions
7. Responsive behavior

The UI should be visually good but not over-engineered.

---

# 25. Responsive Design

Pages must work on:

- Desktop
- Tablet
- Mobile

Creator search should adapt from:

```text
Desktop:

Filters | Results
```

to:

```text
Mobile:

[ Filters ]

Results
```

Portfolio grids should collapse appropriately.

---

# 26. UI States

Major UI features must account for:

```text
Loading
Success
Empty
Error
Unauthorized
Not Found
```

Examples:

```text
Searching creators...
```

```text
No creators found.
Try changing your filters.
```

```text
Unable to load creators.
[ Try Again ]
```

Do not leave users staring at blank pages.

---

# 27. Error Handling

Backend errors should be:

- Logged appropriately.
- Converted into safe user-facing messages.
- Associated with appropriate HTTP status codes.

Never expose stack traces to users.

Bad:

```text
Traceback...
sqlalchemy.exc...
```

Better:

```text
Unable to save the portfolio item.
Please try again.
```

---

# 28. Validation

Validate data at multiple levels.

## Frontend

Provide immediate feedback.

## Backend

Perform authoritative validation.

## Database

Use constraints where appropriate.

Never rely only on frontend validation.

---

# 29. API Error Format

Use a consistent error response where practical.

Example:

```json
{
  "detail": "Unable to create portfolio item."
}
```

For validation errors, provide useful field-level information when possible.

---

# 30. Code Style

Python code should:

- Follow PEP 8.
- Use meaningful names.
- Use type hints.
- Keep functions focused.
- Avoid unnecessary abstraction.
- Avoid giant route handlers.
- Avoid duplicated business logic.

Prefer:

```text
route
 ↓
service
 ↓
repository
```

over:

```text
route containing 200 lines of business logic
```

---

# 31. Function Design

Functions should generally have one clear responsibility.

Bad:

```text
create_creator_and_upload_files_and_send_email_and_generate_ai_profile()
```

Prefer separate responsibilities.

Keep abstractions proportional to the project.

Do not create abstractions merely for the sake of architecture.

---

# 32. Naming

Use descriptive names.

Good:

```text
creator_profile
portfolio_item
creative_brief
search_creators
create_portfolio_item
```

Avoid:

```text
data
obj
temp
thing
foo
```

unless they are genuinely appropriate in local context.

---

# 33. Templates

If using server-rendered HTML templates:

Keep templates focused on presentation.

Do not put significant business logic into templates.

Prefer:

```text
Backend prepares data
        ↓
Template renders data
```

---

# 34. JavaScript

JavaScript should handle:

- UI interactions
- Form enhancements
- Search controls
- Upload previews
- Dynamic fields
- AI Builder interactions

Do not move business authorization or core validation into JavaScript.

---

# 35. Secrets

Never commit:

```text
.env
API keys
passwords
tokens
private credentials
```

Use environment variables.

Provide `.env.example` where useful.

Example:

```text
GROQ_API_KEY=
DATABASE_URL=
SECRET_KEY=
```

Do not put real values in `.env.example`.

---

# 36. Configuration

Configuration should be centralized.

Avoid hardcoding:

- Database URLs
- API keys
- Upload directories
- Environment-specific settings
- Secret values

Development and production settings should be separable.

---

# 37. Logging

Logs should help debugging without exposing secrets.

Useful:

```text
INFO: Creator search completed
INFO: Portfolio uploaded
WARNING: AI provider unavailable
ERROR: Database operation failed
```

Avoid logging:

```text
password=...
api_key=...
token=...
```

---

# 38. Testing Strategy

Testing is especially important because the hackathon prototype may be evaluated automatically.

Prioritize tests for:

## P0

- Authentication
- Creator creation
- Creator profile updates
- Portfolio creation
- Portfolio metadata
- File validation
- Project creation
- Search
- Filtering
- Authorization

## P1

- Project discovery
- Engagement workflow
- Search ranking
- AI Builder failure handling

## P2

- Semantic search
- RAG
- Advanced recommendations

---

# 39. Deterministic Testing

Tests should not depend on live Groq responses.

For AI functionality:

- Mock the AI service.
- Test successful generation.
- Test failure.
- Test malformed AI output.
- Test user editing/confirmation flow.

Core tests should pass even if:

```text
GROQ_API_KEY
```

is unavailable.

---

# 40. Test Data

Tests should use predictable fixtures.

Example creator:

```text
Creator:
Alex Morgan

Skills:
AI Video
Storytelling

Tools:
Runway

Specialization:
Advertising
```

Example project:

```text
Project:
AI Product Campaign

Content Type:
AI Video

Aspect Ratio:
16:9

Skill:
AI Video

Tool:
Runway
```

Tests should verify that relevant creators are returned.

---

# 41. Search Testing

At minimum test:

```text
No filters
One filter
Multiple filters
Keyword search
No results
Invalid filter
Pagination
```

Example:

```text
AI Video + Runway
```

should return creators matching those attributes.

---

# 42. Authorization Testing

Test:

```text
Creator edits own profile → allowed

Creator edits another creator → denied

Company edits own project → allowed

Company edits another company's project → denied

Unauthenticated user accesses protected route → denied
```

---

# 43. Database Testing

Use a test database.

Do not run destructive tests against the real development database.

Test:

- Creation
- Relationships
- Updates
- Deletion where supported
- Constraints

---

# 44. Definition of Done

A feature is complete only when:

- [ ] Backend implementation exists
- [ ] Database integration works
- [ ] Authorization is implemented
- [ ] Validation exists
- [ ] Frontend is connected
- [ ] Loading state exists where needed
- [ ] Empty state exists where needed
- [ ] Error handling exists
- [ ] Tests cover important behavior
- [ ] Existing functionality still works
- [ ] No secrets are exposed
- [ ] Code is understandable

---

# 45. Agent Workflow

When assigned a development task, follow:

```text
1. Understand the requirement
        ↓
2. Inspect existing code
        ↓
3. Identify affected components
        ↓
4. Decide whether the task is P0/P1/P2
        ↓
5. Implement the smallest complete solution
        ↓
6. Run relevant tests
        ↓
7. Fix failures
        ↓
8. Check existing functionality
        ↓
9. Review security and validation
        ↓
10. Summarize changes
```

---

# 46. Before Adding Dependencies

Before installing a dependency:

1. Check whether the standard library can solve it.
2. Check whether the existing stack already provides the functionality.
3. Check whether the dependency is necessary for the MVP.
4. Consider hackathon deployment simplicity.

Avoid dependency bloat.

---

# 47. Before Adding a Feature

Ask:

```text
Does this directly improve the core marketplace?
```

If no:

```text
Can it wait until P1/P2?
```

Do not allow feature creep.

---

# 48. Do Not Overengineer

Avoid:

- Microservices
- Event-driven architecture
- Complex queues
- Kubernetes
- Complex vector infrastructure
- Large frontend frameworks
- Multiple databases without need
- Excessive design patterns
- Premature optimization

The target is a strong, working hackathon prototype.

---

# 49. Migration Strategy

SQLite is the current database.

However, code should make future MySQL migration straightforward.

Avoid:

- SQLite-specific assumptions
- Hardcoded SQLite SQL
- SQLite-only schema behavior
- Database-specific hacks

Use SQLAlchemy models and database abstractions.

---

# 50. Storage Strategy

File storage should be abstracted enough to allow migration later.

Development may use local storage:

```text
uploads/
```

The rest of the application should not depend heavily on the exact storage implementation.

A future storage provider can be introduced without rewriting portfolio logic.

---

# 51. Security Priorities

At minimum protect against:

- Unauthorized access
- Broken ownership checks
- Unsafe file uploads
- Path traversal
- Secret exposure
- SQL injection
- Unsafe HTML rendering
- Invalid input
- Oversized uploads

Use framework/library protections wherever possible.

---

# 52. Performance Priorities

For the hackathon:

Prioritize:

1. Correctness
2. Search responsiveness
3. Reasonable database queries
4. Efficient portfolio listing
5. Good perceived UI performance

Do not optimize prematurely.

---

# 53. Git Practices

Use meaningful commits.

Examples:

```text
feat: add creator profile management
feat: add portfolio metadata
feat: add creator search filters
feat: add company project creation
feat: add AI brief builder
fix: validate portfolio uploads
fix: enforce creator ownership
```

Avoid commits such as:

```text
update
changes
stuff
final
final2
```

---

# 54. Documentation

Important architecture decisions should be documented.

Relevant context files include:

```text
AGENTS.md
architecture.md
code-standard.md
context_ai-workflow-rules.md
progress-tracker.md
project-overview.md
ui-context.md
```

Agents should consult the relevant context file before making substantial changes.

---

# 55. Context File Priority

When context files overlap:

```text
AGENTS.md
    ↓
ai-workflow-rules.md
    ↓
architecture.md
    ↓
code-standard.md
    ↓
project-overview.md
    ↓
ui-context.md
    ↓
progress-tracker.md
```

If a more specific implementation rule exists, follow it unless it conflicts with a higher-priority project requirement.

---

# 56. Progress Tracking

When completing a meaningful feature, update the project's progress tracking.

Record:

- Feature
- Status
- What was implemented
- Tests completed
- Remaining work
- Blockers

Use statuses such as:

```text
NOT STARTED
IN PROGRESS
BLOCKED
COMPLETE
```

Do not mark a feature complete simply because code was written.

---

# 57. Blocker Rules

If blocked:

1. Identify the exact blocker.
2. Determine whether it affects P0/P1/P2.
3. Try a reasonable alternative.
4. Do not silently skip the feature.
5. Record the blocker.

Example:

```text
BLOCKED

Feature:
Groq AI Builder

Reason:
GROQ_API_KEY unavailable.

Impact:
P2 only.

Fallback:
Manual brief creation remains fully functional.
```

---

# 58. Hackathon Time Management

When time is limited:

## First

Make P0 work.

## Second

Make P0 reliable.

## Third

Polish P0 UI.

## Fourth

Implement high-value P1 functionality.

## Fifth

Add AI/RAG bonus functionality.

Do not spend the final development period polishing an incomplete core workflow.

---

# 59. Evaluation-Oriented Development

The challenge evaluates primarily:

- Creator profiles and portfolios
- Brief definition
- Discovery/filtering
- UX
- Presentation/demo

Therefore development should prioritize those areas.

The strongest demo should show:

```text
Create Creator
      ↓
Add Portfolio
      ↓
Add Metadata
      ↓
Create Company Project
      ↓
Search Creators
      ↓
Apply Filters
      ↓
Open Creator
      ↓
Review Portfolio
      ↓
Select Creator
```

Optional:

```text
Create rough idea
      ↓
AI Brief Builder
      ↓
Generated structured brief
      ↓
Edit
      ↓
Save
```

---

# 60. Automated Evaluation Considerations

Because the first round may involve automated testing:

- Keep routes predictable.
- Keep database behavior deterministic.
- Avoid random business behavior.
- Avoid AI-dependent core functionality.
- Validate inputs consistently.
- Return predictable status codes.
- Keep important operations independently testable.
- Do not require manual frontend interaction for backend-critical operations.

---

# 61. Do Not Fake Functionality

Do not implement fake:

- Search results
- Creator matches
- Portfolio counts
- AI responses
- Engagement statuses
- Verification badges

If the UI displays a value, it should come from actual application state unless it is explicitly demo-only data.

---

# 62. Demo Data Rules

Demo/sample data may be used when appropriate.

However:

- Clearly separate seed/demo data from user data.
- Do not hardcode demo results into search logic.
- Do not make search appear functional using static frontend arrays.
- Demo data should use the same database models as real data.

---

# 63. Agent Communication

When reporting completed work, provide:

### What Changed

Short list of implementation changes.

### Files Changed

Relevant files.

### Tests

Tests run and their results.

### Remaining Issues

Any known limitations.

Example:

```text
Implemented:
- Creator profile CRUD
- Portfolio metadata
- Creator search

Tests:
- 18 passed

Remaining:
- Semantic search not implemented
- AI Builder pending Groq configuration
```

Do not claim tests passed if they were not run.

---

# 64. Final Release Checklist

Before considering the MVP ready:

## Authentication

- [ ] Registration works
- [ ] Login works
- [ ] Logout works
- [ ] Roles work
- [ ] Protected routes work

## Creator

- [ ] Creator profile works
- [ ] Skills work
- [ ] Specialization works
- [ ] Tools/models work
- [ ] Workflow works
- [ ] Portfolio creation works
- [ ] Portfolio metadata works
- [ ] File upload works
- [ ] Portfolio display works

## Company

- [ ] Company profile works
- [ ] Project creation works
- [ ] Brief fields work
- [ ] Project listing works
- [ ] Project detail works

## Discovery

- [ ] Creator search works
- [ ] Skills filter works
- [ ] Specialization filter works
- [ ] Tools filter works
- [ ] Content type filter works
- [ ] Format filter works
- [ ] Aspect ratio filter works
- [ ] Multiple filters work
- [ ] Empty results work

## Engagement

- [ ] Creator selection works
- [ ] Authorization works
- [ ] Status is stored correctly

## AI

- [ ] AI Builder is optional
- [ ] Groq key is environment-based
- [ ] AI errors are handled
- [ ] Generated brief is editable
- [ ] Core marketplace works without AI

## UI

- [ ] Desktop works
- [ ] Mobile works
- [ ] Loading states work
- [ ] Empty states work
- [ ] Error states work
- [ ] Forms are understandable
- [ ] Portfolio looks polished

## Testing

- [ ] Core API tests pass
- [ ] Search tests pass
- [ ] Authorization tests pass
- [ ] Upload validation tests pass
- [ ] AI service is mocked in tests
- [ ] No obvious regressions

---

# 65. Final Agent Rule

When making any decision in this repository, prefer:

```text
Simple
        +
Correct
        +
Testable
        +
Secure
        +
Hackathon-relevant
```

over:

```text
Complex
        +
Over-engineered
        +
AI-dependent
        +
Difficult to test
```

The goal is not to build the largest possible system.

The goal is to build a **working, polished, testable AI Content Creator Marketplace** that clearly demonstrates:

```text
AI Creators
     ↕
Profiles
     ↕
Portfolios
     ↕
Structured Metadata
     ↕
Creative Briefs
     ↕
Search & Filtering
     ↕
Creator Discovery
     ↕
Engagement
```

Everything else is secondary.