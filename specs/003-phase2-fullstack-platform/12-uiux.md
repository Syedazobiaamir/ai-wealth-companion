# UI/UX Specification: Phase II Design System

**Feature Branch**: `003-phase2-fullstack-platform`
**Created**: 2026-01-25
**Status**: Active
**Framework**: Next.js 14 + Tailwind CSS + Framer Motion
**Input**: Screen list, Layout system, Design tokens, UX rules, Accessibility, Motion rules, Empty state behavior, Demo mode design

## Overview

This specification defines the complete UI/UX design system for the AI Wealth & Spending Companion Phase II platform. The design emphasizes premium aesthetics with glassmorphism, smooth animations, and excellent accessibility.

### Design Philosophy

1. **Glassmorphism-First**: Frosted glass effects create depth and visual hierarchy
2. **Motion-Driven**: Subtle animations guide attention and create delight
3. **Data-Centric**: Financial data is the hero; UI supports comprehension
4. **Accessible**: WCAG 2.1 AA compliance for inclusive design
5. **Responsive**: Seamless experience across all device sizes

## Screen List

### Primary Screens

| Screen | Route | Purpose | Priority |
|--------|-------|---------|----------|
| Landing Page | `/` | Marketing & onboarding | P1 |
| Dashboard | `/dashboard` | Financial overview | P1 |
| Transactions | `/transactions` | Transaction management | P1 |
| Budget Planner | `/budgets` | Budget management | P2 |
| Analytics | `/analytics` | Charts & insights | P2 |
| Settings | `/settings` | User preferences | P3 |

### Secondary Screens

| Screen | Route | Purpose | Priority |
|--------|-------|---------|----------|
| Login | `/login` | Authentication | P1 |
| Register | `/register` | Account creation | P1 |
| Transaction Detail | `/transactions/{id}` | Single transaction view | P2 |
| Category Manager | `/categories` | Custom categories | P3 |
| Goals | `/goals` | Financial goals | P3 |
| Export | `/export` | Data export | P3 |

### Modal/Overlay Screens

| Modal | Trigger | Purpose |
|-------|---------|---------|
| Add Transaction | FAB or header button | Create transaction |
| Edit Transaction | Row action | Modify transaction |
| Set Budget | Budget card action | Create/edit budget |
| Chatbot Panel | Floating button | AI assistant (shell) |
| Filter Panel | Filter icon | Advanced filters |
| Confirm Delete | Delete action | Deletion confirmation |

## Layout System

### Grid Structure

```
┌─────────────────────────────────────────────────────────┐
│                     Header (64px)                        │
├──────────┬──────────────────────────────────────────────┤
│          │                                              │
│  Sidebar │              Main Content                    │
│  (240px) │              (flex-grow)                     │
│          │                                              │
│          │                                              │
├──────────┴──────────────────────────────────────────────┤
│                    Footer (optional)                     │
└─────────────────────────────────────────────────────────┘
```

### Responsive Breakpoints

| Breakpoint | Width | Layout Behavior |
|------------|-------|-----------------|
| Mobile | < 640px | Single column, bottom nav, full-width cards |
| Tablet | 640px - 1023px | Collapsible sidebar, 2-column grid |
| Desktop | 1024px - 1279px | Fixed sidebar, 3-column grid |
| Large | ≥ 1280px | Wide sidebar, 4-column grid, max-width container |

### Spacing Scale (Tailwind)

| Token | Value | Usage |
|-------|-------|-------|
| space-1 | 4px | Tight inline spacing |
| space-2 | 8px | Component internal spacing |
| space-3 | 12px | Related element spacing |
| space-4 | 16px | Section internal padding |
| space-6 | 24px | Card padding |
| space-8 | 32px | Section gaps |
| space-12 | 48px | Major section spacing |

### Container Widths

| Container | Max Width | Padding |
|-----------|-----------|---------|
| Full | 100% | 16px mobile, 24px tablet+ |
| Standard | 1280px | 24px |
| Narrow | 768px | 24px |
| Article | 640px | 24px |

## Design Tokens

### Color Palette

#### Light Mode

