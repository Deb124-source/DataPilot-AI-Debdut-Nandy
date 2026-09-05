# DataPilot AI Roadmap

The current ZIP contains the complete working code for the features implemented so far.

## Phase 2 — Advanced EDA

1. Histograms using actual value bins
2. Box plots
3. Scatter plots
4. Strongest correlation detection
5. Advanced outlier reports
6. Skewness and distribution analysis
7. Data type recommendations

## Phase 3 — AI Insights

Create an AI insight engine that converts dataset statistics into natural-language findings.

Example:

> The Sales column is strongly correlated with Revenue.
> The Age column contains missing values.
> Income has several extreme observations that may affect analysis.

Possible architecture:

```text
Dataset
   ↓
Profiler
   ↓
EDA Engine
   ↓
Insight Generator
   ↓
LLM / Rule Engine
   ↓
Natural Language Insights
```

## Phase 4 — Chat With Your Dataset

Users ask:

- What is the average salary?
- Which category has the highest sales?
- Show missing data.
- Find the top five records.

Pipeline:

```text
User Question
    ↓
Intent Detection / LLM
    ↓
Safe DataFrame Query
    ↓
Result
    ↓
Explanation
```

## Phase 5 — Reports

Export:

- HTML report
- PDF report
- Excel summary

## Phase 6 — Data Quality Score

Example dimensions:

- Completeness
- Uniqueness
- Consistency
- Validity
- Outlier quality

Output:

```text
Overall Data Quality: 87/100
```

## Phase 7 — Persistent Storage

Replace the current in-memory dataset registry with:

- SQLite for development
- PostgreSQL for production

Store:

- Users
- Projects
- Dataset metadata
- Dataset versions
- Cleaning history
- Reports

## Phase 8 — Authentication

Add:

- Registration
- Login
- JWT authentication
- User projects
- Protected datasets

## Phase 9 — Production Deployment

Recommended architecture:

```text
Frontend
    ↓
FastAPI Backend
    ↓
PostgreSQL
    ↓
Object Storage
```

Potential deployment:

- Frontend: Vercel / Netlify
- Backend: Render / Railway
- Database: PostgreSQL
