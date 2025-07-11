import { Message } from "@/lib/websocket";

interface ChatInterfaceProps {
  messages: Message[];
}

export default function ChatInterface({ messages }: ChatInterfaceProps) {
  return (
    <div className="flex-1 overflow-y-auto p-4 space-y-4">
      {messages.length === 0 ? (
        <div className="text-gray-500 text-center">
          No messages yet. Start the conversation!
        </div>
      ) : (
        messages.map((message, index) => {
          if (message.agent_type === "escalation") {
            return (
              <div
                key={index}
                className="p-3 my-2 text-center text-sm text-yellow-800 bg-yellow-100 border-l-4 border-yellow-500 rounded-md shadow-sm"
              >
                <p>
                  <span className="font-bold">Escalation Queued:</span>{" "}
                  {message.content}
                </p>
              </div>
            );
          }
          return (
            <div
              key={index}
              className={`flex items-end gap-2 ${
                message.type === "user" ? "justify-end" : "justify-start"
              }`}
            >
              <div
                className={`px-4 py-2 rounded-lg max-w-xs md:max-w-md shadow-sm ${
                  message.type === "user"
                    ? "bg-blue-500 text-white"
                    : "bg-white text-gray-800"
                }`}
              >
                <div className="text-xs opacity-75 mb-1 capitalize">
                  {message.type === "user" ? "You" : message.agent_type || "System"}
                </div>
                <div>{message.content}</div>
              </div>
            </div>
          );
        })
      )}
    </div>
  );
} 