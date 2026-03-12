/**
 * Custom Analytics Events Service
 * Tracks user interactions and learning progress
 */

export interface AnalyticsEvent {
  name: string;
  properties?: Record<string, any>;
  timestamp?: number;
}

// Event definitions
export const ANALYTICS_EVENTS = {
  // User interaction events
  TUTORIAL_START: 'tutorial_start',
  TUTORIAL_COMPLETE: 'tutorial_complete',
  DEMO_INTERACTION: 'demo_interaction',
  AGE_GROUP_SELECTED: 'age_group_selected',
  LEARNING_PATH_STARTED: 'learning_path_started',
  WHITE_PAPER_VIEWED: 'white_paper_viewed',
  WHITE_PAPER_DOWNLOADED: 'white_paper_downloaded',
  SPREADSHEET_DEMO_OPENED: 'spreadsheet_demo_opened',
  INTERACTIVE_VISUALIZATION_USED: 'interactive_visualization_used',

  // Engagement events
  SCROLL_DEPTH_50: 'scroll_depth_50',
  SCROLL_DEPTH_75: 'scroll_depth_75',
  SCROLL_DEPTH_100: 'scroll_depth_100',
  TIME_ON_PAGE_30S: 'time_on_page_30s',
  TIME_ON_PAGE_2M: 'time_on_page_2m',
  TIME_ON_PAGE_5M: 'time_on_page_5m',

  // Conversion events
  NEWSLETTER_SIGNUP: 'newsletter_signup',
  FEEDBACK_SUBMITTED: 'feedback_submitted',
  CONTACT_FORM_SUBMITTED: 'contact_form_submitted',

  // Technical events
  ERROR_OCCURRED: 'error_occurred',
  PERFORMANCE_SLOW: 'performance_slow',
  OFFLINE_MODE_ACTIVATED: 'offline_mode_activated',

  // Learning-specific events
  QUIZ_STARTED: 'quiz_started',
  QUIZ_COMPLETED: 'quiz_completed',
  EXERCISE_ATTEMPTED: 'exercise_attempted',
  EXERCISE_COMPLETED: 'exercise_completed',
  CONCEPT_VIEWED: 'concept_viewed',
  VIDEO_PLAYED: 'video_played',
  VIDEO_COMPLETED: 'video_completed',

  // SuperInstance-specific events
  SUPERINSTANCE_CELL_CREATED: 'superinstance_cell_created',
  SUPERINSTANCE_FORMULA_USED: 'superinstance_formula_used',
  CONFIDENCE_CASCADE_TRIGGERED: 'confidence_cascade_triggered',
  PYTHAGOREAN_CALCULATOR_USED: 'pythagorean_calculator_used',
  RATE_BASED_CHANGE_SIMULATED: 'rate_based_change_simulated'
} as const;

/**
 * Track an analytics event
 */
export function trackEvent(event: AnalyticsEvent) {
  const eventData = {
    ...event,
    timestamp: event.timestamp || Date.now(),
    url: window.location.href,
    path: window.location.pathname,
    referrer: document.referrer,
    userAgent: navigator.userAgent.substring(0, 100), // Limit for privacy
    screenResolution: `${window.screen.width}x${window.screen.height}`,
    viewport: `${window.innerWidth}x${window.innerHeight}`
  };

  // Send to Plausible
  if (window.plausible) {
    window.plausible(event.name, { props: event.properties });
  }

  // Store locally for offline tracking
  storeEventLocally(eventData);

  // Send to custom analytics endpoint if configured
  sendToCustomEndpoint(eventData);
}

/**
 * Track a page view
 */
export function trackPageView(path?: string) {
  const pageData = {
    name: 'pageview',
    properties: {
      path: path || window.location.pathname,
      title: document.title
    }
  };

  trackEvent(pageData);
}

/**
 * Track scroll depth
 */
export function trackScrollDepth() {
  let tracked50 = false;
  let tracked75 = false;
  let tracked100 = false;

  const checkScrollDepth = () => {
    const scrollPercentage = (window.scrollY / (document.documentElement.scrollHeight - window.innerHeight)) * 100;

    if (scrollPercentage >= 50 && !tracked50) {
      tracked50 = true;
      trackEvent({ name: ANALYTICS_EVENTS.SCROLL_DEPTH_50 });
    }

    if (scrollPercentage >= 75 && !tracked75) {
      tracked75 = true;
      trackEvent({ name: ANALYTICS_EVENTS.SCROLL_DEPTH_75 });
    }

    if (scrollPercentage >= 100 && !tracked100) {
      tracked100 = true;
      trackEvent({ name: ANALYTICS_EVENTS.SCROLL_DEPTH_100 });
    }
  };

  window.addEventListener('scroll', checkScrollDepth, { passive: true });
}

/**
 * Track time on page
 */
