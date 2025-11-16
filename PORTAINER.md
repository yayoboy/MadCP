# 🚀 Deploy MadCP con Portainer

**Deployment facile e veloce con interfaccia web - nessuna command line necessaria!**

## Quick Start in 3 Passi

### 1️⃣ Apri Portainer

Vai al tuo Portainer: `http://your-server:9000`

### 2️⃣ Crea un nuovo Stack

1. Menu laterale → **Stacks**
2. Clicca **"+ Add stack"**
3. Nome stack: `madcp`

### 3️⃣ Deploy!

**Metodo A: Da Repository (Raccomandato)**

- Build method: **Repository**
- Repository URL: `https://github.com/yayoboy/MadCP`
- Repository reference: `main`
- Compose path: `portainer-stack.yml`

**Metodo B: Web Editor**

- Build method: **Web editor**
- Copia il contenuto di [`portainer-stack.yml`](portainer-stack.yml)
- Incolla nell'editor

### 4️⃣ Configura Variabili

Aggiungi queste variabili d'ambiente (clicca "+ Add environment variable"):

**OBBLIGATORIE:**
```env
POSTGRES_PASSWORD=your-secure-password-here
JWT_SECRET_KEY=your-jwt-secret-min-32-chars
OPENAI_API_KEY=sk-your-openai-key  # Opzionale ma raccomandato
```

**OPZIONALI:**
```env
POSTGRES_DB=madcp
POSTGRES_USER=madcp
DEBUG=false
LOG_LEVEL=INFO
```

### 5️⃣ Deploy

Clicca **"Deploy the stack"** e attendi che tutti i container si avviino (circa 2-3 minuti).

---

## ✅ Verifica

1. Vai su **Stacks** → **madcp**
2. Verifica che tutti i servizi siano **running** (🟢)
3. Apri nel browser: `http://your-server:8000/docs`

Se vedi la documentazione API Swagger, il deployment è riuscito! 🎉

---

## 📦 Servizi Inclusi

| Servizio | Porta | Descrizione |
|----------|-------|-------------|
| **Core API** | 8000 | API REST principale |
| **PostgreSQL** | 5432 | Database |
| **Redis** | 6379 | Cache |
| **Qdrant** | 6333 | Vector database |
| **Prometheus** | 9090 | Metriche (opzionale) |
| **Grafana** | 3001 | Monitoring (opzionale) |

---

## 🔧 Gestione Stack

### Start/Stop

- **Stop**: Stacks → madcp → **Stop**
- **Start**: Stacks → madcp → **Start**
- **Restart**: Stacks → madcp → **Restart**

### Visualizza Logs

1. Menu → **Containers**
2. Clicca sul container (es: `madcp-core-api`)
3. Tab **Logs**
4. Abilita **Auto-refresh** per logs in tempo reale

### Aggiornare

1. Stacks → madcp → **Editor**
2. Clicca **"Update the stack"**
3. Seleziona **"Re-pull images and redeploy"**
4. Clicca **"Update"**

---

## 🆘 Troubleshooting

### Container "Unhealthy"

1. Vai su **Containers**
2. Clicca sul container rosso/giallo
3. Tab **Logs** - controlla errori
4. Verifica variabili d'ambiente in **Inspect**

### Porta già in uso

Modifica le porte in Stacks → Editor:

```yaml
ports:
  - "8080:8000"  # Invece di 8000:8000
```

### Password dimenticata

1. Stacks → madcp → **Editor**
2. Modifica `POSTGRES_PASSWORD`
3. Update the stack

---

## 📖 Documentazione Completa

➡️ **[Guida Deployment Portainer Completa](docs/deployment-portainer.md)**

Include:
- ✅ Configurazione avanzata
- ✅ Template deployment
- ✅ Troubleshooting dettagliato
- ✅ Best practices produzione
- ✅ SSL/TLS setup
- ✅ Backup e restore

---

## 🎯 Template Pre-configurato

Per un setup ancora più rapido:

1. Scarica [`portainer-template.json`](portainer-template.json)
2. Portainer → **Settings** → **App Templates** → **Upload**
3. Vai su **App Templates** → **MadCP**
4. Clicca **Deploy**

---

## 🔗 Link Utili

- **Documentazione Principale**: [README.md](README.md)
- **Architettura**: [docs/architecture.md](docs/architecture.md)
- **API Reference**: Dopo il deploy → `http://your-server:8000/docs`
- **Portainer Documentation**: https://docs.portainer.io/

---

## 💡 Tips

- **Generare JWT Secret**:
  ```bash
  openssl rand -hex 32
  ```
  Oppure usa: https://randomkeygen.com/

- **OpenAI API Key**:
  Ottienila su https://platform.openai.com/api-keys

- **Backup Database**:
  ```bash
  docker exec madcp-postgres pg_dump -U madcp madcp > backup.sql
  ```

---

**Buon deployment! 🎉**

Per supporto: [GitHub Issues](https://github.com/yayoboy/MadCP/issues)
