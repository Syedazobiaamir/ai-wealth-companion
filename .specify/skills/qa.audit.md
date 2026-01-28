# Skill: qa.audit

## Description
Perform comprehensive QA audit of the entire application.

## Trigger
- `/qa.audit` - Full QA audit
- `/qa.audit --ui` - UI/UX audit only
- `/qa.audit --api` - API audit only
- `/qa.audit --security` - Security audit

## Audit Categories

### 1. Functional Testing
- [ ] All CRUD operations work
- [ ] Forms validate correctly
- [ ] Error states display properly
- [ ] Loading states appear
- [ ] Empty states are handled

### 2. UI/UX Audit
- [ ] Design matches specifications
- [ ] Colors follow design system
- [ ] Typography is consistent
- [ ] Spacing/padding is correct
- [ ] Animations work smoothly
- [ ] Dark/light mode works

### 3. Responsive Testing
- [ ] Desktop (1920x1080)
- [ ] Laptop (1366x768)
- [ ] Tablet (768x1024)
- [ ] Mobile (375x667)

### 4. Accessibility Audit
- [ ] Color contrast meets WCAG AA
- [ ] Focus states are visible
- [ ] Keyboard navigation works
- [ ] Screen reader compatible
- [ ] Alt text on images

### 5. Performance Audit
- [ ] Page load < 3s
- [ ] First Contentful Paint < 1.5s
- [ ] No memory leaks
- [ ] Bundle size reasonable
- [ ] Images optimized

### 6. API Audit
- [ ] All endpoints respond
- [ ] Error handling works
- [ ] Validation is thorough
- [ ] Response times < 500ms

### 7. Security Audit
- [ ] No exposed secrets
- [ ] XSS prevention
- [ ] SQL injection prevention
- [ ] CORS configured correctly
- [ ] Input sanitization

## Output Format

```markdown
# QA Audit Report - [Date]

## Summary
- Total Issues: X
- Critical: X
- Major: X
- Minor: X

## Critical Issues
1. [Issue description]
   - Location: [file:line]
   - Impact: [description]
   - Fix: [suggestion]

## Major Issues
...

## Minor Issues
...

## Recommendations
1. [Recommendation]
2. [Recommendation]
```

## Execution

1. Run all test suites
2. Perform manual UI review
3. Check responsive breakpoints
4. Run accessibility scanner
5. Test API endpoints
6. Review security practices
7. Generate report
