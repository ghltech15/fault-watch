---
name: frontend:responsive
description: Make components/pages responsive across all device sizes
argument-hint: "<target-file>"
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
---

<objective>
Ensure UI components work beautifully across all screen sizes.

**Purpose:** Deliver great UX on mobile, tablet, and desktop.

**Output:** Updated components with responsive styles.
</objective>

<process>

## Step 1: Identify Target

Read the target file and analyze:
- Current responsive behavior
- Breakpoint usage
- Layout patterns
- Problem areas

## Step 2: Define Breakpoints

Standard breakpoints (Tailwind default):
- `sm`: 640px (large phones)
- `md`: 768px (tablets)
- `lg`: 1024px (laptops)
- `xl`: 1280px (desktops)
- `2xl`: 1536px (large screens)

## Step 3: Mobile-First Approach

Start with mobile styles, then add breakpoints:

```tsx
// Mobile-first pattern
<div className="
  flex flex-col gap-4        // Mobile: stack vertically
  md:flex-row md:gap-6       // Tablet+: side by side
  lg:gap-8                   // Desktop: more spacing
">
```

## Step 4: Common Patterns

### Grid Layouts
```tsx
<div className="
  grid grid-cols-1           // Mobile: 1 column
  sm:grid-cols-2             // Small: 2 columns
  lg:grid-cols-3             // Large: 3 columns
  xl:grid-cols-4             // XL: 4 columns
  gap-4
">
```

### Typography Scaling
```tsx
<h1 className="
  text-2xl                   // Mobile
  md:text-4xl                // Tablet
  lg:text-5xl                // Desktop
  font-bold
">
```

### Spacing
```tsx
<section className="
  px-4 py-8                  // Mobile: tight padding
  md:px-8 md:py-12           // Tablet: more room
  lg:px-16 lg:py-20          // Desktop: generous
">
```

### Show/Hide Elements
```tsx
// Hide on mobile, show on desktop
<div className="hidden lg:block">Desktop only</div>

// Show on mobile, hide on desktop
<div className="lg:hidden">Mobile only</div>
```

### Navigation
```tsx
// Mobile: hamburger menu
// Desktop: horizontal nav
<nav>
  <button className="lg:hidden">☰</button>
  <ul className="hidden lg:flex gap-6">
    {/* nav items */}
  </ul>
</nav>
```

## Step 5: Test Viewports

Verify at these widths:
- 375px (iPhone SE)
- 390px (iPhone 14)
- 768px (iPad)
- 1024px (iPad Pro)
- 1280px (Laptop)
- 1920px (Desktop)

## Step 6: Handle Edge Cases

- Long text: Use `truncate` or `line-clamp`
- Images: Use `object-cover` and aspect ratios
- Tables: Horizontal scroll on mobile
- Forms: Full-width inputs on mobile
- Modals: Full-screen on mobile, centered on desktop

</process>

<success_criteria>
- [ ] Works on mobile (375px)
- [ ] Works on tablet (768px)
- [ ] Works on desktop (1280px+)
- [ ] No horizontal scroll (unless intended)
- [ ] Touch targets are 44px+ on mobile
- [ ] Text is readable at all sizes
</success_criteria>
