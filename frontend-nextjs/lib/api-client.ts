/**
 * LegalFinanceAI API Client
 * Handles all communication with the FastAPI backend
 */

import { QueryResponse, UploadResponse, HealthResponse } from './types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';
const HEALTH_TIMEOUT = 30000;  // 30s — backend may be loading models or under ingestion load
const QUERY_TIMEOUT = 90000;   // 90 seconds for RAG queries
const UPLOAD_TIMEOUT = 120000; // 2 minutes for file uploads
const HEALTH_RETRY_ATTEMPTS = 3;
const QUERY_RETRY_ATTEMPTS = 2; // Retry on slow queries or network hiccups
const HEALTH_RETRY_DELAY_MS = 3000; // 3s between retries
const QUERY_RETRY_DELAY_MS = 2000;  // 2s between query retries

// Log API configuration on module load
if (typeof window !== 'undefined') {
  console.log(`[API Client] Backend URL: ${API_BASE_URL}`);
}

export class ApiError extends Error {
  constructor(
    public statusCode: number | null,
    public errorType: string,
    message: string
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

async function fetchWithTimeout(
  url: string,
  options: RequestInit & { timeout?: number } = {}
): Promise<Response> {
  const timeout = options.timeout || QUERY_TIMEOUT;
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeout);

  try {
    const response = await fetch(url, {
      ...options,
      signal: controller.signal,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    });
    clearTimeout(timeoutId);
    return response;
  } catch (error) {
    clearTimeout(timeoutId);
    if (error instanceof Error && error.name === 'AbortError') {
      throw new ApiError(null, 'timeout', 'Request timed out. Please try again.');
    }
    throw error;
  }
}

/**
 * Check backend health status with retry logic.
 * Retries up to HEALTH_RETRY_ATTEMPTS times before reporting failure.
 */
export async function checkHealth(): Promise<HealthResponse> {
  let lastError: Error | null = null;

  for (let attempt = 1; attempt <= HEALTH_RETRY_ATTEMPTS; attempt++) {
    try {
      const healthUrl = `${API_BASE_URL}/health`;
      if (attempt === 1) {
        console.log(`[Health Check] Checking: ${healthUrl}`);
      } else {
        console.log(`[Health Check] Retry ${attempt}/${HEALTH_RETRY_ATTEMPTS}...`);
      }

      const response = await fetchWithTimeout(healthUrl, {
        timeout: HEALTH_TIMEOUT,
      });

      if (!response.ok) {
        console.error(`[Health Check] HTTP ${response.status}`);
        throw new ApiError(response.status, 'http_error', `Backend returned HTTP ${response.status}`);
      }

      const data: HealthResponse = await response.json();
      console.log('[Health Check] Backend status:', data.status);
      return data;

    } catch (error) {
      lastError = error instanceof Error ? error : new Error(String(error));

      // If this is an HTTP error (not timeout/network), don't retry
      if (error instanceof ApiError && error.errorType === 'http_error') {
        throw error;
      }

      if (attempt < HEALTH_RETRY_ATTEMPTS) {
        console.warn(
          `[Health Check] Attempt ${attempt} failed: ${lastError.message}. ` +
          `Retrying in ${HEALTH_RETRY_DELAY_MS / 1000}s...`
        );
        await new Promise(resolve => setTimeout(resolve, HEALTH_RETRY_DELAY_MS));
      }
    }
  }

  // All retries exhausted
  const finalMsg = lastError?.message?.includes('timed out')
    ? 'Backend is taking too long to respond. It may be loading models or processing data.'
    : 'Cannot connect to backend. Please ensure the server is running on port 8000.';

  console.error(`[Health Check] All ${HEALTH_RETRY_ATTEMPTS} attempts failed. ${finalMsg}`);
  throw new ApiError(null, 'network_error', finalMsg);
}

/**
 * Send a query to the backend RAG pipeline
 */
export async function sendQuery(
  question: string,
  sessionId: string
): Promise<QueryResponse> {
  let lastError: any = null;

  for (let attempt = 1; attempt <= QUERY_RETRY_ATTEMPTS; attempt++) {
    try {
      const queryUrl = `${API_BASE_URL}/api/v2/query`;
      if (attempt > 1) {
        console.log(`[Query] Retry attempt ${attempt}/${QUERY_RETRY_ATTEMPTS}...`);
      } else {
        console.log(`[Query] Sending to ${queryUrl}`);
      }

      const response = await fetchWithTimeout(queryUrl, {
        method: 'POST',
        body: JSON.stringify({
          question,
          session_id: sessionId,
          use_tools: true, // Ensuring tools are requested
        }),
        timeout: QUERY_TIMEOUT,
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        const errorMsg = errorData.error || errorData.detail || `HTTP ${response.status}`;
        console.error(`[Query] HTTP ${response.status}: ${errorMsg}`);
        
        throw new ApiError(
          response.status,
          errorData.error_type || 'http_error',
          errorMsg
        );
      }

      const data: QueryResponse = await response.json();
      console.log('[Query] Response received:', {
        question: question.substring(0, 30) + (question.length > 30 ? '...' : ''),
        sourceCount: data.sources?.length || 0,
        status: data.success,
      });
      
      return data;

    } catch (error) {
      lastError = error;
      
      // If it's a structural API error (like 404 or 400), don't bother retrying
      if (error instanceof ApiError && error.statusCode && error.statusCode < 500) {
        throw error;
      }

      if (attempt < QUERY_RETRY_ATTEMPTS) {
        const pause = QUERY_RETRY_DELAY_MS * attempt;
        console.warn(`[Query] Attempt ${attempt} failed: ${error instanceof Error ? error.message : 'Unknown error'}. Retrying in ${pause / 1000}s...`);
        await new Promise(resolve => setTimeout(resolve, pause));
      }
    }
  }

  // If we're here, all retries failed
  if (lastError instanceof ApiError) {
    throw lastError;
  }
  
  const errorMsg = lastError instanceof Error ? lastError.message : 'Unknown error';
  if (errorMsg.includes('timed out')) {
    throw new ApiError(null, 'timeout', 'The backend is taking too long to process this query. It may be warming up.');
  }
  throw new ApiError(null, 'network_error', 'Cannot connect to the search engine. Please check your connection.');
}

/**
 * Upload a file to the backend
 */
export async function uploadFile(file: File): Promise<UploadResponse> {
  try {
    const uploadUrl = `${API_BASE_URL}/api/v2/user/upload`;
    console.log(`[Upload] Starting upload of ${file.name}`);

    const formData = new FormData();
    formData.append('file', file);

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), UPLOAD_TIMEOUT);

    const response = await fetch(uploadUrl, {
      method: 'POST',
      body: formData,
      signal: controller.signal,
    });

    clearTimeout(timeoutId);

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      const errorMsg = errorData.error || `HTTP ${response.status}`;
      console.error(`[Upload] HTTP ${response.status}: ${errorMsg}`);
      
      throw new ApiError(response.status, 'http_error', errorMsg);
    }

    const data: UploadResponse = await response.json();
    console.log(`[Upload] Success: ${file.name}`);
    
    return data;
  } catch (error) {
    if (error instanceof ApiError) {
      throw error;
    }

    const errorMsg = error instanceof Error ? error.message : 'Unknown error';
    console.error(`[Upload] Failed: ${errorMsg}`);
    
    if (errorMsg.includes('timed out') || errorMsg.includes('AbortError')) {
      throw new ApiError(null, 'timeout', 'Upload timed out. Please try again.');
    }
    
    throw new ApiError(null, 'network_error', 'Upload failed');
  }
}
