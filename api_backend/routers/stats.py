"""
Analytics and visitor statistics router
Tracks page visits, user behavior, and generates analytics summaries
"""

from fastapi import APIRouter, HTTPException, Request, Query
from pydantic import BaseModel, Field
from supabase import create_client
from user_agents import parse as parse_user_agent
import os
import hashlib
from datetime import datetime, timezone, timedelta
from typing import Optional
import structlog

router = APIRouter(prefix="/api/stats", tags=["stats"])

# Initialize logger
logger = structlog.get_logger()

# Supabase configuration
url = os.getenv("SUPABASE_URL", "")
key = os.getenv("SUPABASE_KEY", "")

if not url or not key:
    logger.warning("supabase_not_configured", message="SUPABASE_URL and SUPABASE_KEY must be set")
    supabase_cli = None
else:
    try:
        supabase_cli = create_client(url, key)
        logger.info("supabase_initialized", service="stats")
    except Exception as e:
        logger.error("supabase_init_failed", error=str(e))
        supabase_cli = None


class VisitData(BaseModel):
    """Visit tracking data model"""
    page_url: str = Field(..., description="Current page URL")
    page_title: Optional[str] = Field(None, description="Page title")
    referrer: Optional[str] = Field(None, description="Referrer URL")
    session_id: str = Field(..., description="Client session ID")
    screen_width: Optional[int] = Field(None, description="Screen width in pixels")
    screen_height: Optional[int] = Field(None, description="Screen height in pixels")
    time_on_page: Optional[int] = Field(None, description="Time spent on page (seconds)")
    scroll_depth: Optional[int] = Field(None, description="Max scroll depth (percentage)")


class EventData(BaseModel):
    """Event tracking data model"""
    session_id: str = Field(..., description="Client session ID")
    event_type: str = Field(..., description="Event type (click, download, etc.)")
    event_data: dict = Field(default_factory=dict, description="Additional event data")
    page_url: str = Field(..., description="Page where event occurred")


def hash_ip(ip: str) -> str:
    """Hash IP address for privacy"""
    return hashlib.sha256(ip.encode()).hexdigest()[:16]


def extract_device_info(user_agent_string: str) -> dict:
    """
    Parse user agent string to extract device information

    Returns dict with browser, OS, and device type information
    """
    ua = parse_user_agent(user_agent_string)

    return {
        "browser": ua.browser.family,
        "browser_version": ua.browser.version_string,
        "os": ua.os.family,
        "os_version": ua.os.version_string,
        "device_type": "mobile" if ua.is_mobile else "tablet" if ua.is_tablet else "bot" if ua.is_bot else "desktop",
        "is_bot": ua.is_bot
    }


def get_client_ip(request: Request) -> str:
    """Extract real client IP from request headers"""
    # Check common proxy headers (CloudFront, ALB, Nginx, etc.)
    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        # X-Forwarded-For can be a comma-separated list, take the first one
        return forwarded_for.split(",")[0].strip()

    real_ip = request.headers.get("x-real-ip")
    if real_ip:
        return real_ip

    return request.client.host if request.client else "unknown"


def get_location_from_headers(request: Request) -> dict:
    """
    Extract location from CloudFront/CDN headers

    CloudFront adds: CloudFront-Viewer-Country, CloudFront-Viewer-City, etc.
    AliCloud CDN adds: Ali-CDN-Real-IP, similar location headers
    """
    return {
        "country": request.headers.get("cloudfront-viewer-country") or
                  request.headers.get("x-country-code") or
                  request.headers.get("cf-ipcountry") or None,
        "city": request.headers.get("cloudfront-viewer-city") or
               request.headers.get("x-city") or None,
    }


@router.post("/track")
async def track_visit(visit: VisitData, request: Request):
    """
    Track a page visit with detailed analytics

    Captures device info, location, and user behavior metrics.
    """
    if not supabase_cli:
        logger.error("visit_tracking_failed", reason="supabase_not_configured")
        raise HTTPException(
            status_code=503,
            detail="Analytics service is not available"
        )

    try:
        # Extract client information
        client_ip = get_client_ip(request)
        user_agent = request.headers.get("user-agent", "unknown")

        # Parse device information
        device_info = extract_device_info(user_agent)

        # Get location from headers (CDN-provided)
        location = get_location_from_headers(request)

        # Skip bot traffic (optional - comment out if you want to track bots)
        if device_info["is_bot"]:
            logger.info(
                "bot_visit_skipped",
                bot_type=device_info["browser"],
                page=visit.page_url
            )
            return {"message": "Bot visit logged", "tracked": False}

        # Prepare data for database
        data = {
            "session_id": visit.session_id,
            "ip_hash": hash_ip(client_ip),
            "country": location.get("country"),
            "city": location.get("city"),
            "user_agent": user_agent,
            "device_type": device_info["device_type"],
            "browser": device_info["browser"],
            "browser_version": device_info["browser_version"],
            "os": device_info["os"],
            "os_version": device_info["os_version"],
            "screen_width": visit.screen_width,
            "screen_height": visit.screen_height,
            "page_url": visit.page_url,
            "page_title": visit.page_title,
            "referrer": visit.referrer,
            "time_on_page": visit.time_on_page,
            "scroll_depth": visit.scroll_depth,
            "created_at": datetime.now(timezone.utc).isoformat()
        }

        # Insert into Supabase
        result = supabase_cli.table("visits").insert(data).execute()

        # Log successful tracking
        logger.info(
            "visit_tracked",
            page=visit.page_url,
            device=device_info["device_type"],
            browser=device_info["browser"],
            country=location.get("country"),
            session=visit.session_id[:8]  # Log partial session ID
        )

        return {
            "message": "Visit tracked successfully",
            "tracked": True
        }

    except Exception as e:
        logger.error(
            "visit_tracking_error",
            error=str(e),
            error_type=type(e).__name__,
            page=visit.page_url
        )
        # Don't fail the request, just log the error
        return {
            "message": "Visit tracking failed",
            "tracked": False,
            "error": str(e)
        }


