# Skill: qa.test-frontend

## Description
Run frontend tests (unit, component, E2E).

## Trigger
- `/qa.test-frontend` - Run all frontend tests
- `/qa.test-frontend --unit` - Run unit tests only
- `/qa.test-frontend --e2e` - Run E2E tests only
- `/qa.test-frontend --coverage` - Run with coverage

## Execution Steps

1. **Navigate to frontend**
   ```bash
   cd frontend
   ```

2. **Run unit/component tests**
   ```bash
   npm test -- --passWithNoTests
   npm test -- --coverage
   ```

3. **Run E2E tests (Playwright)**
   ```bash
   npx playwright test
   npx playwright test --ui  # Interactive mode
   ```

4. **Output**
   - Test results summary
   - Coverage percentage (for unit tests)
   - Screenshot diffs (for visual regression)
   - Failed test details

## Example Output

```
PASS  __tests__/utils/formatters.test.ts
  formatCurrency
    ✓ formats positive numbers (2ms)
    ✓ formats negative numbers (1ms)
    ✓ handles string input (1ms)
  formatPercentage
    ✓ formats with decimals (1ms)

Test Suites: 5 passed, 5 total
Tests:       23 passed, 23 total
Coverage:    87.5%
```

## Prerequisites

Install test dependencies:
```bash
npm install -D jest @testing-library/react @testing-library/jest-dom
npm install -D @playwright/test
npx playwright install
```
