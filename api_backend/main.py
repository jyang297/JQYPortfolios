"""
FastAPI Backend for Portfolio
Main application entry point with structured logging and metrics
"""

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
import os
import time
import structlog
from dotenv import load_dotenv

# Import routers
from routers import stats, contact

# Load environment variables
load_dotenv()

# Configuration
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:4321").split(",")
ENABLE_METRICS = os.getenv("ENABLE_METRICS", "true").lower() == "true"
ENABLE_REQUEST_LOGGING = os.getenv("ENABLE_REQUEST_LOGGING", "true").lower() == "true"
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# Prometheus metrics (cloud-agnostic, works with AWS CloudWatch, AliCloud ARMS, or standalone Prometheus)
http_requests_total = Counter(
    'portfolio_http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

http_request_duration_seconds = Histogram(
    'portfolio_http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint']
)

# Initialize FastAPI
app = FastAPI(
    title="Portfolio API",
    description="Backend API for ML/AI Engineer Portfolio - Multi-cloud ready",
    version="1.0.0",
    docs_url="/api/docs" if ENVIRONMENT == "development" else None,
    redoc_url="/api/redoc" if ENVIRONMENT == "development" else None,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def logging_and_metrics_middleware(request: Request, call_next):
    """
    Middleware for request logging and metrics collection
    Works with any cloud provider or log aggregation service
    """
    start_time = time.time()

    # Extract request info
    path = request.url.path
    method = request.method

    # Log request start
    if ENABLE_REQUEST_LOGGING:
        logger.info(
            "request_started",
            method=method,
            path=path,
            client_ip=request.client.host if request.client else "unknown"
        )

    # Process request
    response = await call_next(request)

    # Calculate duration
    duration = time.time() - start_time

    # Record metrics
    if ENABLE_METRICS:
        http_requests_total.labels(
            method=method,
            endpoint=path,
            status=response.status_code
        ).inc()

        http_request_duration_seconds.labels(
            method=method,
            endpoint=path
        ).observe(duration)

    # Log request completion
    if ENABLE_REQUEST_LOGGING:
        logger.info(
            "request_completed",
            method=method,
            path=path,
            status_code=response.status_code,
            duration_seconds=round(duration, 3)
        )

    return response


@app.get("/")
async def root():
    """Root endpoint - health check"""
    logger.info("root_endpoint_accessed")
    return {
        "status": "ok",
        "message": "Portfolio API is running",
        "version": "1.0.0",
        "environment": ENVIRONMENT
    }


@app.get("/api/health")
async def health_check():
    """
    Detailed health check endpoint
    Used by load balancers and monitoring systems
    """
    supabase_url = os.getenv("SUPABASE_URL", "")
    supabase_configured = bool(supabase_url)

    health_status = {
        "status": "healthy",
        "service": "portfolio-api",
        "version": "1.0.0",
        "environment": ENVIRONMENT,
        "components": {
            "supabase": "configured" if supabase_configured else "not_configured",
            "metrics": "enabled" if ENABLE_METRICS else "disabled",
            "logging": "enabled" if ENABLE_REQUEST_LOGGING else "disabled"
        }
    }

    logger.info("health_check_performed", **health_status)
    return health_status


@app.get("/metrics")
async def metrics():
    """
    Prometheus-compatible metrics endpoint
    Works with:
    - Prometheus (self-hosted or Grafana Cloud)
    - AWS CloudWatch Container Insights
    - AliCloud ARMS Prometheus
    - Any Prometheus-compatible scraper
    """
    if not ENABLE_METRICS:
        return Response(content="Metrics disabled", status_code=404)

    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


# Include routers
app.include_router(stats.router)
app.include_router(contact.router)


# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    """Log application startup"""
    logger.info(
        "application_startup",
        environment=ENVIRONMENT,
        metrics_enabled=ENABLE_METRICS,
        logging_enabled=ENABLE_REQUEST_LOGGING
    )


@app.on_event("shutdown")
async def shutdown_event():
    """Log application shutdown"""
    logger.info("application_shutdown")
