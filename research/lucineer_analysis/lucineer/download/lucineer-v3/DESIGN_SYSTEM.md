# Lucineer Design System Documentation
## Version 3.0 - "Become a Lucineer"
## Comprehensive Style Guide & Brand Guidelines

**Last Updated:** March 2026
**Design Philosophy:** Offline-first, accessible, professional yet approachable

---

## Section 1: Brand Identity

### Brand Name: Lucineer

**Pronunciation:** loo-sih-NEER
**Portmanteau:** Lucid + Engineer
**Tagline:** Become a Lucineer

### Brand Pillars

1. **Clarity Through Simplicity** - Complex concepts made intuitive
2. **Progressive Mastery** - From playground to professional
3. **Open Innovation** - Free, open-source, community-driven
4. **Offline-First** - Works anywhere, anytime
5. **AI-Augmented Creation** - Lucineer as co-inventor

### Brand Voice

| Attribute | Do | Don't |
|-----------|-----|-------|
| Approachable | "Let's explore..." | "You must..." |
| Encouraging | "Great progress!" | "You failed..." |
| Precise | Technical accuracy | Oversimplification |
| Inclusive | Diverse examples | Single perspective |
| Professional | Clear, confident | Condescending |

---

## Section 2: Visual Identity

### Logo System

**Primary Logo:**
- Wand2 icon (from Lucide) in gradient container
- Gradient: Green (#22c55e) to Emerald (#10b981)
- Container: Rounded square (border-radius: 12px)

**Logo Usage:**
```
┌─────────────────────────────────────┐
│  [Logo Icon] Lucineer               │
│              Become a Lucineer      │
└─────────────────────────────────────┘
```

### Primary Color Palette

```css
/* Brand Primary - Growth & Innovation */
--green-400: #4ade80;  /* Accents, highlights */
--green-500: #22c55e;  /* Primary actions */
--green-600: #16a34a;  /* Hover states */

/* Brand Secondary - Technology & Depth */
--blue-400: #60a5fa;   /* Secondary accents */
--blue-500: #3b82f6;   /* Links, emphasis */
--blue-600: #2563eb;   /* Hover states */

/* Brand Tertiary - Creativity & Learning */
--purple-400: #a78bfa; /* Creative elements */
--purple-500: #8b5cf6; /* Playful accents */
--purple-600: #7c3aed; /* Deep emphasis */
```

### Dark Theme (Default)

```css
--dark-50:  #f7f7f8;   /* Light text on dark */
--dark-100: #ececf1;   /* Subtle text */
--dark-200: #d9d9e3;   /* Borders */
--dark-300: #c5c5d2;   /* Disabled */
--dark-400: #acacbe;   /* Muted */
--dark-500: #8e8ea0;   /* Placeholder */
--dark-600: #565869;   /* Secondary bg */
--dark-700: #40414f;   /* Card bg */
--dark-800: #343541;   /* Panel bg */
--dark-900: #202123;   /* Page bg */
--dark-950: #0d0d0f;   /* Deepest bg */
```

### Age Group Accent System

```css
/* Young Learners (4-10) - Playful, Warm */
--age-young-primary:    #3b82f6;  /* Blue */
--age-young-secondary:  #f59e0b;  /* Amber */
--age-young-accent:     #ec4899;  /* Pink */

/* Middle School (11-14) - Cool, Engaging */
--age-middle-primary:   #8b5cf6;  /* Purple */
--age-middle-secondary: #06b6d4;  /* Cyan */
--age-middle-accent:    #f43f5e;  /* Rose */

/* High School (15-18) - Bold, Technical */
--age-high-primary:     #f59e0b;  /* Amber */
--age-high-secondary:   #10b981;  /* Emerald */
--age-high-accent:      #6366f1;  /* Indigo */

/* Professional (18+) - Serious, Efficient */
--age-pro-primary:      #22c55e;  /* Green */
--age-pro-secondary:    #64748b;  /* Slate */
--age-pro-accent:       #0ea5e9;  /* Sky */
```

---

## Section 3: Typography

### Font Stack

```css
/* Primary: System fonts for performance and offline support */
--font-sans: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
             "Helvetica Neue", Arial, sans-serif;

/* Monospace: Code and technical content */
--font-mono: "SF Mono", "Fira Code", "JetBrains Mono",
             Consolas, "Liberation Mono", monospace;
```

### Type Scale

```css
--text-xs:   0.75rem;    /* 12px - Captions */
--text-sm:   0.875rem;   /* 14px - Body small */
--text-base: 1rem;       /* 16px - Body text */
--text-lg:   1.125rem;   /* 18px - Lead paragraphs */
--text-xl:   1.25rem;    /* 20px - Subheadings */
--text-2xl:  1.5rem;     /* 24px - Section headings */
--text-3xl:  1.875rem;   /* 30px - Page headings */
--text-4xl:  2.25rem;    /* 36px - Hero secondary */
--text-5xl:  3rem;       /* 48px - Hero primary */
--text-6xl:  3.75rem;    /* 60px - Display large */
--text-7xl:  4.5rem;     /* 72px - Hero headline */
```

### Typography Hierarchy

| Element | Size | Weight | Color | Usage |
|---------|------|--------|-------|-------|
| Hero Title | 7xl | 700 | gradient | Main headline |
| Section Title | 3xl | 600 | white | Section headers |
| Card Title | xl | 600 | accent | Card headers |
| Body | base | 400 | gray-300 | Paragraphs |
| Caption | sm | 400 | gray-500 | Labels, hints |
| Code | sm | 400 | green-400 | Code blocks |
| Button | sm | 500 | white | Actions |

---

## Section 4: Component Library

### Buttons

```css
/* Primary Button - Main CTAs */
.btn-primary {
  background: linear-gradient(135deg, #16a34a, #22c55e);
  color: white;
  padding: 10px 20px;
  border-radius: 12px;
  font-weight: 500;
  transition: all 0.2s ease;
  box-shadow: 0 0 20px rgba(34, 197, 94, 0.3);
}

.btn-primary:hover {
  box-shadow: 0 0 30px rgba(34, 197, 94, 0.5);
  transform: translateY(-1px);
}

/* Secondary Button - Alternative actions */
.btn-secondary {
  background: var(--dark-700);
  color: white;
  padding: 10px 20px;
  border-radius: 12px;
  border: 1px solid var(--dark-600);
  transition: all 0.2s ease;
}

/* Ghost Button - Subtle actions */
.btn-ghost {
  background: transparent;
  color: var(--gray-400);
  padding: 10px 20px;
  border-radius: 12px;
  transition: all 0.2s ease;
}
```

### Cards

```css
/* Standard Card */
.card {
  background: var(--dark-800);
  border-radius: 16px;
  border: 1px solid var(--dark-600);
  padding: 24px;
  transition: all 0.3s ease;
}

.card:hover {
  border-color: rgba(34, 197, 94, 0.3);
  transform: translateY(-4px);
}

/* Glass Card - For overlays */
.card-glass {
  background: rgba(52, 53, 65, 0.8);
  backdrop-filter: blur(12px);
  border-radius: 16px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

/* Feature Card - Highlighted content */
.card-feature {
  background: linear-gradient(135deg,
    rgba(34, 197, 94, 0.05) 0%,
    transparent 50%);
  border-radius: 16px;
  border: 1px solid var(--dark-600);
  padding: 24px;
}
```

### Code Blocks

```css
.code-block {
  background: var(--dark-900);
  border-radius: 12px;
  border: 1px solid var(--dark-600);
  overflow: hidden;
}

.code-header {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  background: var(--dark-700);
  border-bottom: 1px solid var(--dark-600);
}

.code-dots {
  display: flex;
  gap: 8px;
}

.code-dot-red   { background: #ef4444; }
.code-dot-yellow { background: #f59e0b; }
.code-dot-green { background: #22c55e; }

.code-content {
  padding: 20px;
  font-family: var(--font-mono);
  font-size: 14px;
  overflow-x: auto;
}
```

---

## Section 5: Animation System

### Timing Functions

```css
--ease-in:      cubic-bezier(0.4, 0, 1, 1);
--ease-out:     cubic-bezier(0, 0, 0.2, 1);
--ease-in-out:  cubic-bezier(0.4, 0, 0.2, 1);
--ease-bounce:  cubic-bezier(0.68, -0.55, 0.265, 1.55);
--ease-elastic: cubic-bezier(0.68, -0.6, 0.32, 1.6);
```

### Duration Scale

```css
--duration-fast:   150ms;  /* Micro-interactions */
--duration-normal: 200ms;  /* Standard transitions */
--duration-slow:   300ms;  /* Complex animations */
--duration-slower: 500ms;  /* Page transitions */
--duration-slowest: 1000ms; /* Hero animations */
```

### Animation Presets

```css
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes slideUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes pulseGlow {
  0%, 100% { box-shadow: 0 0 20px rgba(34, 197, 94, 0.3); }
  50% { box-shadow: 0 0 40px rgba(34, 197, 94, 0.6); }
}

@keyframes gradientShift {
  0%, 100% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
}

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-20px); }
}
```

---

## Section 6: Layout Patterns

### Container Widths

```css
--container-sm:  640px;
--container-md:  768px;
--container-lg:  1024px;
--container-xl:  1280px;
--container-2xl: 1536px;
```

### Spacing System (8px base)

```css
--space-1:  4px;
--space-2:  8px;
--space-3:  12px;
--space-4:  16px;
--space-5:  20px;
--space-6:  24px;
--space-8:  32px;
--space-10: 40px;
--space-12: 48px;
--space-16: 64px;
--space-20: 80px;
--space-24: 96px;
```

---

## Section 7: Accessibility

### Focus States

```css
:focus-visible {
  outline: 2px solid var(--green-400);
  outline-offset: 2px;
}

.skip-link {
  position: absolute;
  top: -40px;
  left: 0;
  padding: 8px 16px;
  background: var(--green-500);
  color: white;
  z-index: 100;
}

.skip-link:focus {
  top: 0;
}
```

### Motion Preferences

```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```

### Screen Reader Support

```css
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border-width: 0;
}
```

---

## Section 8: TernaryAir Brand Extension

### Sub-Brand Identity

TernaryAir is the chip design studio within Lucineer. It maintains the parent brand while having distinct identity markers.

**Logo Treatment:**
- Uses Cpu icon (from Lucide)
- Same green gradient as parent
- "TernaryAir" in semi-bold
- "Chip Design Studio" tagline

**Color Usage:**
- Primary: Green (same as Lucineer)
- Secondary: Teal for technical elements
- Accent: Purple for AI features

**Typography Distinction:**
- More monospace usage
- Technical code snippets
- Diagrams and schematics

---

## Section 9: Partner Ecosystem Guidelines

### SuperInstance.AI Integration

**Position:** Footer partner link, low visibility
**Color:** Neutral gray (#6b7280)
**Size:** Small text (12px)

### LucidDreamer.com Integration

**Position:** Footer partner link, low visibility
**Color:** Neutral gray (#6b7280)
**Size:** Small text (12px)

### Partner Link Styling

```css
.partner-link {
  color: #6b7280;
  font-size: 12px;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: color 0.2s ease;
}

.partner-link:hover {
  color: #9ca3af;
}
```

---

## Section 10: Performance Standards

### Core Web Vitals Targets

| Metric | Target | Threshold |
|--------|--------|-----------|
| LCP | < 1.5s | < 2.5s |
| FID | < 50ms | < 100ms |
| CLS | < 0.1 | < 0.25 |
| TTI | < 2s | < 3.8s |

### Optimization Strategies

1. System fonts for instant loading
2. SVG icons (Lucide) for scalability
3. CSS-only animations where possible
4. Lazy loading for below-fold content
5. IndexedDB for offline data

---

## Appendix: Icon System

**Icon Library:** Lucide React

**Core Icons:**
- Navigation: Home, Book, Cpu, Settings, Download
- Actions: Play, Pause, Refresh, Download, Upload
- Status: Check, X, AlertTriangle, Info
- Social: Github, Twitter, Linkedin, Mail
- Brand: Wand2 (Lucineer), Cpu (TernaryAir)

**Icon Sizing:**
- Navigation: 16-20px
- Actions: 16-24px
- Feature highlights: 24-32px
- Hero elements: 32-48px

---

*Document Version: 3.0.0*
*Last Updated: March 2026*
*Maintained by: Lucineer Design Team*
