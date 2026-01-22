---
name: frontend:redesign
description: Redesign a page or component with modern UI patterns
argument-hint: "<target> [--style=minimal|dramatic|dashboard|landing]"
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash
  - Task
  - WebSearch
  - AskUserQuestion
---

<objective>
Redesign a page or component with modern UI patterns, improved UX, and visual appeal.

**Purpose:** Transform existing UI into a polished, engaging experience.

**Output:** Updated component files with new design implementation.
</objective>

<context>
@./frontend/app/globals.css
@./frontend/tailwind.config.js
</context>

<process>

## Step 1: Understand Current State

Read the target file(s) and identify:
- Current layout structure
- Components being used
- Data being displayed
- User interactions
- Pain points or issues

## Step 2: Gather Requirements

Ask user about:
1. **Target audience**: Who uses this?
2. **Key actions**: What should users do?
3. **Visual style**: Minimal, dramatic, playful, professional?
4. **Inspiration**: Any reference sites or designs?

## Step 3: Research Modern Patterns

If needed, search for:
- Current design trends (2024-2026)
- Similar app designs
- UI pattern libraries
- Animation inspiration

## Step 4: Plan the Redesign

Create a mental model of:

### Layout
- Information hierarchy (what's most important?)
- Visual flow (where does the eye go?)
- White space usage
- Responsive breakpoints

### Visual Design
- Color scheme (existing or new?)
- Typography scale
- Shadow and depth
- Border and radius

### Interactions
- Hover states
- Click feedback
- Loading states
- Transitions/animations

### Components Needed
- New components to create
- Existing components to modify
- Components to remove

## Step 5: Implement Changes

Execute in order:
1. Update global styles if needed (colors, fonts)
2. Create new components
3. Modify existing components
4. Update page layout
5. Add animations/transitions
6. Test responsive behavior

### Style Presets

**Minimal**
- Lots of white space
- Subtle shadows
- Muted colors
- Simple animations

**Dramatic**
- Bold colors
- Strong contrasts
- Dynamic animations
- Large typography

**Dashboard**
- Dense information
- Card-based layout
- Status indicators
- Real-time updates

**Landing**
- Hero section
- Feature highlights
- Social proof
- Clear CTAs

## Step 6: Verify Quality

Check:
- [ ] Looks good on mobile (375px)
- [ ] Looks good on tablet (768px)
- [ ] Looks good on desktop (1280px+)
- [ ] Animations are smooth (60fps)
- [ ] Colors have sufficient contrast
- [ ] Interactive elements are obvious
- [ ] Build passes without errors

</process>

<success_criteria>
- [ ] Visual design significantly improved
- [ ] UX patterns are modern and intuitive
- [ ] Responsive across all breakpoints
- [ ] Animations enhance (not distract)
- [ ] Accessibility maintained or improved
- [ ] Code is clean and maintainable
- [ ] User approves the changes
</success_criteria>
