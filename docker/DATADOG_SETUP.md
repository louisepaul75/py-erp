# Datadog Setup for pyERP

This document provides instructions on how to set up and use Datadog monitoring with the pyERP system in production.

## Prerequisites

1. A Datadog account (you can sign up at [datadoghq.com](https://www.datadoghq.com/))
2. A Datadog API key (available in your Datadog account settings)

## Configuration

### 1. Set Environment Variables

Before deploying the production environment, make sure to set the following environment variables:

```bash
# Required
DD_API_KEY=your_datadog_api_key_here

# Optional (defaults are provided)
DD_SITE=datadoghq.com  # Use datadoghq.eu for EU region
DD_ENV=production
DD_SERVICE=pyerp
DD_VERSION=1.0.0
```

You can set these variables in your deployment environment or update them directly in the `docker/docker.env.prod` file.

### 2. Deploy with Docker Compose

The Datadog agent is already configured in the `docker-compose.prod.yml` file. To deploy with Datadog monitoring:

```bash
cd docker
docker-compose -f docker-compose.prod.yml up -d
```

## Monitoring Features

The Datadog integration provides the following monitoring capabilities:

1. **Application Performance Monitoring (APM)**
   - Traces for Django views and API endpoints
   - Database query monitoring
   - Celery task monitoring

2. **Infrastructure Monitoring**
   - Host metrics (CPU, memory, disk, network)
   - Container metrics
   - Process monitoring

3. **Log Management**
   - Centralized log collection
   - Log parsing and analysis
   - Alert on log patterns

4. **Real User Monitoring (RUM)**
   - Page load times
   - Frontend errors
   - User session tracking

## Datadog Dashboard

After deploying, you can access your Datadog dashboard at:
- [https://app.datadoghq.com/dashboard/lists](https://app.datadoghq.com/dashboard/lists)

## Troubleshooting

If you encounter issues with the Datadog integration:

1. Check the Datadog agent logs:
   ```bash
   docker logs datadog-agent
   ```

2. Verify the API key is correctly set in the environment variables.

3. Ensure the Datadog agent container has access to the Docker socket.

4. Check that the `ddtrace` Python package is correctly installed and running.

## Additional Resources

- [Datadog Documentation](https://docs.datadoghq.com/)
- [Datadog Python Integration](https://docs.datadoghq.com/tracing/setup_overview/setup/python/)
- [Datadog Docker Integration](https://docs.datadoghq.com/agent/docker/) 