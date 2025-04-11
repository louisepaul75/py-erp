# Willkommen zur pyERP Dokumentation

Dies ist die zentrale technische Dokumentation für das pyERP System.

Nutze die Navigation, um die automatisch generierte API-Referenz zu erkunden.

Für die REST-API Dokumentation, siehe die [Swagger UI](/api/swagger/).  <!-- Korrekter Link --> 

Im Entwicklungsmodus ist die Swagger UI unter [http://localhost:8000/api/swagger/](http://localhost:8000/api/swagger/) erreichbar. 

nav:
  - Home: index.md
  - Entwicklung:
      - Setup: development/setup.md
      - Docker: development/docker.md
      - Lokale Entwicklung: development/local.md
  - API:
      - Übersicht: api/overview.md
      - Authentifizierung: api/auth.md
      - Endpoints: api/endpoints.md
  - Frontend:
      - Architektur: frontend/architecture.md
      - Komponenten: frontend/components.md
      - State Management: frontend/state.md
  - Deployment:
      - Prozess: deployment/process.md
      - CI/CD: deployment/ci-cd.md
      - Monitoring: deployment/monitoring.md
  - Datenbank:
      - Schema: database/schema.md
      - Migrationen: database/migrations.md
      - Backup: database/backup.md
  - Testing:
      - Strategie: testing/strategy.md
      - Unit Tests: testing/unit.md
      - Integration Tests: testing/integration.md
  - Sicherheit:
      - Richtlinien: security/guidelines.md
      - Auth: security/auth.md
      - DSGVO: security/gdpr.md 

plugins:
  - search
  - mkdocstrings
  - git-revision-date  # Zeigt das letzte Änderungsdatum an
  - minify  # Minimiert HTML/CSS/JS
  - pdf-export  # Ermöglicht PDF-Export
  - mermaid2  # Für Diagramme
  - tags  # Für bessere Kategorisierung 