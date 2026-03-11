'use client';

import { useState, useEffect, useCallback, useRef } from 'react';
import { checkHealth, ApiError } from '@/lib/api-client';
import { HealthResponse } from '@/lib/types';

// Delay first check so the page renders before pinging the backend
const INITIAL_CHECK_DELAY_MS = 2000;
// Poll less aggressively when backend may be under load
const POLL_INTERVAL_MS = 90000; // 90 seconds

export function useHealth() {
  const [healthStatus, setHealthStatus] = useState<HealthResponse | null>(null);
  // null = unknown (before first check), true = healthy, false = unhealthy
  const [isHealthy, setIsHealthy] = useState<boolean | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastChecked, setLastChecked] = useState<Date | null>(null);
  const intervalRef = useRef<NodeJS.Timeout | null>(null);
  const initialTimerRef = useRef<NodeJS.Timeout | null>(null);

  const performHealthCheck = useCallback(async () => {
    try {
      const response = await checkHealth();
      setHealthStatus(response);
      // Accept both 'healthy' and 'ok' as valid statuses
      setIsHealthy(response.status === 'healthy' || response.status === 'ok');
      setError(null);
      setLastChecked(new Date());
    } catch (err) {
      const errorMessage =
        err instanceof ApiError ? err.message : 'Health check failed';
      setError(errorMessage);
      setIsHealthy(false);
      console.error('[useHealth] Error:', JSON.stringify(errorMessage));
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    // Wait briefly before the first check — lets the page render first
    initialTimerRef.current = setTimeout(() => {
      performHealthCheck();

      // Then poll on a regular interval
      intervalRef.current = setInterval(() => {
        performHealthCheck();
      }, POLL_INTERVAL_MS);
    }, INITIAL_CHECK_DELAY_MS);

    return () => {
      if (initialTimerRef.current) clearTimeout(initialTimerRef.current);
      if (intervalRef.current) clearInterval(intervalRef.current);
    };
  }, [performHealthCheck]);

  const manualRefresh = useCallback(async () => {
    setIsLoading(true);
    await performHealthCheck();
  }, [performHealthCheck]);

  return {
    // Treat null (unknown) as healthy to avoid blocking the UI during startup
    isHealthy: isHealthy !== false,
    isLoading,
    error,
    healthStatus,
    lastChecked,
    refresh: manualRefresh,
  };
}
