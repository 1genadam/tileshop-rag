#!/usr/bin/env python3
"""
Comprehensive health check for Tileshop RAG system
Validates all critical components and dependencies
"""

import sys
import json
import time
import psutil
from datetime import datetime
from typing import Dict, Any, List, Tuple

def check_database_connection() -> Tuple[bool, str]:
    """Check PostgreSQL database connectivity"""
    try:
        from modules.db_manager import DatabaseManager
        db_manager = DatabaseManager()
        
        # Test basic connection
        conn = db_manager.get_connection()
        if not conn:
            return False, "Database connection failed"
        
        # Test basic query
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        cursor.close()
        
        if result and result[0] == 1:
            return True, "Database connection healthy"
        else:
            return False, "Database query failed"
            
    except Exception as e:
        return False, f"Database error: {str(e)}"

def check_flask_app() -> Tuple[bool, str]:
    """Check Flask application health"""
    try:
        import requests
        response = requests.get("http://localhost:8080/health", timeout=5)
        if response.status_code == 200:
            return True, "Flask application responding"
        else:
            return False, f"Flask app returned status {response.status_code}"
    except Exception as e:
        return False, f"Flask app error: {str(e)}"

def check_disk_space() -> Tuple[bool, str]:
    """Check available disk space"""
    try:
        usage = psutil.disk_usage('/')
        free_gb = usage.free / (1024**3)
        total_gb = usage.total / (1024**3)
        percent_used = (usage.used / usage.total) * 100
        
        if free_gb < 1.0:  # Less than 1GB free
            return False, f"Low disk space: {free_gb:.1f}GB free ({percent_used:.1f}% used)"
        elif percent_used > 90:
            return False, f"Disk usage critical: {percent_used:.1f}% used"
        else:
            return True, f"Disk space healthy: {free_gb:.1f}GB free ({percent_used:.1f}% used)"
            
    except Exception as e:
        return False, f"Disk check error: {str(e)}"

def check_memory_usage() -> Tuple[bool, str]:
    """Check system memory usage"""
    try:
        memory = psutil.virtual_memory()
        percent_used = memory.percent
        available_gb = memory.available / (1024**3)
        
        if percent_used > 95:
            return False, f"Memory critical: {percent_used:.1f}% used"
        elif percent_used > 90:
            return False, f"Memory high: {percent_used:.1f}% used"
        else:
            return True, f"Memory healthy: {percent_used:.1f}% used, {available_gb:.1f}GB available"
            
    except Exception as e:
        return False, f"Memory check error: {str(e)}"

def check_python_dependencies() -> Tuple[bool, str]:
    """Check critical Python dependencies"""
    try:
        required_modules = [
            'flask',
            'flask_socketio', 
            'psycopg2',
            'requests',
            'anthropic',
            'gunicorn'
        ]
        
        missing = []
        for module in required_modules:
            try:
                __import__(module)
            except ImportError:
                missing.append(module)
        
        if missing:
            return False, f"Missing dependencies: {', '.join(missing)}"
        else:
            return True, "All dependencies available"
            
    except Exception as e:
        return False, f"Dependency check error: {str(e)}"

def check_scraper_functionality() -> Tuple[bool, str]:
    """Check curl_scraper.py functionality"""
    try:
        import subprocess
        result = subprocess.run(['python3', 'curl_scraper.py', '--help'], 
                              capture_output=True, timeout=10)
        if result.returncode == 0:
            return True, "Scraper module functional"
        else:
            return False, f"Scraper check failed: {result.stderr.decode()}"
    except Exception as e:
        return False, f"Scraper check error: {str(e)}"

def run_comprehensive_health_check() -> Dict[str, Any]:
    """Run all health checks and return comprehensive status"""
    
    print("🏥 Tileshop RAG System - Comprehensive Health Check")
    print("=" * 60)
    
    checks = [
        ("Database Connection", check_database_connection),
        ("Flask Application", check_flask_app),
        ("Disk Space", check_disk_space),
        ("Memory Usage", check_memory_usage),
        ("Python Dependencies", check_python_dependencies),
        ("Scraper Functionality", check_scraper_functionality),
    ]
    
    results = {}
    all_healthy = True
    
    for check_name, check_func in checks:
        print(f"\n🔍 Checking {check_name}...")
        try:
            is_healthy, message = check_func()
            status = "✅ HEALTHY" if is_healthy else "❌ UNHEALTHY"
            print(f"   {status}: {message}")
            
            results[check_name] = {
                "healthy": is_healthy,
                "message": message,
                "timestamp": datetime.now().isoformat()
            }
            
            if not is_healthy:
                all_healthy = False
                
        except Exception as e:
            error_msg = f"Check failed: {str(e)}"
            print(f"   ❌ ERROR: {error_msg}")
            results[check_name] = {
                "healthy": False,
                "message": error_msg,
                "timestamp": datetime.now().isoformat()
            }
            all_healthy = False
    
    # Overall status
    overall_status = "HEALTHY" if all_healthy else "UNHEALTHY"
    print(f"\n{'='*60}")
    print(f"🎯 OVERALL SYSTEM STATUS: {overall_status}")
    print(f"{'='*60}")
    
    results["overall"] = {
        "healthy": all_healthy,
        "status": overall_status,
        "timestamp": datetime.now().isoformat(),
        "checks_run": len(checks)
    }
    
    return results

def health_check_endpoint():
    """Simple health check for Flask endpoint"""
    try:
        # Quick database connectivity check
        from modules.db_manager import DatabaseManager
        db_manager = DatabaseManager()
        conn = db_manager.get_connection()
        
        if conn:
            return {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "service": "tileshop-rag",
                "version": "1.0.0"
            }
        else:
            return {
                "status": "unhealthy",
                "error": "Database connection failed",
                "timestamp": datetime.now().isoformat()
            }
    except Exception as e:
        return {
            "status": "unhealthy", 
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--json":
        # JSON output for programmatic use
        results = run_comprehensive_health_check()
        print(json.dumps(results, indent=2))
        sys.exit(0 if results["overall"]["healthy"] else 1)
    else:
        # Human-readable output
        results = run_comprehensive_health_check()
        sys.exit(0 if results["overall"]["healthy"] else 1)