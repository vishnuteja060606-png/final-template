# UI Context

## 1. Purpose

This document defines the UI/UX direction, layout principles, page structure, reusable components, interaction patterns, and visual priorities for the **AI Content Creator Marketplace**.

The UI should make the product feel like a modern marketplace specifically designed for AI-native creative talent.

The interface must prioritize:

1. Creator profiles
2. AI portfolios
3. Portfolio metadata
4. Company/project briefs
5. Creator discovery
6. Search and filtering
7. Creator evaluation
8. Simple creator selection/engagement
9. Reliable forms and feedback
10. Optional AI-assisted workflows

The UI should remain simple enough to build quickly with:

- HTML
- CSS
- JavaScript
- Bootstrap

Do not introduce unnecessary frontend complexity.

---

# 2. Product UI Identity

## Product Name

**AI Content Creator Marketplace**

## Product Concept

A marketplace where:

- AI creators showcase their creative capabilities.
- Brands and companies publish creative requirements.
- Companies discover creators using AI-specific search criteria.
- Companies evaluate creators through their profiles and portfolios.
- Optional AI features help companies create better briefs.

The UI should communicate:

> Discover the right AI creator for your creative project.

---

# 3. Primary UX Goal

The most important user journey is:

```text
Company
    ↓
Create / View Project
    ↓
Search Creators
    ↓
Apply Filters
    ↓
Review Results
    ↓
Open Creator Profile
    ↓
Review Portfolio
    ↓
Evaluate Skills / Tools / Workflow
    ↓
Select / Engage Creator
```

The UI should make this journey obvious.

A user should never need to guess:

- where to search
- where to create a project
- how to filter creators
- how to view a portfolio
- how to understand creator capabilities
- what action to take next

---

# 4. UI Design Principles

## 4.1 Simple First

Do not over-design the application.

Prefer:

- Clear cards
- Clear buttons
- Clear forms
- Clear headings
- Consistent spacing
- Strong visual hierarchy

Avoid:

- Excessive animations
- Complex navigation
- Too many popups
- Unnecessary modals
- Decorative UI with no purpose
- Excessive gradients
- Complicated dashboards

---

## 4.2 Marketplace First

The interface should feel like a marketplace rather than an AI chatbot.

AI should enhance the marketplace.

The primary experience is:

```text
Profile
+
Portfolio
+
Project
+
Search
+
Discovery
```

Not:

```text
Chatbot
+
AI generation
+
Marketplace
```

---

## 4.3 Portfolio First

Creator portfolios are one of the most important visual elements.

Portfolio work should be visually prominent.

Metadata should be easy to scan without overwhelming the user.

---

## 4.4 Search First for Companies

Companies should be able to quickly move from:

```text
"I need an AI creator"
```

to:

```text
"Here are 5 relevant creators."
```

Search and filtering should therefore be one of the strongest UI areas.

---

## 4.5 Forms Should Be Structured

Forms should not feel like large walls of text.

Use:

- Sections
- Labels
- Help text
- Select inputs
- Multi-selects
- Tags
- Checkboxes where appropriate
- Clear required-field indicators

---

# 5. Visual Direction

The UI should have a modern creative/technology feel.

## Desired Characteristics

- Clean
- Modern
- Professional
- Creative
- Minimal
- Responsive
- Portfolio-oriented
- AI-native

## Avoid

- Corporate-looking legacy UI
- Overly colorful dashboards
- Excessive glassmorphism
- Excessive gradients
- Heavy animations
- Cluttered layouts

The application should look polished without requiring a complex design system.

---

# 6. Frontend Technology

## Required

- HTML
- CSS
- JavaScript
- Bootstrap

## Optional

Small custom CSS files may be used for:

- Typography
- Spacing
- Cards
- Portfolio presentation
- Search UI
- Badges
- Responsive improvements

JavaScript should be used for:

- Search interactions
- Filter updates
- Form enhancements
- Upload previews
- Dynamic fields
- AI Builder interactions
- Lightweight UI state

Do not add a frontend framework unless there is a clear requirement.

---

# 7. Global Layout

The application should use a consistent structure.

```text
┌────────────────────────────────────────────────────┐
│ Logo / Brand       Discover    Projects    Dashboard│
│                                      Profile / Login│
├────────────────────────────────────────────────────┤
│                                                    │
│                    Page Content                    │
│                                                    │
│                                                    │
├────────────────────────────────────────────────────┤
│ Footer                                             │
└────────────────────────────────────────────────────┘
```

---

# 8. Navigation

## Unauthenticated Navigation

Possible navigation:

```text
Logo
Creators
Projects
Login
Sign Up
```

The exact public navigation can remain small.

---

## Creator Navigation

```text
Logo
Discover Projects
My Profile
My Portfolio
Dashboard
Logout
```

---

## Company Navigation

```text
Logo
Discover Creators
My Projects
Company Profile
Dashboard
Logout
```

---

# 9. Navbar Rules

The navbar should:

- Remain consistent across pages
- Clearly show the current section
- Be responsive
- Collapse on smaller screens
- Avoid excessive links

Use Bootstrap's responsive navbar behavior.

The navbar should not become a dashboard itself.

---

# 10. Homepage

## Goal

Immediately explain what the marketplace does.

## Hero

Example structure:

```text
Find the right AI creator
for your next creative project.

Discover AI creators through their skills,
tools, workflows, and real portfolio work.

[ Find Creators ]    [ Create Profile ]
```

The hero should communicate the marketplace value quickly.

---

# 11. Homepage Sections

Recommended sections:

## Hero

Main product proposition.

## How It Works

```text
01
Create your profile

02
Showcase your AI work

03
Publish or discover projects

04
Find the right creative match
```

## Featured Creators

Show a small number of creator cards.

## Featured Projects

Show selected projects.

## AI-Native Discovery

Explain that users can search by:

- Skills
- Specialization
- Tools/models
- Content type
- Portfolio metadata

## Call to Action

Examples:

```text
Are you an AI creator?
[ Create Creator Profile ]
```

```text
Looking for AI talent?
[ Find Creators ]
```

---

# 12. Authentication UI

## Login Page

Simple centered form.

```text
┌──────────────────────────────┐
│        Welcome back          │
│                              │
│ Email                        │
│ [________________________]   │
│                              │
│ Password                     │
│ [________________________]   │
│                              │
│ [ Login ]                    │
│                              │
│ Don't have an account?       │
│ Sign up                      │
└──────────────────────────────┘
```

---

# 13. Registration Page

Registration should ask only for information needed initially.

```text
Name
Email
Password
Account Type
    ○ Creator
    ○ Company / Brand
```

After registration:

```text
Creator → Creator Profile setup

Company → Company Profile setup
```

Do not create an unnecessarily long registration form.

---

# 14. Creator Dashboard

The creator dashboard should be action-oriented.

Example:

```text
Creator Dashboard

Welcome, Creator Name

┌────────────┐ ┌────────────┐ ┌────────────┐
│ Profile    │ │ Portfolio  │ │ Projects   │
│ 85%        │ │ 8 works    │ │ 4 matches  │
└────────────┘ └────────────┘ └────────────┘

Quick Actions

[ Edit Profile ]
[ Add Portfolio Work ]
[ Discover Projects ]

Recent Portfolio
────────────────────────────────────────────

Recent Opportunities
────────────────────────────────────────────
```

---

# 15. Creator Profile Editor

The profile editor should be divided into clear sections.

## Basic Information

- Display name
- Headline
- Bio

## Specialization

Examples:

- AI Video
- AI Animation
- Generative Advertising
- AI Graphics
- Social Content

## Skills

Use tags or multi-select.

Example:

```text
[ AI Video ] [ Prompting ] [ Storyboarding ]
[ Motion ] [ Generative Advertising ]
```

## Tools / Models

Example:

```text
[ Runway ] [ Midjourney ] [ Sora ]
[ Stable Diffusion ] [ Kling ]
```

## Workflow

Large but structured text area.

Example helper text:

> Describe how you typically approach an AI creative project.

## Save

Use a prominent primary action:

```text
[ Save Profile ]
```

---

# 16. Public Creator Profile

This is one of the most important pages in the application.

The company should be able to understand the creator quickly.

Recommended structure:

