import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "AI Diagnosis Council",
  description: "Phase 1 mock AI diagnosis report MVP",
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
