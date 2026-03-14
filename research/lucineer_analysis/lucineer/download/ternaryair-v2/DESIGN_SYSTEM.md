# TernaryAir Design System Documentation
## Version 2.0 - Comprehensive Style Guide

**Last Updated:** March 2026  
**Design Philosophy:** Offline-first, accessible, engaging for all ages

---

## Section 1: Brand Philosophy

### Core Principles

1. **Offline-First**: Everything works immediately on load. No API required to start learning.
2. **Playful Professional**: Fun enough for kids, serious enough for engineers.
3. **Progressive Depth**: Same concepts scale from age 4 to professional.
4. **Open Everything**: Every module downloadable, modifiable, shareable.
5. **Visual Embodiment**: Concepts should be innately understood through visuals.

### The Viral Hook Strategy

**First 3 Seconds:**
- Hero animation captures attention
- Clear value proposition visible
- Interactive element tempts click
- Download button prominently placed

**First 30 Seconds:**
- Try a mini-simulator without signup
- See something visually rewarding
- Understand what the site offers
- Have a reason to share

**First 5 Minutes:**
- Complete a learning module
- Download something useful
- Connect to their first API (optional)
- Bookmark or share with a friend

---

## Section 2: Color System

### Primary Palette

```css
/* Brand Greens - Growth, Learning, Go */
--green-400: #4ade80;  /* Accents, highlights */
--green-500: #22c55e;  /* Primary actions */
--green-600: #16a34a;  /* Hover states */

/* Dark Theme - Professional, Focused */
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

### Age Group Accent Colors

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

### Semantic Colors

```css
/* Status Indicators */
--success: #22c55e;     /* Completed, safe */
--warning: #f59e0b;     /* Attention needed */
--error:   #ef4444;     /* Failure, danger */
--info:    #3b82f6;     /* Information */

/* Technical Indicators */
--timing-good:    #22c55e;  /* Timing met */
--timing-warning: #f59e0b;  /* Close to limit */
--timing-violate: #ef4444;  /* Timing violation */

/* Simulator States */
--state-idle:    #64748b;  /* Waiting */
--state-active:  #3b82f6;  /* Running */
--state-success: #22c55e;  /* Completed */
--state-fail:    #ef4444;  /* Error */
```

---

## Section 3: Typography

### Font Stack

```css
/* Primary: System fonts for performance */
--font-sans: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, 
             Oxygen, Ubuntu, Cantarell, sans-serif;

/* Monospace: Code and technical content */
--font-mono: "SF Mono", "Fira Code", "JetBrains Mono", 
             Consolas, "Liberation Mono", monospace;

/* Display: Headlines and hero text */
--font-display: var(--font-sans); /* System font for offline */
```

### Type Scale

```css
/* Mobile-first scale (base: 16px) */
--text-xs:   0.75rem;    /* 12px - Captions, labels */
--text-sm:   0.875rem;   /* 14px - Body small, meta */
--text-base: 1rem;       /* 16px - Body text */
--text-lg:   1.125rem;   /* 18px - Lead paragraphs */
--text-xl:   1.25rem;    /* 20px - Subheadings */
--text-2xl:  1.5rem;     /* 24px - Section headings */
--text-3xl:  1.875rem;   /* 30px - Page headings */
--text-4xl:  2.25rem;    /* 36px - Hero secondary */
--text-5xl:  3rem;       /* 48px - Hero primary */
--text-6xl:  3.75rem;    /* 60px - Display large */
--text-7xl:  4.5rem;     /* 72px - Hero headline */

/* Line Heights */
--leading-tight:  1.25;
--leading-normal: 1.5;
--leading-relaxed: 1.625;
--leading-loose:  2;
```

### Typography Usage

| Element | Size | Weight | Color | Use Case |
|---------|------|--------|-------|----------|
| Hero Title | 7xl | 700 | gradient | Main headline |
| Section Title | 3xl | 600 | white | Section headers |
| Card Title | xl | 600 | accent | Card headers |
| Body | base | 400 | gray-300 | Paragraphs |
| Caption | sm | 400 | gray-500 | Labels, hints |
| Code | sm | 400 | green-400 | Code blocks |
| Button | sm | 500 | white | Actions |

---

## Section 4: Spacing System

### Scale (8px base)

```css
--space-0:   0;       /* 0px */
--space-0.5: 0.125rem; /* 2px */
--space-1:   0.25rem;  /* 4px */
--space-1.5: 0.375rem; /* 6px */
--space-2:   0.5rem;   /* 8px */
--space-2.5: 0.625rem; /* 10px */
--space-3:   0.75rem;  /* 12px */
--space-3.5: 0.875rem; /* 14px */
--space-4:   1rem;     /* 16px */
--space-5:   1.25rem;  /* 20px */
--space-6:   1.5rem;   /* 24px */
--space-7:   1.75rem;  /* 28px */
--space-8:   2rem;     /* 32px */
--space-9:   2.25rem;  /* 36px */
--space-10:  2.5rem;   /* 40px */
--space-12:  3rem;     /* 48px */
--space-14:  3.5rem;   /* 56px */
--space-16:  4rem;     /* 64px */
--space-20:  5rem;     /* 80px */
--space-24:  6rem;     /* 96px */
--space-32:  8rem;     /* 128px */
```

### Component Spacing

```css
/* Section Padding */
--section-py: var(--space-20);  /* 80px vertical */
--section-px: var(--space-4);   /* 16px horizontal */

