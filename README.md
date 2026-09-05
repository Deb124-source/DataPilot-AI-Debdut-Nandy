# DataPilot AI

An AI-inspired smart data processing platform for:
- Uploading CSV, Excel, JSON, TSV and Parquet datasets
- Dataset profiling
- Smart cleaning
- Dataset version management
- Automated EDA
- Interactive visualizations
- Automatic data insights

## Project structure

```text
DataPilot-AI/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── routes/
│   │   └── services/
│   └── requirements.txt
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── script.js
└── README.md
```

## Run backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Backend:
http://127.0.0.1:8000

API docs:
http://127.0.0.1:8000/docs

## Run frontend

Open `frontend/index.html` using VS Code Live Server.

## Supported formats

- CSV
- Excel (.xlsx, .xls)
- JSON
- TSV
- Parquet

## Next planned modules

The `docs/NEXT_STEPS.md` file contains the roadmap for future work:
- AI-generated insights
- Chat with dataset
- Export reports
- Data quality scoring
- Advanced outlier analysis
- SQL support
- Authentication and user projects
- Database persistence
