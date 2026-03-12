/**
 * AegisNet JavaScript SDK — Secure AI Infrastructure Control.
 */

export interface AegisMessage {
  role: 'user' | 'assistant' | 'system';
  content: string;
}

export interface AegisChatOptions {
  model?: string;
  routingStrategy?: 'auto' | 'cost_optimized' | 'performance' | 'quality' | 'optimized';
  maxTokens?: number;
  temperature?: number;
  userId?: string;
}

export class AegisNet {
  private apiKey: string;
  private baseUrl: string;

  constructor(apiKey: string, baseUrl: string = 'http://localhost:8000') {
    this.apiKey = apiKey;
    this.baseUrl = baseUrl.replace(/\/$/, '');
  }

  /**
   * Send a chat request to AegisNet.
   */
  async chat(messages: AegisMessage[], options: AegisChatOptions = {}): Promise<any> {
    const response = await fetch(`${this.baseUrl}/api/v1/chat`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${this.apiKey}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        messages,
        model: options.model,
        routing_strategy: options.routingStrategy || 'auto',
        max_tokens: options.maxTokens || 1024,
        temperature: options.temperature || 0.7,
        user_id: options.userId || 'anonymous',
      }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(`AegisNet Error: ${error.detail || response.statusText}`);
    }

    return response.json();
  }

  /**
   * Stream a chat response from AegisNet using Server-Sent Events.
   */
  async *stream(messages: AegisMessage[], options: AegisChatOptions = {}): AsyncIterableIterator<string> {
    const response = await fetch(`${this.baseUrl}/api/v1/chat/stream`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${this.apiKey}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        messages,
        model: options.model,
        routing_strategy: options.routingStrategy || 'auto',
        max_tokens: options.maxTokens || 1024,
        temperature: options.temperature || 0.7,
        user_id: options.userId || 'anonymous',
      }),
    });

    if (!response.ok) {
      throw new Error(`AegisNet Streaming Error: ${response.statusText}`);
    }

    const reader = response.body?.getReader();
    if (!reader) throw new Error('Response body is null');

    const decoder = new TextDecoder();
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      const chunk = decoder.decode(value);
      const lines = chunk.split('\n');
      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const content = line.slice(6).trim();
          if (content) yield content;
        }
      }
    }
  }
}