```text
┌─────────────────────────────────────────────────┐
│ Creator Name                                    │
│ AI Video Creator                                │
│                                                 │
│ AI Video • Advertising • Generative Media       │
│                                                 │
│ [ Contact / Select Creator ]                    │
└─────────────────────────────────────────────────┘

About
───────────────────────────────────────────────────

Specialization
───────────────────────────────────────────────────

Skills
[ Video ] [ Animation ] [ Prompting ]

Tools & Models
[ Runway ] [ Midjourney ] [ Sora ]

Workflow
───────────────────────────────────────────────────

Portfolio
───────────────────────────────────────────────────

[Work 1] [Work 2] [Work 3]
[Work 4] [Work 5] [Work 6]
```

---

# 17. Creator Profile Hierarchy

Information priority:

### Highest

1. Creator name
2. Specialization
3. Portfolio
4. Primary skills

### Medium

5. Tools/models
6. Workflow
7. Bio

### Supporting

8. Tags
9. Experience
10. Additional information

The user should understand the creator's value before reading every detail.

---

# 18. Portfolio Grid

Portfolio should use a responsive grid.

Desktop:

```text
┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│             │ │             │ │             │
│   Preview   │ │   Preview   │ │   Preview   │
│             │ │             │ │             │
├─────────────┤ ├─────────────┤ ├─────────────┤
│ Work Title  │ │ Work Title  │ │ Work Title  │
│ AI Video    │ │ Animation   │ │ Advertising │
└─────────────┘ └─────────────┘ └─────────────┘
```

Mobile:

```text
┌──────────────────────┐
│       Preview        │
├──────────────────────┤
│ Work Title           │
│ AI Video             │
└──────────────────────┘
```

---

# 19. Portfolio Card

Each portfolio card should show:

- Preview
- Title
- Content type
- Short description
- Tools/models
- Important tags

Example:

```text
┌──────────────────────────┐
│                          │
│        Preview           │
│                          │
├──────────────────────────┤
│ Nike AI Campaign         │
│ AI Video • 16:9          │
│                          │
│ Runway • Gen-3           │
│ Advertising             │
│                          │
│ [ View Work ]            │
└──────────────────────────┘
```

---

# 20. Portfolio Detail Page

The detail page should provide complete information.

```text
Portfolio Work

┌──────────────────────────────┐
│                              │
│          Media               │
│                              │
└──────────────────────────────┘

Title
Description

Content Type
AI Video

Format
MP4

Aspect Ratio
16:9

Tools / Models
Runway

Skills
AI Video • Editing • Prompting

Specialization
Advertising

Workflow
...
```

The company should not need to guess what tools or techniques were used.

---

# 21. Add Portfolio Form

The form should be structured.

## Work Information

- Title
- Description
- File

## Creative Metadata

- Content type
- Format
- Aspect ratio
- Specialization

## Skills

- Skills/tags

## AI Information

- Tools/models
- Workflow

Example:

```text
Add Portfolio Work

Work Title
[________________________]

Description
[________________________]
[                        ]

Upload File
[ Choose File ]

Content Type
[ AI Video ▼ ]

Format
[ MP4 ▼ ]

Aspect Ratio
[ 16:9 ▼ ]

Tools / Models
[ Runway ] [ Add Tool ]

Skills
[ AI Video ] [ Prompting ]

Specialization
[ Advertising ▼ ]

Workflow
[________________________]
[                        ]

[ Save Portfolio Work ]
```

---

# 22. Upload UI

File uploads should provide immediate feedback.

States:

### Initial

```text
Drag & drop file here

or

[ Choose File ]
```

### Selected

```text
✓ example-video.mp4
12.4 MB

[ Change File ]
```

### Uploading

```text
Uploading...

████████████░░░░
```

### Success

```text
✓ Upload complete
```

### Error

```text
Unable to upload this file.

Supported formats: ...
Maximum size: ...
```

Do not expose technical stack traces.

---

# 23. Company Dashboard

Example:

```text
Company Dashboard

Welcome, Company Name

┌────────────┐ ┌────────────┐ ┌────────────┐
│ Projects   │ │ Published  │ │ Matches    │
│ 8          │ │ 5          │ │ 12         │
└────────────┘ └────────────┘ └────────────┘

Quick Actions

[ Create Project ]
[ Discover Creators ]

My Projects
────────────────────────────────────────
```

---

# 24. Company Profile

The company profile should be simple.

```text
Company Name

Industry
Creative / Advertising

About
...

Website
...

Tags
[ Advertising ] [ Fashion ] [ Media ]
```

---

# 25. Project Creation UI

The project creation form is one of the most important forms.

It should feel like a structured creative brief.

## Section 1 — Project Basics

- Project title
- Description

## Section 2 — Campaign

- Campaign requirements
- Intended use

## Section 3 — Creative Requirements

- Content type
- Style
- Format
- Aspect ratio

## Section 4 — Creator Requirements

- Skills
- Tools/models
- Specialization

## Section 5 — Commercial Use

- Commercial-use requirements

## Section 6 — Publishing

```text
[ Save Draft ]    [ Publish Project ]
```

---

# 26. Project Form UX

Do not put every field into one visually overwhelming block.

Use sections.

Example:

```text
Create Creative Project

1. Project Basics
────────────────────────────
Title
Description

2. Creative Direction
────────────────────────────
Content Type
Style
Format
Aspect Ratio

3. Creator Requirements
────────────────────────────
Skills
Tools / Models
Specialization

4. Usage
────────────────────────────
Commercial Use Requirements

5. Publish
────────────────────────────
[ Save Draft ] [ Publish ]
```

---

# 27. Project Detail Page

Example:

```text
AI Product Launch Video

Company Name

Project Overview
...

Creative Requirements

Content Type
AI Video

Style
Cinematic

Format
MP4

Aspect Ratio
16:9

Commercial Use
Required

Creator Requirements

Skills
AI Video
Advertising
Storytelling

Tools
Runway
Kling

[ Find Suitable Creators ]
```

---

# 28. Creator Search Page

This should be one of the strongest pages in the application.

Recommended layout:

```text
Discover AI Creators

┌──────────────────────────────────────────────┐
│ Search creators, skills, tools...            │
└──────────────────────────────────────────────┘

┌──────────────┐  ┌────────────────────────────┐
│ Filters      │  │ 24 creators found          │
│              │  │                            │
│ Skills       │  │ Creator Card              │
│ [ ... ]      │  │                            │
│              │  │ Creator Card              │
│ Specialize   │  │                            │
│ [ ... ]      │  │ Creator Card              │
│              │  │                            │
│ Tools        │  │ Creator Card              │
│ [ ... ]      │  │                            │
│ Content Type │  │                            │
│ [ ... ]      │  │                            │
│              │  │                            │
│ [Clear]      │  │                            │
└──────────────┘  └────────────────────────────┘
```

Desktop can use sidebar filters.

Mobile should move filters into a collapsible section or off-canvas panel.

---

# 29. Search Bar

Search placeholder:

```text
Search creators by skills, tools, specialization...
```

The search bar should be prominent.

It should support terms related to:

- Creator name
- Skills
- Tools/models
- Specialization
- Portfolio descriptions

---

# 30. Filter Components

Use Bootstrap controls where practical.

## Skills

Checkboxes or multi-select.

## Specialization

Select/dropdown.

## Tools

Multi-select/tag selection.

## Content Type

Examples:

- Video
- Animation
- Graphics
- Advertising
- Social Content

## Format

Examples:

- MP4
- PNG
- JPG
- GIF
- Other supported formats

## Aspect Ratio

Examples:

- 16:9
- 9:16
- 1:1
- 4:5

The available options should reflect actual backend-supported values.

---

# 31. Active Filter UI

Active filters should be visible.

Example:

```text
Active Filters:

[ AI Video × ]
[ Runway × ]
[ Advertising × ]
[ 16:9 × ]

[ Clear All ]
```

Users should be able to remove individual filters.

---

# 32. Search Result Card

Creator result cards should communicate suitability quickly.

Example:

```text
┌─────────────────────────────────────┐
│ Avatar / Preview                    │
│                                     │
│ Alex Morgan                         │
│ AI Video & Advertising              │
│                                     │
│ Skills                              │
│ AI Video • Storytelling • Motion    │
│                                     │
│ Tools                               │
│ Runway • Kling                      │
│                                     │
│ Portfolio: 12 works                 │
│                                     │
│ [ View Profile ]                    │
└─────────────────────────────────────┘
```

Do not overload cards with every metadata field.

---

# 33. Search Results States

