---
name: frontend:audit
description: Audit existing UI - identify issues, inconsistencies, and improvement opportunities
argument-hint: "[component-path]"
allowed-tools:
  - Read
  - Glob
  - Grep
  - Task
  - AskUserQuestion
---

<objective>
Perform a comprehensive audit of the frontend UI to identify issues, inconsistencies, and areas for improvement.

**Purpose:** Understand the current state of the UI before making changes.

**Output:** A detailed audit report with actionable recommendations.
</objective>

<process>

## Step 1: Scan Component Structure

Search for all React/Vue/Svelte components:
- `**/*.tsx`, `**/*.jsx` for React
- `**/*.vue` for Vue
- `**/*.svelte` for Svelte

Identify:
- Component count and organization
- Naming conventions used
- File structure patterns

## Step 2: Analyze Design System

Check for consistency in:
- **Colors**: Extract all color values, check for hardcoded vs tokens
- **Typography**: Font sizes, weights, line heights
- **Spacing**: Margins, paddings, gaps
- **Components**: Button styles, card styles, form inputs

Look for:
- `globals.css`, `tailwind.config.js`, theme files
- CSS variables, design tokens
- Inconsistent styling patterns

## Step 3: Check Component Patterns

For each major component, evaluate:
- Props interface clarity
- State management approach
- Error handling
- Loading states
- Accessibility attributes (aria-*, role)
- Responsive behavior

## Step 4: Identify Issues

Categorize findings:

### Critical
- Broken functionality
- Accessibility violations
- Security concerns

### Major
- Inconsistent design patterns
- Poor user experience
- Missing error states
- No loading indicators

### Minor
- Code style inconsistencies
- Missing TypeScript types
- Optimization opportunities

## Step 5: Generate Report

Create audit report with:
- Executive summary
- Component inventory
- Issue list by severity
- Recommended actions
- Priority order for fixes

</process>

<success_criteria>
- [ ] All components scanned
- [ ] Design system analyzed
- [ ] Issues categorized by severity
- [ ] Actionable recommendations provided
- [ ] Priority order established
</success_criteria>
