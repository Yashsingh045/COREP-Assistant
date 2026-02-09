# COREP Reporting Assistant

**AI-powered regulatory reporting assistant for UK banks**. Converts natural-language scenarios into populated COREP templates using GPT-4o-mini, regulatory text retrieval, and automated validation.

> **Prototype Scope**: Demonstrates C 01.00 (Own Funds) template only

## 🎯 Features

- ✅ **Regulatory Text Retrieval** - Hybrid search (keyword + semantic) over PRA Rulebook & EBA COREP instructions
- ✅ **LLM Integration** - GPT-4o-mini generates structured JSON with justifications
- ✅ **Validation Engine** - Automated checks for mandatory fields, ranges, and cross-field consistency
- ✅ **HTML Rendering** - Color-coded templates with hover tooltips
- ✅ **Audit Logging** - Complete JSON audit trail for compliance
- ✅ **CLI Interface** - Command-line tool for rapid testing

## 🏗️ Architecture

```
Natural Language → Retrieval → LLM → Validation → HTML + Audit
     Query          (pgvector)   (GPT-4o)  (Rules)    (Jinja2)
```

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- PostgreSQL 14+ with pgvector
- OpenAI API key

### Installation

```bash
# 1. Clone repository
git clone https://github.com/Yashsingh045/COREP-Assistant.git
cd COREP-Assistant

# 2. Install PostgreSQL + pgvector (macOS)
brew install postgresql@14
brew services start postgresql@14

# 3. Create database
createdb corep_assistant

# 4. Backend setup
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 5. Configure environment
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY

# 6. Initialize database and populate sample data
python db/schema.py
python populate_db_mock.py  # Uses mock embeddings (or populate_db.py for real)

# 7. Start backend
python main.py
```

Backend runs at `http://localhost:8000`

## 📖 Usage

### CLI Query

```bash
source backend/venv/bin/activate

python cli/query.py \
  --question "What are the Tier 1 capital components?" \
  --scenario "Bank has £500m CET1 capital and £100m AT1 instruments"
```

**Output**: JSON with populated fields, justifications, and validation warnings

### View Audit Logs

```bash
python cli/view_logs.py          # Show 10 recent logs
python cli/view_logs.py --limit 20
python cli/view_logs.py --log-id 20260209_123456_789012
```

### Run Test Scenarios

```bash
bash tests/test_scenarios.sh
```

## 🔌 API Endpoints

### Core Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check with system info |
| `/api/retrieve` | POST | Retrieve regulatory paragraphs |
| `/api/analyze` | POST | Analyze scenario and generate COREP output |
| `/api/render` | POST | Render COREP output as HTML |

### Example: Analyze Scenario

```bash
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What are the capital components?",
    "scenario": "Bank has £500m CET1 and £100m AT1",
    "template": "C_01_00",
    "top_k": 5
  }'
```

**Response**:
```json
{
  "template": "C_01_00",
  "fields": [
    {
      "row": "010",
      "metric_name": "Common Equity Tier 1 capital",
      "value": 500000000.0,
      "currency": "GBP",
      "status": "populated",
      "justification": "Bank has £500m CET1 capital...",
      "source_paragraphs": ["CRR Article 26", "COREP C0100_010"]
    }
  ],
  "validation_warnings": []
}
```

## 📁 Project Structure

```
COREP-Assistant/
├── backend/
│   ├── main.py                 # FastAPI application
│   ├── config.py               # Configuration management
│   ├── requirements.txt
│   ├── api/                    # API endpoints
│   │   ├── analyze.py         # Scenario analysis
│   │   ├── retrieve.py        # Text retrieval
│   │   └── render.py          # HTML rendering
│   ├── db/                     # Database
│   │   ├── schema.py          # PostgreSQL + pgvector schema
│   │   └── loader.py          # Data loading utilities
│   ├── llm/                    # LLM integration
│   │   ├── client.py          # OpenAI API wrapper
│   │   ├── prompts.py         # Prompt templates
│   │   └── schema.py          # Pydantic output models
│   ├── retrieval/              # Retrieval system
│   │   ├── embeddings.py      # OpenAI embeddings
│   │   └── search.py          # Hybrid search
│   ├── validation/             # Validation engine
│   │   └── engine.py          # Validation rules
│   ├── renderer/               # HTML rendering
│   │   └── template.py        # Jinja2 templates
│   └── audit/                  # Audit logging
│       └── logger.py          # JSON audit logger
├── cli/
│   ├── query.py               # CLI query tool
│   └── view_logs.py           # Log viewer
├── data/
│   └── pra_corep_c01.json     # Sample regulatory text (10 docs)
├── tests/
│   └── test_scenarios.sh      # E2E test scenarios
└── logs/                       # Audit trail (generated)
```

## 🧪 Testing

### Unit Tests

```bash
cd backend
source venv/bin/activate

# Test validation engine
python test_validation.py

# Test HTML rendering
python test_render.py
```

### End-to-End Tests

```bash
# Run all 4 test scenarios
bash tests/test_scenarios.sh
```

**Test Scenarios:**
1. Basic CET1 + AT1 capital
2. Complete own funds with T2
3. Missing Tier 2 data
4. Edge case: Zero AT1

## 🎨 HTML Output

The `/api/render` endpoint generates professional HTML with:

- **Color-coded status**:
  - 🟢 Green (populated)
  - 🔴 Red (missing)
  - 🟡 Yellow (inconsistent)
- **Hover tooltips** with justifications and regulatory sources
- **Validation warnings** section
- **Responsive design**

## 📊 Validation Rules

1. **Mandatory Fields** - Rows 010, 030, 050 must be populated
2. **Numeric Ranges** - Detects negative/unreasonable values
3. **Data Types** - Ensures capital fields are numeric
4. **Consistency** - Validates:
   - T1 (030) = CET1 (010) + AT1 (020)
   - Total (050) = T1 (030) + T2 (040)

## 🔍 Sample Data

**10 regulatory documents** (PRA Rulebook + EBA COREP):
- CRR Articles on capital definitions
- COREP C 01.00 instructions
- Own funds calculation rules

## 📝 Environment Variables

```env
# .env file
OPENAI_API_KEY=sk-...
DATABASE_URL=postgresql://localhost/corep_assistant
OPENAI_MODEL=gpt-4o-mini
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
ENVIRONMENT=development
```

## 🚧 Limitations

- **Prototype scope**: C 01.00 template only
- **Mock embeddings**: Due to OpenAI quota, using random embeddings for demo
- **Sample data**: 10 regulatory documents (production would need full rulebook)
- **No authentication**: Not production-ready

## 🔮 Future Enhancements

- [ ] Support for all COREP templates (C 02.00, C 03.00, etc.)
- [ ] Real-time OpenAI embeddings (requires quota increase)
- [ ] React frontend UI
- [ ] Multi-user authentication
- [ ] Export to Excel/PDF
- [ ] Regulatory update tracking

## 📚 Tech Stack

| Component | Technology |
|-----------|-----------|
| **Backend** | FastAPI, Python 3.12 |
| **Database** | PostgreSQL 14 + pgvector |
| **LLM** | OpenAI GPT-4o-mini |
| **Embeddings** | OpenAI text-embedding-3-small |
| **Validation** | Pydantic |
| **Templates** | Jinja2 |
| **CLI** | Python argparse, httpx |

## 📄 License

Prototype for demonstration purposes.

## 👤 Author

Yash Singh - [GitHub](https://github.com/Yashsingh045)

---

**Built with** ❤️ **for regulatory reporting automation**
