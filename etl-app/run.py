#!/usr/bin/env python3
"""
ETL Pipeline Application Runner
"""
import uvicorn
import sys
import os

# Add app directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def main():
    """Run the ETL Pipeline API"""
    print("=" * 60)
    print("Starting ETL Pipeline API Server")
    print("=" * 60)
    print("API Documentation: http://localhost:8000/api/docs")
    print("Health Check: http://localhost:8000/health")
    print("=" * 60)
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )


if __name__ == "__main__":
    main()
