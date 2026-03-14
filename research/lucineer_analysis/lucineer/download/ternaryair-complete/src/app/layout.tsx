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
  title: "TernaryAir - Open Source Mask-Locked Ternary Inference Hardware",
  description: "The hardware boundary between you and AI. Open-source ternary inference chip for secure, private, and affordable AI inference. MIT License.",
  keywords: [
    "AI",
    "hardware",
    "inference",
    "ternary",
    "BitNet",
    "air-gapped",
    "privacy",
    "security",
    "open source",
    "FPGA",
    "RTL",
    "mask-locked",
    "edge AI",
    "local LLM",
  ],
  authors: [{ name: "Casey DiGennaro", url: "https://superinstance.ai" }],
  openGraph: {
    title: "TernaryAir - Open Source Mask-Locked Ternary Inference Hardware",
    description: "The hardware boundary between you and AI. $99, 100+ tok/s, 3-5W USB. MIT licensed.",
    type: "website",
    locale: "en_US",
    images: [{ url: "/og-image.png", width: 1200, height: 630 }],
  },
  twitter: {
    card: "summary_large_image",
    title: "TernaryAir - Open Source Mask-Locked Inference Hardware",
    description: "The hardware boundary between you and AI. $99, 100+ tok/s, 3-5W USB.",
    creator: "@superinstance",
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
        className={`${inter.variable} ${jetbrainsMono.variable} font-sans bg-[#050505] text-white antialiased`}
      >
        <Navigation />
        <main className="min-h-screen">{children}</main>
        <Footer />
      </body>
    </html>
  );
}
