# Entwicklungsumgebung Setup

## Voraussetzungen

- Python 3.9 oder höher
- Node.js 18 oder höher
- Docker und Docker Compose
- Git

## Erste Schritte

1. Repository klonen:
```bash
git clone https://github.com/your-org/pyERP.git
cd pyERP
```

2. Entwicklungsumgebung mit Docker starten:
```bash
docker-compose up -d
```

## Verfügbare Services

| Service | Port | Beschreibung |
|---------|------|-------------|
| Frontend (Next.js) | 3000 | Web-Interface |
| Backend (Django) | 8000 | REST API |
| Swagger UI | 8000/api/swagger | API-Dokumentation |
| PostgreSQL | 5432 | Datenbank |
| Redis | 6379 | Cache & Message Broker |

## Entwicklungsmodus

### Frontend Development Server

```bash
cd frontend
npm install
npm run dev
```

### Backend Development Server

```bash
python -m venv venv
source venv/bin/activate  # Unter Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py runserver
```

## Wichtige URLs

- Frontend: [http://localhost:3000](http://localhost:3000)
- API: [http://localhost:8000/api/](http://localhost:8000/api/)
- Swagger UI: [http://localhost:8000/api/swagger/](http://localhost:8000/api/swagger/)
- Admin Interface: [http://localhost:8000/admin/](http://localhost:8000/admin/)

## Entwicklungswerkzeuge

### Code Formatierung

- Python: Black, isort
- JavaScript/TypeScript: Prettier, ESLint

### Linting

- Python: Flake8, Pylint
- JavaScript/TypeScript: ESLint

### Testing

- Python: pytest
- JavaScript/TypeScript: Jest, React Testing Library

## Troubleshooting

### Häufige Probleme

1. **Redis Verbindungsfehler**
   ```
   Redis unavailable after 3 attempts - falling back to memory broker
   ```
   Lösung: Redis-Service neustarten oder Verbindungseinstellungen überprüfen

2. **Datenbank-Migrations Fehler**
   ```
   Skipping database migrations due to known issues with migrations...
   ```
   Lösung: Migrations manuell ausführen:
   ```bash
   python manage.py migrate
   ```

### Logs einsehen

```bash
# Docker Logs
docker-compose logs -f

# Spezifische Service-Logs
docker-compose logs -f backend
docker-compose logs -f frontend
```

## Nächste Schritte

- [Lokale Entwicklung](local.md)
- [Docker-Konfiguration](docker.md)
- [API-Dokumentation](../api/overview.md) 