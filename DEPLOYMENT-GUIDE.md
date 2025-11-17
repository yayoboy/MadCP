# 🚀 MadCP - Guida Rapida al Deployment

**Scegli il metodo di deployment più adatto alle tue esigenze:**

---

## 📦 Opzione 1: Docker Compose (Locale/Development)

**Ideale per**: Sviluppo locale, testing, ambiente singolo server

### Requisiti

- Docker 24.0+
- Docker Compose 2.20+
- 4GB RAM minimo
- 20GB spazio disco

### Step-by-Step

#### 1. Prepara l'Ambiente

```bash
# Clone repository
git clone https://github.com/yayoboy/MadCP.git
cd MadCP

# Copia file di configurazione
cp .env.example .env
```

#### 2. Configura Variabili d'Ambiente

Modifica il file `.env`:

```bash
nano .env
```

**Configurazione minima richiesta**:

```env
# Database
POSTGRES_PASSWORD=your_secure_password_here

# Security
JWT_SECRET_KEY=generate_a_long_secure_key_min_32_chars

# LLM (opzionale ma raccomandato)
OPENAI_API_KEY=sk-your-openai-key-here
```

**Genera JWT Secret** (raccomandato):

```bash
# Linux/Mac
openssl rand -hex 32

# Windows PowerShell
-join ((48..57) + (65..90) + (97..122) | Get-Random -Count 32 | % {[char]$_})
```

#### 3. Avvia i Servizi

```bash
# Build e avvia tutti i container
docker-compose up -d

# Verifica stato
docker-compose ps

# Controlla logs
docker-compose logs -f
```

#### 4. Verifica il Deployment

Esegui lo script di verifica:

```bash
./scripts/verify.sh
```

Oppure manualmente:

```bash
# Health check
curl http://localhost:8000/health

# API documentation
open http://localhost:8000/docs  # O apri nel browser
```

**Output atteso**:

```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T10:00:00Z",
  "version": "1.0.0",
  "environment": "development"
}
```

#### 5. Inizializza il Database (Opzionale)

Se vuoi importare lo schema SQL iniziale:

```bash
# Uncommenta questa riga nel docker-compose.yml (servizio postgres):
# - ./infrastructure/docker/postgres/init.sql:/docker-entrypoint-initdb.d/init.sql:ro

# Poi ricrea il container
docker-compose down postgres
docker-compose up -d postgres
```

### Comandi Utili

```bash
# Visualizza stato container
docker-compose ps

# Segui logs di tutti i servizi
docker-compose logs -f

# Logs di un servizio specifico
docker-compose logs -f core-api

# Riavvia un servizio
docker-compose restart core-api

# Ferma tutti i servizi
docker-compose down

# Ferma e rimuovi volumi (attenzione: cancella tutti i dati!)
docker-compose down -v

# Ricostruisci immagini
docker-compose build --no-cache

# Scala un servizio
docker-compose up -d --scale core-api=2
```

### Troubleshooting

**Problema**: Container non si avvia

```bash
# Controlla logs
docker-compose logs core-api

# Verifica variabili d'ambiente
docker-compose config

# Ricostruisci immagine
docker-compose build core-api
docker-compose up -d core-api
```

**Problema**: Porta già in uso

Modifica `.env`:

```env
API_PORT=8080      # Invece di 8000
POSTGRES_PORT=5433 # Invece di 5432
```

**Problema**: Database connection error

```bash
# Verifica che PostgreSQL sia healthy
docker-compose ps postgres

# Controlla logs
docker-compose logs postgres

# Reset database
docker-compose down postgres
docker volume rm madcp_postgres_data
docker-compose up -d postgres
```

---

## 🎯 Opzione 2: Portainer (Production-Ready)

**Ideale per**: Produzione, team collaboration, gestione visuale, multi-server

### Requisiti

- Portainer CE/BE 2.19+ installato e funzionante
- Accesso a Portainer UI
- Repository GitHub accessibile dal server

### Step-by-Step

#### 1. Accedi a Portainer

1. Apri browser: `http://your-server:9000`
2. Login con le tue credenziali
3. Seleziona il tuo endpoint Docker

#### 2. Crea un Nuovo Stack

1. Menu laterale → **Stacks**
2. Click su **"+ Add stack"**
3. Nome: `madcp`

#### 3. Scegli il Metodo di Deploy

**Metodo A: Da Repository Git** (Raccomandato)

1. Build method: **Repository**
2. Repository URL: `https://github.com/yayoboy/MadCP`
3. Repository reference: `main`
4. Compose path: `portainer-stack.yml`
5. Authentication: Se repository privato, aggiungi credenziali

**Metodo B: Web Editor**

1. Build method: **Web editor**
2. Copia contenuto di `portainer-stack.yml`
3. Incolla nell'editor
4. Portainer validerà la sintassi YAML

#### 4. Configura Environment Variables

Nella sezione "Environment variables", aggiungi:

**VARIABILI OBBLIGATORIE**:

| Nome | Valore | Descrizione |
|------|--------|-------------|
| `POSTGRES_PASSWORD` | `SecurePass123!` | Password PostgreSQL (min 12 caratteri) |
| `JWT_SECRET_KEY` | `your-secret-key-32-chars-min` | Chiave JWT (min 32 caratteri) |

**VARIABILI RACCOMANDATE**:

| Nome | Valore | Descrizione |
|------|--------|-------------|
| `OPENAI_API_KEY` | `sk-xxxxx` | API Key OpenAI per funzionalità AI |
| `DEBUG` | `false` | Modalità debug (false in produzione) |
| `LOG_LEVEL` | `WARNING` | Livello logging (WARNING/ERROR in prod) |

**VARIABILI OPZIONALI**:

