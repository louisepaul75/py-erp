'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { Activity, ChevronDown, ChevronUp, AlertTriangle } from 'lucide-react';
import { cn } from '@/lib/utils';
import { API_URL } from '@/lib/config';
import useAppTranslation from '@/hooks/useTranslationWrapper';

interface HealthStatus {
  status: string;
  database: {
    status: string;
    message: string;
  };
  environment: string;
  version: string;
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
      const footer = document.querySelector('footer');
      if (footer) {
        const height = footer.getBoundingClientRect().height;
        document.documentElement.style.setProperty('--footer-height', `${height}px`);
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
        const devBarContent = document.querySelector('.dev-bar-content');
        if (devBarContent) {
          const height = devBarContent.getBoundingClientRect().height;
          document.documentElement.style.setProperty('--dev-bar-height', `${height}px`);
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
        const response = await fetch(`${API_URL}/health`);
        if (response.ok) {
          const data = await response.json();
          setHealthStatus(data);
          setApiAvailable(true);
        } else {
          console.error('Failed to fetch health status');
          setApiAvailable(false);
        }
      } catch (error) {
        console.error('Error fetching health status:', error);
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
        
        const response = await fetch(`${API_URL}/git/branch`, { 
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
  const isDevelopment = process.env.NODE_ENV === 'development' || healthStatus?.environment === 'development';
  
  // Mock data for when API is not available
  const mockHealthStatus = {
    status: 'healthy',
    database: { status: 'connected', message: 'Database is connected' },
    environment: 'development',
    version: '1.0.0-dev'
  };
  
  // Use real data if available, otherwise use mock data
  const displayHealthStatus = apiAvailable ? healthStatus : mockHealthStatus;
  
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
            className="flex items-center gap-2 text-sm"
          >
            {isLoading ? (
              <div className="h-4 w-4 rounded-full bg-gray-300 animate-pulse"></div>
            ) : (
              displayHealthStatus?.status === 'healthy' ? (
                <Activity className="h-4 w-4 text-green-500" />
              ) : (
                <AlertTriangle className="h-4 w-4 text-red-500" />
              )
            )}
            <span className={cn(
              "font-medium",
              isLoading ? "text-gray-500" : 
                displayHealthStatus?.status === 'healthy' ? "text-green-600" : "text-red-600"
            )}>
              {isLoading ? t('messages.loading') : 
                displayHealthStatus?.status === 'healthy' ? t('health.systemHealthy') : t('health.systemIssues')}
            </span>
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
                <div>{displayHealthStatus?.environment || 'Development'}</div>
                
                <div className="text-gray-600">{t('health.version')}:</div>
                <div>{displayHealthStatus?.version || '1.0.0'}</div>
                
                <div className="text-gray-600">{t('health.databaseStatus')}:</div>
                <div className={cn(
                  displayHealthStatus?.database?.status === 'connected' ? 'text-green-600' : 'text-red-600'
                )}>
                  {displayHealthStatus?.database?.status || 'Unknown'}
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