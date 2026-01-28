# Research: Phase II Full-Stack Financial Platform

**Date**: 2026-01-19
**Branch**: `003-phase2-fullstack-platform`

## Research Summary

All technology choices are pre-determined by the constitution (Phase II Laws). This document confirms best practices and patterns for the mandated stack.

## Technology Research

### 1. FastAPI + SQLModel Best Practices

**Decision**: Use FastAPI with SQLModel for type-safe ORM with Pydantic validation

**Rationale**:
- SQLModel combines SQLAlchemy with Pydantic for type-safe database models
- Same model class works for both database operations and API request/response validation
- Async support via asyncpg driver for high concurrency
- Built-in OpenAPI documentation generation

**Best Practices Identified**:
- Use dependency injection for database sessions (`Depends(get_session)`)
- Separate models into Table models (database) and Read/Create models (API)
- Use `AsyncSession` for non-blocking database operations
- Implement repository pattern for testability
- Use `lifespan` context manager for startup/shutdown events

**Alternatives Considered**:
- Django REST Framework: More opinionated, heavier, slower for async workloads
- Flask + SQLAlchemy: Less type-safe, manual schema generation
- Litestar: Less mature ecosystem

### 2. Next.js 14 App Router Patterns

**Decision**: Use Next.js 14 App Router with Server Components

**Rationale**:
- App Router is the future of Next.js (Pages Router deprecated)
- Server Components reduce client-side JavaScript bundle
- Built-in layouts, loading states, and error boundaries
- Streaming and Suspense for better perceived performance

**Best Practices Identified**:
- Use Server Components for data fetching, Client Components for interactivity
- Place `'use client'` directive only where needed (forms, charts, animations)
- Use route groups `(group)` for organization without affecting URL
- Implement loading.tsx and error.tsx for each route segment
- Use `generateMetadata` for SEO

**Alternatives Considered**:
- Vite + React: No SSR out of box, more config needed
- Remix: Smaller ecosystem, less UI library compatibility
- SvelteKit: Would require team to learn new framework

### 3. Neon PostgreSQL Connection Strategy

**Decision**: Use Neon serverless driver with connection pooling

**Rationale**:
- Neon provides serverless PostgreSQL with auto-scaling
- WebSocket-based serverless driver reduces cold start latency
- Connection pooling essential for serverless environments
- Branch-based development databases for testing

**Best Practices Identified**:
- Use `@neondatabase/serverless` driver for edge/serverless
- Use standard `asyncpg` for traditional server deployment
- Configure connection pooling via Neon console (not application-level)
- Use environment variables for connection string (never hardcode)
- Implement query timeout (30s default) to prevent runaway queries

**Connection String Pattern**:
```
postgresql://user:password@ep-xxx.region.aws.neon.tech/dbname?sslmode=require
```

**Alternatives Considered**:
- Supabase: Good, but Neon specified in constitution
- PlanetScale: MySQL-based, not PostgreSQL
- AWS RDS: Not serverless, always-on cost

### 4. Glassmorphism Implementation

**Decision**: Use Tailwind CSS with backdrop-filter for glass effects

**Rationale**:
- Native CSS backdrop-filter has good browser support (95%+)
- Tailwind's `backdrop-blur-lg` provides consistent implementation
- Fallback to solid semi-transparent backgrounds for unsupported browsers

**Best Practices Identified**:
- Use `bg-white/10` or `bg-black/5` for transparency
- Apply `backdrop-blur-lg` (16px blur) for frosted effect
- Add subtle border with `border-white/20` for definition
- Use `shadow-xl shadow-purple-500/10` for glow effect
- Ensure sufficient contrast for accessibility (WCAG 2.1 AA)

**CSS Pattern**:
```css
.glass-card {
  @apply bg-white/10 backdrop-blur-lg rounded-2xl border border-white/20 shadow-xl;
}

/* Fallback for browsers without backdrop-filter support */
@supports not (backdrop-filter: blur(16px)) {
  .glass-card {
    @apply bg-gray-800/90;
  }
}
```

