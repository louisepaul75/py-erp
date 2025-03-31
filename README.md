# pyERP - Enterprise Resource Planning System

## Monitoring System

The pyERP system includes a comprehensive monitoring setup based on the ELK stack (Elasticsearch, Logstash, Kibana) and Sentry. The monitoring system can be run in three different modes:

1. **Integrated Mode (Default)**: Monitoring tools are installed directly in the main pyERP container.
   ```bash
   ./rebuild_docker.dev.sh
   ```

2. **Separate Mode**: Monitoring services run in their own container, isolating them from the main application.
   ```bash
   ./rebuild_docker.dev.sh --monitoring separate
   ```

3. **Remote Mode**: Connect to a deployed monitoring system at a remote IP address.
   ```bash
   ./rebuild_docker.dev.sh --monitoring remote
   ```

### Monitoring Services

- **Elasticsearch**: Database for storing logs and metrics
  - URL: http://localhost:9200 (default)
  
- **Kibana**: Web interface for visualizing and exploring data
  - URL: http://localhost:5601 (default)
  
- **Sentry**: Error tracking and performance monitoring
  - Integrated with the Django application

To view logs from the monitoring container:
```bash
docker logs pyerp-elastic-kibana
```

### Monitoring Scripts

All monitoring-related scripts are located in the `scripts/monitoring` directory:

- `setup_monitoring.sh`: Basic monitoring setup script
- `setup_monitoring_complete.sh`: Complete monitoring setup for remote installations

For manual setup of remote monitoring:
```bash
./scripts/monitoring/setup_monitoring_complete.sh 
```

## API Documentation

The API documentation is generated using [drf-spectacular](https://drf-spectacular.readthedocs.io/) and deployed automatically to Netlify when changes are pushed to the main branch.

### Automatic Deployment

The Swagger documentation is automatically deployed to Netlify using GitHub Actions when changes are made to the API code or configuration. To set up the deployment:

1. Ensure you have a Netlify account and have created a site for the API documentation
2. Add the following secrets to your GitHub repository:
   - `NETLIFY_SITE_ID`: Your Netlify Site ID
   - `NETLIFY_AUTH_TOKEN`: Your Netlify Auth Token

The deployment will automatically trigger when changes are pushed to:
- `pyerp/config/settings/**`
- `pyerp/api/**`
- `requirements/**`
- `.github/workflows/swagger-netlify.yml`
- `netlify.toml`

### Local Development

To generate and view the Swagger documentation locally:

```bash
# Generate Swagger JSON
python manage.py spectacular --file swagger.json

# To view the documentation using the built-in Swagger UI:
python manage.py runserver
# Then visit: http://localhost:8000/api/schema/swagger-ui/
```