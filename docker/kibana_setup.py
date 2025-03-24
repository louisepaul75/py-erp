#!/usr/bin/env python3
"""
Kibana setup script to create developer-based dashboards.
This script creates a dashboard in Kibana that allows filtering logs by developer.
"""

import os
import sys
import json
import requests
import time
from urllib.parse import urljoin


def wait_for_kibana(kibana_url, max_retries=30, retry_interval=5):
    """Wait for Kibana to be available."""
    print(f"Waiting for Kibana at {kibana_url}...")
    
    for i in range(max_retries):
        try:
            response = requests.get(urljoin(kibana_url, "/api/status"))
            if response.status_code == 200:
                print("Kibana is available!")
                return True
        except requests.exceptions.RequestException:
            pass
        
        print(f"Kibana not yet available, retrying in {retry_interval}s...")
        time.sleep(retry_interval)
    
    print("Kibana did not become available in time")
    return False


def create_index_pattern(kibana_url, index_pattern="pyerp-*"):
    """Create an index pattern for PyERP logs in Kibana."""
    url = urljoin(kibana_url, "/api/index_patterns/index_pattern")
    
    data = {
        "index_pattern": {
            "title": index_pattern,
            "timeFieldName": "@timestamp"
        }
    }
    
    headers = {"kbn-xsrf": "true", "Content-Type": "application/json"}
    
    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code in (200, 201):
            print(f"Successfully created index pattern: {index_pattern}")
            return response.json()
        else:
            print(f"Failed to create index pattern: {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error creating index pattern: {e}")
        return None


def create_developer_dashboard(kibana_url, index_pattern_id):
    """Create a dashboard for filtering logs by developer."""
    url = urljoin(kibana_url, "/api/saved_objects/dashboard/developer-dashboard")
    
    # Create a visualization for developer.id field
    vis_url = urljoin(kibana_url, "/api/saved_objects/visualization/developer-id-vis")
    vis_data = {
        "attributes": {
            "title": "Logs by Developer",
            "visState": json.dumps({
                "title": "Logs by Developer",
                "type": "pie",
                "params": {
                    "type": "pie",
                    "addTooltip": True,
                    "addLegend": True,
                    "legendPosition": "right",
                    "isDonut": False
                },
                "aggs": [
                    {
                        "id": "1",
                        "enabled": True,
                        "type": "count",
                        "schema": "metric",
                        "params": {}
                    },
                    {
                        "id": "2",
                        "enabled": True,
                        "type": "terms",
                        "schema": "segment",
                        "params": {
                            "field": "developer.id",
                            "size": 20,
                            "order": "desc",
                            "orderBy": "1"
                        }
                    }
                ]
            }),
            "kibanaSavedObjectMeta": {
                "searchSourceJSON": json.dumps({
                    "index": index_pattern_id,
                    "filter": [],
                    "query": {"query": "", "language": "kuery"}
                })
            }
        }
    }
    
    headers = {"kbn-xsrf": "true", "Content-Type": "application/json"}
    
    try:
        # Create visualization
        vis_response = requests.put(vis_url, headers=headers, json=vis_data)
        if vis_response.status_code not in (200, 201):
            print(f"Failed to create visualization: {vis_response.text}")
            return None
        
        # Create the dashboard
        dashboard_data = {
            "attributes": {
                "title": "Developer Log Dashboard",
                "hits": 0,
                "description": "Dashboard for filtering logs by developer",
                "panelsJSON": json.dumps([
                    {
                        "embeddableConfig": {},
                        "gridData": {
                            "h": 15,
                            "i": "1",
                            "w": 24,
                            "x": 0,
                            "y": 0
                        },
                        "id": "developer-id-vis",
                        "panelIndex": "1",
                        "type": "visualization",
                        "version": "7.10.2"
                    }
                ]),
                "optionsJSON": json.dumps({
                    "hidePanelTitles": False,
                    "useMargins": True
                }),
                "version": 1,
                "timeRestore": False,
                "kibanaSavedObjectMeta": {
                    "searchSourceJSON": json.dumps({
                        "query": {
                            "language": "kuery",
                            "query": ""
                        },
                        "filter": []
                    })
                }
            }
        }
        
        response = requests.put(url, headers=headers, json=dashboard_data)
        if response.status_code in (200, 201):
            print("Successfully created developer dashboard")
            return response.json()
        else:
            print(f"Failed to create dashboard: {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error creating dashboard: {e}")
        return None


def main():
    """Main entry point for the script."""
    kibana_host = os.environ.get('KIBANA_HOST', 'localhost')
    kibana_port = os.environ.get('KIBANA_PORT', '5601')
    kibana_url = f"http://{kibana_host}:{kibana_port}"
    
    index_prefix = os.environ.get('ELASTICSEARCH_INDEX_PREFIX', 'pyerp')
    index_pattern = f"{index_prefix}-*"
    
    # Wait for Kibana to be available
    if not wait_for_kibana(kibana_url):
        sys.exit(1)
    
    # Create the index pattern
    index_pattern_response = create_index_pattern(kibana_url, index_pattern)
    if not index_pattern_response:
        sys.exit(1)
    
    # Get the ID of the created index pattern
    index_pattern_id = index_pattern_response.get("id")
    if not index_pattern_id:
        print("Could not get index pattern ID")
        sys.exit(1)
    
    # Create the developer dashboard
    dashboard_response = create_developer_dashboard(kibana_url, index_pattern_id)
    if not dashboard_response:
        sys.exit(1)
    
    print(f"Dashboard URL: {kibana_url}/app/kibana#/dashboard/developer-dashboard")
    
    return 0


if __name__ == "__main__":
    sys.exit(main()) 