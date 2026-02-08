# COREP Reporting Assistant (Prototype)

LLM-assisted PRA COREP reporting assistant for UK banks. Demonstrates end-to-end behavior: natural-language question → regulatory text retrieval → structured LLM output → populated COREP template.

**Prototype Scope**: Focus on C 01.00 (Own Funds) template only.

## Tech Stack

- **Backend**: Python FastAPI
- **LLM**: OpenAI GPT-4o-mini
- **Database**: PostgreSQL + pgvector
- **Vector Search**: FAISS (local)
- **Interface**: CLI (primary), React (optional)

## Setup Instructions

### Prerequisites

- Python 3.11+
- PostgreSQL 14+ with pgvector extension
- OpenAI API key

### 1. Install PostgreSQL and pgvector

```bash
# macOS (using Homebrew)
brew install postgresql@14
brew services start postgresql@14

# Install pgvector extension
git clone https://github.com/pgvector/pgvector.git
cd pgvector
make
make install
```

### 2. Create Database

```bash
createdb corep_assistant
```

### 3. Backend Setup

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY

# Initialize database
python db/schema.py
```

### 4. Run Backend

```bash
python main.py
```

Backend will start at `http://localhost:8000`

### 5. Test with CLI

```bash
# In a new terminal
cd cli

python query.py \
  --question "What is the Tier 1 capital requirement?" \
  --scenario "Bank has £500m CET1 capital and £100m AT1 instruments" \
  --template C_01_00
```

## Project Structure

```
corep-assistant/
├── backend/
│   ├── main.py              # FastAPI app
│   ├── config.py            # Settings
│   ├── requirements.txt
│   ├── db/
│   │   └── schema.py        # PostgreSQL schema
│   ├── api/                 # (Feature 2+)
│   ├── llm/                 # (Feature 3+)
│   ├── retrieval/           # (Feature 2+)
│   ├── validation/          # (Feature 5+)
│   ├── templates/           # (Feature 4+)
│   └── logging/             # (Feature 6+)
├── cli/
│   └── query.py             # CLI interface
├── data/                    # (Feature 2+)
├── logs/                    # (Feature 6+)
└── README.md
```

## Development Status

- ✅ Feature 1: Backend Setup & CLI Interface
- ⏳ Feature 2: Regulatory Text Retrieval
- ⏳ Feature 3: LLM Integration
- ⏳ Feature 4: Template Renderer
- ⏳ Feature 5: Validation Engine
- ⏳ Feature 6: Audit Logging
- ⏳ Feature 7: End-to-End Testing

## API Endpoints

### Current (Feature 1)
- `GET /` - Root endpoint
- `GET /health` - Health check

### Upcoming
- `POST /api/retrieve` - Retrieve regulatory paragraphs (Feature 2)
- `POST /api/analyze` - Analyze scenario and populate template (Feature 3)
- `POST /api/render` - Render HTML template (Feature 4)

## License

Prototype for demonstration purposes.
