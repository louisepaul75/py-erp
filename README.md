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

To view logs from the monitoring containers:
```bash
docker logs pyerp-elasticsearch
docker logs pyerp-kibana
```

### Monitoring Scripts

All monitoring-related scripts are located in the `scripts/monitoring` directory:

- `setup_monitoring.sh`: Basic monitoring setup script
- `setup_monitoring_complete.sh`: Complete monitoring setup for remote installations

For manual setup of remote monitoring:
```bash
./scripts/monitoring/setup_monitoring_complete.sh 