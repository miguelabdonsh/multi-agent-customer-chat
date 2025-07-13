export interface Message {
  content: string;
  type: "user" | "system";
  agent_type?: string;
}

export class WebSocketClient {
  private ws: WebSocket | null = null;
  private url: string;
  
  constructor(url: string = "ws://localhost:8000/ws") {
    this.url = url;
  }
  
  /**
   * Establish WebSocket connection
   */
  connect(
    onMessage: (message: Message) => void,
    onOpen: () => void,
    onClose: () => void
  ): void {
    this.ws = new WebSocket(this.url);

    this.ws.onopen = () => {
      console.log("WebSocket connected");
      onOpen();
    };

    this.ws.onmessage = (event) => {
      const message: Message = JSON.parse(event.data);
      onMessage(message);
    };

    this.ws.onerror = (error) => {
      console.error("WebSocket error:", error);
      onClose(); // Also treat errors as a disconnect
    };

    this.ws.onclose = () => {
      console.log("WebSocket disconnected");
      onClose();
    };
  }
  
  /**
   * Send message to server
   */
  sendMessage(content: string): void {
    if (this.ws?.readyState === WebSocket.OPEN) {
      const message: Omit<Message, "agent_type"> = { content, type: "user" };
      this.ws.send(JSON.stringify(message));
    }
  }
  
  /**
   * Close connection
   */
  disconnect(): void {
    this.ws?.close();
  }
} 