## Results

Show:

```text
24 creators found
```

## Loading

```text
Searching creators...
```

Use a spinner or skeleton where appropriate.

## Empty

```text
No creators found.

Try removing some filters or changing your search.

[ Clear Filters ]
```

## Error

```text
We couldn't load creators right now.

[ Try Again ]
```

---

# 34. Project Search Page

The project discovery page should mirror creator search.

```text
Discover Projects

[ Search projects... ]

Filters

Content Type
Specialization
Skills
Tools
Format
Aspect Ratio

Results
────────────────────────────

Project Card
Project Card
Project Card
```

---

# 35. Project Card

Example:

```text
┌──────────────────────────────┐
│ AI Product Launch Video      │
│                              │
│ Company Name                 │
│                              │
│ AI Video • 16:9              │
│ Advertising                 │
│                              │
│ Skills                       │
│ Video • Storytelling         │
│                              │
│ [ View Project ]             │
└──────────────────────────────┘
```

---

# 36. Creator Selection UI

After reviewing a creator:

```text
Creator Profile

[ Select Creator ]
```

The action should clearly communicate what happens.

Possible confirmation:

```text
Select Alex Morgan?

This will send a creator engagement request
for "AI Product Launch Video".

[ Cancel ] [ Confirm Selection ]
```

Do not use ambiguous button labels.

---

# 37. Engagement Status

Use simple status badges.

Examples:

```text
Requested
Pending
Accepted
Declined
Completed
```

Avoid creating a complex workflow unless required.

---

# 38. AI Builder UI

The AI Builder should feel like an assistant inside the project-creation workflow.

Example:

```text
AI Brief Builder

Describe your project in your own words.

┌──────────────────────────────────────────┐
│ I need a cinematic AI video campaign     │
│ for a new sports shoe.                   │
│                                          │
└──────────────────────────────────────────┘

[ Generate Brief ]
```

Then:

```text
Generated Brief

Title
[ AI Sports Shoe Campaign ]

Description
[ ... ]

Content Type
[ AI Video ]

Style
[ Cinematic ]

Aspect Ratio
[ 16:9 ]

Commercial Use
[ Yes ]

Required Skills
[ ... ]

Required Tools
[ ... ]

[ Regenerate ] [ Edit ] [ Use This Brief ]
```

---

# 39. AI Builder Rules

The AI Builder should:

- Never automatically publish
- Never overwrite user data without confirmation
- Show generated content clearly
- Allow editing
- Handle generation failures
- Work only when Groq is configured

Failure state:

```text
AI generation is currently unavailable.

You can continue by creating the brief manually.

[ Create Manually ]
```

---

# 40. Dashboard UI Principles

Dashboards should answer:

> What should I do next?

Do not fill dashboards with meaningless statistics.

Useful dashboard elements:

- Profile completion
- Portfolio count
- Active projects
- Recent opportunities
- Quick actions
- Recent activity

---

# 41. Cards

Use cards consistently for:

- Creators
- Portfolio items
- Projects
- Dashboard summaries

Cards should have:

- Clear heading
- Useful supporting information
- Consistent spacing
- Clear action

Avoid deeply nested cards.

---

# 42. Badges

Badges should represent meaningful metadata.

Good examples:

```text
AI Video
Runway
Advertising
16:9
Animation
```

Avoid using badges for every piece of information.

Use visual hierarchy to distinguish important metadata.

---

# 43. Buttons

Define consistent button meanings.

## Primary

Main action:

```text
Create Project
Save Profile
Add Portfolio
Search Creators
```

## Secondary

Supporting action:

```text
Cancel
Edit
View Details
```

## Destructive

Actions such as:

```text
Delete
Remove
```

should use clear destructive styling and confirmation where appropriate.

---

# 44. Forms

Every form should have:

- Clear labels
- Input validation
- Helpful placeholder/example where useful
- Required indicator where needed
- Error message
- Success feedback

Avoid relying only on placeholder text as labels.

---

# 45. Form Validation

Validation should happen:

1. Client-side for immediate feedback
2. Server-side for security and correctness

Server-side validation is authoritative.

Example:

```text
Title
[                         ]

Please enter a project title.
```

---

# 46. Empty States

Every major collection should have an intentional empty state.

