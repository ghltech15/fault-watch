---
name: frontend:styles
description: Create or update CSS/Tailwind styles and design tokens
argument-hint: "[add|update|audit] [--target=file-or-selector]"
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
---

<objective>
Manage CSS styles, Tailwind configuration, and design tokens.

**Purpose:** Maintain consistent, scalable styling across the application.

**Output:** Updated style files with proper organization.
</objective>

<process>

## Commands

### `frontend:styles audit`
Scan all styles and report:
- Duplicate styles
- Unused CSS classes
- Hardcoded values that should be tokens
- Inconsistent patterns
- Tailwind class usage

### `frontend:styles add <name>`
Add new style definitions:
- CSS custom properties
- Tailwind utilities
- Animation keyframes
- Component classes

### `frontend:styles update <target>`
Modify existing styles:
- Update color values
- Change spacing
- Modify animations
- Fix inconsistencies

## Style Organization

### CSS Variables (globals.css)
```css
:root {
  /* Colors */
  --color-primary: #dc2626;
  --color-background: #0a0a0a;

  /* Typography */
  --font-sans: 'Inter', sans-serif;
  --font-mono: 'JetBrains Mono', monospace;

  /* Spacing */
  --space-1: 0.25rem;
  --space-2: 0.5rem;

  /* Animations */
  --duration-fast: 150ms;
  --duration-normal: 300ms;
  --ease-out: cubic-bezier(0.33, 1, 0.68, 1);
}
```

### Tailwind Config
```js
module.exports = {
  theme: {
    extend: {
      colors: {
        primary: 'var(--color-primary)',
        background: 'var(--color-background)',
      },
      animation: {
        'pulse-slow': 'pulse 3s ease-in-out infinite',
      }
    }
  }
}
```

### Component Classes
```css
/* Base component styles */
.card { @apply bg-surface border border-border rounded-xl p-5; }
.btn { @apply px-4 py-2 rounded-lg font-medium transition; }
.btn-primary { @apply bg-primary text-white hover:bg-primary/90; }
```

### Animations
```css
@keyframes fade-in {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.animate-fade-in {
  animation: fade-in 0.3s var(--ease-out);
}
```

## Best Practices

1. **Use CSS variables** for values used more than twice
2. **Use Tailwind utilities** for one-off styles
3. **Create component classes** for repeated patterns
4. **Name animations** descriptively (fade-in, slide-up, pulse-glow)
5. **Group related styles** with comments
6. **Order properties** consistently (layout, box model, typography, visual)

</process>

<success_criteria>
- [ ] Styles are organized and documented
- [ ] No duplicate definitions
- [ ] Design tokens used consistently
- [ ] Tailwind config is clean
- [ ] Animations are performant
</success_criteria>
