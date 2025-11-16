# MadCP - Modern AI-Driven Code Platform

<div align="center">

![MadCP Logo](docs/assets/logo.png)

**Piattaforma modulare e agnostica per lo sviluppo software moderno**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](https://www.docker.com/)
[![Kubernetes](https://img.shields.io/badge/kubernetes-ready-blue.svg)](https://kubernetes.io/)

[Documentazione](#documentazione) • [Quick Start](#quick-start) • [Architettura](#architettura) • [API](#api) • [Contributing](#contributing)

</div>

---

## 📋 Indice

- [Introduzione](#introduzione)
- [Caratteristiche Principali](#caratteristiche-principali)
- [Architettura](#architettura)
- [Quick Start](#quick-start)
- [Installazione](#installazione)
- [Configurazione](#configurazione)
- [Utilizzo](#utilizzo)
- [API Reference](#api-reference)
- [Plugin System](#plugin-system)
- [Deployment](#deployment)
- [Sviluppo](#sviluppo)
- [Testing](#testing)
- [Documentazione](#documentazione)
- [Contributing](#contributing)
- [Roadmap](#roadmap)
- [License](#license)

---

## 🎯 Introduzione

**MadCP** (Modern AI-Driven Code Platform) è un server MCP avanzato progettato per supportare team di sviluppo con strumenti intelligenti di analisi del codebase, ricerca semantica, generazione automatica di patch e pianificazione assistita da AI.

### Scopo

Il server MCP offre una piattaforma modulare e agnostica che:

- 🔍 **Analizza** il codebase in profondità (parsing, AST, dipendenze, metriche)
- 🧠 **Comprende** il codice tramite embeddings e ricerca semantica
- 🔧 **Suggerisce** fix, refactor e genera diff pronti per PR
- 📊 **Pianifica** automaticamente issue e task basandosi sull'analisi del repository
- 🔌 **Si estende** tramite un sistema di plugin modulari
- 🌐 **Si integra** facilmente in qualsiasi workflow (locale, LAN, cloud)

### Perché MadCP?

- **Riduzione Costi Token**: Tecniche avanzate di caching, RAG e retrieval riducono drasticamente il consumo di token LLM
- **Multi-linguaggio**: Supporto estensibile per Python, JavaScript, TypeScript, Go, Java, Rust e altri
- **Developer-Friendly**: Web UI completa per configurazione e manutenzione
- **Production-Ready**: Architettura a microservizi scalabile, con supporto Docker e Kubernetes
- **Sicuro**: OAuth2/OIDC, RBAC, TLS integrati di default

---

## ✨ Caratteristiche Principali

### Core Features

#### 🔍 Code Analysis
- **Parsing Multi-linguaggio**: Tree-sitter per AST accurati
- **Dependency Graph**: Analisi completa delle dipendenze
- **Code Metrics**: Complessità ciclomatica, LOC, code smells
- **Pattern Detection**: Individuazione automatica di anti-pattern

#### 🧠 Semantic Search
- **Vector Embeddings**: Rappresentazione semantica di codice e documentazione
- **Similarity Search**: Ricerca per somiglianza concettuale
- **Context Retrieval**: RAG ottimizzato per domande tecniche
- **Smart Chunking**: Strategie intelligenti per segmentazione del codice

#### 🔧 AI Assistance
- **Fix Suggestions**: Suggerimenti automatici per bug e code smell
- **Refactoring**: Proposte di refactoring basate su best practices
- **Diff Generation**: Generazione di patch pronte per PR
- **Code Review**: Assistenza automatica nella code review

#### 📊 Planning & Automation
- **Repository Analysis**: Analisi completa del progetto
- **Issue Generation**: Creazione automatica di issue da TODO e problemi
- **Task Breakdown**: Suddivisione intelligente di task complessi
- **Project Insights**: Dashboard con metriche e KPI di progetto

#### 🔌 Plugin System
- **Modulare**: Architettura plugin-based estendibile
- **Sandboxed**: Esecuzione sicura dei plugin
- **Hot Reload**: Caricamento dinamico senza restart
- **Plugin Registry**: Repository centralizzato di plugin

#### 🌐 Web UI
- **Dashboard Intuitiva**: Interfaccia user-friendly per tutte le funzionalità
- **Configuration Management**: Gestione configurazioni tramite UI
- **Real-time Updates**: WebSocket per aggiornamenti in tempo reale
- **Analytics**: Visualizzazione metriche e statistiche

### Non-Functional Features

- ⚡ **Alta Performance**: Architettura asincrona e caching intelligente
- 📈 **Scalabilità**: Microservizi scalabili orizzontalmente
- 🔒 **Sicurezza**: OAuth2, JWT, RBAC, TLS
- 📊 **Observability**: Prometheus, Grafana, OpenTelemetry
- 🐳 **Portabilità**: Docker, Kubernetes, bare-metal
- 🛠️ **Configurabilità**: YAML, environment variables, UI

---

## 🏗️ Architettura

MadCP utilizza un'architettura a **microservizi** per garantire scalabilità, manutenibilità e resilienza.

```
┌─────────────────────────────────────────────────────────┐
│                  API Gateway (Nginx)                     │
│         Load Balancing • Rate Limiting • TLS             │
└──────────────────────┬──────────────────────────────────┘
                       │
        ┌──────────────┼──────────────┐
        │              │              │
┌───────▼──────┐ ┌────▼─────┐ ┌──────▼───────┐
│ Auth Service │ │Core API  │ │  Web UI      │
│  (Keycloak)  │ │ (FastAPI)│ │ (Next.js)    │
└──────────────┘ └────┬─────┘ └──────────────┘
                      │
        ┌─────────────┼─────────────────┐
        │             │                 │
┌───────▼────────┐ ┌─▼──────────┐ ┌────▼──────────┐
│ Code Analysis  │ │ Embedding  │ │ Planning      │
│   Service      │ │  Service   │ │  Service      │
│ (AST, Parse)   │ │ (Vectors)  │ │ (AI Planning) │
└────────┬───────┘ └─────┬──────┘ └───────┬───────┘
         │               │                 │
┌────────▼───────────────▼─────────────────▼───────┐
│            Plugin Manager Service                 │
│         (Dynamic Plugin Loading)                  │
└────────┬──────────────────────────────────────────┘
         │
┌────────▼──────────────────────────────────────────┐
│                  Data Layer                       │
│  PostgreSQL  │  Qdrant  │  Redis  │  S3/MinIO    │
└───────────────────────────────────────────────────┘
```

### Componenti Principali

| Componente | Tecnologia | Descrizione |
|------------|-----------|-------------|
| **API Gateway** | Nginx | Reverse proxy, load balancing, rate limiting |
| **Core API** | FastAPI | API REST principale, orchestrazione servizi |
| **Auth Service** | Keycloak | Autenticazione OAuth2/OIDC, gestione utenti |
| **Code Analysis** | Python + Tree-sitter | Parsing, AST, analisi dipendenze |
| **Embedding Service** | Python + LangChain | Generazione embeddings, vector search |
| **Planning Service** | Python + LLM | AI planning, issue generation |
| **Plugin Manager** | Python | Gestione plugin, sandboxing |
| **Web UI** | Next.js + React | Interfaccia utente completa |
| **PostgreSQL** | PostgreSQL 15+ | Database relazionale per metadata |
| **Qdrant** | Qdrant | Vector database per embeddings |
| **Redis** | Redis 7+ | Caching, sessioni, message queue |

Per dettagli completi, vedi [Documentazione Architettura](docs/architecture.md).

---

## 🚀 Quick Start

### Prerequisiti

- **Docker** 24.0+ e **Docker Compose** 2.20+
- **Python** 3.11+ (per sviluppo locale)
- **Node.js** 18+ (per Web UI)
- Almeno **4GB RAM** disponibili

### Installazione Rapida (Docker)

```bash
# 1. Clone del repository
git clone https://github.com/yayoboy/MadCP.git
cd MadCP

# 2. Copia il file di configurazione
cp .env.example .env

# 3. Modifica le variabili d'ambiente (opzionale)
nano .env

# 4. Avvia tutti i servizi
docker-compose up -d

# 5. Verifica lo stato dei servizi
docker-compose ps

# 6. Accedi alla Web UI
# http://localhost:3000
```

### Verifica Installazione

```bash
# Health check del Core API
curl http://localhost:8000/health

# Verifica servizi
curl http://localhost:8000/api/v1/status
```

**Output atteso:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "services": {
    "database": "connected",
    "redis": "connected",
    "vector_db": "connected"
  }
}
```

---

## 📦 Installazione

### Opzione 1: Docker Compose (Raccomandato)

Vedi [Quick Start](#quick-start).

### Opzione 2: Installazione Manuale

#### Backend

```bash
# 1. Setup Python environment
cd services/core-api
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. Installa dipendenze
pip install -r requirements.txt

# 3. Setup database
alembic upgrade head

# 4. Avvia il server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend

```bash
# 1. Installa dipendenze
cd web-ui
npm install

# 2. Configura environment
cp .env.example .env.local

# 3. Avvia dev server
npm run dev
```

#### Database e Redis

```bash
# PostgreSQL
docker run -d \
  --name madcp-postgres \
  -e POSTGRES_PASSWORD=madcp_password \
  -e POSTGRES_DB=madcp \
  -p 5432:5432 \
  postgres:15-alpine

# Redis
docker run -d \
  --name madcp-redis \
  -p 6379:6379 \
  redis:7-alpine

# Qdrant (Vector DB)
docker run -d \
  --name madcp-qdrant \
  -p 6333:6333 \
  qdrant/qdrant
```

### Opzione 3: Kubernetes

```bash
# 1. Setup namespace
kubectl create namespace madcp

# 2. Deploy con Helm
helm install madcp ./infrastructure/helm/madcp \
  --namespace madcp \
  --values infrastructure/helm/madcp/values-production.yaml

# 3. Verifica deployment
kubectl get pods -n madcp
```

Vedi [Deployment Guide](docs/deployment.md) per dettagli completi.

---

## ⚙️ Configurazione

### File di Configurazione

MadCP supporta configurazione tramite:

1. **File YAML**: `config/default.yaml`, `config/production.yaml`
2. **Environment Variables**: `.env`
3. **Web UI**: Interfaccia di configurazione

### Configurazione Base

```yaml
# config/default.yaml
app:
  name: "MadCP"
  version: "1.0.0"
  environment: "development"
  debug: true

api:
  host: "0.0.0.0"
  port: 8000
  cors_origins:
    - "http://localhost:3000"
  rate_limit: "100/minute"

database:
  url: "postgresql://madcp:password@localhost:5432/madcp"
  pool_size: 10
  max_overflow: 20

redis:
  url: "redis://localhost:6379/0"
  password: null
  max_connections: 50

vector_db:
  provider: "qdrant"
  url: "http://localhost:6333"
  collection_name: "madcp_embeddings"

llm:
  provider: "openai"  # openai, anthropic, local
  api_key: "${OPENAI_API_KEY}"
  model: "gpt-4-turbo-preview"
  max_tokens: 4096
  temperature: 0.7

embeddings:
  provider: "openai"
  model: "text-embedding-3-small"
  dimensions: 1536
  batch_size: 100

plugins:
  enabled: true
  directory: "./plugins"
  auto_reload: true

security:
  oauth2_enabled: true
  jwt_secret: "${JWT_SECRET}"
  jwt_algorithm: "HS256"
  access_token_expire_minutes: 30

observability:
  prometheus_enabled: true
  grafana_enabled: true
  tracing_enabled: true
  log_level: "INFO"
```

### Environment Variables

```bash
# .env.example

# Application
APP_ENV=development
DEBUG=true

# Database
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=madcp
POSTGRES_USER=madcp
POSTGRES_PASSWORD=madcp_secure_password

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=

# Vector Database
QDRANT_HOST=localhost
QDRANT_PORT=6333

# LLM Providers
OPENAI_API_KEY=sk-your-key-here
ANTHROPIC_API_KEY=your-key-here

# Security
JWT_SECRET=your-super-secret-jwt-key-change-this
OAUTH2_CLIENT_ID=
OAUTH2_CLIENT_SECRET=

# Web UI
NEXT_PUBLIC_API_URL=http://localhost:8000

# Observability
PROMETHEUS_PORT=9090
GRAFANA_PORT=3001
```

---

## 💻 Utilizzo

### Via API REST

```python
import requests

# 1. Analizza un repository
response = requests.post(
    "http://localhost:8000/api/v1/analysis/repository",
    json={
        "repository_url": "https://github.com/username/repo",
        "branch": "main",
        "languages": ["python", "javascript"]
    }
)
analysis_id = response.json()["id"]

# 2. Ottieni risultati analisi
results = requests.get(
    f"http://localhost:8000/api/v1/analysis/{analysis_id}"
).json()

# 3. Ricerca semantica
search_results = requests.post(
    "http://localhost:8000/api/v1/search/semantic",
    json={
        "query": "function for database connection pooling",
        "repository_id": results["repository_id"],
        "limit": 10
    }
).json()

# 4. Genera fix per un bug
fix = requests.post(
    "http://localhost:8000/api/v1/assist/fix",
    json={
        "file_path": "src/database.py",
        "issue_description": "Memory leak in connection pool",
        "context": search_results
    }
).json()
```

### Via Web UI

1. **Dashboard**: Panoramica di tutti i repository analizzati
2. **Analyze**: Carica e analizza un nuovo repository
3. **Search**: Ricerca semantica nel codebase
4. **Assist**: Richiedi fix, refactor o code review
5. **Plan**: Genera issue e task automaticamente
6. **Plugins**: Gestisci plugin installati
7. **Settings**: Configurazione e preferenze

### Via CLI (Coming Soon)

```bash
# Analizza repository locale
madcp analyze ./my-project

# Ricerca semantica
madcp search "authentication middleware"

# Genera fix
madcp fix --file src/auth.py --issue "SQL injection vulnerability"
```

---

## 📚 API Reference

### Endpoints Principali

#### Analysis API

| Endpoint | Method | Descrizione |
|----------|--------|-------------|
| `/api/v1/analysis/repository` | POST | Avvia analisi di un repository |
| `/api/v1/analysis/{id}` | GET | Ottieni risultati analisi |
| `/api/v1/analysis/{id}/metrics` | GET | Metriche del codice |
| `/api/v1/analysis/{id}/dependencies` | GET | Grafo dipendenze |

#### Search API

| Endpoint | Method | Descrizione |
|----------|--------|-------------|
| `/api/v1/search/semantic` | POST | Ricerca semantica |
| `/api/v1/search/code` | POST | Ricerca per pattern di codice |
| `/api/v1/search/files` | POST | Ricerca file |

#### Assist API

| Endpoint | Method | Descrizione |
|----------|--------|-------------|
| `/api/v1/assist/fix` | POST | Suggerisci fix per bug |
| `/api/v1/assist/refactor` | POST | Suggerisci refactoring |
| `/api/v1/assist/review` | POST | Code review automatica |
| `/api/v1/assist/diff` | POST | Genera diff/patch |

#### Planning API

| Endpoint | Method | Descrizione |
|----------|--------|-------------|
| `/api/v1/planning/analyze` | POST | Analisi progetto per planning |
| `/api/v1/planning/issues` | POST | Genera issue automatiche |
| `/api/v1/planning/tasks` | POST | Breakdown task complessi |

Documentazione API completa: [API Reference](docs/api-reference.md)

OpenAPI/Swagger UI: `http://localhost:8000/docs`

---

## 🔌 Plugin System

### Struttura Plugin

```python
# plugins/python/my_plugin.py

from madcp.plugin import Plugin, PluginMetadata

class MyPlugin(Plugin):
    metadata = PluginMetadata(
        name="my-plugin",
        version="1.0.0",
        description="Plugin example",
        author="Your Name",
        dependencies=["tree-sitter-python"]
    )

    def on_load(self):
        """Chiamato quando il plugin viene caricato"""
        self.logger.info("Plugin loaded")

    def analyze_code(self, code: str, language: str):
        """Analisi custom del codice"""
        # Your logic here
        return {"analysis": "result"}

    def on_unload(self):
        """Cleanup quando plugin viene scaricato"""
        pass
```

### Plugin Disponibili

Vedi [Plugin Directory](plugins/README.md) per lista completa.

---

## 🚢 Deployment

### Docker Compose (Development)

```bash
docker-compose up -d
```

### Docker Compose (Production)

```bash
docker-compose -f docker-compose.prod.yml up -d
```

### Kubernetes + Helm

```bash
helm install madcp ./infrastructure/helm/madcp \
  --namespace madcp \
  --values values-production.yaml
```

### Cloud Providers

- **AWS**: [AWS Deployment Guide](docs/deployment-aws.md)
- **GCP**: [GCP Deployment Guide](docs/deployment-gcp.md)
- **Azure**: [Azure Deployment Guide](docs/deployment-azure.md)

---

## 🛠️ Sviluppo

### Setup Ambiente di Sviluppo

```bash
# 1. Clone repository
git clone https://github.com/yayoboy/MadCP.git
cd MadCP

# 2. Setup pre-commit hooks
pip install pre-commit
pre-commit install

# 3. Avvia ambiente dev
docker-compose -f docker-compose.dev.yml up -d

# 4. Installa dipendenze
cd services/core-api
pip install -r requirements-dev.txt

# 5. Run tests
pytest
```

### Struttura del Codice

```
services/core-api/
├── app/
│   ├── __init__.py
│   ├── main.py              # Entry point FastAPI
│   ├── config.py            # Configurazione
│   ├── api/                 # Endpoints API
│   │   ├── v1/
│   │   │   ├── analysis.py
│   │   │   ├── search.py
│   │   │   ├── assist.py
│   │   │   └── planning.py
│   ├── core/                # Business logic
│   ├── models/              # Database models
│   ├── schemas/             # Pydantic schemas
│   ├── services/            # Service layer
│   ├── utils/               # Utilities
│   └── db/                  # Database utilities
├── tests/
├── alembic/                 # DB migrations
├── requirements.txt
└── Dockerfile
```

### Code Style

- **Python**: Black, isort, flake8, mypy
- **JavaScript**: ESLint, Prettier
- **Commit**: Conventional Commits

```bash
# Format code
black .
isort .

# Lint
flake8 .
mypy .

# Test
pytest --cov
```

---

## 🧪 Testing

### Unit Tests

```bash
# Python
pytest tests/unit

# JavaScript
npm run test:unit
```

### Integration Tests

```bash
pytest tests/integration
```

### E2E Tests

```bash
pytest tests/e2e
```

### Performance Tests

```bash
locust -f tests/performance/locustfile.py
```

### Coverage

```bash
pytest --cov --cov-report=html
```

---

## 📖 Documentazione

- [Architecture](docs/architecture.md) - Architettura dettagliata
- [API Reference](docs/api-reference.md) - Documentazione API completa
- [Plugin Development](docs/plugin-development.md) - Guida sviluppo plugin
- [Deployment](docs/deployment.md) - Guide deployment
- [Configuration](docs/configuration.md) - Riferimento configurazione
- [Troubleshooting](docs/troubleshooting.md) - Risoluzione problemi
- [Security](docs/security.md) - Best practices sicurezza
- [Performance](docs/performance.md) - Ottimizzazione performance

---

## 🤝 Contributing

Contributi benvenuti! Vedi [CONTRIBUTING.md](CONTRIBUTING.md) per linee guida.

### Process

1. Fork del repository
2. Crea feature branch (`git checkout -b feature/amazing-feature`)
3. Commit delle modifiche (`git commit -m 'Add amazing feature'`)
4. Push al branch (`git push origin feature/amazing-feature`)
5. Apri una Pull Request

### Code of Conduct

Vedi [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).

---

## 🗺️ Roadmap

### v1.0.0 (Q2 2024) - Foundation ✅
- [x] Core API architecture
- [x] Code analysis service
- [x] Embedding service
- [x] Basic Web UI
- [x] Docker support

### v1.1.0 (Q3 2024) - Enhancement
- [ ] Advanced plugin system
- [ ] GitHub/GitLab integration
- [ ] Advanced planning features
- [ ] Performance optimization
- [ ] Comprehensive documentation

### v1.2.0 (Q4 2024) - Production Ready
- [ ] Kubernetes support
- [ ] Multi-tenancy
- [ ] Advanced security features
- [ ] Analytics dashboard
- [ ] CLI tool

### v2.0.0 (Q1 2025) - Enterprise
- [ ] Enterprise features
- [ ] SaaS offering
- [ ] Advanced AI models
- [ ] Custom model training
- [ ] Enterprise support

---

## 📄 License

Questo progetto è rilasciato sotto licenza **MIT**. Vedi [LICENSE](LICENSE) per dettagli.

---

## 👥 Team

- **Lead Developer**: [@yayoboy](https://github.com/yayoboy)

---

## 🙏 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) - Framework web moderno
- [LangChain](https://langchain.com/) - Framework LLM
- [Tree-sitter](https://tree-sitter.github.io/) - Parser multi-linguaggio
- [Qdrant](https://qdrant.tech/) - Vector database

---

## 📞 Supporto

- **Issues**: [GitHub Issues](https://github.com/yayoboy/MadCP/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yayoboy/MadCP/discussions)
- **Email**: support@madcp.dev

---

<div align="center">

**Made with ❤️ by the MadCP Team**

[⬆ Torna all'inizio](#madcp---modern-ai-driven-code-platform)

</div>