## No Portfolio

```text
Your portfolio is empty.

Show companies what you can create.

[ Add Your First Work ]
```

## No Projects

```text
You haven't created any projects yet.

[ Create Project ]
```

## No Search Results

```text
No creators match these filters.

Try broadening your search.

[ Clear Filters ]
```

Empty states should help the user take the next action.

---

# 47. Loading States

Use lightweight loading indicators.

Examples:

```text
Loading profile...
```

```text
Searching creators...
```

```text
Uploading portfolio work...
```

Avoid blank screens while waiting for API responses.

---

# 48. Error States

Errors should be understandable.

Bad:

```text
500 Internal Server Error
```

Better:

```text
We couldn't load your portfolio right now.

Please try again.

[ Try Again ]
```

Technical details should be logged server-side rather than displayed to normal users.

---

# 49. Toasts / Alerts

Use Bootstrap alerts or toasts for lightweight feedback.

Examples:

```text
✓ Profile saved successfully.
```

```text
✓ Portfolio work added.
```

```text
✓ Project published.
```

```text
Unable to save changes. Please try again.
```

Success messages should disappear when appropriate.

Important errors should remain visible until understood or dismissed.

---

# 50. Responsive Design

The application must work on:

- Desktop
- Tablet
- Mobile

## Desktop

Use multi-column layouts where useful.

## Tablet

Reduce columns.

## Mobile

Stack content vertically.

Example:

Desktop:

```text
Filters | Results
```

Mobile:

```text
[ Filters ]

Results
```

---

# 51. Mobile Search

On mobile:

```text
Discover Creators

[ Search creators... ]

[ Filters ]

24 creators found

Creator Card
Creator Card
Creator Card
```

Filters can open in a Bootstrap offcanvas or collapse component.

---

# 52. Accessibility

The UI should include:

- Semantic HTML
- Labels for form fields
- Keyboard-accessible controls
- Visible focus states
- Meaningful button text
- Alt text for meaningful images
- Sufficient text contrast
- Proper heading hierarchy

Accessibility should not require a separate complex system.

---

# 53. Media Preview Rules

Portfolio previews should depend on the media type.

For images:

```text
<img>
```

For video:

```text
<video controls>
```

For unsupported preview types:

```text
File available

[ View / Download ]
```

Never assume every uploaded file can safely be embedded directly.

---

# 54. Aspect Ratio Presentation

Aspect ratio is an important portfolio and search attribute.

Display it clearly:

```text
16:9
9:16
1:1
4:5
```

On cards, use compact badges.

On detail pages, display it as metadata.

---

# 55. Creator Skills Presentation

Skills should be easy to scan.

Example:

```text
Skills

[ AI Video ]
[ Prompt Engineering ]
[ Storytelling ]
[ Motion Design ]
[ Generative Advertising ]
```

Avoid displaying skills as one long paragraph.

---

# 56. Tools / Models Presentation

Tools should be clearly separated from skills.

Example:

```text
Tools & Models

[ Runway ]
[ Midjourney ]
[ Kling ]
[ Stable Diffusion ]
```

This distinction matters because companies may search specifically for creators experienced with a particular AI tool/model.

---

# 57. Specialization Presentation

Specialization should be prominent.

Example:

```text
SPECIALIZATION

AI Advertising & Product Video
```

Use a heading or highlighted metadata block.

---

# 58. Workflow Presentation

Workflow is supporting information.

Example:

```text
Workflow

Concept → Prompt Development → Generation
→ Editing → Color → Final Delivery
```

Do not make workflow visually more prominent than portfolio work.

---

# 59. Creator Profile Trust

The profile should feel credible through information density rather than exaggerated UI.

Useful trust signals:

- Number of portfolio works
- Tools/models listed
- Detailed workflow
- Skills
- Specialization
- Optional verification badge

Do not invent ratings, reviews, or verification unless the backend actually supports them.

---

# 60. Search Result Ranking UI

If relevance ranking is implemented, results should still look predictable.

Do not expose complicated AI scores such as:

```text
97.83% semantic match
```

unless there is a real product reason.

Prefer:

```text
Best Match
```

or simply order results appropriately.

---

# 61. Optional Semantic Search UI

If semantic search is added, keep the interface simple.

Example:

