'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { ChevronDown, ChevronUp } from 'lucide-react';
import { cn } from '@/lib/utils';
import { API_URL } from '@/lib/config';
import useAppTranslation from '@/hooks/useTranslationWrapper';

interface HealthCheckResult {
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

interface OverallHealthStatus {
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
  const [healthChecks, setHealthChecks] = useState<HealthCheckResult | null>(null);
  const [overallHealth, setOverallHealth] = useState<OverallHealthStatus | null>(null);
  const [isLoadingChecks, setIsLoadingChecks] = useState(true);
  const [isLoadingHealth, setIsLoadingHealth] = useState(true);
  const [gitBranch, setGitBranch] = useState<GitBranchInfo | null>(null);
  const [isDevBarExpanded, setIsDevBarExpanded] = useState(false);
  const [apiAvailable, setApiAvailable] = useState(true);
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
  
  // Fetch health checks (for dev bar condition)
  useEffect(() => {
    const healthUrl = `${API_URL}/health/`
    const monitoringUrl = `${API_URL}/v1/monitoring/health-checks/`

    const fetchBackendStatus = async () => {
      setIsLoadingChecks(true);
      try {
        let response: Response
        try {
          console.log("Fetching monitoring status from:", monitoringUrl)
          response = await fetch(monitoringUrl, {
            headers: {
              Accept: "application/json",
            }
          });
        } catch (error) {
          console.warn("Monitoring endpoint failed, trying health endpoint...")
          try {
            console.log("Fetching health status from:", healthUrl)
            response = await fetch(healthUrl, {
              headers: {
                Accept: "application/json",
              }
            });
          } catch (error) {
            console.error('Error fetching health checks:', error);
            setHealthChecks(null);
            return;
          }
        }

        if (response.ok) {
          try {
            const contentType = response.headers.get('content-type');
            if (contentType && contentType.includes('application/json')) {
              const data = await response.json();
              setHealthChecks(data);
            } else {
              console.error('Health checks API returned non-JSON content');
              setHealthChecks(null);
            }
          } catch (parseError) {
            console.error('Failed to parse health checks response as JSON:', parseError);
            setHealthChecks(null);
          }
        } else {
          console.error('Failed to fetch health checks');
          setHealthChecks(null);
        }
      } catch (error) {
        console.error('Error fetching health checks:', error);
        setHealthChecks(null);
      } finally {
        setIsLoadingChecks(false);
      }
    };
    
    fetchBackendStatus();
    
    const interval = setInterval(fetchBackendStatus, 60000);
    return () => clearInterval(interval);
  }, []);

  // Fetch overall health status (for version and status indicator)
  useEffect(() => {
    // Define controller outside the fetch function so cleanup can access it
    let controller: AbortController;

    const fetchOverallHealthData = async () => {
      // Re-initialize controller for each fetch attempt (including intervals)
      controller = new AbortController();
      const signal = controller.signal;
      
      setIsLoadingHealth(true);
      let timeoutId: NodeJS.Timeout | null = null;
      
      try {
        // Set timeout for this specific fetch attempt
        timeoutId = setTimeout(() => controller.abort('timeout'), 5000); 

        const response = await fetch(`${API_URL}/health/`, {
          signal: signal, // Use the signal from the outer scope
          headers: {
            'Accept': 'application/json'
          }
        });

        // Clear the timeout if the fetch completed successfully
        if (timeoutId) clearTimeout(timeoutId);

        if (response.ok) {
          try {
            const contentType = response.headers.get('content-type');
            if (contentType && contentType.includes('application/json')) {
              const data = await response.json();
              // Only update state if the component hasn't been unmounted (signal not aborted)
              if (!signal.aborted) {
                setOverallHealth(data);
                setApiAvailable(true);
              }
            } else {
              console.error('Health API returned non-JSON content');
               if (!signal.aborted) {
                 setOverallHealth(null);
                 setApiAvailable(false);
               }
            }
          } catch (parseError) {
            console.error('Failed to parse health response as JSON:', parseError);
             if (!signal.aborted) {
               setOverallHealth(null);
               setApiAvailable(false);
             }
          }
        } else {
          console.error('Failed to fetch overall health status');
           if (!signal.aborted) {
             setOverallHealth(null);
             setApiAvailable(false);
           }
        }
      } catch (error) {
         // Only handle error if it wasn't an intentional abort
        if (!(error instanceof DOMException && error.name === 'AbortError')) {
           console.error('Error fetching overall health status:', error);
           // Check signal again before setting state in error case
           if (!signal.aborted) {
             setOverallHealth(null);
             setApiAvailable(false);
           }
        } else if (controller.signal.reason === 'timeout') {
            // Log specifically if the abort was due to timeout
            console.log('Overall health request timed out');
            if (!signal.aborted) { // Check signal before setting state
              setOverallHealth(null);
              setApiAvailable(false);
            }
        } // Otherwise (regular abort on unmount), do nothing
      } finally {
        // Clear timeout just in case it's still pending after an error
        if (timeoutId) clearTimeout(timeoutId);
        // Only update loading state if not aborted
        if (!signal.aborted) {
          setIsLoadingHealth(false);
        }
      }
    };

    fetchOverallHealthData();

    const interval = setInterval(fetchOverallHealthData, 60000);
    
    // Cleanup function: clear interval AND abort ongoing fetch
    return () => {
      clearInterval(interval);
      // Check if controller exists before aborting (it might not if effect cleans up before first fetch starts)
      if (controller) {
         controller.abort(); 
      }
    };
  }, []); // Keep empty dependency array
  
