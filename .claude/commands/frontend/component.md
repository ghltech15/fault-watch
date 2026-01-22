---
name: frontend:component
description: Create or modify a React component with best practices
argument-hint: "<component-name> [--path=path] [--type=card|form|modal|list|chart]"
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash
---

<objective>
Create or modify a React component following project conventions and best practices.

**Purpose:** Quickly scaffold production-ready components that match the existing codebase style.

**Output:** A complete React component with types, styles, and exports.
</objective>

<process>

## Step 1: Analyze Existing Patterns

Before creating/modifying, scan the codebase for:
- Existing component structure (functional vs class)
- Import patterns (named vs default exports)
- Styling approach (Tailwind, CSS modules, styled-components)
- TypeScript patterns (interfaces vs types)
- State management (useState, useReducer, Zustand, Redux)

Read 2-3 existing components to match the style.

## Step 2: Determine Component Type

Based on argument or context:

| Type | Structure |
|------|-----------|
| card | Container with header, content, optional footer |
| form | Input fields, validation, submit handling |
| modal | Overlay, backdrop, close button, content |
| list | Array rendering, empty state, loading state |
| chart | Data visualization with library integration |

## Step 3: Create Component Structure

For each component, include:

```tsx
'use client' // if needed for Next.js

import { useState } from 'react'
import { motion } from 'framer-motion' // if animations needed

interface ComponentNameProps {
  // Required props
  data: DataType
  // Optional props with defaults
  variant?: 'default' | 'compact'
  className?: string
  // Event handlers
  onAction?: () => void
}

export function ComponentName({
  data,
  variant = 'default',
  className,
  onAction
}: ComponentNameProps) {
  // State
  const [isLoading, setIsLoading] = useState(false)

  // Early returns for edge cases
  if (!data) return null

  return (
    <div className={cn('base-styles', className)}>
      {/* Component content */}
    </div>
  )
}
```

## Step 4: Add Essential Features

Include as appropriate:
- Loading state with skeleton/spinner
- Error state with retry option
- Empty state with helpful message
- Responsive design (mobile-first)
- Animations (entry, hover, state changes)
- Accessibility (aria-labels, keyboard nav)

## Step 5: Create Index Export

Update or create index.ts:
```ts
export { ComponentName } from './ComponentName'
```

## Step 6: Verify Build

Run build/type check to ensure no errors.

</process>

<success_criteria>
- [ ] Component matches existing codebase patterns
- [ ] TypeScript interfaces defined
- [ ] Loading/error/empty states handled
- [ ] Responsive design included
- [ ] Accessibility attributes added
- [ ] Exported from index file
- [ ] Build passes without errors
</success_criteria>
