"""
Contact form router
Handles contact form submissions and stores them in Supabase
"""

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, EmailStr, Field
from supabase import create_client
import os
from datetime import datetime, timezone
import structlog

router = APIRouter(prefix="/api/contact", tags=["contact"])

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
        logger.info("supabase_initialized", service="contact")
    except Exception as e:
        logger.error("supabase_init_failed", error=str(e))
        supabase_cli = None


class ContactMessage(BaseModel):
    """Contact form data model"""
    name: str = Field(..., min_length=1, max_length=100, description="Sender's name")
    email: EmailStr = Field(..., description="Sender's email address")
    subject: str | None = Field(None, max_length=200, description="Message subject")
    message: str = Field(..., min_length=10, max_length=5000, description="Message content")


@router.post("/submit")
async def submit_contact(contact: ContactMessage, request: Request):
    """
    Submit a contact form message

    Stores the message in Supabase and logs the submission.
    """
    if not supabase_cli:
        logger.error("contact_submit_failed", reason="supabase_not_configured")
        raise HTTPException(
            status_code=503,
            detail="Contact service is not available. Please try again later."
        )

    try:
        # Get client info for logging
        client_ip = request.headers.get("x-forwarded-for", request.client.host if request.client else "unknown")

        # Prepare data for Supabase
        data = {
            "name": contact.name,
            "email": contact.email,
            "subject": contact.subject or "No subject",
            "message": contact.message,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "ip_address": client_ip  # For spam prevention
        }

        # Insert into Supabase
        result = supabase_cli.table("contact_messages").insert(data).execute()

        # Log successful submission
        logger.info(
            "contact_message_received",
            email=contact.email,
            has_subject=bool(contact.subject),
            message_length=len(contact.message),
            ip=client_ip
        )

        return {
            "success": True,
            "message": "Thank you for your message! I'll get back to you soon.",
            "id": result.data[0]["id"] if result.data else None
        }

    except Exception as e:
        logger.error(
            "contact_submit_error",
            error=str(e),
            error_type=type(e).__name__
        )
        raise HTTPException(
            status_code=500,
            detail=f"Failed to submit message: {str(e)}"
        )


@router.get("/health")
async def contact_health():
    """Health check for contact service"""
    return {
        "status": "healthy" if supabase_cli else "degraded",
        "service": "contact",
        "supabase_configured": supabase_cli is not None
    }