```text
Search creators

"Creators who make cinematic product videos
using generative AI"

[ Search ]
```

Structured filters should remain available.

The user should not need to understand embeddings, vectors, RAG, or LangChain.

---

# 62. Navigation Flow

## Public

```text
Home
 ├── Creators
 ├── Projects
 ├── Login
 └── Register
```

## Creator

```text
Dashboard
 ├── My Profile
 ├── My Portfolio
 ├── Discover Projects
 └── Engagements
```

## Company

```text
Dashboard
 ├── Company Profile
 ├── My Projects
 ├── Discover Creators
 └── Engagements
```

---

# 63. Breadcrumbs

Use breadcrumbs on deeper pages where useful.

Example:

```text
Creators / Alex Morgan / Portfolio / Product Campaign
```

Do not use breadcrumbs on simple pages where they add no value.

---

# 64. Modal Usage

Use modals sparingly.

Good uses:

- Confirm deletion
- Confirm creator selection
- Quick confirmation

Avoid using modals for:

- Long forms
- Full profile pages
- Portfolio editing
- Complex project creation

Prefer dedicated pages for substantial workflows.

---

# 65. Confirmation Dialogs

Destructive actions should ask for confirmation.

Example:

```text
Delete Portfolio Work?

This action cannot be undone.

[ Cancel ] [ Delete ]
```

Selection actions can also use confirmation when they create a meaningful engagement state.

---

# 66. Notifications

Keep notifications simple.

Possible notifications:

- Profile updated
- Portfolio uploaded
- Project published
- Creator selected
- Engagement request received

Avoid building a full notification platform unless required.

---

# 67. UI Data States

Every major page should account for:

```text
Loading
Success
Empty
Error
Unauthorized
Not Found
```

Do not design only the happy path.

---

# 68. 404 Page

Simple:

```text
Page Not Found

The page you're looking for doesn't exist.

[ Go Home ]
```

---

# 69. 403 Page

Simple:

```text
Access Denied

You don't have permission to access this page.

[ Go Back ]
```

---

# 70. 500 Page

Simple:

```text
Something went wrong.

We're having trouble completing this request.

[ Try Again ]
```

Do not expose stack traces.

---

# 71. Design Consistency

The following should remain consistent throughout the application:

- Button styles
- Card styles
- Form styles
- Border radius
- Spacing
- Typography
- Alert styles
- Badge styles
- Heading hierarchy
- Navigation

Avoid page-specific visual systems.

---

# 72. CSS Organization

Keep custom CSS organized.

Recommended:

```text
static/
└── css/
    ├── base.css
    ├── components.css
    ├── forms.css
    ├── portfolio.css
    └── responsive.css
```

Do not put large amounts of CSS directly inside HTML templates.

---

# 73. JavaScript Organization

Recommended:

```text
static/
└── js/
    ├── main.js
    ├── search.js
    ├── portfolio.js
    ├── project.js
    └── ai-builder.js
```

Only create separate files when the feature complexity justifies it.

Avoid one giant JavaScript file.

---

# 74. Frontend API Interaction

JavaScript API requests should:

- Handle loading
- Handle success
- Handle errors
- Handle authentication failures
- Avoid exposing secrets
- Avoid duplicating backend business logic

The frontend should not decide whether the current user is authorized to perform an operation.

The backend remains authoritative.

---

# 75. Security UI Rules

Never:

- Display API keys
- Display passwords
- Trust client-side role checks
- Allow frontend-only authorization
- Render unsafe uploaded content
- Inject unsanitized user HTML

User-generated text should be rendered safely.

---

# 76. Performance UI Rules

Prefer:

- Lazy loading where useful
- Optimized previews
- Pagination
- Limited result counts
- Efficient API calls

Avoid:

- Loading every portfolio item on initial page load
- Repeated unnecessary API requests
- Large unnecessary frontend dependencies

---

# 77. Portfolio Discovery Priority

Portfolio should influence creator discovery.

For example, a company searching for:

```text
AI product video
Runway
16:9
Advertising
```

should be able to find creators whose portfolio metadata matches those attributes.

The UI should make these matching attributes visible.

---

# 78. Company-to-Creator Experience

The ideal company experience:

