#!/usr/bin/env python3
"""
iNetZero Frontend Server - FastAPI
Serves the React frontend and proxies API requests to the backend
"""

from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import logging
import httpx

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="iNetZero Frontend Server",
    description="Frontend SPA server with API proxy",
    version="1.0.0",
)

# Get frontend dist directory
FRONTEND_DIST = Path(__file__).parent / "frontend" / "dist"
FRONTEND_INDEX = FRONTEND_DIST / "index.html"

logger.info(f"Frontend dist: {FRONTEND_DIST}")
logger.info(f"Frontend exists: {FRONTEND_DIST.exists()}")

# Mount static assets
if (FRONTEND_DIST / "assets").exists():
    app.mount("/assets", StaticFiles(directory=str(FRONTEND_DIST / "assets")), name="assets")
    logger.info("✅ Assets mounted at /assets")

# Health check endpoint
@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "iNetZero Frontend Server",
        "version": "1.0.0"
    }

# Serve frontend for all non-asset routes (SPA routing)
@app.get("/{full_path:path}")
async def serve_frontend(full_path: str):
    """
    Serve frontend SPA - returns index.html for all non-asset routes
    This allows React Router to handle all client-side routes
    """
    # Return index.html for SPA routing
    if FRONTEND_INDEX.exists():
        logger.info(f"Serving index.html for route: /{full_path}")
        return FileResponse(FRONTEND_INDEX)

    logger.error(f"Frontend index.html not found at {FRONTEND_INDEX}")
    return JSONResponse({"error": "Frontend not found"}, status_code=404)

# Default GET handler for root
@app.get("/")
async def root():
    """Serve index.html at root"""
    if FRONTEND_INDEX.exists():
        logger.info("Serving index.html at root")
        return FileResponse(FRONTEND_INDEX)

    logger.error(f"Frontend index.html not found at {FRONTEND_INDEX}")
    return JSONResponse({"error": "Frontend not found"}, status_code=404)


if __name__ == "__main__":
    import uvicorn

    print("\n╔════════════════════════════════════════════════════════════════╗")
    print("║     iNetZero Frontend Server - FastAPI                         ║")
    print("╚════════════════════════════════════════════════════════════════╝")
    print(f"\n📁 Frontend Directory: {FRONTEND_DIST}")
    print(f"✅ Frontend Ready: {FRONTEND_DIST.exists()}\n")
    print("🚀 Starting server on http://127.0.0.1:3000")
    print("   Press Ctrl+C to stop\n")

    uvicorn.run(
        app,
        host="127.0.0.1",
        port=3000,
        log_level="info",
    )
