# County Health Data API

A Vercel-deployed API that provides access to county-level health data based on ZIP codes. The API includes functionality to convert CSV files to SQLite databases and query health measures by ZIP code.

## Features

### CSV to SQLite Conversion
The `csv_to_sqlite.py` script converts CSV files to SQLite database tables:
```bash
python3 csv_to_sqlite.py data.db zip_county.csv
python3 csv_to_sqlite.py data.db county_health_rankings.csv
```

### County Data API Endpoint
The `/county_data` endpoint accepts POST requests with JSON data to retrieve county health measures:

```bash
curl -X POST https://matthewsau8-vercel.vercel.app/county_data \
  -H "Content-Type: application/json" \
  -d '{"zip":"02138","measure_name":"Adult obesity"}'
```

## Supported Health Measures
- Violent crime rate
- Unemployment
- Children in poverty
- Diabetic screening
- Mammography screening
- Preventable hospital stays
- Uninsured
- Sexually transmitted infections
- Physical inactivity
- Adult obesity
- Premature Death
- Daily fine particulate matter

## API Response Format
```json
[
  {
    "confidence_interval_lower_bound": "0.22",
    "confidence_interval_upper_bound": "0.24",
    "county": "Middlesex County",
    "county_code": "17",
    "data_release_year": "2012",
    "denominator": "263078",
    "fipscode": "25017",
    "measure_id": "11",
    "measure_name": "Adult obesity",
    "numerator": "60771.02",
    "raw_value": "0.23",
    "state": "MA",
    "state_code": "25",
    "year_span": "2009"
  }
]
```

## Error Handling
- 400: Missing required parameters (zip or measure_name)
- 404: ZIP code or measure not found in database
- 418: Easter egg response for coffee=teapot parameter

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run locally:
```bash
python api/index.py
```

## Dependencies
- Flask==2.3.3
- Werkzeug==2.3.7
