/**
 * LegalFinanceAI Frontend - Type Definitions
 */

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  sources?: Source[];
  timestamp: Date;
  error?: string;
  isSafetyBlock?: boolean;
  metadata?: QueryResponse['metadata'];
}

export interface Source {
  reference_id: number;
  source: string;
  domain: string;
  origin: 'system' | 'user';
  relevance_score: number;
  excerpt: string;
  citation_spans?: Array<{
    claim: string;
    start: number;
    end: number;
  }>;
}

export interface QueryResponse {
  success: boolean;
  question: string;
  domain: string;
  answer: string;
  sources: Source[];
  validation: {
    overall_valid: boolean;
    has_citations: boolean;
    has_disclaimer: boolean;
    issues: string[];
  };
  metadata: {
    model: string;
    token_usage: {
      prompt_tokens: number;
      completion_tokens: number;
      total_tokens: number;
    };
    total_time_ms: number;
    tool_calls?: Array<{
      tool: string;
      args: any;
      result: any;
    }>;
    [key: string]: any;
  };
  error?: string;
  error_type?: string;
  timestamp: string;
}

export interface UploadResponse {
  success: boolean;
  filename: string;
  chunks_created?: number;
  session_id?: string;
  message?: string;
  error?: string;
}

export interface HealthResponse {
  status: 'healthy' | 'degraded' | 'unhealthy';
  timestamp: string;
  checks: {
    [key: string]: {
      status: 'healthy' | 'unhealthy';
      latency_ms: number;
      message: string;
    };
  };
}

export interface HealthStatus {
  status: 'online' | 'offline' | 'checking';
  checks: HealthResponse['checks'];
  lastChecked: Date | null;
}

export interface UploadedFile {
  name: string;
  size: number;
  type: string;
  uploadedAt: Date;
}

export interface ToastNotification {
  id: string;
  type: 'success' | 'error' | 'info' | 'warning';
  message: string;
  duration?: number;
}
