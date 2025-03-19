'use client';

import { useState, useEffect } from 'react';
import { Activity, AlertTriangle, Clock, Database, Server, RefreshCw, WifiOff } from 'lucide-react';
import { API_URL } from '@/lib/config';

interface HealthCheckResult {
  component: string;
  status: string;
  details: string;
  response_time: number;
  timestamp: string;
}

interface HealthStatus {
  status: string;
  database: {
    status: string;
    message: string;
  };
  environment: string;
  version: string;
}

export default function HealthStatusPage() {
  const [healthStatus, setHealthStatus] = useState<HealthStatus | null>(null);
  const [healthChecks, setHealthChecks] = useState<HealthCheckResult[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [apiErrors, setApiErrors] = useState<{health: boolean; checks: boolean}>({
    health: false,
    checks: false
  });

  const fetchHealthStatus = async () => {
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 5000);
      
      const response = await fetch(`${API_URL}/core/health`, {
        signal: controller.signal
      });
      
      clearTimeout(timeoutId);
      
      if (response.ok) {
        const data = await response.json();
        setHealthStatus(data);
        setApiErrors(prev => ({...prev, health: false}));
      } else {
        console.error('Failed to fetch health status');
        setApiErrors(prev => ({...prev, health: true}));
      }
    } catch (error) {
      console.error('Error fetching health status:', error);
      setApiErrors(prev => ({...prev, health: true}));
    }
  };

  const fetchHealthChecks = async () => {
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 5000);
      
      const response = await fetch(`${API_URL}/monitoring/health-checks`, {
        signal: controller.signal
      });
      
      clearTimeout(timeoutId);
      
      if (response.ok) {
        const data = await response.json();
        if (data.success && Array.isArray(data.results)) {
          setHealthChecks(data.results);
          setApiErrors(prev => ({...prev, checks: false}));
        }
      } else {
        console.error('Failed to fetch health checks');
        setApiErrors(prev => ({...prev, checks: true}));
      }
    } catch (error) {
      console.error('Error fetching health checks:', error);
      setApiErrors(prev => ({...prev, checks: true}));
    }
  };

  const refreshData = async () => {
    setIsRefreshing(true);
    await Promise.all([fetchHealthStatus(), fetchHealthChecks()]);
    setIsRefreshing(false);
  };

  useEffect(() => {
    const fetchData = async () => {
      setIsLoading(true);
      await Promise.all([fetchHealthStatus(), fetchHealthChecks()]);
      setIsLoading(false);
    };

    fetchData();
  }, []);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy':
      case 'success':
        return 'bg-green-100 text-green-800 border-green-200';
      case 'warning':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'error':
      case 'unhealthy':
        return 'bg-red-100 text-red-800 border-red-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'healthy':
      case 'success':
        return <Activity className="h-5 w-5 text-green-500" />;
      case 'warning':
        return <AlertTriangle className="h-5 w-5 text-yellow-500" />;
      case 'error':
      case 'unhealthy':
        return <AlertTriangle className="h-5 w-5 text-red-500" />;
      default:
        return <Activity className="h-5 w-5 text-gray-500" />;
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleString();
  };

  if (isLoading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
        </div>
      </div>
    );
  }

  // Mock data for when API is not available
  const mockHealthStatus = {
    status: 'healthy',
    database: { status: 'connected', message: 'Database is connected' },
    environment: 'development',
    version: '1.0.0-dev'
  };

  // Use real data if available, otherwise use mock data
  const displayHealthStatus = apiErrors.health ? mockHealthStatus : healthStatus;

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">System Health Status</h1>
        <button
          onClick={refreshData}
          disabled={isRefreshing}
          className="flex items-center gap-2 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 disabled:opacity-50"
        >
          <RefreshCw className={`h-4 w-4 ${isRefreshing ? 'animate-spin' : ''}`} />
          Refresh
        </button>
      </div>

      {/* API Connection Status */}
      {(apiErrors.health || apiErrors.checks) && (
        <div className="p-4 mb-6 border rounded-lg bg-yellow-100 text-yellow-800 border-yellow-200">
          <div className="flex items-center gap-3">
            <WifiOff className="h-5 w-5 text-yellow-500" />
            <h2 className="text-lg font-semibold">
              API Connection Issues
            </h2>
          </div>
          <p className="mt-2">
            Unable to connect to some backend API endpoints. The information shown may be incomplete or unavailable.
            {process.env.NODE_ENV === 'development' && (
              <span className="block mt-1 text-sm">
                Make sure your Django backend is running on port 8050 and accessible.
              </span>
            )}
          </p>
        </div>
      )}

      {/* Overall System Status */}
      <div className={`p-4 mb-8 border rounded-lg ${getStatusColor(displayHealthStatus?.status || 'unknown')}`}>
        <div className="flex items-center gap-3">
          {getStatusIcon(displayHealthStatus?.status || 'unknown')}
          <h2 className="text-lg font-semibold">
            Overall System Status: {displayHealthStatus?.status === 'healthy' ? 'Healthy' : 'Issues Detected'}
          </h2>
        </div>
        <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="flex items-center gap-2">
            <Database className="h-5 w-5 text-gray-500" />
            <span className="font-medium">Database:</span>
            <span className={displayHealthStatus?.database?.status === 'connected' ? 'text-green-600' : 'text-red-600'}>
              {displayHealthStatus?.database?.status || 'Unknown'}
            </span>
          </div>
          <div className="flex items-center gap-2">
            <Server className="h-5 w-5 text-gray-500" />
            <span className="font-medium">Environment:</span>
            <span>{displayHealthStatus?.environment || 'Unknown'}</span>
          </div>
          <div className="flex items-center gap-2">
            <Clock className="h-5 w-5 text-gray-500" />
            <span className="font-medium">Version:</span>
            <span>{displayHealthStatus?.version || 'Unknown'}</span>
          </div>
        </div>
      </div>

      {/* Component Health Checks */}
      <h2 className="text-xl font-semibold mb-4">Component Health Checks</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {healthChecks.length > 0 ? (
          healthChecks.map((check, index) => (
            <div
              key={index}
              className={`p-4 border rounded-lg ${getStatusColor(check.status)}`}
            >
              <div className="flex items-center gap-2 mb-2">
                {getStatusIcon(check.status)}
                <h3 className="font-semibold">
                  {check.component.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                </h3>
              </div>
              <p className="text-sm mb-3">{check.details}</p>
              <div className="flex justify-between text-xs text-gray-500">
                <span>Response time: {check.response_time?.toFixed(2) || 'N/A'} ms</span>
                <span>{formatDate(check.timestamp)}</span>
              </div>
            </div>
          ))
        ) : (
          <div className="col-span-2 p-4 border rounded-lg bg-gray-50">
            <p className="text-center text-gray-500">
              {apiErrors.checks 
                ? 'Unable to fetch health check data from the API' 
                : 'No health check data available'}
            </p>
          </div>
        )}
      </div>
    </div>
  );
} 