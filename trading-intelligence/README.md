# Personal Trading Intelligence System

AI-powered market intelligence platform for personal trading decision support.

**This is NOT an autonomous trading bot.** The system collects, filters, analyzes, and presents market information. All trading decisions remain with the user.

## Architecture

```
USER → AI Agent → Development Machine → GitHub → CI/CD → Ubuntu Production Server
                                                              ↓
                                              Docker Services (PostgreSQL, Redis,
                                              Backend, Telegram Bot, Workers)
                                                              ↓
                                                        Telegram → USER
```

## Hardware

| Machine | Role | Hardware |
|---------|------|----------|
| Old Laptop | 24/7 Production Server | i7 7th Gen, 16GB RAM, 250GB |
| New Laptop | AI/Dev Workstation | Ryzen 7 7840HS, RTX 4070 Laptop (8GB), 32GB RAM |

## Quick Start

### Prerequisites

- Python 3.12+
- Docker + Docker Compose
- Git

### Development Setup

```bash
# Clone
git clone <repo-url>
cd trading-intelligence

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac

# Install
pip install -e ".[dev]"

# Copy environment config
cp .env.example .env
# Edit .env with your values

# Run tests
pytest

# Start services (production)
docker compose -f docker/docker-compose.yml up -d
```

## Project Structure

```
trading-intelligence/
├── backend/          # FastAPI backend API
├── telegram_bot/     # Telegram bot interface
├── workers/          # Background data collectors
│   ├── news/         # RSS + web news collection
│   ├── market/       # Market price data (Binance, etc.)
│   └── macro/        # Macroeconomic data (FRED, BEA, etc.)
├── ai/               # AI layer
│   ├── providers/    # LLM provider abstraction
│   ├── rag/          # RAG pipeline
│   ├── embeddings/   # Embedding generation
│   └── intelligence/ # Market intelligence engine
├── indicators/       # Technical analysis
├── backtesting/      # Backtesting engine
├── database/         # Schema + migrations
├── tests/            # Unit + integration tests
├── scripts/          # Setup + diagnostic scripts
├── configs/          # YAML configuration
├── docker/           # Dockerfiles + compose
└── docs/            # Documentation
```

## Safety Boundaries

- No broker/exchange trading API keys in the system
- No automatic order execution
- No automatic position opening/closing
- All trade decisions are made by the user
- Telegram output is decision support, not trade recommendations

## License

Proprietary — Personal use only.