/* Card Padding */
--card-p: var(--space-6);       /* 24px */

/* Button Padding */
--btn-py: var(--space-2.5);     /* 10px vertical */
--btn-px: var(--space-5);       /* 20px horizontal */

/* Input Padding */
--input-py: var(--space-2);     /* 8px vertical */
--input-px: var(--space-3);     /* 12px horizontal */
```

---

## Section 5: Component Library

### Buttons

```css
/* Primary Button */
.btn-primary {
  background: linear-gradient(135deg, var(--green-600), var(--green-500));
  color: white;
  padding: var(--btn-py) var(--btn-px);
  border-radius: var(--radius-lg);
  font-weight: 500;
  transition: all 0.2s;
  box-shadow: 0 0 20px rgba(34, 197, 94, 0.3);
}

.btn-primary:hover {
  box-shadow: 0 0 30px rgba(34, 197, 94, 0.5);
  transform: translateY(-1px);
}

/* Secondary Button */
.btn-secondary {
  background: var(--dark-700);
  color: white;
  padding: var(--btn-py) var(--btn-px);
  border-radius: var(--radius-lg);
  border: 1px solid var(--dark-600);
  transition: all 0.2s;
}

.btn-secondary:hover {
  background: var(--dark-600);
  border-color: var(--dark-500);
}

/* Ghost Button */
.btn-ghost {
  background: transparent;
  color: var(--gray-400);
  padding: var(--btn-py) var(--btn-px);
  border-radius: var(--radius-lg);
  transition: all 0.2s;
}

.btn-ghost:hover {
  background: var(--dark-700);
  color: white;
}
```

### Cards

```css
/* Standard Card */
.card {
  background: var(--dark-800);
  border-radius: var(--radius-xl);
  border: 1px solid var(--dark-600);
  padding: var(--card-p);
  transition: all 0.3s;
}

.card:hover {
  border-color: var(--green-500);
  transform: translateY(-4px);
}

/* Glass Card (for overlays) */
.card-glass {
  background: rgba(52, 53, 65, 0.8);
  backdrop-filter: blur(12px);
  border-radius: var(--radius-xl);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

/* Feature Card */
.card-feature {
  background: linear-gradient(135deg, 
    rgba(34, 197, 94, 0.05) 0%, 
    transparent 50%);
  border-radius: var(--radius-xl);
  border: 1px solid var(--dark-600);
  padding: var(--card-p);
}
```

### Code Blocks

```css
.code-block {
  background: var(--dark-900);
  border-radius: var(--radius-lg);
  border: 1px solid var(--dark-600);
  overflow: hidden;
}

.code-header {
  display: flex;
  align-items: center;
  padding: var(--space-3) var(--space-4);
  background: var(--dark-700);
  border-bottom: 1px solid var(--dark-600);
}

.code-dots {
  display: flex;
  gap: var(--space-2);
}

.code-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
}

