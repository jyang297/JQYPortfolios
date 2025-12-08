/**
 * Analytics tracking utility
 * Connects frontend to FastAPI backend analytics endpoints
 */

// Get API URL from environment variable or default to localhost
const API_URL = import.meta.env.PUBLIC_API_URL || 'http://localhost:8000';

interface VisitData {
  session_id: string;
  page_url: string;
  page_title?: string;
  referrer?: string;
  screen_width?: number;
  screen_height?: number;
  time_on_page?: number;
  scroll_depth?: number;
}

interface EventData {
  session_id: string;
  event_type: string;
  event_data: Record<string, any>;
  page_url: string;
}

/**
 * Get or create a session ID
 * Stored in sessionStorage (lasts until browser tab is closed)
 */
function getOrCreateSessionId(): string {
  const SESSION_KEY = 'portfolio_session_id';

  if (typeof window === 'undefined') {
    return 'server-side-render';
  }

  let sessionId = sessionStorage.getItem(SESSION_KEY);

  if (!sessionId) {
    sessionId = `${Date.now()}-${Math.random().toString(36).substring(2, 11)}`;
    sessionStorage.setItem(SESSION_KEY, sessionId);
  }

  return sessionId;
}

/**
 * Track a page view
 * Automatically called on page load
 */
export async function trackPageView(additionalData: Partial<VisitData> = {}): Promise<void> {
  if (typeof window === 'undefined') {
    return; // Don't track during SSR
  }

  const sessionId = getOrCreateSessionId();

  const visitData: VisitData = {
    session_id: sessionId,
    page_url: window.location.pathname,
    page_title: document.title,
    referrer: document.referrer || undefined,
    screen_width: window.screen.width,
    screen_height: window.screen.height,
    ...additionalData
  };

  try {
    const response = await fetch(`${API_URL}/api/stats/track`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(visitData),
    });

    if (!response.ok) {
      console.warn('Failed to track page view:', response.statusText);
    }
  } catch (error) {
    console.error('Analytics tracking error:', error);
    // Fail silently - don't break the user experience
  }
}

/**
 * Track a custom event (clicks, downloads, form submissions, etc.)
 */
export async function trackEvent(
  eventType: string,
  eventData: Record<string, any> = {}
): Promise<void> {
  if (typeof window === 'undefined') {
    return;
  }

  const sessionId = getOrCreateSessionId();

  const data: EventData = {
    session_id: sessionId,
    event_type: eventType,
    event_data: eventData,
    page_url: window.location.pathname,
  };

  try {
    const response = await fetch(`${API_URL}/api/stats/event`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      console.warn('Failed to track event:', response.statusText);
    }
  } catch (error) {
    console.error('Event tracking error:', error);
  }
}

/**
 * Track time spent on page and scroll depth
 * Call this when user leaves the page
 */
export function setupPageEngagement(): void {
  if (typeof window === 'undefined') {
    return;
  }

  const startTime = Date.now();
  let maxScrollDepth = 0;

  // Track scroll depth
  const updateScrollDepth = () => {
    const windowHeight = window.innerHeight;
    const documentHeight = document.documentElement.scrollHeight;
    const scrollTop = window.scrollY;

    const scrollPercentage = Math.round(
      ((scrollTop + windowHeight) / documentHeight) * 100
    );

    maxScrollDepth = Math.max(maxScrollDepth, scrollPercentage);
  };

  window.addEventListener('scroll', updateScrollDepth, { passive: true });

  // Send data when user leaves
  const sendEngagementData = () => {
    const timeOnPage = Math.round((Date.now() - startTime) / 1000); // seconds

    // Use sendBeacon for reliable delivery even when page is closing
    const data = {
      session_id: getOrCreateSessionId(),
      page_url: window.location.pathname,
      time_on_page: timeOnPage,
      scroll_depth: maxScrollDepth,
    };

    if (navigator.sendBeacon) {
      const blob = new Blob([JSON.stringify(data)], {
        type: 'application/json',
      });
      navigator.sendBeacon(`${API_URL}/api/stats/track`, blob);
    } else {
      // Fallback for browsers without sendBeacon
      trackPageView({ time_on_page: timeOnPage, scroll_depth: maxScrollDepth });
    }
  };

  // Send data on page unload
  window.addEventListener('beforeunload', sendEngagementData);

  // Also send on visibility change (tab switching)
  document.addEventListener('visibilitychange', () => {
    if (document.visibilityState === 'hidden') {
      sendEngagementData();
    }
  });
}

/**
 * Convenience function to track common events
 */
export const analytics = {
  // Track project clicks
  projectClick: (projectId: string, projectName: string) => {
    trackEvent('project_click', { project_id: projectId, project_name: projectName });
  },

  // Track resume download
  resumeDownload: () => {
    trackEvent('resume_download', { timestamp: new Date().toISOString() });
  },

  // Track contact form submission
  contactFormSubmit: (success: boolean) => {
    trackEvent('contact_form_submit', { success });
  },

  // Track blog post view
  blogPostView: (postSlug: string, postTitle: string) => {
    trackEvent('blog_post_view', { post_slug: postSlug, post_title: postTitle });
  },

  // Track external link clicks
  externalLinkClick: (url: string, linkText: string) => {
    trackEvent('external_link_click', { url, link_text: linkText });
  },

  // Track social media clicks
  socialClick: (platform: string, url: string) => {
    trackEvent('social_click', { platform, url });
  },
};