```env
POSTGRES_DB=madcp
POSTGRES_USER=madcp
ANTHROPIC_API_KEY=sk-ant-xxxxx
API_PORT=8000
REDIS_MAX_MEMORY=512mb
```

**💡 Tip**: Usa "Advanced mode" per incollare tutte le variabili insieme:

```env
POSTGRES_PASSWORD=SecurePass123!
JWT_SECRET_KEY=f7d9c8b6a5e4d3c2b1a0987654321fedcba0123456789abcdef
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxx
DEBUG=false
LOG_LEVEL=WARNING
```

#### 5. Deploy!

1. Scroll in fondo alla pagina
2. Click su **"Deploy the stack"**
3. Portainer inizierà il deployment (può richiedere 2-5 minuti)

#### 6. Verifica il Deployment

**In Portainer UI**:

1. Vai su **Stacks** → **madcp**
2. Verifica che lo stato sia "Running" (verde)
3. Vai su **Containers**
4. Controlla che tutti i container siano "healthy" (🟢)

**Containers attesi**:

- ✅ `madcp-postgres` - healthy
- ✅ `madcp-redis` - healthy
- ✅ `madcp-qdrant` - healthy
- ✅ `madcp-core-api` - healthy

**Controlla Logs**:

1. Click su container `madcp-core-api`
2. Tab "Logs"
3. Abilita "Auto-refresh"
4. Cerca "Application startup complete" o simili

**Testa l'API**:

Apri nel browser:

```
http://YOUR_SERVER_IP:8000/docs
```

Dovresti vedere la documentazione Swagger interattiva.

**Health Check**:

```bash
curl http://YOUR_SERVER_IP:8000/health
```

#### 7. Configurazione Post-Deployment

**Abilita Auto-Update** (Opzionale):

1. Stacks → madcp → Editor
2. Scroll in basso
3. Abilita "Enable GitOps updates"
4. Scegli metodo:
   - **Polling**: Controlla repo ogni X minuti
   - **Webhook**: Trigger manuale o da GitHub
5. Save

**Configura Backup Automatici**:

1. Vai su **Volumes**
2. Seleziona `madcp_postgres_data`
3. Click su "Backup"
4. Configura schedule automatico

### Gestione dello Stack

**Start/Stop/Restart**:

1. Stacks → madcp
2. Usa i pulsanti: **Stop** / **Start** / **Restart**

**Update Stack**:

1. Stacks → madcp → Editor
2. Modifica configurazione se necessario
3. Click **"Update the stack"**
4. Seleziona **"Re-pull images and redeploy"**
5. Click **"Update"**

**Visualizza Logs**:

1. Containers → Click su un container
2. Tab "Logs"
3. Usa filtri e auto-refresh

**Scaling** (Core API):

1. Containers → madcp-core-api
2. Click "Duplicate/Edit"
3. Modifica nome: `madcp-core-api-2`
4. Modifica porta: `8001:8000`
5. Deploy

### Troubleshooting Portainer

**Container "Unhealthy"**:

1. Controlla logs del container in Portainer
2. Verifica environment variables in Stack Editor
3. Assicurati che `POSTGRES_PASSWORD` e `JWT_SECRET_KEY` siano impostate

**Build Failed**:

1. Verifica che il repository sia accessibile
2. Controlla che Dockerfile esista in `services/core-api/`
3. Verifica connessione internet del server Portainer

**Porta già in uso**:

1. Stack → madcp → Editor
2. Aggiungi environment variable: `API_PORT=8080`
3. Update the stack

---

## 🔐 Security Checklist (Produzione)

Prima di usare in produzione:

- [ ] **Password sicure** - Usa password complesse (min 16 caratteri)
- [ ] **JWT Secret** - Genera con `openssl rand -hex 32`
- [ ] **DEBUG=false** - Disabilita debug mode
- [ ] **LOG_LEVEL** - Imposta a WARNING o ERROR
- [ ] **Firewall** - Limita accesso alle porte
- [ ] **SSL/TLS** - Configura reverse proxy (Nginx/Traefik)
- [ ] **Backup** - Configura backup automatici database
- [ ] **Monitoring** - Abilita Prometheus + Grafana
- [ ] **Updates** - Pianifica update regolari
- [ ] **Access Control** - Configura RBAC in Portainer

---

## 🆘 Supporto

**Problemi?**

1. Consulta [Troubleshooting](docs/troubleshooting.md)
2. Controlla [GitHub Issues](https://github.com/yayoboy/MadCP/issues)
3. Leggi [Deployment Portainer Completo](docs/deployment-portainer.md)

**Documentazione**:

- [README principale](README.md)
- [Architettura](docs/architecture.md)
- [API Reference](http://localhost:8000/docs) (dopo deploy)

**Scripts utili**:

```bash
./scripts/verify.sh    # Verifica deployment
./scripts/setup.sh     # Setup completo
./scripts/dev.sh       # Development mode
./scripts/clean.sh     # Cleanup
```

---

## ✅ Quick Reference

### Docker Compose

```bash
# Start
docker-compose up -d

# Stop
docker-compose down

# Logs
docker-compose logs -f

# Restart
docker-compose restart

# Rebuild
docker-compose build --no-cache
```

### Portainer

```
Deploy: Stacks → Add stack → Repository → Deploy
Logs:   Containers → Click container → Logs tab
Update: Stacks → madcp → Pull and redeploy
Stop:   Stacks → madcp → Stop button
```

### Verifiche

```bash
# Health check
curl http://localhost:8000/health

# Test completo
./scripts/verify.sh

# Controlla container
docker ps | grep madcp

# Controlla volumi
docker volume ls | grep madcp
```

---

**Buon deployment! 🚀**