| Token | Hex | Tailwind | Usage |
|-------|-----|----------|-------|
| background | #F9FAFB | gray-50 | Page background |
| surface | #FFFFFF | white | Cards, panels |
| surface-elevated | #FFFFFF | white | Modals, dropdowns |
| primary | #7C3AED | purple-600 | Primary actions |
| primary-hover | #6D28D9 | purple-700 | Primary hover |
| secondary | #3B82F6 | blue-500 | Secondary actions |
| accent | linear-gradient | purple-600 to blue-500 | Highlights |
| text-primary | #111827 | gray-900 | Headings, body |
| text-secondary | #6B7280 | gray-500 | Captions, hints |
| text-muted | #9CA3AF | gray-400 | Disabled, placeholders |
| border | #E5E7EB | gray-200 | Dividers, borders |
| success | #10B981 | emerald-500 | Income, positive |
| warning | #F59E0B | amber-500 | Alerts, recurring |
| error | #EF4444 | red-500 | Expenses, errors |

#### Dark Mode

| Token | Hex | Tailwind | Usage |
|-------|-----|----------|-------|
| background | #0F172A | slate-900 | Page background |
| surface | #1E293B | slate-800 | Cards, panels |
| surface-elevated | #334155 | slate-700 | Modals, dropdowns |
| primary | #A78BFA | purple-400 | Primary actions |
| primary-hover | #C4B5FD | purple-300 | Primary hover |
| secondary | #60A5FA | blue-400 | Secondary actions |
| text-primary | #F1F5F9 | slate-100 | Headings, body |
| text-secondary | #94A3B8 | slate-400 | Captions, hints |
| text-muted | #64748B | slate-500 | Disabled |
| border | #334155 | slate-700 | Dividers, borders |

### Glassmorphism Tokens

| Token | Light Mode | Dark Mode |
|-------|------------|-----------|
| glass-bg | rgba(255, 255, 255, 0.7) | rgba(30, 41, 59, 0.7) |
| glass-blur | backdrop-blur-lg (16px) | backdrop-blur-lg (16px) |
| glass-border | rgba(255, 255, 255, 0.3) | rgba(255, 255, 255, 0.1) |
| glass-shadow | 0 8px 32px rgba(124, 58, 237, 0.1) | 0 8px 32px rgba(0, 0, 0, 0.3) |

### Typography

| Token | Font | Size | Weight | Line Height |
|-------|------|------|--------|-------------|
| heading-1 | Inter | 36px / 2.25rem | 700 | 1.2 |
| heading-2 | Inter | 30px / 1.875rem | 700 | 1.25 |
| heading-3 | Inter | 24px / 1.5rem | 600 | 1.3 |
| heading-4 | Inter | 20px / 1.25rem | 600 | 1.4 |
| body-lg | Manrope | 18px / 1.125rem | 400 | 1.6 |
| body | Manrope | 16px / 1rem | 400 | 1.5 |
| body-sm | Manrope | 14px / 0.875rem | 400 | 1.5 |
| caption | Manrope | 12px / 0.75rem | 400 | 1.4 |
| mono | JetBrains Mono | 14px | 400 | 1.5 |

### Border Radius

| Token | Value | Usage |
|-------|-------|-------|
| rounded-sm | 4px | Chips, tags |
| rounded | 8px | Buttons, inputs |
| rounded-lg | 12px | Cards (mobile) |
| rounded-xl | 16px | Cards (tablet) |
| rounded-2xl | 24px | Cards (desktop), modals |
| rounded-full | 9999px | Avatars, circular buttons |

### Shadows

| Token | Value | Usage |
|-------|-------|-------|
| shadow-sm | 0 1px 2px rgba(0,0,0,0.05) | Subtle elevation |
| shadow | 0 4px 6px rgba(0,0,0,0.1) | Default cards |
| shadow-lg | 0 10px 15px rgba(0,0,0,0.1) | Elevated cards |
| shadow-xl | 0 20px 25px rgba(0,0,0,0.15) | Modals, dropdowns |
| shadow-glow | 0 0 40px rgba(124,58,237,0.15) | Hero elements |

## UX Rules

### Navigation Rules

1. **Persistent Navigation**: Sidebar always visible on desktop, collapsible on tablet
2. **Breadcrumbs**: Show on all detail pages (3+ levels deep)
3. **Back Button**: Always present on detail/modal screens
4. **Active State**: Current route highlighted in nav with gradient accent
5. **Mobile Bottom Nav**: Fixed bottom navigation with 4-5 primary items

### Form Rules

1. **Label Position**: Above input, left-aligned
2. **Required Fields**: Indicated with asterisk and explained in form header
3. **Validation**: Real-time inline validation on blur, summary on submit
4. **Error Display**: Red border, error message below input, icon inside input
5. **Success State**: Green checkmark on valid inputs
6. **Submit Button**: Disabled until form valid, loading state during submission
7. **Cancel Action**: Always available, confirms if changes unsaved

### Data Display Rules

