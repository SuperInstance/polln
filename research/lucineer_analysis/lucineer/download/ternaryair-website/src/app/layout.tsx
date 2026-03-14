import type { Metadata } from "next";
import { Inter, JetBrains_Mono } from "next/font/google";
import "./globals.css";
import Navigation from "@/components/Navigation";
import Footer from "@/components/Footer";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
});

const jetbrainsMono = JetBrains_Mono({
  subsets: ["latin"],
  variable: "--font-jetbrains",
});

export const metadata: Metadata = {
  title: "TernaryAir - Open Source Air-Gapped Ternary Inference Hardware",
  description:
    "The hardware boundary between you and AI. Open-source ternary inference engine for secure, private, and affordable AI inference.",
  keywords: [
    "AI",
    "hardware",
    "inference",
    "ternary",
    "air-gapped",
    "privacy",
    "security",
    "open source",
    "FPGA",
    "RTL",
  ],
  authors: [{ name: "Casey DiGennaro", url: "https://superinstance.ai" }],
  openGraph: {
    title: "TernaryAir - Open Source Air-Gapped Ternary Inference Hardware",
    description:
      "The hardware boundary between you and AI. Open-source ternary inference engine for secure, private, and affordable AI inference.",
    type: "website",
    locale: "en_US",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body
        className={`${inter.variable} ${jetbrainsMono.variable} font-sans bg-dark-900 text-white antialiased`}
      >
        <Navigation />
        <main className="min-h-screen">{children}</main>
        <Footer />
      </body>
    </html>
  );
}
