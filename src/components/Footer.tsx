import React, { useEffect, useState } from 'react';

const Footer: React.FC = () => {
  const [overallHealth, setOverallHealth] = useState<any | null>(null);
  const [healthChecks, setHealthChecks] = useState<any | null>(null);
  const [gitBranch, setGitBranch] = useState<any | null>(null);
  const [apiAvailable, setApiAvailable] = useState<boolean>(false);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    // Initial fetch
    const fetchInitialData = async () => {
      const healthData = await fetchWithRetry(() => fetch('/api/health/'), 3, 500);
      const checksData = await fetchWithRetry(
        () => fetch('/api/v1/monitoring/health-checks/'),
        3,
        500
      );
      const branchData = await fetchWithRetry(
        () => fetch('/api/v1/git/branch/'), // Use v1 endpoint
        3,
        500
      );
      
      if (healthData) {
        setOverallHealth(healthData);
        setApiAvailable(true);
      } else {
        console.error('Health API returned non-JSON content');
        setOverallHealth(null);
        setApiAvailable(false);
      }
      
      if (checksData) {
        setHealthChecks(checksData);
      } else {
        console.error('Health checks API returned non-JSON content');
        setHealthChecks(null);
      }

      if (branchData) {
        setGitBranch(branchData);
      } else {
        console.error('Git branch API returned non-JSON content');
        setGitBranch(null);
      }
      setLoading(false);
    };

    fetchInitialData();
  }, []);

  const fetchWithRetry = async (
    fetcher: () => Promise<Response>,
    retries: number,
    delay: number
  ): Promise<any | null> => {
    let lastError: any = null;
    for (let i = 0; i < retries; i++) {
      try {
        const response = await fetcher();
        if (response.ok) {
          const contentType = response.headers.get('content-type');
          if (contentType && contentType.includes('application/json')) {
            return await response.json();
          }
          // Handle non-JSON but OK responses if necessary, or return null/error
          console.warn('Received non-JSON OK response', response.url);
          return null; // Or throw an error if JSON is strictly required
        }
        // Optionally check for specific status codes if needed
        lastError = new Error(`Request failed with status ${response.status}`);
      } catch (error) {
        lastError = error;
      }
      if (i < retries - 1) {
        await new Promise((resolve) => setTimeout(resolve, delay * Math.pow(2, i)));
      }
    }
    console.error('Fetch failed after retries:', lastError);
    return null;
  };

  return (
    <div>
      {/* Render your footer content here */}
    </div>
  );
};

export default Footer; 