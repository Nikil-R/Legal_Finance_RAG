'use client';

import { useState, useEffect, useCallback, useRef } from 'react';
import { checkHealth, ApiError } from '@/lib/api-client';
import { HealthResponse } from '@/lib/types';

export function useHealth() {
  const [healthStatus, setHealthStatus] = useState<HealthResponse | null>(null);
  const [isHealthy, setIsHealthy] = useState(true);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastChecked, setLastChecked] = useState<Date | null>(null);
  const intervalRef = useRef<NodeJS.Timeout | null>(null);

  const performHealthCheck = useCallback(async () => {
    try {
      const response = await checkHealth();
      setHealthStatus(response);
      setIsHealthy(response.status === 'healthy');
      setError(null);
      setLastChecked(new Date());
    } catch (err) {
      const errorMessage =
        err instanceof ApiError ? err.message : 'Health check failed';
      setError(errorMessage);
      setIsHealthy(false);
      console.error('[useHealth] Error:', errorMessage);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    // Initial check
    performHealthCheck();

    // Poll every 60 seconds
    intervalRef.current = setInterval(() => {
      performHealthCheck();
    }, 60000);

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [performHealthCheck]);

  const manualRefresh = useCallback(async () => {
    setIsLoading(true);
    await performHealthCheck();
  }, [performHealthCheck]);

  return {
    isHealthy,
    isLoading,
    error,
    healthStatus,
    lastChecked,
    refresh: manualRefresh,
  };
}