### 5. Recharts vs Chart.js

**Decision**: Use Recharts for chart rendering

**Rationale**:
- Built specifically for React with declarative API
- Smaller bundle size than Chart.js when tree-shaken
- Composable components match React patterns
- Built-in responsive container
- Easy theming with Tailwind colors

**Best Practices Identified**:
- Use `ResponsiveContainer` wrapper for all charts
- Implement custom tooltips matching design system
- Lazy load chart components to reduce initial bundle
- Use `animationDuration={300}` to match design system timing
- Implement empty states when no data available

**Alternatives Considered**:
- Chart.js: Canvas-based, harder to style, larger bundle
- D3.js: Low-level, overkill for standard charts
- Visx: Good, but less documentation

### 6. Framer Motion Animation Patterns

**Decision**: Use Framer Motion for all animations

**Rationale**:
- React-specific with declarative API
- Hardware-accelerated animations
- Built-in gesture support
- AnimatePresence for exit animations
- Layout animations for smooth transitions

**Best Practices Identified**:
- Use `motion` components for animated elements
- Define animation variants for reusable patterns
- Use `whileHover`, `whileTap` for microinteractions
- Keep duration between 200-300ms per design system
- Use `AnimatePresence` for mount/unmount animations
- Use `layout` prop for automatic layout animations

**Animation Variants Pattern**:
```typescript
const cardVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.3 } },
  hover: { scale: 1.02, transition: { duration: 0.2 } }
};
```

### 7. Dark/Light Theme Implementation

**Decision**: Use CSS variables with next-themes library

**Rationale**:
- `next-themes` handles SSR hydration correctly
- CSS variables enable instant theme switching
- LocalStorage persistence built-in
- System preference detection supported

**Best Practices Identified**:
- Define theme colors as CSS variables in globals.css
- Use Tailwind's `dark:` variant for conditional styles
- Store user preference in localStorage
- Respect system preference as default
- Avoid flash of unstyled content (FOUC)

**Implementation Pattern**:
```typescript
// ThemeProvider wraps app
<ThemeProvider attribute="class" defaultTheme="system">
  {children}
</ThemeProvider>

// Use dark: variant in Tailwind
<div className="bg-white dark:bg-gray-900">
```

### 8. API Rate Limiting Strategy

**Decision**: Implement rate limiting with slowapi middleware

**Rationale**:
- Protection against abuse required by constitution
- Per-IP rate limiting sufficient for single-user Phase II
- Can upgrade to token-based limiting in Phase III

**Best Practices Identified**:
- Use `slowapi` library (FastAPI-specific wrapper for limits)
- Configure limits per endpoint (e.g., 100/minute for reads, 30/minute for writes)
- Return 429 status with Retry-After header
- Log rate limit violations for monitoring
- Allow configurable limits via environment variables

**Configuration Pattern**:
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.get("/api/v1/transactions")
@limiter.limit("100/minute")
async def list_transactions(...):
    ...
```

## Resolved Unknowns

All technical context items resolved:

| Item | Resolution |
|------|------------|
| Language/Version | Python 3.11+, TypeScript 5.x |
| Primary Dependencies | FastAPI, SQLModel, Next.js 14, Tailwind, Framer Motion, Recharts |
| Storage | Neon PostgreSQL with asyncpg/serverless driver |
| Testing | pytest + pytest-asyncio, Jest + RTL |
| Target Platform | Modern web browsers (Chrome, Firefox, Safari, Edge) |
| Performance Goals | LCP < 2s, API p95 < 500ms |
| Constraints | Single-user, UI-only chatbot, no bank connections |
| Scale/Scope | ~10 endpoints, ~8 screens, ~30 components |

## Phase 1 Ready

All NEEDS CLARIFICATION items resolved. Proceed to Phase 1: Design & Contracts.