@router.post("/event")
async def track_event(event: EventData, request: Request):
    """
    Track custom events (clicks, downloads, form submissions, etc.)
    """
    if not supabase_cli:
        logger.error("event_tracking_failed", reason="supabase_not_configured")
        raise HTTPException(
            status_code=503,
            detail="Analytics service is not available"
        )

    try:
        data = {
            "session_id": event.session_id,
            "event_type": event.event_type,
            "event_data": event.event_data,
            "page_url": event.page_url,
            "created_at": datetime.now(timezone.utc).isoformat()
        }

        result = supabase_cli.table("events").insert(data).execute()

        logger.info(
            "event_tracked",
            event_type=event.event_type,
            page=event.page_url,
            session=event.session_id[:8]
        )

        return {"message": "Event tracked successfully", "tracked": True}

    except Exception as e:
        logger.error(
            "event_tracking_error",
            error=str(e),
            event_type=event.event_type
        )
        return {"message": "Event tracking failed", "tracked": False}


@router.get("/summary")
async def get_summary(
    days: int = Query(default=30, ge=1, le=365, description="Number of days to include in summary")
):
    """
    Get analytics summary

    Returns aggregated statistics for the specified time period.
    """
    if not supabase_cli:
        raise HTTPException(status_code=503, detail="Analytics service is not available")

    try:
        # Calculate date range
        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(days=days)

        # Get visit count
        visits_result = supabase_cli.table("visits") \
            .select("*", count="exact") \
            .gte("created_at", start_date.isoformat()) \
            .execute()

        # Get unique sessions
        sessions_result = supabase_cli.table("visits") \
            .select("session_id") \
            .gte("created_at", start_date.isoformat()) \
            .execute()

        unique_sessions = len(set(v["session_id"] for v in sessions_result.data if "session_id" in v))

        # Get device breakdown
        device_result = supabase_cli.table("visits") \
            .select("device_type") \
            .gte("created_at", start_date.isoformat()) \
            .execute()

        device_counts = {}
        for visit in device_result.data:
            device_type = visit.get("device_type", "unknown")
            device_counts[device_type] = device_counts.get(device_type, 0) + 1

        # Get top pages
        pages_result = supabase_cli.table("visits") \
            .select("page_url") \
            .gte("created_at", start_date.isoformat()) \
            .execute()

        page_counts = {}
        for visit in pages_result.data:
            page_url = visit.get("page_url", "unknown")
            page_counts[page_url] = page_counts.get(page_url, 0) + 1

        top_pages = sorted(page_counts.items(), key=lambda x: x[1], reverse=True)[:10]

        # Get referrer breakdown
        referrer_result = supabase_cli.table("visits") \
            .select("referrer") \
            .gte("created_at", start_date.isoformat()) \
            .execute()

        referrer_counts = {}
        for visit in referrer_result.data:
            referrer = visit.get("referrer") or "direct"
            referrer_counts[referrer] = referrer_counts.get(referrer, 0) + 1

        top_referrers = sorted(referrer_counts.items(), key=lambda x: x[1], reverse=True)[:10]

        logger.info("summary_generated", days=days, total_visits=visits_result.count)

        return {
            "period_days": days,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "total_visits": visits_result.count,
            "unique_visitors": unique_sessions,
            "devices": device_counts,
            "top_pages": [{"url": url, "visits": count} for url, count in top_pages],
            "top_referrers": [{"source": ref, "visits": count} for ref, count in top_referrers]
        }

    except Exception as e:
        logger.error("summary_generation_error", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to generate summary: {str(e)}")


@router.get("/health")
async def stats_health():
    """Health check for stats service"""
    return {
        "status": "healthy" if supabase_cli else "degraded",
        "service": "stats",
        "supabase_configured": supabase_cli is not None
    }