.code-dot-red   { background: #ef4444; }
.code-dot-yellow { background: #f59e0b; }
.code-dot-green { background: #22c55e; }

.code-content {
  padding: var(--space-5);
  font-family: var(--font-mono);
  font-size: var(--text-sm);
  overflow-x: auto;
}
```

---

## Section 6: Animation System

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
/* Fade In */
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

/* Slide Up */
@keyframes slideUp {
  from { 
    opacity: 0; 
    transform: translateY(20px); 
  }
  to { 
    opacity: 1; 
    transform: translateY(0); 
  }
}

/* Scale In */
@keyframes scaleIn {
  from { 
    opacity: 0; 
    transform: scale(0.95); 
  }
  to { 
    opacity: 1; 
    transform: scale(1); 
  }
}

/* Pulse Glow */
@keyframes pulseGlow {
  0%, 100% { 
    box-shadow: 0 0 20px rgba(34, 197, 94, 0.3); 
  }
  50% { 
    box-shadow: 0 0 40px rgba(34, 197, 94, 0.6); 
  }
}

/* Gradient Shift */
@keyframes gradientShift {
  0%, 100% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
}

/* Float */
@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-20px); }
}

/* Signal Pulse (for simulators) */
@keyframes signalPulse {
  0% { transform: scaleX(0); opacity: 1; }
  100% { transform: scaleX(1); opacity: 0; }
}
```

---

## Section 7: Layout Patterns

### Container Widths

```css
--container-sm:  640px;
--container-md:  768px;
--container-lg:  1024px;
--container-xl:  1280px;
--container-2xl: 1536px;
--container-prose: 65ch;
```

### Grid System

```css
/* Standard Grid */
.grid-auto {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: var(--space-6);
}

/* Feature Grid (3 columns) */
.grid-features {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--space-6);
}

@media (max-width: 1024px) {
  .grid-features {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 640px) {
  .grid-features {
    grid-template-columns: 1fr;
  }
}

/* Dashboard Grid */
.grid-dashboard {
  display: grid;
  grid-template-columns: 280px 1fr;
  gap: var(--space-6);
  min-height: 100vh;
}

@media (max-width: 1024px) {
  .grid-dashboard {
    grid-template-columns: 1fr;
  }
}
```

---

## Section 8: Accessibility Guidelines

### Color Contrast

- All text must meet WCAG AA standards (4.5:1 for body, 3:1 for large)
- Interactive elements must have visible focus states
- Never rely on color alone to convey information

### Focus States

```css
/* Keyboard Focus */
:focus-visible {
  outline: 2px solid var(--green-400);
  outline-offset: 2px;
}

/* Skip Link */
.skip-link {
  position: absolute;
  top: -40px;
  left: 0;
  padding: var(--space-2) var(--space-4);
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
/* Visually Hidden (screen reader only) */
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

## Section 9: Age-Specific Design Patterns

### Young Learners (4-10)

**Visual Style:**
- Larger touch targets (min 44px)
- Brighter, warmer colors
- More rounded corners (radius-xl)
- Animated characters and mascots
- Celebratory feedback animations

**Interaction:**
- Simple gestures (tap, drag)
- Immediate visual feedback
- No text-heavy content
- Audio cues optional
- Progress stars and badges

**Layout:**
- Larger fonts (scale +20%)
- More white space
- Fewer options per screen
- Bigger buttons

### Middle School (11-14)

**Visual Style:**
- Cool, tech-inspired colors
- Moderate complexity
- Achievement systems visible
- Social elements introduced

**Interaction:**
- Keyboard shortcuts introduced
- Code snippets appear
- Multi-step challenges
- Leaderboards visible

### High School (15-18)

**Visual Style:**
- Technical aesthetic
- Real code examples
- Career connections shown
- Project-based learning

**Interaction:**
- Full keyboard support
- Git-like version concepts
- Export/save functionality
- Collaboration features

### Professional (18+)

**Visual Style:**
- Efficient, minimal
- Data-dense acceptable
- Dark mode default
- Technical accuracy paramount

**Interaction:**
- Keyboard-first design
- CLI alternatives
- API integration
- Export to professional tools

---

## Section 10: Offline-First Architecture

### Service Worker Strategy

```javascript
// Cache-first for static assets
// Network-first for API calls (with fallback)
// IndexedDB for user data

const CACHE_NAME = 'ternaryair-v1';
const STATIC_ASSETS = [
  '/',
  '/learning',
  '/timing-playground',
  '/downloads',
  '/offline.html',
];

// Install: Cache static assets
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(STATIC_ASSETS);
    })
  );
});

// Fetch: Cache-first strategy
self.addEventListener('fetch', (event) => {
  event.respondWith(
    caches.match(event.request).then((response) => {
      return response || fetch(event.request);
    })
  );
});
```

### Local Storage Schema

```typescript
interface TernaryAirStorage {
  // User Settings
  settings: {
    theme: 'dark' | 'light' | 'system';
    ageGroup: 'young' | 'middle' | 'high' | 'pro';
    soundEnabled: boolean;
    animationsEnabled: boolean;
  };

  // Progress Tracking
  progress: {
    lessonsCompleted: string[];
    achievements: string[];
    totalTime: number;
    lastVisit: string;
  };

  // API Connections (encrypted)
  apiKeys: {
    provider: string;
    key: string; // Encrypted
    addedAt: string;
  }[];

  // Downloads
  downloads: {
    moduleId: string;
    downloadedAt: string;
    version: string;
  }[];

  // Community (if age verified)
  community: {
    username: string;
    contributions: string[];
    recognitions: string[];
  } | null;
}
```

---

## Section 11: Download Center Design

### Module Download Card

```html
<div class="download-card">
  <div class="download-icon">
    <!-- Module icon SVG -->
  </div>
  <div class="download-info">
    <h3 class="download-title">Traffic Light Simulator</h3>
    <p class="download-size">2.4 MB</p>
    <div class="download-meta">
      <span>v1.2.0</span>
      <span>•</span>
      <span>Standalone HTML</span>
    </div>
  </div>
  <button class="download-btn">
    <DownloadIcon />
    Download
  </button>
