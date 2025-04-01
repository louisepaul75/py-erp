'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { ChevronDown, ChevronUp } from 'lucide-react';
import { cn } from '@/lib/utils';
import { API_URL } from '@/lib/config';
import useAppTranslation from '@/hooks/useTranslationWrapper';

interface HealthStatus {
  success: boolean;
  results: Array<{
    component: string;
    status: string;
    details: string;
    response_time: number;
    timestamp: string;
  }>;
  authenticated: boolean;
  server_time: string;
}

interface GitBranchInfo {
  branch: string;
  error?: string;
}

export function Footer() {
  const [healthStatus, setHealthStatus] = useState<HealthStatus | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [gitBranch, setGitBranch] = useState<GitBranchInfo | null>(null);
  const [isDevBarExpanded, setIsDevBarExpanded] = useState(false);
  const [apiAvailable, setApiAvailable] = useState(false);
  const { t } = useAppTranslation();
  
  // Measure footer height and set CSS variable
  useEffect(() => {
    const updateFooterHeight = () => {
      try {
        const footer = document.querySelector('footer');
        if (footer && footer.getBoundingClientRect) {
          const height = footer.getBoundingClientRect().height;
          document.documentElement.style.setProperty('--footer-height', `${height}px`);
        }
      } catch (error) {
        console.error('Error updating footer height:', error);
      }
    };
    
    // Initial measurement
    updateFooterHeight();
    
    // Update on window resize
    window.addEventListener('resize', updateFooterHeight);
    return () => window.removeEventListener('resize', updateFooterHeight);
  }, []);
  
  // Update CSS variable for dev bar height when expanded/collapsed
  useEffect(() => {
    if (isDevBarExpanded) {
      // Set a small delay to ensure the DOM has updated
      setTimeout(() => {
        try {
          const devBarContent = document.querySelector('.dev-bar-content');
          if (devBarContent && devBarContent.getBoundingClientRect) {
            const height = devBarContent.getBoundingClientRect().height;
            document.documentElement.style.setProperty('--dev-bar-height', `${height}px`);
          } else {
            // Fallback height if element not found
            document.documentElement.style.setProperty('--dev-bar-height', '200px');
          }
        } catch (error) {
          console.error('Error updating dev bar height:', error);
          // Fallback in case of error
          document.documentElement.style.setProperty('--dev-bar-height', '200px');
        }
      }, 10);
    } else {
      document.documentElement.style.setProperty('--dev-bar-height', '0px');
    }
  }, [isDevBarExpanded]);
  
  // Fetch health status
  useEffect(() => {
    const fetchHealthStatus = async () => {
      try {
        const response = await fetch(`${API_URL}/monitoring/health-checks/`);
        if (response.ok) {
          const data = await response.json();
          setHealthStatus(data);
          setApiAvailable(true);
        } else {
          console.error('Failed to fetch health status');
          setHealthStatus(null);
          setApiAvailable(false);
        }
      } catch (error) {
        console.error('Error fetching health status:', error);
        setHealthStatus(null);
        setApiAvailable(false);
      } finally {
        setIsLoading(false);
      }
    };
    
    fetchHealthStatus();
    
    // Refresh health status every 60 seconds
    const interval = setInterval(fetchHealthStatus, 60000);
    return () => clearInterval(interval);
  }, []);
  
  // Fetch git branch info
  useEffect(() => {
    const fetchGitBranch = async () => {
      try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 3000);
        
        const response = await fetch(`${API_URL}/git/branch/`, { 
          signal: controller.signal 
        });
        
        clearTimeout(timeoutId);
        
        if (response.ok) {
          const data = await response.json();
          setGitBranch(data);
        } else {
          console.error('Failed to fetch git branch info');
        }
      } catch (error) {
        // Silently handle the error - we'll use fallback values
        if (error instanceof DOMException && error.name === 'AbortError') {
          console.log('Git branch request timed out');
        } else {
          console.error('Error fetching git branch:', error);
        }
      }
    };
    
    fetchGitBranch();
  }, []);
  
  // Always show dev mode bar in development
  const isDevelopment = process.env.NODE_ENV === 'development' || healthStatus?.results.some(r => r.component === 'api' && r.status === 'error');
  
  // Mock data for when API is not available
  const mockHealthStatus = {
    success: false,
    results: [{
      component: 'api',
      status: 'error',
      details: 'API is not available',
      response_time: 0,
      timestamp: new Date().toISOString()
    }],
    authenticated: false,
    server_time: new Date().toISOString()
  };
  
  // Use real data if available, otherwise use mock data
  const displayHealthStatus = apiAvailable ? healthStatus : mockHealthStatus;
  
  // Calculate overall status
  const isHealthy = displayHealthStatus?.success && displayHealthStatus?.results.every(r => r.status === 'success');
  
  return (
    <>
      {/* Footer */}
      <footer className="bg-gray-100 dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700 fixed bottom-0 w-full z-10">
        <div className="container mx-auto px-4 py-3 flex justify-between items-center">
          <div className="text-sm text-gray-600 dark:text-gray-400">
            &copy; {new Date().getFullYear()} pyERP System
          </div>
          
          <Link 
            href="/health-status" 
            className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200 transition-colors"
          >
            <span>v{process.env.NEXT_PUBLIC_APP_VERSION || '1.0.0'}</span>
            {isLoading ? (
              <div 
                data-testid="loading-spinner"
                className="h-3 w-3 rounded-full bg-gray-300 animate-pulse"
              />
            ) : (
              <div 
                data-testid="api-status-indicator"
                className={cn(
                  "h-3 w-3 rounded-full",
                  isHealthy ? "bg-green-500" : "bg-red-500"
                )}
              />
            )}
          </Link>
        </div>
      </footer>
      
      {/* Dev Mode Bar - Positioned above footer */}
      {isDevelopment && (
        <div className="fixed w-full z-20" style={{
          bottom: `var(--footer-height, 2.75rem)`
        }}>
          <button
            onClick={() => setIsDevBarExpanded(!isDevBarExpanded)}
            className="w-full bg-orange-500 text-white py-1 px-4 flex items-center justify-between"
          >
            <span className="font-medium">
              DEV MODE {gitBranch?.branch ? `(${gitBranch.branch})` : '(local)'}
            </span>
            {isDevBarExpanded ? (
              <ChevronUp className="h-4 w-4" />
            ) : (
              <ChevronDown className="h-4 w-4" />
            )}
          </button>
          
          {isDevBarExpanded && (
            <div className="bg-orange-100 p-4 border-t border-orange-300 dev-bar-content absolute bottom-full w-full">
              <h3 className="font-semibold text-orange-800 mb-2">{t('health.debugInfo')}</h3>
              <div className="grid grid-cols-2 gap-2 text-sm">
                <div className="text-gray-600">{t('health.environment')}:</div>
                <div>Development</div>
                
                <div className="text-gray-600">{t('health.version')}:</div>
                <div>{process.env.NEXT_PUBLIC_APP_VERSION || '1.0.0'}</div>
                
                <div className="text-gray-600">{t('health.databaseStatus')}:</div>
                <div className={cn(
                  displayHealthStatus?.results.find(r => r.component === 'database')?.status === 'success' ? 'text-green-600' : 'text-red-600'
                )}>
                  {displayHealthStatus?.results.find(r => r.component === 'database')?.status === 'success' ? 'Healthy' : 'Unhealthy'}
                </div>
                
                <div className="text-gray-600">{t('health.gitBranch')}:</div>
                <div>{gitBranch?.branch || gitBranch?.error || 'local'}</div>
                
                <div className="text-gray-600">{t('health.apiAvailable')}:</div>
                <div className={apiAvailable ? 'text-green-600' : 'text-red-600'}>
                  {apiAvailable ? t('common.yes') : t('common.no')}
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </>
  );
} 