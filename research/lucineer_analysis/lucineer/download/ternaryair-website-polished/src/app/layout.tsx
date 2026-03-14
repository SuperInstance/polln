import type { Metadata } from "next";
import { Inter, JetBrains_Mono } from "next/font/google";
import "./globals.css";
import Navigation from "@/components/Navigation";
import Footer from "@/components/Footer";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
  display: "swap",
});

const jetbrainsMono = JetBrains_Mono({
  subsets: ["latin"],
  variable: "--font-jetbrains",
  display: "swap",
});

export const metadata: Metadata = {
  title: {
    default: "TernaryAir - Open Source Air-Gapped Ternary Inference Hardware",
    template: "%s | TernaryAir",
  },
  description:
    "The hardware boundary between you and AI. Open-source ternary inference engine for secure, private, and affordable AI inference. $99 target price, 100+ tok/s, USB powered.",
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
    "mask-locked",
    "RAU",
    "BitNet",
    "edge AI",
    "local AI",
    "private AI",
    "offline AI",
    "USB AI",
    "MIT license",
  ],
  authors: [{ name: "Casey DiGennaro", url: "https://superinstance.ai" }],
  creator: "Casey DiGennaro",
  publisher: "SuperInstance.AI",
  robots: {
    index: true,
    follow: true,
  },
  openGraph: {
    type: "website",
    locale: "en_US",
    url: "https://ternaryair.com",
    siteName: "TernaryAir",
    title: "TernaryAir - Open Source Air-Gapped Ternary Inference Hardware",
    description:
      "The hardware boundary between you and AI. Open-source ternary inference engine for secure, private, and affordable AI inference.",
    images: [
      {
        url: "/og-image.png",
        width: 1200,
        height: 630,
        alt: "TernaryAir - Hardware Boundary Between You and AI",
      },
    ],
  },
  twitter: {
    card: "summary_large_image",
    title: "TernaryAir - Open Source Air-Gapped Ternary Inference Hardware",
    description:
      "The hardware boundary between you and AI. $99, 100+ tok/s, USB powered, MIT licensed.",
    creator: "@superinstance",
    images: ["/og-image.png"],
  },
  github: "https://github.com/superinstance/ternaryair",
  category: "Technology",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <head>
        <link rel="icon" href="/favicon.ico" sizes="any" />
        <link rel="icon" href="/icon.svg" type="image/svg+xml" />
        <link rel="apple-touch-icon" href="/apple-touch-icon.png" />
        <link rel="manifest" href="/manifest.json" />
      </head>
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