export function trackTimeOnPage() {
  const startTime = Date.now();

  const checkTimeThresholds = () => {
    const timeOnPage = Date.now() - startTime;

    if (timeOnPage >= 30000 && !sessionStorage.getItem('tracked_30s')) {
      sessionStorage.setItem('tracked_30s', 'true');
      trackEvent({ name: ANALYTICS_EVENTS.TIME_ON_PAGE_30S });
    }

    if (timeOnPage >= 120000 && !sessionStorage.getItem('tracked_2m')) {
      sessionStorage.setItem('tracked_2m', 'true');
      trackEvent({ name: ANALYTICS_EVENTS.TIME_ON_PAGE_2M });
    }

    if (timeOnPage >= 300000 && !sessionStorage.getItem('tracked_5m')) {
      sessionStorage.setItem('tracked_5m', 'true');
      trackEvent({ name: ANALYTICS_EVENTS.TIME_ON_PAGE_5M });
      clearInterval(intervalId);
    }
  };

  const intervalId = setInterval(checkTimeThresholds, 1000);

  // Clean up on page unload
  window.addEventListener('beforeunload', () => clearInterval(intervalId));
}

/**
 * Track SuperInstance-specific interactions
 */
export function trackSuperInstanceInteraction(type: string, details?: Record<string, any>) {
  const eventMap: Record<string, string> = {
    'cell_created': ANALYTICS_EVENTS.SUPERINSTANCE_CELL_CREATED,
    'formula_used': ANALYTICS_EVENTS.SUPERINSTANCE_FORMULA_USED,
    'confidence_cascade': ANALYTICS_EVENTS.CONFIDENCE_CASCADE_TRIGGERED,
    'pythagorean_calculator': ANALYTICS_EVENTS.PYTHAGOREAN_CALCULATOR_USED,
    'rate_based_change': ANALYTICS_EVENTS.RATE_BASED_CHANGE_SIMULATED
  };

  const eventName = eventMap[type];
  if (eventName) {
    trackEvent({ name: eventName, properties: details });
  }
}

/**
 * Track educational progress
 */
export function trackLearningProgress(event: string, lessonId?: string, score?: number) {
  const properties: Record<string, any> = {};

  if (lessonId) properties.lessonId = lessonId;
  if (score !== undefined) properties.score = score;

  // Update local progress tracking
  const progress = getStoredProgress();
  if (lessonId) {
    progress[lessonId] = {
      ...progress[lessonId],
      lastEvent: event,
      lastUpdated: Date.now(),
      ...(score !== undefined && { score })
    };
    localStorage.setItem('learning_progress', JSON.stringify(progress));
  }

  trackEvent({ name: event, properties });
}

/**
 * Store event locally for offline usage tracking
 */
function storeEventLocally(eventData: any) {
  try {
    const stored = localStorage.getItem('analytics_events');
    const events = stored ? JSON.parse(stored) : [];

    events.push(eventData);

    // Keep only last 100 events
    if (events.length > 100) {
      events.splice(0, events.length - 100);
    }

    localStorage.setItem('analytics_events', JSON.stringify(events));
  } catch (e) {
    console.warn('Failed to store analytics event:', e);
  }
}

/**
 * Send to custom analytics endpoint
 */
async function sendToCustomEndpoint(eventData: any) {
  // In a real implementation, send to your analytics API
  // For now, we'll simulate the API call
  try {
    // await fetch('/api/analytics', {
    //   method: 'POST',
    //   headers: { 'Content-Type': 'application/json' },
    //   body: JSON.stringify(eventData)
    // });
  } catch (e) {
    // Fail silently - event is already stored locally
  }
}

/**
 * Get stored learning progress
 */
function getStoredProgress(): Record<string, any> {
  try {
    const stored = localStorage.getItem('learning_progress');
    return stored ? JSON.parse(stored) : {};
  } catch (e) {
    return {};
  }
}

/**
 * Initialize analytics on page load
 */
export function initAnalytics() {
  // Add global trackEvent function
  window.trackEvent = trackEvent;
  window.trackPageView = trackPageView;

  // Track initial page view
  trackPageView();

  // Track scroll depth
  trackScrollDepth();

  // Track time on page
  trackTimeOnPage();

  // Track offline/online status
  window.addEventListener('online', () => {
    trackEvent({ name: ANALYTICS_EVENTS.OFFLINE_MODE_ACTIVATED, properties: { status: 'online' } });
  });

  window.addEventListener('offline', () => {
    trackEvent({ name: ANALYTICS_EVENTS.OFFLINE_MODE_ACTIVATED, properties: { status: 'offline' } });
  });
}

// Extend window interface
declare global {
  interface Window {
    plausible?: (event: string, options?: { props?: Record<string, any> }) => void;
    trackEvent: (event: AnalyticsEvent) => void;
    trackPageView: (path?: string) => void;
  }
}