1. **Numbers**: Right-aligned in tables, formatted with locale separators
2. **Currency**: Always show currency symbol (PKR, $), 2 decimal places
3. **Dates**: Relative for recent (Today, Yesterday), absolute for older
4. **Percentages**: Show with % symbol, color-coded (green positive, red negative)
5. **Large Numbers**: Abbreviate (1.2M, 50K) in charts, full in detail views
6. **Loading**: Skeleton screens, not spinners (except for actions)

### Feedback Rules

1. **Success Messages**: Toast notification, 3-second auto-dismiss, green accent
2. **Error Messages**: Toast notification, manual dismiss required, red accent
3. **Confirmations**: Modal dialog for destructive actions
4. **Progress**: Determinate progress bar for known durations, indeterminate for unknown
5. **Empty States**: Illustration + message + primary action

## Accessibility

### WCAG 2.1 AA Requirements

| Criterion | Requirement | Implementation |
|-----------|-------------|----------------|
| 1.1.1 | Non-text content | Alt text on all images, aria-labels on icons |
| 1.4.1 | Use of color | Never color-alone indicators, always text/icon backup |
| 1.4.3 | Contrast (min) | 4.5:1 for normal text, 3:1 for large text |
| 1.4.11 | Non-text contrast | 3:1 for UI components and graphics |
| 2.1.1 | Keyboard | All interactions keyboard accessible |
| 2.4.3 | Focus order | Logical tab order, visible focus indicators |
| 2.4.7 | Focus visible | 2px outline, offset, contrasting color |
| 3.2.1 | On focus | No unexpected context changes |
| 4.1.2 | Name, role, value | ARIA labels on custom components |

### Focus Management

```css
/* Focus ring styling */
:focus-visible {
  outline: 2px solid var(--primary);
  outline-offset: 2px;
  border-radius: inherit;
}
```

### Screen Reader Support

| Component | ARIA Implementation |
|-----------|---------------------|
| Modal | role="dialog", aria-modal="true", aria-labelledby |
| Navigation | role="navigation", aria-label="Main" |
| Sidebar | role="complementary" |
| Alerts | role="alert", aria-live="polite" |
| Loading | aria-busy="true", aria-live="polite" |
| Tables | scope="col/row", caption |
| Charts | role="img", aria-label with data summary |

### Color Blindness Considerations

| Type | Challenge | Solution |
|------|-----------|----------|
| Red-green | Income/expense colors | Add icons (↑/↓), patterns |
| All types | Chart segments | Use patterns, labels, legends |

## Motion Rules

### Animation Principles

1. **Purposeful**: Animation serves UX, not decoration
2. **Swift**: Fast enough to not impede, slow enough to perceive
3. **Natural**: Easing curves that feel physical
4. **Consistent**: Same actions have same animations everywhere

### Timing Tokens

| Token | Duration | Easing | Usage |
|-------|----------|--------|-------|
| instant | 100ms | ease-out | Hover states, toggles |
| fast | 150ms | ease-out | Buttons, chips |
| normal | 200ms | ease-in-out | Cards, panels |
| slow | 300ms | ease-in-out | Modals, page transitions |
| gentle | 500ms | cubic-bezier(0.4, 0, 0.2, 1) | Hero animations |

### Easing Curves

```javascript
const easings = {
  easeOut: 'cubic-bezier(0, 0, 0.2, 1)',      // Decelerate
  easeIn: 'cubic-bezier(0.4, 0, 1, 1)',       // Accelerate
  easeInOut: 'cubic-bezier(0.4, 0, 0.2, 1)',  // Standard
  spring: 'cubic-bezier(0.34, 1.56, 0.64, 1)' // Bouncy
};
```

### Animation Catalog

| Animation | Trigger | Motion |
|-----------|---------|--------|
| Page enter | Route change | Fade in + slide up (300ms) |
| Card enter | Scroll into view | Fade in + scale 0.95→1 (200ms) |
| Modal open | User action | Fade in + scale 0.9→1 (200ms) |
| Modal close | User action | Fade out + scale 1→0.95 (150ms) |
| Button hover | Mouse enter | Scale 1.02 (100ms) |
| Button press | Mouse down | Scale 0.98 (50ms) |
| Toast enter | Event | Slide in from right (200ms) |
| Toast exit | Auto/manual | Fade out + slide right (150ms) |
| List item | Data load | Staggered fade in (50ms delay each) |
| Chart bars | Data load | Grow from zero (300ms, staggered) |
| Progress bar | Value change | Width transition (200ms) |
| Theme switch | Toggle | Cross-fade (300ms) |

### Reduced Motion

```css
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```

## Empty State Behavior

