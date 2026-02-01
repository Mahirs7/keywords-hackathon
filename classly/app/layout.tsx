import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "StudyHub - Your Unified Learning Dashboard",
  description: "All your coursework from Canvas, Gradescope, PrairieLearn, and more in one place.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body className={`${inter.className} bg-[#0a0e13] text-white antialiased`}>
        {children}
      </body>
    </html>
  );
}
