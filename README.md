# Genesis Crew - AI-Powered Software Development

An autonomous software engineering collective that transforms user ideas into production-ready software using AI agents.

## 🚀 Quick Start

### 1. Install Dependencies
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Set Up Environment
```bash
# Option 1: Use the setup script (recommended)
python setup_env.py

# Option 2: Manual setup
cp .env.example .env
# Edit .env with your API keys
```

### 3. Run the Genesis Crew
```bash
python genesis_crew_main.py
```

## 🔧 Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENAI_API_KEY` | ✅ Yes | Your OpenAI API key for AI agents |
| `LANGCHAIN_API_KEY` | ❌ No | LangSmith API key for observability |
| `LANGCHAIN_PROJECT` | ❌ No | LangSmith project name |
| `SUPABASE_URL` | ❌ No | Supabase database URL |
| `SUPABASE_KEY` | ❌ No | Supabase anonymous key |

## 📁 Project Structure

```
├── genesis_crew_main.py    # Main application
├── setup_env.py           # Environment setup script
├── .env                   # Environment variables (create this)
├── .env.example          # Environment template
├── requirements.txt      # Python dependencies
└── build/               # Generated artifacts (created at runtime)
```

## 🤖 How It Works

The Genesis Crew consists of specialized AI agents:

1. **Product Manager** - Creates detailed PRDs from user ideas
2. **Solution Architect** - Designs system architecture and database schema
3. **Backend Developer** - Implements FastAPI services with Supabase
4. **Frontend Specialist** - Creates modern, responsive frontend applications
5. **QA Engineer** - Creates comprehensive test suites
6. **DevOps Engineer** - Generates Docker and deployment configurations

## 🛠️ Features

- **Autonomous Workflow** - LangGraph-powered state machine
- **Full-Stack Development** - Complete backend and frontend applications
- **Tool Integration** - File operations and web search
- **Modern Frontend** - React, Vue, or vanilla JS with responsive design
- **Observability** - LangSmith tracing and monitoring
- **Production Ready** - Docker, testing, and deployment configs
- **Supabase Integration** - Database schema and client generation

## 📝 Example Usage

The system will generate a complete "Quote of the Day" web service with:
- FastAPI backend with REST API
- Modern responsive frontend interface
- Supabase database integration
- Comprehensive test suite
- Docker containerization
- Full-stack deployment configurations

## 🔍 Troubleshooting

### Missing API Keys
```bash
python setup_env.py  # Interactive setup
```

### Environment Issues
```bash
source venv/bin/activate
python -c "import genesis_crew_main; print('✅ Environment OK')"
```

### Tool Compatibility
The system uses CrewAI 0.177.0 with custom tool wrappers for full compatibility.
