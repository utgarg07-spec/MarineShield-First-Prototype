/**
 * Real-Time AIS WebSocket Client for MarineShield Frontend
 */

export type ConnectionStatus = 'CONNECTING' | 'CONNECTED' | 'DISCONNECTED' | 'ERROR';

export interface AISWebSocketOptions {
  url?: string;
  onObservation?: (obs: any) => void;
  onStatusChange?: (status: ConnectionStatus) => void;
}

export class AISWebSocketClient {
  private socket: WebSocket | null = null;
  private url: string;
  private onObservation?: (obs: any) => void;
  private onStatusChange?: (status: ConnectionStatus) => void;
  private isIntentionalClose = false;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;

  constructor(options: AISWebSocketOptions = {}) {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.host;
    this.url = options.url || `${protocol}//${host}/api/v1/ws/ais`;
    this.onObservation = options.onObservation;
    this.onStatusChange = options.onStatusChange;
  }

  public connect(): void {
    if (this.socket && (this.socket.readyState === WebSocket.OPEN || this.socket.readyState === WebSocket.CONNECTING)) {
      return;
    }

    this.isIntentionalClose = false;
    this.updateStatus('CONNECTING');

    try {
      this.socket = new WebSocket(this.url);

      this.socket.onopen = () => {
        this.reconnectAttempts = 0;
        this.updateStatus('CONNECTED');
      };

      this.socket.onmessage = (event) => {
        try {
          const payload = JSON.parse(event.data);
          if (payload.type === 'ais_observation' && payload.data && this.onObservation) {
            this.onObservation(payload.data);
          }
        } catch {
          // Ignore malformed WS frames
        }
      };

      this.socket.onerror = () => {
        this.updateStatus('ERROR');
      };

      this.socket.onclose = () => {
        this.updateStatus('DISCONNECTED');
        if (!this.isIntentionalClose && this.reconnectAttempts < this.maxReconnectAttempts) {
          this.reconnectAttempts++;
          setTimeout(() => this.connect(), Math.min(1000 * Math.pow(2, this.reconnectAttempts), 10000));
        }
      };
    } catch {
      this.updateStatus('ERROR');
    }
  }

  public disconnect(): void {
    this.isIntentionalClose = true;
    if (this.socket) {
      this.socket.close();
      this.socket = null;
    }
    this.updateStatus('DISCONNECTED');
  }

  private updateStatus(status: ConnectionStatus): void {
    if (this.onStatusChange) {
      this.onStatusChange(status);
    }
  }
}
