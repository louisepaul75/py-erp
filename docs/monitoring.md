# pyERP Monitoring System

This document describes the monitoring system integrated into pyERP, which provides comprehensive logging, error tracking, and performance monitoring capabilities.

## Components

The monitoring system consists of three main components:

1. **Centralized Log Collection with Elasticsearch & Filebeat**
   - Collects and indexes all logs from the ERP system
   - Provides powerful search and analysis capabilities
   - Stores logs in a structured format with context information

2. **Visualization and Reporting with Kibana**
   - Provides dashboards for visualizing log data
   - Enables interactive analysis of system activities
   - Helps track warehouse operations, user activities, and system performance

3. **Error Tracking and Performance Monitoring with Sentry**
   - Captures and reports errors and exceptions in real-time
   - Provides detailed context for debugging
   - Monitors application performance

## Architecture

All components run within the same Docker container as the pyERP application, making deployment and management simpler.

```
┌─────────────────────────────────────────────────────────────┐
│                      pyERP Container                        │
│                                                             │
│  ┌─────────────┐      ┌─────────────┐     ┌─────────────┐   │
│  │             │      │             │     │             │   │
│  │  Django     │──┬──▶│  Filebeat   │────▶│ Elasticsearch│   │
│  │  Application│  │   │             │     │             │   │
│  │             │  │   └─────────────┘     └──────┬──────┘   │
│  └─────────────┘  │                              │          │
│         │         │                              │          │
│         ▼         │                              ▼          │
│  ┌─────────────┐  │                       ┌─────────────┐   │
│  │             │  │                       │             │   │
│  │   Sentry    │  │                       │   Kibana    │   │
│  │  Integration│  │                       │             │   │
│  │             │  │                       │             │   │
│  └─────────────┘  │                       └─────────────┘   │
│         ▲         │                                         │
│         └─────────┘                                         │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Configuration

The monitoring system is automatically configured when the Docker container starts. The configuration includes:

- Structured JSON logging for all Django components
- Log rotation to prevent disk space issues
- Request ID tracking for tracing requests across the system
- Integration with Sentry for error tracking
- Elasticsearch indices for efficient log storage and retrieval
- Kibana dashboards for visualization

## Usage

### Accessing Kibana

Kibana is available at http://localhost:5601 when the container is running. You can use it to:

- View real-time logs
- Create custom dashboards
- Set up alerts for specific events
- Analyze system performance

### Using Structured Logging in Code

To add context to your logs, use the provided logger:

```python
from pyerp.config.logging_config import get_logger

logger = get_logger(__name__)

# Log with context
logger.info("User performed inventory adjustment", extra={
    'user_id': user.id,
    'item_id': item.id,
    'quantity_before': old_quantity,
    'quantity_after': new_quantity,
    'warehouse_id': warehouse.id
})
```

### Viewing Sentry Errors

Sentry is integrated directly into the Django application. Errors are automatically captured and can be viewed in the Sentry dashboard.

## Maintenance

### Log Rotation

Logs are automatically rotated to prevent disk space issues. The rotation configuration is:

- Maximum file size: 10 MB
- Number of backup files: 10

### Elasticsearch Indices

Elasticsearch indices are created with a date pattern (`pyerp-logs-YYYY.MM.DD`), which allows for easy management of older logs.

#### Log Retention Policy

The system has been configured with the following log retention policies:

1. **Filebeat Logs**: The `filebeat_stdout.log` file is limited to 500MB and will rotate automatically when it reaches this size.

2. **Elasticsearch Storage**: A size-based retention policy limits the total Elasticsearch storage to 1GB. When the storage limit is reached, the oldest indices are automatically deleted to make room for new logs.

3. **Index Lifecycle Management (ILM)**: Elasticsearch uses ILM policies to manage index growth and automatically delete old indices to maintain the 1GB storage limit.

To reconfigure these settings, you can:

```bash
# Adjust Filebeat log size limit
# Edit docker/filebeat_config.yml: rotateeverybytes parameter

# Adjust Elasticsearch storage limit
# Edit scripts/configure_elasticsearch_retention.sh: modify max_size values
```

## Troubleshooting

If you encounter issues with the monitoring system:

1. Check the container logs: `docker logs pyerp-dev`
2. Verify Elasticsearch is running: `curl http://localhost:9200`
3. Check Kibana status: `curl http://localhost:5601/api/status`
4. Ensure Filebeat is properly configured: Check `/app/logs/filebeat-out.log` 