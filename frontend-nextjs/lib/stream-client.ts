/**
 * Streaming API client — consumes SSE from /api/v2/stream
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';

export interface StreamCallbacks {
  onStatus?: (status: string) => void;
  onToken?: (token: string) => void;
  onSources?: (sources: any[], metadata: any, disclaimer: string) => void;
  onDone?: (totalMs: number) => void;
  onError?: (error: string) => void;
}

/**
 * Stream a query via SSE.
 * Returns a cleanup function to abort the stream.
 */
export function streamQuery(
  question: string,
  sessionId: string,
  callbacks: StreamCallbacks,
  domain: string = 'all'
): () => void {
  const url = new URL(`${API_BASE_URL}/api/v2/query/stream`);
  url.searchParams.set('question', question);
  url.searchParams.set('domain', domain);
  if (sessionId) url.searchParams.set('session_id', sessionId);

  // We need to pass auth token — for now use the same token storage as existing client
  const token = typeof window !== 'undefined' ? localStorage.getItem('auth_token') || 'local-test-key' : 'local-test-key';

  const controller = new AbortController();

  const run = async () => {
    try {
      const response = await fetch(url.toString(), {
        headers: { 
          'Authorization': `Bearer ${token}`,
          'X-API-Key': token // Support both if needed
        },
        signal: controller.signal,
      });

      if (!response.ok || !response.body) {
        const errorData = await response.json().catch(() => ({}));
        callbacks.onError?.(errorData.error || `HTTP ${response.status}`);
        return;
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() ?? '';   // keep incomplete last line

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6));
              const type = data.type;
              
              switch (type) {
                case 'status':
                  callbacks.onStatus?.(data.message);
                  break;
                case 'chunk':
                case 'token':
                  callbacks.onToken?.(data.content || data.token);
                  break;
                case 'sources':
                  callbacks.onSources?.(data.sources ?? [], {}, '');
                  break;
                case 'metadata':
                  // Optionally handle metadata if onSources wasn't enough
                  break;
                case 'disclaimer':
                  // Add disclaimer when it arrives
                  callbacks.onToken?.('\n\n---\n*' + data.content + '*');
                  break;
                case 'done':
                  callbacks.onDone?.(0);
                  break;
                case 'correction':
                  // Append validation correction to token stream
                  callbacks.onToken?.('\n\n' + data.message);
                  break;
                case 'error':
                  callbacks.onError?.(data.error ?? 'Unknown error');
                  break;
              }
            } catch {
              // ignore parse errors on malformed data lines
            }
          }
        }
      }
    } catch (err: any) {
      if (err?.name !== 'AbortError') {
        callbacks.onError?.(err?.message ?? 'Stream error');
      }
    }
  };

  run();
  return () => controller.abort();
}
