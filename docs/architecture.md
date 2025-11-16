# MadCP - Architettura del Sistema

## Indice

- [Panoramica](#panoramica)
- [Architettura a Microservizi](#architettura-a-microservizi)
- [Componenti Principali](#componenti-principali)
- [Flussi di Dati](#flussi-di-dati)
- [Database Design](#database-design)
- [Sicurezza](#sicurezza)
- [Scalabilità](#scalabilità)
- [Osservabilità](#osservabilità)

---

## Panoramica

MadCP utilizza un'architettura a **microservizi** modulare progettata per garantire:

- **Scalabilità orizzontale**: Ogni servizio può essere scalato indipendentemente
- **Resilienza**: Fallimenti isolati non compromettono l'intero sistema
- **Manutenibilità**: Componenti separati facilitano aggiornamenti e debugging
- **Flessibilità**: Facile aggiunta di nuovi servizi e funzionalità

### Principi Architetturali

1. **Separation of Concerns**: Ogni servizio ha una responsabilità specifica
2. **API-First**: Tutti i servizi comunicano tramite API ben definite
3. **Event-Driven**: Comunicazione asincrona tramite message queue dove appropriato
4. **Stateless Services**: I servizi non mantengono stato, facilitando la scalabilità
5. **Database per Service**: Ogni servizio gestisce i propri dati (quando necessario)

---

## Architettura a Microservizi

```
┌─────────────────────────────────────────────────────────────────┐
│                        Load Balancer / CDN                       │
└────────────────────────────┬────────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────┐
│                     API Gateway (Nginx)                          │
│                                                                  │
│  • Reverse Proxy                                                 │
│  • Load Balancing                                                │
│  • Rate Limiting                                                 │
│  • SSL/TLS Termination                                           │
│  • Request Routing                                               │
└──────────┬───────────────────────────────────┬───────────────────┘
           │                                   │
    ┌──────▼──────┐                    ┌──────▼──────────┐
    │  Auth       │                    │   Web UI        │
    │  Service    │                    │  (Next.js)      │
    │ (Keycloak)  │                    │                 │
    └──────┬──────┘                    └─────────────────┘
           │
    ┌──────▼──────────────────────────────────────────────┐
    │              Core API (FastAPI)                     │
    │                                                      │
    │  • Request Orchestration                             │
    │  • Business Logic Coordination                       │
    │  • Authentication/Authorization                      │
    │  • API Versioning                                    │
    └──────┬──────────────────────────────────────────────┘
           │
    ┌──────┴────────────────────────────┬─────────────────┐
    │                                   │                 │
┌───▼──────────┐  ┌────────────┐  ┌────▼─────────┐  ┌───▼─────────┐
│ Code         │  │ Embedding  │  │  Planning    │  │   Plugin    │
│ Analysis     │  │  Service   │  │  Service     │  │   Manager   │
│              │  │            │  │              │  │             │
│ • Parsing    │  │ • Vector   │  │ • Analysis   │  │ • Loading   │
│ • AST        │  │ • Semantic │  │ • Issues     │  │ • Sandbox   │
│ • Metrics    │  │ • Search   │  │ • Tasks      │  │ • Registry  │
└───┬──────────┘  └─────┬──────┘  └──────┬───────┘  └─────┬───────┘
    │                   │                 │                │
┌───▼───────────────────▼─────────────────▼────────────────▼───────┐
│                        Data Layer                                 │
│                                                                   │
│  ┌──────────┐  ┌─────────┐  ┌────────┐  ┌────────────────┐      │
│  │PostgreSQL│  │ Qdrant  │  │ Redis  │  │ S3 / MinIO     │      │
│  │          │  │         │  │        │  │                │      │
│  │• Metadata│  │• Vectors│  │• Cache │  │• File Storage  │      │
│  │• Users   │  │• Search │  │• Queue │  │• Repositories  │      │
│  └──────────┘  └─────────┘  └────────┘  └────────────────┘      │
└───────────────────────────────────────────────────────────────────┘
```

---

## Componenti Principali

### 1. API Gateway (Nginx)

**Responsabilità:**
- Reverse proxy per tutti i servizi
- Load balancing tra istanze
- Rate limiting e protezione DDoS
- SSL/TLS termination
- Request routing basato su path

**Configurazione:**
```nginx
location /api/ {
    proxy_pass http://core-api:8000/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
}
```

### 2. Core API (FastAPI)

**Responsabilità:**
- Orchestrazione delle richieste
- Coordinamento tra servizi
- Autenticazione e autorizzazione
- API versioning
- Validazione input/output
- Error handling centralizzato

**Tecnologie:**
- **FastAPI**: Framework web moderno e veloce
- **Pydantic**: Validazione e serializzazione dati
- **SQLAlchemy**: ORM per database
- **Alembic**: Gestione migrazioni

**Struttura:**
```
services/core-api/
├── app/
│   ├── api/v1/          # Endpoints API versione 1
│   ├── core/            # Business logic
│   ├── models/          # Database models
│   ├── schemas/         # Pydantic schemas
│   ├── services/        # Service layer
│   └── utils/           # Utilities
└── tests/
```

### 3. Code Analysis Service

**Responsabilità:**
- Parsing del codice sorgente
- Generazione AST (Abstract Syntax Tree)
- Calcolo metriche (complessità, LOC, etc.)
- Analisi dipendenze
- Pattern detection

**Tecnologie:**
- **Tree-sitter**: Parser multi-linguaggio
- **Radon**: Metriche di complessità
- **Lizard**: Analisi complessità
- **Astroid**: AST Python avanzato

**Linguaggi Supportati:**
- Python
- JavaScript / TypeScript
- Go
- Java
- Rust
- C / C++

**Workflow:**
```
1. Repository Clone
   ↓
2. File Detection & Filtering
   ↓
3. Language Detection
   ↓
4. Parallel Parsing (Tree-sitter)
   ↓
5. AST Generation
   ↓
6. Metrics Calculation
   ↓
7. Dependency Graph Building
   ↓
8. Results Storage (PostgreSQL + Cache)
```

### 4. Embedding Service

**Responsabilità:**
- Generazione embeddings del codice
- Chunking intelligente del codice
- Indicizzazione nel vector database
- Ricerca semantica
- Similarity search

**Tecnologie:**
- **OpenAI Embeddings**: text-embedding-3-small
- **Sentence Transformers**: Modelli locali
- **Qdrant**: Vector database
- **LangChain**: Orchestrazione RAG

**Processo di Embedding:**
```python
# Pseudo-codice
def generate_embeddings(code_file):
    # 1. Chunking intelligente
    chunks = smart_chunk_code(
        code=code_file.content,
        max_tokens=512,
        overlap=50,
        respect_syntax=True  # Non spezza funzioni/classi
    )

    # 2. Generazione embeddings
    embeddings = []
    for chunk in chunks:
        embedding = embedding_model.embed(chunk)
        embeddings.append({
            'content': chunk,
            'vector': embedding,
            'metadata': {
                'file': code_file.path,
                'language': code_file.language,
                'start_line': chunk.start_line,
                'end_line': chunk.end_line
            }
        })

    # 3. Indicizzazione in Qdrant
    vector_db.upsert(
        collection='madcp_embeddings',
        points=embeddings
    )
```

### 5. Planning Service

**Responsabilità:**
- Analisi del progetto per planning
- Generazione automatica di issue
- Breakdown di task complessi
- Stima effort
- Prioritizzazione

**Workflow:**
```
Repository → Analysis → Pattern Detection → LLM Processing → Issues/Tasks
```

**Features:**
- Estrazione TODO/FIXME
- Identificazione code smells
- Suggerimenti miglioramenti
- Generazione descrizioni issue
- Stima complessità

### 6. Plugin Manager

**Responsabilità:**
- Caricamento dinamico plugin
- Sandboxing per sicurezza
- Gestione lifecycle plugin
- Plugin discovery
- API Plugin

**Architettura Plugin:**
```python
class PluginBase:
    metadata: PluginMetadata

    def on_load(self):
        """Inizializzazione plugin"""
        pass

    def on_unload(self):
        """Cleanup plugin"""
        pass

    # Hook per estendere funzionalità
    def analyze_code(self, code, language):
        pass

    def post_analysis(self, results):
        pass
```

---

## Flussi di Dati

### 1. Analisi Repository

```
┌─────────────┐
│   Client    │
└──────┬──────┘
       │ POST /api/v1/analysis/repository
       ▼
┌─────────────────┐
│   Core API      │
│  - Validazione  │
│  - Job creation │
└──────┬──────────┘
       │ Enqueue job
       ▼
┌─────────────────┐
│  Task Queue     │
│  (Celery/Redis) │
└──────┬──────────┘
       │ Process job
       ▼
┌─────────────────┐
│ Code Analysis   │
│  - Clone repo   │
│  - Parse files  │
│  - Calc metrics │
└──────┬──────────┘
       │ Store AST & metrics
       ▼
┌─────────────────┐
│  PostgreSQL     │
└─────────────────┘
       │
       │ Generate embeddings
       ▼
┌─────────────────┐
│ Embedding Svc   │
│  - Chunk code   │
│  - Gen vectors  │
└──────┬──────────┘
       │ Store vectors
       ▼
┌─────────────────┐
│    Qdrant       │
└─────────────────┘
```

### 2. Ricerca Semantica

```
┌─────────────┐
│   Client    │
└──────┬──────┘
       │ POST /api/v1/search/semantic
       │ { query: "auth middleware" }
       ▼
┌─────────────────┐
│   Core API      │
│  - Validazione  │
└──────┬──────────┘
       │ Forwartoa Embedding Service
       ▼
┌─────────────────┐
│ Embedding Svc   │
│  - Gen query    │
│    embedding    │
└──────┬──────────┘
       │ Search similar vectors
       ▼
┌─────────────────┐
│    Qdrant       │
│  - Similarity   │
│    search       │
│  - Top K        │
└──────┬──────────┘
       │ Retrieve metadata
       ▼
┌─────────────────┐
│  PostgreSQL     │
│  - File info    │
│  - Context      │
└──────┬──────────┘
       │ Return results
       ▼
┌─────────────────┐
│   Client        │
│  - Ranked       │
│    results      │
└─────────────────┘
```

### 3. AI Assistance (Fix Generation)

```
Client Request
    ↓
Core API (validation)
    ↓
Semantic Search (context retrieval)
    ↓
LLM Service
    ├─→ Context injection
    ├─→ Prompt engineering
    └─→ Fix generation
    ↓
Response formatting
    ↓
Return to client
```

---

## Database Design

### PostgreSQL Schema

```sql
-- Repositories
repositories
├── id (UUID, PK)
├── name
├── url
├── branch
├── status
└── timestamps

-- Analysis Results
analysis_results
├── id (UUID, PK)
├── repository_id (FK)
├── status
├── metrics (JSONB)
├── dependencies (JSONB)
└── timestamps

-- Code Files
code_files
├── id (UUID, PK)
├── repository_id (FK)
├── file_path
├── language
├── content
├── content_hash
└── timestamps

-- Embeddings
embeddings
├── id (UUID, PK)
├── file_id (FK)
├── chunk_index
├── content
├── vector_id (ref to Qdrant)
└── created_at

-- Issues (Planning)
issues
├── id (UUID, PK)
├── repository_id (FK)
├── title
├── description
├── priority
├── category
├── estimated_effort
├── status
└── timestamps
```

### Vector Database (Qdrant)

```
Collection: madcp_embeddings
├── Vector Dimension: 1536
├── Distance Metric: Cosine
└── Payload:
    ├── file_path
    ├── language
    ├── content
    ├── start_line
    ├── end_line
    └── repository_id
```

---

## Sicurezza

### 1. Autenticazione

**OAuth2 / OIDC (Keycloak)**
- Single Sign-On (SSO)
- Federazione identità
- Multi-factor authentication

**JWT Tokens**
- Access token (30 min)
- Refresh token (7 giorni)
- Firma HMAC-SHA256

**API Keys**
- Per integrazioni M2M
- Rate limiting dedicato
- Scadenza configurabile

### 2. Autorizzazione

**RBAC (Role-Based Access Control)**

```yaml
Roles:
  admin:
    permissions: ["*"]

  developer:
    permissions:
      - read:*
      - write:analysis
      - write:search

  viewer:
    permissions:
      - read:*
```

### 3. Protezione Dati

- **Encryption at Rest**: Database encryption (PostgreSQL)
- **Encryption in Transit**: TLS 1.3
- **Secrets Management**: Environment variables, HashiCorp Vault
- **Input Validation**: Pydantic schemas
- **SQL Injection Prevention**: Parameterized queries (SQLAlchemy)
- **XSS Prevention**: Output escaping
- **CSRF Protection**: Token-based

### 4. Rate Limiting

```python
# Per utente
@rate_limit(limit="100/minute", key="user_id")

# Per IP
@rate_limit(limit="1000/hour", key="ip_address")

# Per endpoint
@rate_limit(limit="10/minute", key="endpoint:semantic_search")
```

---

## Scalabilità

### Scalabilità Orizzontale

**Stateless Services**
- Nessuno stato locale
- Session in Redis
- Cache distribuita

**Load Balancing**
- Round-robin
- Least connections
- Health-based routing

**Auto-scaling (Kubernetes)**
```yaml
autoscaling:
  minReplicas: 2
  maxReplicas: 10
  metrics:
    - type: cpu
      target: 70%
    - type: memory
      target: 80%
    - type: custom
      name: requests_per_second
      target: 1000
```

### Caching Strategy

**Multi-Level Caching**

```
Request
  ↓
L1: In-Memory Cache (FastAPI)
  ↓ (miss)
L2: Redis Cache
  ↓ (miss)
L3: Database Query
  ↓
Cache population (L2 → L1)
  ↓
Response
```

**Cache Invalidation**
- Time-based expiration (TTL)
- Event-based invalidation
- Manual purge API

---

## Osservabilità

### 1. Logging

**Structured Logging (JSON)**
```json
{
  "timestamp": "2024-01-01T10:00:00Z",
  "level": "INFO",
  "service": "core-api",
  "trace_id": "abc123",
  "user_id": "user-456",
  "message": "Analysis completed",
  "duration_ms": 1234
}
```

**Log Aggregation**: ELK Stack (Elasticsearch, Logstash, Kibana)

### 2. Metrics (Prometheus)

**Application Metrics**
- Request rate
- Response time (p50, p95, p99)
- Error rate
- Active users

**Business Metrics**
- Analyses completed
- Searches performed
- Token consumption
- Plugin usage

**Infrastructure Metrics**
- CPU usage
- Memory usage
- Disk I/O
- Network traffic

### 3. Tracing (OpenTelemetry)

**Distributed Tracing**
```
HTTP Request
  ├─ Core API (10ms)
  │  ├─ Auth Check (2ms)
  │  └─ Request Validation (1ms)
  │
  ├─ Code Analysis Service (500ms)
  │  ├─ Repository Clone (200ms)
  │  ├─ File Parsing (250ms)
  │  └─ Metrics Calc (50ms)
  │
  └─ Embedding Service (300ms)
     ├─ Chunking (50ms)
     ├─ Embedding Gen (200ms)
     └─ Vector Store (50ms)

Total: 810ms
```

### 4. Alerting

**Alert Rules (Prometheus Alertmanager)**
```yaml
- alert: HighErrorRate
  expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.05
  for: 5m
  annotations:
    summary: "High error rate detected"

- alert: SlowResponses
  expr: histogram_quantile(0.95, http_request_duration_seconds) > 2
  for: 5m
  annotations:
    summary: "95th percentile response time > 2s"
```

**Notification Channels**
- Email
- Slack
- PagerDuty
- Webhooks

---

## Performance Optimization

### 1. Database Optimization

- **Connection Pooling**: 10-20 connections
- **Query Optimization**: Indexes, EXPLAIN ANALYZE
- **Materialized Views**: Pre-computed aggregations
- **Partitioning**: Time-based partitioning per grandi dataset

### 2. Caching Strategy

- **Query Results**: Cache ricerche frequenti
- **Embeddings**: Cache embeddings generati
- **AST**: Cache alberi sintattici
- **Static Assets**: CDN caching

### 3. Async Processing

- **Background Jobs**: Celery per task lunghi
- **Batch Processing**: Elaborazione parallela file
- **Streaming**: Streaming results per grandi dataset

---

## Disaster Recovery

### Backup Strategy

**Database Backups**
- Daily full backup
- Hourly incremental
- Retention: 30 giorni
- Cross-region replication

**Vector Database**
- Snapshot giornalieri
- Export periodici

**Repository Data**
- S3/MinIO versioning
- Lifecycle policies

### High Availability

**Database**: PostgreSQL Replication (Primary + Standby)
**Redis**: Redis Sentinel / Cluster
**Application**: Multi-instance con load balancing

---

## Conclusioni

L'architettura di MadCP è progettata per essere:

- ✅ **Scalabile**: Crescita orizzontale facile
- ✅ **Resiliente**: Fault tolerance e recovery
- ✅ **Osservabile**: Monitoring completo
- ✅ **Sicura**: Multiple layers di sicurezza
- ✅ **Performante**: Caching e ottimizzazioni
- ✅ **Manutenibile**: Codice pulito e ben documentato

Per domande o suggerimenti, consultare la [documentazione completa](../README.md) o aprire una [issue](https://github.com/yayoboy/MadCP/issues).