  // Fetch git branch info
  useEffect(() => {
    const fetchGitBranch = async () => {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 5000); // 5 second timeout
      
      try {
        
        const response = await fetch(`${API_URL}/v1/git/branch/`, { 
          signal: controller.signal,
          headers: {
            'Accept': 'application/json'
          }
        });
        
        clearTimeout(timeoutId);
        
        if (response.ok) {
          try {
            const contentType = response.headers.get('content-type');
            if (contentType && contentType.includes('application/json')) {
              const data = await response.json();
              setGitBranch(data);
            } else {
              console.error('Git branch API returned non-JSON content');
              setGitBranch(null);
            }
          } catch (parseError) {
            console.error('Failed to parse git branch response as JSON:', parseError);
            setGitBranch(null);
          }
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
  
  // Show dev mode bar in development OR if the health checks endpoint reports an API error
  const isDevelopment = process.env.NODE_ENV === 'development' || healthChecks?.results.some(r => r.component === 'api' && r.status === 'error');
  
  // Mock data for when API is not available (based on /health/ failure)
  const mockOverallHealth: OverallHealthStatus = {
    status: 'error',
    database: { status: 'unknown', message: 'API unavailable' },
    environment: 'unknown',
    version: process.env.NEXT_PUBLIC_APP_VERSION || '0.0.0'
  };
  
  // Use real data if available, otherwise use mock data
  const displayOverallHealth = apiAvailable ? overallHealth : mockOverallHealth;
  
  // Calculate overall status based on /health/ endpoint response
  const overallStatus = displayOverallHealth?.status || 'error';

  // Combine loading states
  const isLoading = isLoadingChecks || isLoadingHealth;
  
  return (
    <>
      {/* Footer */}
      <footer className="bg-footer text-footer-foreground border-t border-border fixed bottom-0 w-full z-10">
        <div className="container mx-auto px-4 py-3 flex justify-between items-center">
          <div className="text-sm">
            &copy; {new Date().getFullYear()} pyERP
          </div>
          
          <Link 
            href="/health-status" 
            className="flex items-center gap-2 text-sm hover:text-primary transition-colors"
          >
            <span>v{displayOverallHealth?.version || process.env.NEXT_PUBLIC_APP_VERSION || '0.0.0'}</span>
            {isLoading ? (
              <div 
                data-testid="loading-spinner"
                className="h-3 w-3 rounded-full bg-muted animate-pulse"
              />
            ) : (
              <div 
                data-testid="api-status-indicator"
                className={cn(
                  "h-3 w-3 rounded-full",
                  overallStatus === 'healthy' ? "bg-status-success" :
                  overallStatus === 'warning' ? "bg-status-warning" :
                  "bg-status-error"
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
            className="w-full bg-status-warning text-status-error-foreground py-1 px-4 flex items-center justify-between"
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
            <div className="bg-muted p-4 border-t border-status-warning dev-bar-content absolute bottom-full w-full">
              <h3 className="font-semibold text-foreground mb-2">{t('health.debugInfo')}</h3>
              <div className="grid grid-cols-2 gap-2 text-sm">
                <div className="text-muted-foreground">{t('health.environment')}:</div>
                <div className="text-foreground">{displayOverallHealth?.environment || 'unknown'}</div>
                
                <div className="text-muted-foreground">{t('health.version')}:</div>
                <div className="text-foreground">{displayOverallHealth?.version || 'unknown'}</div>
                
                <div className="text-muted-foreground">{t('health.databaseStatus')}:</div>
                <div className={cn(
                  displayOverallHealth?.database?.status === 'connected' ? 'text-primary' : 'text-destructive'
                )}>
                  {displayOverallHealth?.database?.status === 'connected' ? 'Connected' : 'Disconnected'}
                </div>
                
                <div className="text-muted-foreground">{t('health.gitBranch')}:</div>
                <div className="text-foreground">{gitBranch?.branch || gitBranch?.error || 'local'}</div>
                
                <div className="text-muted-foreground">{t('health.apiAvailable')}:</div>
                <div className={apiAvailable ? 'text-primary' : 'text-destructive'}>
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