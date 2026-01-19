---
name: frontend:design
description: Generate v0.dev prompts from API files automatically
argument-hint: "[api-file]"
allowed-tools:
  - Read
  - Glob
  - Grep
  - Write
  - AskUserQuestion
---

<objective>
Analyze an API file (FastAPI, Flask, Express) and generate a production-ready v0.dev prompt for creating a modern dashboard UI.

**Purpose:** Automate the translation of backend API structure into frontend specifications that v0.dev can render immediately.

**Output:** A single `.frontend/v0-prompt.md` file ready to paste into v0.dev.
</objective>

<execution_context>
@.claude/frontend-design/templates/v0-prompt.md
</execution_context>

<process>

## Step 1: Locate and Read API File

If argument provided:
- Read the specified file directly

If no argument:
- Search for common API files: `api.py`, `main.py`, `app.py`, `server.js`, `index.ts`
- Read the first match found

## Step 2: Extract API Structure

Parse the API file to identify:

### Endpoints
Look for route decorators/definitions:
- FastAPI: `@app.get()`, `@app.post()`, `@router.get()`
- Flask: `@app.route()`, `@blueprint.route()`
- Express: `app.get()`, `router.post()`

For each endpoint, extract:
- HTTP method (GET, POST, PUT, DELETE)
- Path (`/api/dashboard`, `/api/banks/{ticker}`)
- Response model if defined
- Description from docstring

### Data Models
Look for Pydantic models, TypedDict, interfaces:
- Class definitions with type hints
- Response model schemas
- Nested object structures

### Key Metrics
Identify the "hero" data points:
- Numerical values that should be displayed prominently
- Status indicators (enums, boolean flags)
- Time-sensitive data (countdowns, timestamps)
- Lists/arrays that become tables or cards

## Step 3: Determine UI Components

Map API structure to UI components:

| API Pattern | UI Component |
|-------------|--------------|
| Single number endpoint | Hero metric card |
| Object with multiple fields | Detail card |
| Array of objects | Card grid or table |
| Nested objects | Expandable sections |
| Boolean/enum status | Status badge |
| Timestamp/countdown | Timer component |
| Percentage/ratio | Progress bar or gauge |

## Step 4: Generate v0.dev Prompt

Create a comprehensive prompt following the template structure:

### Design System Section
- Define color palette based on data types (success/warning/danger states)
- Typography hierarchy (hero numbers, headings, body, captions)
- Spacing and layout grid

### Layout Section
- Header with branding and key metrics
- Main content area with card grid
- Responsive breakpoints

### Components Section
For each identified component:
- Component name and purpose
- Props based on API response fields
- Visual states (loading, error, empty)
- Interactions (click, hover, expand)

### Data Integration Section
- List all API endpoints
- Map endpoints to components
- Specify refresh intervals
- Define loading states

### Animation Section
- Entry animations for cards
- Number counting animations
- Status change transitions
- Loading skeletons

## Step 5: Write Output File

Create `.frontend/v0-prompt.md` with:
- Complete v0.dev prompt text
- Ready to copy-paste
- No additional formatting needed

</process>

<success_criteria>
- [ ] API file successfully parsed
- [ ] All endpoints identified and documented
- [ ] Data models mapped to UI components
- [ ] v0.dev prompt includes design system
- [ ] v0.dev prompt includes layout specification
- [ ] v0.dev prompt includes component definitions
- [ ] v0.dev prompt includes data integration
- [ ] Output file created at `.frontend/v0-prompt.md`
- [ ] Prompt is ready to paste into v0.dev without editing
</success_criteria>

<output>
After completion, the user will have:

1. **`.frontend/v0-prompt.md`** - Complete v0.dev prompt

The user can then:
1. Copy the contents of `.frontend/v0-prompt.md`
2. Paste into v0.dev
3. Get a working Next.js dashboard
4. Connect to their API backend
</output>
