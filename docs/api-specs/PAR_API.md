"""
API Specification - PAR (Portfolio at Risk) Endpoints

Base URL: /api/v1/par
"""

## GET /summary

Get PAR summary metrics across the portfolio.

**Query Parameters:**
- `start_date` (optional): ISO format date
- `end_date` (optional): ISO format date

**Response:**
```json
{
  "par_30": 5.2,
  "par_60": 3.1,
  "par_90": 2.0,
  "par_180_plus": 1.5,
  "total_par": 11.8,
  "total_portfolio": 1250000,
  "par_amount": 147500,
  "currency": "USD"
}
```

## GET /by-region

Get PAR metrics broken down by region.

**Response:**
```json
{
  "regions": [
    {
      "region_id": "region_1",
      "region_name": "North Region",
      "par_percentage": 12.5,
      "total_exposure": 250000,
      "accounts_at_risk": 45
    }
  ]
}
```

## GET /by-branch

Get PAR metrics broken down by branch.

**Response:**
```json
{
  "branches": [
    {
      "branch_id": 101,
      "branch_name": "Main Branch",
      "par_percentage": 8.2,
      "total_exposure": 500000,
      "accounts_at_risk": 32
    }
  ]
}
```

## GET /trend

Get historical PAR trend data.

**Query Parameters:**
- `days`: Number of days to retrieve (default: 90)
- `frequency`: Data frequency - daily, weekly, monthly (default: daily)

**Response:**
```json
{
  "data": [
    {
      "date": "2024-01-01",
      "par_percentage": 11.5,
      "total_par_amount": 143750
    }
  ],
  "trend": "increasing"
}
```

---

## Error Responses

All endpoints may return:

```json
{
  "detail": "Error description",
  "status_code": 400
}
```

**Status Codes:**
- 200: Success
- 400: Bad request
- 401: Unauthorized
- 404: Not found
- 500: Server error