</div>
```

### Download Categories

1. **Complete Package** - Full site, all modules, all docs
2. **Simulators** - Individual interactive tools
3. **Learning Modules** - Age-specific lessons
4. **Documentation** - Research papers, guides
5. **Source Code** - Full repository
6. **Offline Pack** - Minimal for offline use

---

## Section 12: API Connection Hub Design

### Provider Cards

```html
<div class="api-provider-card">
  <div class="provider-logo">
    <!-- Provider logo SVG -->
  </div>
  <div class="provider-info">
    <h3>OpenAI</h3>
    <p class="provider-type">GPT-4, DALL-E, Embeddings</p>
    <div class="provider-status">
      <span class="status-dot connected"></span>
      Connected
    </div>
  </div>
  <button class="configure-btn">Configure</button>
</div>
```

### Provider Categories

**Free Tiers:**
- Groq (fast inference)
- x.ai (Grok access)
- HuggingFace (open models)

**Low Cost:**
- DeepSeek ($0.14/1M tokens)
- z.ai
- Kimi.ai
- Mini.ai

**Major Players:**
- OpenAI
- Anthropic
- Google AI
- Mistral

**Local:**
- Ollama (fully offline)
- LM Studio
- LocalAI

### Connection Flow

1. User clicks "Connect"
2. Modal opens with instructions
3. User enters API key
4. Key encrypted and stored locally
5. Test call validates connection
6. Status updates to "Connected"

---

## Section 13: Research Hub Design

### Document Card

```html
<article class="research-card">
  <div class="research-type">Technical Report</div>
  <h3 class="research-title">
    Kimi Swarm Research Report v13
  </h3>
  <p class="research-excerpt">
    Comprehensive analysis of BitNet, Taalas, iFairy, and 
    FPGA implementations for mask-locked inference chips...
  </p>
  <div class="research-meta">
    <span class="research-date">March 2026</span>
    <span class="research-pages">47 pages</span>
    <div class="research-tags">
      <span class="tag">FPGA</span>
      <span class="tag">BitNet</span>
      <span class="tag">Edge AI</span>
    </div>
  </div>
  <div class="research-actions">
    <button>Read Online</button>
    <button>Download PDF</button>
  </div>
</article>
```

### Research Categories

1. **Technical Deep Dives** - Chip architecture, timing analysis
2. **Market Research** - Competitive analysis, pricing
3. **Educational Research** - Pedagogy, learning science
4. **Community Papers** - User contributions

---

## Section 14: Community Features Design

### Recognition System

**Badge Types:**
- 🎓 Learner - Completed first module
- 🚀 Explorer - Downloaded offline pack
- 🔧 Builder - Contributed code
- 📚 Teacher - Created educational content
- 🌟 Star - Community recognition

### Contribution Flow

1. User creates improvement/modification
2. Submits via GitHub PR or community form
3. Review by maintainers
4. Merge and recognition awarded
5. Contributor badge updated

### Age Verification

For Cloudflare sync and community features:
- Terms of service agreement
- Age confirmation checkbox
- Optional ID verification via Cloudflare
- Parental consent flow for under 18

---

## Section 15: Performance Targets

### Core Web Vitals

| Metric | Target | Threshold |
|--------|--------|-----------|
| LCP | < 1.5s | < 2.5s |
| FID | < 50ms | < 100ms |
| CLS | < 0.1 | < 0.25 |
| TTI | < 2s | < 3.8s |
| TBT | < 150ms | < 300ms |

### Optimization Strategies

1. **Code Splitting** - Route-based chunks
2. **Image Optimization** - WebP, AVIF, lazy loading
3. **Font Loading** - System fonts, subset custom fonts
4. **Critical CSS** - Inline above-fold styles
5. **Tree Shaking** - Remove unused code
6. **Compression** - Brotli, gzip

---

## Appendix A: Icon System

Use Lucide React icons throughout:
- Navigation: Home, Book, Cpu, Settings, Download
- Actions: Play, Pause, Refresh, Download, Upload
- Status: Check, X, AlertTriangle, Info
- Social: Github, Twitter, Linkedin, Mail

---

## Appendix B: Writing Style

### Voice

- **Approachable**: No jargon without explanation
- **Encouraging**: Celebrate progress, normalize mistakes
- **Precise**: Technical accuracy when needed
- **Inclusive**: Diverse examples and representation

### Microcopy

- Buttons: Action verbs ("Start Learning", "Download Now")
- Errors: Solution-focused ("Try refreshing the page")
- Success: Celebratory ("Awesome! You completed the module!")
- Empty states: Encouraging ("Start your journey!")

---

*Document Version: 2.0.0*  
*Maintained by: TernaryAir Design Team*
