# Skill: qa.test-backend

## Description
Run backend tests and generate coverage report.

## Trigger
- `/qa.test-backend` - Run all backend tests
- `/qa.test-backend --coverage` - Run with coverage report
- `/qa.test-backend <pattern>` - Run tests matching pattern

## Execution Steps

1. **Activate virtual environment**
   ```bash
   cd backend && source venv/bin/activate
   ```

2. **Run tests**
   ```bash
   # All tests
   pytest -v

   # With coverage
   pytest --cov=src --cov-report=html --cov-report=term-missing

   # Specific pattern
   pytest -v -k "<pattern>"
   ```

3. **Output**
   - Test results summary
   - Coverage percentage
   - Failed test details
   - Suggestions for fixes

## Example Output

```
========================= test session starts =========================
collected 73 items

tests/unit/test_utils.py ........                               [ 10%]
tests/integration/test_transactions.py ..............           [ 30%]
tests/integration/test_budgets.py ............                  [ 46%]
tests/integration/test_summary.py ............                  [ 63%]

========================= 73 passed in 2.34s ==========================

Coverage Report:
Name                          Stmts   Miss  Cover
-------------------------------------------------
src/api/routes/transactions.py   45      2    96%
src/api/routes/budgets.py        38      1    97%
src/services/summary.py          67      5    93%
-------------------------------------------------
TOTAL                           450     32    93%
```

## Error Handling

If tests fail:
1. Show failed test name and location
2. Display assertion error message
3. Suggest potential fixes
4. Do NOT auto-fix production code
