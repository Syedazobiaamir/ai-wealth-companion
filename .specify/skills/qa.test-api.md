# Skill: qa.test-api

## Description
Test API endpoints manually or generate API test cases.

## Trigger
- `/qa.test-api` - Test all API endpoints
- `/qa.test-api <endpoint>` - Test specific endpoint
- `/qa.test-api --generate` - Generate test cases for all endpoints

## Execution Steps

1. **Discover endpoints**
   ```bash
   curl http://localhost:8000/openapi.json
   ```

2. **Test each endpoint**
   - GET endpoints: Verify response structure
   - POST endpoints: Test valid and invalid payloads
   - PUT/PATCH endpoints: Test updates
   - DELETE endpoints: Test deletion

3. **Validate responses**
   - Status codes (200, 201, 400, 404, 500)
   - Response schema matches types
   - Error messages are helpful

## API Test Matrix

| Endpoint | Method | Test Cases |
|----------|--------|------------|
| /health | GET | Returns healthy status |
| /api/v1/categories | GET | Returns list of categories |
| /api/v1/transactions | GET | Returns paginated transactions |
| /api/v1/transactions | POST | Creates transaction, validates required fields |
| /api/v1/transactions/{id} | GET | Returns single transaction, 404 if not found |
| /api/v1/transactions/{id} | DELETE | Soft deletes transaction |
| /api/v1/budgets | GET | Returns budgets for month/year |
| /api/v1/budgets | POST | Creates budget, validates category exists |
| /api/v1/budgets/status | GET | Returns budget status with spent/remaining |
| /api/v1/summary/dashboard | GET | Returns full dashboard data |

## Example Test Commands

```bash
# Health check
curl -s http://localhost:8000/health

# Get categories
curl -s http://localhost:8000/api/v1/categories

# Create transaction
curl -X POST http://localhost:8000/api/v1/transactions \
  -H "Content-Type: application/json" \
  -d '{"type":"expense","amount":50,"category_id":"uuid","date":"2026-01-21"}'

# Get dashboard
curl -s "http://localhost:8000/api/v1/summary/dashboard?start_date=2026-01-01&end_date=2026-01-31"
```

## Validation Checklist

- [ ] All endpoints return correct status codes
- [ ] Response bodies match TypeScript types
- [ ] Error responses include helpful messages
- [ ] Pagination works correctly
- [ ] Filters and search work
- [ ] Date ranges are validated
