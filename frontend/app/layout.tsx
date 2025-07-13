import type { Metadata } from "next";
import './globals.css'

export const metadata: Metadata = {
  title: "Multi-Agent Customer Chat",
  description: "A multi-agent system for customer support with modern AI assistance.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="h-full">
      <head>
        <script src="https://cdn.tailwindcss.com"></script>
      </head>
      <body className="h-full antialiased bg-gradient-to-br from-slate-900 via-blue-900 to-indigo-900 text-white">
        {children}
      </body>
    </html>
  );
}