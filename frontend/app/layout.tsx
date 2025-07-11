import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Multi-Agent Customer Chat",
  description: "A multi-agent system for customer support.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
} 