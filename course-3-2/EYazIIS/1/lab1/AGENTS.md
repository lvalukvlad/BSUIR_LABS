# AGENTS.md - Agent Coding Guidelines

This document provides guidelines for agents working on this NLP Dictionary project.

## Project Overview

This is a full-stack NLP application for Russian language morphological analysis:
- **Backend**: Python/FastAPI with pymorphy3 for Russian morphology
- **Frontend**: TypeScript/React/Vite

## Build & Run Commands

### Backend

```bash
# Install dependencies (from backend/)
cd backend
pip install -r requirements.txt

# Run development server
python main.py
# Or: uvicorn main:app --host 127.0.0.1 --port 8000 --reload

# Run API at custom port
uvicorn main:app --host 127.0.0.1 --port 8080
```

### Frontend

```bash
# Install dependencies (from frontend/)
cd frontend
npm install

# Run development server
npm run dev

# Build for production
npm run build
```

## Testing

### Backend Tests

Tests are located in `backend/tests/` and run using Python directly:

```bash
# Run all backend tests
cd backend
python -m tests.test_morphology
python -m tests.test_parser
python -m tests.test_generator

# Run single test file
python tests/test_morphology.py
python tests/test_parser.py

# Run single test function
python -c "
import sys
sys.path.insert(0, '.')
from tests.test_morphology import test_analyzer_basic
test_analyzer_basic()
"

# Run API tests (requires server running)
python tests/test_api.py
```

### Frontend Tests

No test framework is currently configured for frontend.

## Code Style Guidelines

### Python (Backend)

**Imports**
- Standard library imports first
- Third-party imports second
- Local imports last
- Use absolute imports from package root
```python
# Correct
from core.morphology.analyzer import RussianMorphAnalyzer
from fastapi import APIRouter

# Avoid
import sys
sys.path.insert(0, '.')
```

**Types**
- Use type hints for function parameters and return values
- Use `typing` module for complex types
```python
from typing import List, Optional, Dict

def analyze(text: str) -> Dict[str, Any]:
    ...
```

**Naming Conventions**
- Constants: `SCREAMING_SNAKE_CASE`
- Classes: `PascalCase`
- Functions/variables: `snake_case`
- Private functions: prefix with `_`

**Error Handling**
- Use try/except for external operations (file I/O, network)
- Catch specific exceptions when possible
- Use FastAPI's `HTTPException` for API errors
```python
try:
    result = parser.parse(content)
except Exception as e:
    raise HTTPException(status_code=400, detail=str(e))
```

**Code Organization**
- One class per file (or related classes)
- Keep functions small and focused
- Use docstrings for public APIs (in Russian, as project uses Russian)
- Group related constants in classes or modules

**API Design**
- Use Pydantic models for request/response schemas
- Group endpoints by feature using routers
- Return consistent JSON structure
- Use Russian labels for grammemes (падеж, род, число)

### TypeScript/React (Frontend)

**Naming**
- Components: `PascalCase`
- Functions/variables: `camelCase`
- Files: `kebab-case.tsx`

**Types**
- Use explicit types for props and function signatures
- Define shared types in `src/api/types.ts`

**Components**
- Use functional components with hooks
- Keep components small and focused
- Extract reusable logic into custom hooks (`src/hooks/`)

**Code Organization**
```
src/
├── api/          # API client and types
├── components/  # React components
├── hooks/       # Custom hooks
└── utils/       # Utility functions
```

## Project Structure

```
backend/
├── api/
│   ├── routes/      # API endpoint handlers
│   └── deps.py      # Dependencies
├── core/
│   ├── morphology/ # NLP analysis
│   ├── parser/     # File parsers
│   └── dictionary/ # Dictionary storage
├── schemas/        # Pydantic models
├── storage/        # Data persistence
├── utils/          # Helpers
├── tests/          # Unit tests
└── main.py         # App entry point

frontend/
├── src/
│   ├── api/        # API client
│   ├── components/ # React components
│   ├── hooks/      # Custom hooks
│   └── utils/      # Utilities
└── package.json
```

## Common Tasks

### Running the full application

```bash
# Terminal 1: Backend
cd backend
python main.py

# Terminal 2: Frontend
cd frontend
npm run dev
```

### Testing a specific endpoint

```bash
# Health check
curl http://127.0.0.1:8000/api/health

# Analyze text file
curl -X POST -F "file=@test.txt" http://127.0.0.1:8000/api/analyze
```

### Adding a new API endpoint

1. Create route in `backend/api/routes/`
2. Add router to `backend/main.py`
3. Add frontend component in `frontend/src/components/`
4. Add API method in `frontend/src/api/endpoints.ts`
