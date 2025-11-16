# MadCP - Deployment con Portainer

Guida completa per il deployment di MadCP tramite Portainer.

## Indice

- [Prerequisiti](#prerequisiti)
- [Metodo 1: Deploy Rapido (Web Editor)](#metodo-1-deploy-rapido-web-editor)
- [Metodo 2: Deploy da Git Repository](#metodo-2-deploy-da-git-repository)
- [Metodo 3: Deploy da Template](#metodo-3-deploy-da-template)
- [Configurazione Variabili](#configurazione-variabili)
- [Gestione Stack](#gestione-stack)
- [Monitoring e Logs](#monitoring-e-logs)
- [Troubleshooting](#troubleshooting)
- [Aggiornamenti](#aggiornamenti)

---

## Prerequisiti

### Server Requirements

- **Docker**: 20.10+
- **Portainer**: 2.0+ (Community o Business Edition)
- **RAM**: Minimo 4GB disponibili
- **Disk**: Minimo 20GB liberi
- **CPU**: 2+ cores raccomandati

### Accesso Portainer

Assicurati di avere:
- ✅ Accesso all'interfaccia web Portainer (es. `http://your-server:9000`)
- ✅ Permessi di amministratore o di creare stack
- ✅ Endpoint Docker configurato e attivo

---

## Metodo 1: Deploy Rapido (Web Editor)

**Ideale per**: Test rapidi, deployment semplici, ambienti di sviluppo

### Passo 1: Accedi a Portainer

1. Apri il browser e vai a `http://your-server:9000`
2. Login con le tue credenziali
3. Seleziona il tuo Docker endpoint (es. "local")

### Passo 2: Crea un Nuovo Stack

1. Nel menu laterale, vai su **Stacks**
2. Clicca su **"+ Add stack"**
3. Inserisci nome stack: `madcp`

### Passo 3: Inserisci la Configurazione

1. Seleziona **"Web editor"**
2. Copia e incolla il contenuto di `portainer-stack.yml` nell'editor

   **Oppure** copia direttamente:

```yaml
version: '3.8'

networks:
  madcp:
    driver: bridge
    name: madcp-network

volumes:
  postgres_data:
  redis_data:
  qdrant_data:
  app_data:
  prometheus_data:
  grafana_data:

services:
  postgres:
    image: postgres:15-alpine
    container_name: madcp-postgres
    restart: unless-stopped
    environment:
      POSTGRES_DB: ${POSTGRES_DB:-madcp}
      POSTGRES_USER: ${POSTGRES_USER:-madcp}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    networks:
      - madcp
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U madcp"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    container_name: madcp-redis
    restart: unless-stopped
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"
    networks:
      - madcp
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 5

  qdrant:
    image: qdrant/qdrant:latest
    container_name: madcp-qdrant
    restart: unless-stopped
    volumes:
      - qdrant_data:/qdrant/storage
    ports:
      - "6333:6333"
    networks:
      - madcp
    healthcheck:
      test: ["CMD", "wget", "--spider", "http://localhost:6333/"]
      interval: 10s
      timeout: 5s
      retries: 5

  core-api:
    image: ghcr.io/yayoboy/madcp/core-api:latest
    container_name: madcp-core-api
    restart: unless-stopped
    environment:
      DATABASE_URL: postgresql://${POSTGRES_USER:-madcp}:${POSTGRES_PASSWORD}@postgres:5432/${POSTGRES_DB:-madcp}
      REDIS_URL: redis://redis:6379/0
      QDRANT_URL: http://qdrant:6333
      OPENAI_API_KEY: ${OPENAI_API_KEY}
      JWT_SECRET_KEY: ${JWT_SECRET_KEY}
      DEBUG: "false"
    volumes:
      - app_data:/app/data
    ports:
      - "8000:8000"
    networks:
      - madcp
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
      qdrant:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

### Passo 4: Configura le Variabili d'Ambiente

Scorri in basso fino a **"Environment variables"** e clicca su **"+ Add environment variable"**

**Variabili OBBLIGATORIE:**

| Nome | Valore | Descrizione |
|------|--------|-------------|
| `POSTGRES_PASSWORD` | `tua-password-sicura` | Password PostgreSQL |
| `JWT_SECRET_KEY` | `genera-chiave-32-chars` | Chiave JWT (min 32 caratteri) |
| `OPENAI_API_KEY` | `sk-...` | API Key OpenAI (opzionale ma raccomandato) |

**Variabili OPZIONALI:**

| Nome | Valore Default | Descrizione |
|------|----------------|-------------|
| `POSTGRES_DB` | `madcp` | Nome database |
| `POSTGRES_USER` | `madcp` | User database |
| `ANTHROPIC_API_KEY` | - | API Key Anthropic Claude |
| `DEBUG` | `false` | Modalità debug |
| `LOG_LEVEL` | `INFO` | Livello logging |

**💡 Suggerimento**: Usa il pulsante **"Advanced mode"** per incollare tutte le variabili in formato `KEY=VALUE`:

```env
POSTGRES_PASSWORD=MiaSuperPassword123!
JWT_SECRET_KEY=una-chiave-molto-lunga-e-sicura-almeno-32-caratteri
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxx
POSTGRES_DB=madcp
POSTGRES_USER=madcp
```

### Passo 5: Deploy dello Stack

1. Scorri in fondo alla pagina
2. Clicca su **"Deploy the stack"**
3. Attendi che Portainer scarichi le immagini e avvii i container

### Passo 6: Verifica il Deployment

1. Vai su **Stacks** → **madcp**
2. Verifica che tutti i servizi siano **running** (icona verde)
3. Controlla i logs cliccando su ogni container
4. Testa l'API visitando: `http://your-server:8000/docs`

---

## Metodo 2: Deploy da Git Repository

**Ideale per**: Deployment ripetibili, versioning, team collaboration

### Passo 1: Prepara il Repository

Se il repository è privato, configura le credenziali Git in Portainer:

1. Vai su **Settings** → **Registries**
2. Aggiungi le tue credenziali Git

### Passo 2: Crea Stack da Repository

1. Vai su **Stacks** → **"+ Add stack"**
2. Nome: `madcp`
3. Seleziona **"Repository"** come build method

### Passo 3: Configura Repository

Compila i seguenti campi:

- **Repository URL**: `https://github.com/yayoboy/MadCP`
- **Repository reference**: `main` (o il tuo branch)
- **Compose path**: `portainer-stack.yml`
- **Authentication**: Se necessario, seleziona le credenziali

### Passo 4: Auto-aggiornamento (Opzionale)

Abilita auto-update per aggiornamenti automatici:

1. Attiva **"Enable GitOps updates"**
2. Imposta intervallo: `5 minutes` (o altro)
3. Il webhook sarà generato automaticamente

### Passo 5: Configura Variabili

Aggiungi le variabili d'ambiente come nel Metodo 1, Passo 4

### Passo 6: Deploy

Clicca **"Deploy the stack"**

---

## Metodo 3: Deploy da Template

**Ideale per**: Deployment ricorrenti, multiple istanze, onboarding veloce

### Passo 1: Importa il Template

1. Scarica `portainer-template.json` dal repository
2. In Portainer, vai su **Settings** → **App Templates**
3. Clicca su **"Upload"** e seleziona il file JSON

### Passo 2: Deploy da Template

1. Vai su **App Templates**
2. Trova **"MadCP"** nei template
3. Clicca su **"Deploy the stack"**
4. Compila i parametri richiesti
5. Clicca **"Deploy"**

---

## Configurazione Variabili

### Generazione JWT Secret

Genera una chiave sicura per JWT:

**Linux/Mac:**
```bash
openssl rand -hex 32
```

**Windows (PowerShell):**
```powershell
-join ((48..57) + (65..90) + (97..122) | Get-Random -Count 32 | % {[char]$_})
```

**Online:**
- Vai su https://randomkeygen.com/
- Usa "Fort Knox Passwords" (256-bit)

### API Keys

**OpenAI:**
1. Vai su https://platform.openai.com/api-keys
2. Crea una nuova API key
3. Copia e conserva (verrà mostrata una sola volta)

**Anthropic Claude:**
1. Vai su https://console.anthropic.com/
2. Settings → API Keys
3. Crea nuova key

### Variabili Avanzate

Per configurazioni avanzate, aggiungi queste variabili:

```env
# Performance
DB_POOL_SIZE=10
REDIS_MAX_MEMORY=512mb
MAX_CONCURRENT_REQUESTS=100

# Features
FEATURE_SEMANTIC_SEARCH=true
FEATURE_CODE_ANALYSIS=true
FEATURE_AI_ASSISTANCE=true
FEATURE_PLANNING=true
PLUGINS_ENABLED=true

# Monitoring
PROMETHEUS_ENABLED=true
SENTRY_ENABLED=false
LOG_FORMAT=json

# Security
CORS_ORIGINS=http://localhost:3000,https://your-domain.com
ALLOWED_HOSTS=localhost,your-domain.com
```

---

## Gestione Stack

### Avviare/Fermare lo Stack

1. Vai su **Stacks** → **madcp**
2. Usa i pulsanti:
   - **Stop** - Ferma tutti i container
   - **Start** - Avvia tutti i container
   - **Restart** - Riavvia tutti i container

### Aggiornare le Variabili d'Ambiente

1. Vai su **Stacks** → **madcp**
2. Clicca su **"Editor"** tab
3. Modifica le variabili nella sezione "Environment variables"
4. Clicca **"Update the stack"**
5. Seleziona **"Re-pull images and redeploy"** se hai modificato immagini
6. Clicca **"Update"**

### Scalare i Servizi

Per scalare il Core API (multiple istanze):

1. Vai su **Containers**
2. Seleziona `madcp-core-api`
3. Clicca **"Duplicate/Edit"**
4. Modifica il nome: `madcp-core-api-2`
5. **IMPORTANTE**: Modifica la porta: `8001:8000`
6. Deploy

Poi aggiungi un load balancer (nginx, traefik) davanti.

---

## Monitoring e Logs

### Visualizzare i Logs

**Da Portainer UI:**

1. Vai su **Containers**
2. Clicca sul container desiderato
3. Clicca su **"Logs"** tab
4. Usa i filtri:
   - **Lines**: Numero righe da mostrare
   - **Auto-refresh**: Aggiornamento automatico
   - **Timestamps**: Mostra timestamp

**Logs Specifici:**

- **Core API**: Container `madcp-core-api`
- **Database**: Container `madcp-postgres`
- **Redis**: Container `madcp-redis`
- **Qdrant**: Container `madcp-qdrant`

### Health Checks

Verifica lo stato di salute:

1. Vai su **Containers**
2. Controlla la colonna **"Health"**:
   - 🟢 **healthy** - Tutto OK
   - 🟡 **starting** - In avvio
   - 🔴 **unhealthy** - Problemi

### Prometheus & Grafana (Opzionale)

Se hai abilitato il profilo `monitoring`:

1. **Prometheus**: `http://your-server:9090`
2. **Grafana**: `http://your-server:3001`
   - Username: `admin`
   - Password: Valore di `GRAFANA_ADMIN_PASSWORD`

---

## Troubleshooting

### Container in Stato "Unhealthy"

**Problema**: Container `madcp-core-api` è unhealthy

**Soluzione**:
1. Controlla i logs: Vai su Containers → madcp-core-api → Logs
2. Verifica connessioni database:
   ```bash
   # Esegui shell nel container
   docker exec -it madcp-core-api sh

   # Testa connessione PostgreSQL
   curl http://localhost:8000/health/detailed
   ```
3. Verifica variabili d'ambiente in Stack → Editor

**Problema**: Database connection error

**Soluzione**:
1. Verifica che `POSTGRES_PASSWORD` sia impostata correttamente
2. Controlla che il container PostgreSQL sia healthy
3. Verifica la `DATABASE_URL`:
   ```
   postgresql://madcp:PASSWORD@postgres:5432/madcp
   ```

### Stack Non Si Avvia

**Problema**: Errore durante il deploy

**Soluzioni comuni**:

1. **Porta già in uso**:
   - Modifica le porte in `portainer-stack.yml`
   - Es: Cambia `"8000:8000"` in `"8080:8000"`

2. **Variabili mancanti**:
   - Controlla errori nel log di deploy
   - Assicurati che tutte le variabili obbligatorie siano impostate

3. **Immagini non disponibili**:
   - Se usi build locale, assicurati che il Dockerfile sia presente
   - Altrimenti usa un'immagine pre-built

### Performance Issues

**Problema**: API lenta o timeout

**Soluzioni**:

1. **Aumenta risorse container**:
   - Vai su Containers → madcp-core-api → "Duplicate/Edit"
   - Sezione "Resources"
   - Aumenta Memory limit e CPU

2. **Ottimizza database**:
   ```env
   DB_POOL_SIZE=20
   DB_MAX_OVERFLOW=40
   ```

3. **Aumenta Redis memory**:
   ```env
   REDIS_MAX_MEMORY=1gb
   ```

### Backup e Restore

**Backup Volumi**:

```bash
# Backup PostgreSQL
docker exec madcp-postgres pg_dump -U madcp madcp > backup.sql

# Backup volume (alternativo)
docker run --rm \
  -v madcp_postgres_data:/data \
  -v $(pwd):/backup \
  alpine tar czf /backup/postgres-backup.tar.gz /data
```

**Restore**:

```bash
# Restore PostgreSQL
docker exec -i madcp-postgres psql -U madcp madcp < backup.sql

# Restore volume
docker run --rm \
  -v madcp_postgres_data:/data \
  -v $(pwd):/backup \
  alpine tar xzf /backup/postgres-backup.tar.gz -C /
```

---

## Aggiornamenti

### Aggiornare lo Stack

**Metodo 1: UI Portainer**

1. Vai su **Stacks** → **madcp**
2. Clicca **"Editor"** tab
3. Clicca **"Update the stack"**
4. Seleziona **"Re-pull images and redeploy"**
5. Clicca **"Update"**

**Metodo 2: Git Auto-Update**

Se hai configurato GitOps:
1. Portainer rileverà automaticamente i cambiamenti
2. Oppure trigger manuale: Stacks → madcp → "Pull and redeploy"

### Aggiornare una Singola Immagine

1. Vai su **Images**
2. Trova l'immagine (es: `madcp/core-api`)
3. Clicca **"Pull"** per scaricare l'ultima versione
4. Vai su **Containers** → `madcp-core-api`
5. Clicca **"Recreate"**

### Rolling Update (Zero Downtime)

Per aggiornamenti senza downtime:

1. **Scala a 2 istanze** del core-api
2. **Aggiorna la prima** istanza
3. **Attendi che sia healthy**
4. **Aggiorna la seconda** istanza
5. **Rimuovi istanze extra** se necessario

---

## Best Practices Portainer

### 1. Organizzazione

- **Usa Tag**: Aggiungi tag agli stack per categorizzarli
  - Tags: `production`, `madcp`, `ai`

- **Nomenclatura**: Usa nomi consistenti
  - Stack: `madcp-prod`, `madcp-dev`
  - Containers: Prefix con ambiente

### 2. Sicurezza

- **Access Control**: Limita accesso agli stack:
  - Vai su Stack → madcp → "Access control"
  - Assegna a team/user specifici

- **Secrets**: Usa Docker Secrets per dati sensibili:
  ```yaml
  secrets:
    jwt_secret:
      external: true

  services:
    core-api:
      secrets:
        - jwt_secret
  ```

### 3. Monitoring

- **Webhooks**: Configura webhook per notifiche:
  - Stack → madcp → Webhooks
  - Integra con Slack, Discord, etc.

- **Regular Health Checks**: Configura alerting
  - Usa Portainer Business per alerting avanzato

### 4. Backup

- **Backup Automatici**: Configura backup scheduled
- **Snapshot Volumes**: Prima di aggiornamenti importanti
- **Export Stack**: Salva la configurazione stack
  - Stack → madcp → "Export"

---

## Deployment in Produzione

### Checklist Pre-Produzione

- [ ] Password sicure per tutti i servizi
- [ ] JWT_SECRET_KEY generato e sicuro (32+ caratteri)
- [ ] API Keys configurate (OpenAI, Anthropic)
- [ ] DEBUG=false
- [ ] LOG_LEVEL=WARNING o ERROR
- [ ] CORS_ORIGINS configurato per il tuo dominio
- [ ] SSL/TLS configurato (Traefik, Nginx)
- [ ] Backup automatici configurati
- [ ] Monitoring abilitato (Prometheus + Grafana)
- [ ] Limiti risorse impostati sui container
- [ ] Health checks funzionanti

### Configurazione SSL/TLS

**Con Traefik** (raccomandato):

```yaml
services:
  traefik:
    image: traefik:v2.10
    command:
      - "--providers.docker=true"
      - "--entrypoints.web.address=:80"
      - "--entrypoints.websecure.address=:443"
      - "--certificatesresolvers.letsencrypt.acme.email=your@email.com"
      - "--certificatesresolvers.letsencrypt.acme.storage=/letsencrypt/acme.json"
      - "--certificatesresolvers.letsencrypt.acme.httpchallenge.entrypoint=web"
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
      - traefik-letsencrypt:/letsencrypt
    networks:
      - madcp

  core-api:
    labels:
      - "traefik.http.routers.madcp-api.rule=Host(`api.yourdomain.com`)"
      - "traefik.http.routers.madcp-api.entrypoints=websecure"
      - "traefik.http.routers.madcp-api.tls.certresolver=letsencrypt"
```

### Risorse Raccomandate

**Produzione (carico medio)**:

| Servizio | CPU | RAM | Storage |
|----------|-----|-----|---------|
| Core API | 1 core | 2GB | - |
| PostgreSQL | 1 core | 2GB | 20GB |
| Redis | 0.5 core | 512MB | 5GB |
| Qdrant | 1 core | 2GB | 50GB |
| **Totale** | **3.5 cores** | **6.5GB** | **75GB** |

**Produzione (carico alto)**:

| Servizio | CPU | RAM | Storage |
|----------|-----|-----|---------|
| Core API (x2) | 2 cores | 4GB | - |
| PostgreSQL | 2 cores | 4GB | 100GB |
| Redis | 1 core | 1GB | 10GB |
| Qdrant | 2 cores | 4GB | 200GB |
| **Totale** | **7 cores** | **13GB** | **310GB** |

---

## Link Utili

- **Portainer Documentation**: https://docs.portainer.io/
- **MadCP Repository**: https://github.com/yayoboy/MadCP
- **MadCP Documentation**: https://github.com/yayoboy/MadCP/tree/main/docs
- **Docker Compose Reference**: https://docs.docker.com/compose/

---

## Supporto

Per problemi o domande:

1. **Controlla i logs** in Portainer
2. **Consulta il troubleshooting** in questa guida
3. **Apri una issue**: https://github.com/yayoboy/MadCP/issues
4. **Documentazione completa**: [README.md](../README.md)

---

**Happy Deploying! 🚀**
