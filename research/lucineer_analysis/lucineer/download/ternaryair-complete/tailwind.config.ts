import type { Config } from 'tailwindcss';

const config: Config = {
  content: [
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
    colors: {
    // Dark theme colors
    dark: {
    50: '#0f0f0f',
  100: '#0a0a0a',
  200: '#0f0f0f',
  300: '#050505',
  400: '#080808',
  500: '#0a0a0a',
  600: '#0f0f0f',
  700: '#1a1a1a',
  800: '#0f0f0f',
  900: '#050505',
  950: '#080808',
  },
    // Primary green
  primary: {
  50: '#166534',
  100: '#15803d',
  200: '#16a34a',
  300: '#22c55e',
  400: '#4ade80',
  500: '#22c55e',
  600: '#16a34a',
  700: '#15803d',
  800: '#166534',
  900: '#14532d',
  },
    },
    fontFamily: {
      sans: ['var(--font-inter)', 'Inter', 'sans-serif'],
      mono: ['var(--font-jetbrains)', 'JetBrains Mono', 'monospace'],
    },
  },
};

export default config;
