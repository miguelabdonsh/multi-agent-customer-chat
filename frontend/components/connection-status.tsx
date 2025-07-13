"use client";

interface ConnectionStatusProps {
  isConnected: boolean;
}

export default function ConnectionStatus({ isConnected }: ConnectionStatusProps) {
  return (
    <div className="text-sm text-gray-500">
      Status:{" "}
      <span className={isConnected ? "text-green-600" : "text-red-600"}>
        {isConnected ? "Connected" : "Disconnected"}
      </span>
    </div>
  );
} 