### Empty State Components

| Context | Illustration | Message | Primary Action |
|---------|--------------|---------|----------------|
| No transactions | Wallet illustration | "No transactions yet" | "Add your first transaction" |
| No budgets | Target illustration | "No budgets set" | "Create a budget" |
| No goals | Flag illustration | "No goals defined" | "Set a financial goal" |
| No search results | Search illustration | "No results found" | "Clear filters" |
| No chart data | Chart illustration | "Not enough data" | "Add transactions to see trends" |
| Network error | Cloud-off illustration | "Connection lost" | "Retry" |

### Empty State Structure

```
┌─────────────────────────────────────────┐
│                                         │
│         [Illustration 120x120]          │
│                                         │
│           Primary Message               │
│         (heading-3, center)             │
│                                         │
│      Secondary message explaining       │
│      what user can do (body-sm,         │
│      text-secondary, center)            │
│                                         │
│         [ Primary Action ]              │
│                                         │
└─────────────────────────────────────────┘
```

### Loading States

| Context | Loading Type | Duration Hint |
|---------|--------------|---------------|
| Page load | Skeleton screen | None |
| Data fetch | Skeleton in place | None |
| Form submit | Button spinner | Indeterminate |
| File upload | Progress bar | Determinate |
| AI processing | Animated dots + message | "Thinking..." |

### Skeleton Variants

- **Text skeleton**: Rounded rectangles, 60-80% width variation
- **Card skeleton**: Full card shape with content placeholders
- **Chart skeleton**: Chart outline with pulsing bars/lines
- **Avatar skeleton**: Circular placeholder

## Demo Mode Design

### Demo Mode Indicators

1. **Banner**: Fixed top banner "Demo Mode - Using sample data"
2. **Badge**: "Demo" badge on user avatar
3. **Data Label**: Subtle "(sample)" suffix on sensitive values
4. **Color Accent**: Distinct border color on demo data cards

### Demo Data Set

| Entity | Sample Count | Variety |
|--------|--------------|---------|
| Transactions | 50 | Mixed income/expense, all categories |
| Categories | 13 (system) | All default categories |
| Budgets | 5 | Different statuses (normal, warning, exceeded) |
| Goals | 3 | Different progress levels |
| Date Range | Last 3 months | Realistic distribution |

### Demo Mode Features

1. **Reset Button**: One-click reset to initial demo state
2. **Guided Tour**: Optional walkthrough highlighting key features
3. **Feature Flags**: Can enable/disable specific features
4. **Speed Mode**: Animations at 2x speed for quick demos
5. **Offline Support**: Demo works without network

### Demo Mode UX

```
┌─────────────────────────────────────────────────────────┐
│ ⚠️ Demo Mode - Using sample data       [Exit Demo] [?]  │
├─────────────────────────────────────────────────────────┤
│                                                         │
│                   Normal UI content                     │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

## Component Specifications

### Button Variants

| Variant | Background | Text | Border | Usage |
|---------|------------|------|--------|-------|
| Primary | gradient (purple→blue) | white | none | Main actions |
| Secondary | transparent | primary | primary | Secondary actions |
| Ghost | transparent | text-primary | none | Tertiary actions |
| Destructive | red-500 | white | none | Delete actions |
| Disabled | gray-200 | gray-400 | none | Inactive state |

### Card Variants

| Variant | Background | Border | Shadow | Usage |
|---------|------------|--------|--------|-------|
| Glass | glass-bg + blur | glass-border | shadow-lg | Primary cards |
| Solid | surface | border | shadow | Secondary cards |
| Gradient | gradient-bg | none | shadow-glow | Hero cards |
| Interactive | glass-bg | border | shadow-xl on hover | Clickable cards |

### Input States

| State | Border | Background | Label | Icon |
|-------|--------|------------|-------|------|
| Default | gray-300 | white | text-secondary | none |
| Focus | primary | white | primary | none |
| Valid | success | white | text-secondary | checkmark (green) |
| Error | error | red-50 | error | warning (red) |
| Disabled | gray-200 | gray-50 | text-muted | none |

## Success Criteria

| Metric | Target |
|--------|--------|
| Lighthouse Performance | > 90 |
| Lighthouse Accessibility | 100 |
| First Contentful Paint | < 1.2s |
| Largest Contentful Paint | < 2.0s |
| Cumulative Layout Shift | < 0.1 |
| First Input Delay | < 100ms |
| WCAG 2.1 AA | Full compliance |
| Mobile usability | All features accessible |
| Animation smoothness | 60fps |
| Theme switching | < 300ms |