```text
I have a project.
        ↓
I define the requirements.
        ↓
I search for creators.
        ↓
I filter by relevant AI attributes.
        ↓
I see why each creator is relevant.
        ↓
I inspect their actual work.
        ↓
I select the best creator.
```

The UI should support this without unnecessary navigation.

---

# 79. Creator-to-Company Experience

The ideal creator experience:

```text
I create my identity.
        ↓
I show what I can do.
        ↓
I document my AI tools and workflow.
        ↓
I showcase actual work.
        ↓
Companies can find me.
        ↓
I discover relevant opportunities.
```

---

# 80. AI Builder UX Principle

AI generation should reduce work rather than introduce uncertainty.

The user should always understand:

1. What they entered
2. What the AI generated
3. What can be edited
4. What will be saved
5. When the project becomes published

Never hide these transitions.

---

# 81. Demo UI Priority

For the hackathon demo, prioritize visual polish on these pages:

### Priority 1

Creator Profile

### Priority 2

Portfolio

### Priority 3

Creator Search

### Priority 4

Project / Brief

### Priority 5

Company Dashboard

### Priority 6

AI Builder

The main demo path should look polished even if less-important pages are simpler.

---

# 82. Demo-Friendly Data

The UI should support realistic demo content.

Example creator:

```text
Alex Morgan

AI Video & Generative Advertising

Skills:
AI Video
Storytelling
Motion Design

Tools:
Runway
Kling
Midjourney

Portfolio:
12 works
```

Example project:

```text
AI Sports Shoe Campaign

Content Type:
AI Video

Style:
Cinematic

Aspect Ratio:
16:9

Commercial Use:
Required

Skills:
AI Video
Advertising
Storytelling
```

Demo data should clearly demonstrate why creator discovery is useful.

---

# 83. UI Definition of Done

A UI feature is complete when:

- [ ] Layout is implemented
- [ ] Responsive behavior works
- [ ] Loading state exists where needed
- [ ] Empty state exists where needed
- [ ] Error state exists where needed
- [ ] Form validation works
- [ ] Backend integration works
- [ ] Authorization behavior is respected
- [ ] Visual hierarchy is clear
- [ ] Buttons/actions are understandable
- [ ] No obvious console errors
- [ ] Feature works on a mobile-sized viewport
- [ ] Feature does not break existing pages

---

# 84. UI Anti-Patterns

Avoid:

- Giant forms without sections
- Huge dashboard statistic grids
- Too many colors
- Too many badges
- Unnecessary animations
- Modal-heavy workflows
- Tiny text
- Poor mobile layouts
- Frontend-only authorization
- AI-only workflows
- Generic stock UI that hides the marketplace's AI-specific value

---

# 85. UI Priority Order

When development time is limited:

```text
1. Usability
2. Correct functionality
3. Creator portfolio presentation
4. Search/filter experience
5. Structured project forms
6. Responsive layout
7. Error/empty/loading states
8. Visual polish
9. Advanced animation
```

Never sacrifice functionality for visual polish.

---

# 86. Final UI Structure

The finished application should roughly provide:

```text
PUBLIC
│
├── Home
├── Creator Discovery
├── Project Discovery
├── Login
└── Register

CREATOR
│
├── Dashboard
├── Profile
├── Portfolio
│   ├── Portfolio List
│   ├── Add Work
│   └── Work Detail
├── Discover Projects
└── Engagements

COMPANY
│
├── Dashboard
├── Company Profile
├── Projects
│   ├── Project List
│   ├── Create Project
│   └── Project Detail
├── Discover Creators
│   ├── Search
│   ├── Filters
│   └── Creator Profile
└── Engagements

OPTIONAL AI
│
└── AI Brief Builder
```

---

# 87. Final UX Principle

The UI should always answer three questions clearly:

### For a creator:

> What do I create?

> How do I create it?

> Why should a company choose me?

### For a company:

> What do I need?

> Which creators can do it?

> Why is this creator a good match?

### For the marketplace:

> How do we connect the right project with the right AI creator?

The interface should make these answers visible through:

```text
Creator Profile
        +
Portfolio
        +
Portfolio Metadata
        +
Structured Brief
        +
Search
        +
Filters
        +
Creator Evaluation
        +
Selection
```

That is the core UI experience of the AI Content Creator Marketplace.