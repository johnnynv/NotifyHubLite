"""
NotifyHubLite FastAPI Application
"""
from fastapi import FastAPI, Depends, HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn

from app.config import settings
from app.database import create_tables


# Security scheme for API key authentication
security = HTTPBearer()


def verify_api_key(credentials: HTTPAuthorizationCredentials = Security(security)):
    """
    Verify API key from Authorization header
    """
    if credentials.credentials != settings.api_key:
        raise HTTPException(
            status_code=401,
            detail="Invalid API key"
        )
    return credentials


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan events
    """
    # Startup
    print("🚀 Starting NotifyHubLite API...")
    # TODO: Initialize database tables after fixing connection
    # create_tables()
    print("✅ API startup complete")
    
    yield
    
    # Shutdown
    print("🛑 Shutting down NotifyHubLite API...")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Rich text email API with attachments and PDF preview",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=settings.cors_methods,
    allow_headers=settings.cors_headers,
)


@app.get("/")
async def root():
    """
    API root endpoint
    """
    return {
        "message": "Welcome to NotifyHubLite API",
        "version": settings.app_version,
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.app_version
    }


@app.get("/protected")
async def protected_endpoint(credentials: HTTPAuthorizationCredentials = Depends(verify_api_key)):
    """
    Example protected endpoint
    """
    return {
        "message": "Access granted",
        "authenticated": True
    }


# Include API routers
from app.api import emails, attachments
app.include_router(emails.router, prefix="/api/v1/emails", tags=["emails"])
app.include_router(attachments.router, prefix="/api/v1/attachments", tags=["attachments"])


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )
