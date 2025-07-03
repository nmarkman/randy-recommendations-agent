"""
Health check system for monitoring API status and overall system health.
"""
import requests
import time
import logging
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
from config.settings import settings

logger = logging.getLogger('Randy.HealthChecks')

class HealthStatus:
    """Health status constants."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"

class HealthCheckResult:
    """Result of a health check."""
    
    def __init__(self, service_name: str, status: str, response_time: float = None, 
                 message: str = None, details: Dict = None):
        self.service_name = service_name
        self.status = status
        self.response_time = response_time
        self.message = message
        self.details = details or {}
        self.timestamp = datetime.now()
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for logging/storage."""
        return {
            'service_name': self.service_name,
            'status': self.status,
            'response_time': self.response_time,
            'message': self.message,
            'details': self.details,
            'timestamp': self.timestamp.isoformat()
        }

def check_google_places_api() -> HealthCheckResult:
    """
    Check Google Places API health.
    
    Returns:
        HealthCheckResult with API status
    """
    start_time = time.time()
    
    try:
        # Test with a simple search query
        url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
        params = {
            'query': 'restaurants in Charleston SC',
            'key': settings.GOOGLE_PLACES_API_KEY,
            'type': 'restaurant',
            'language': 'en'
        }
        
        response = requests.get(url, params=params, timeout=10)
        response_time = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            
            # Check for API errors
            if data.get('status') == 'OK':
                return HealthCheckResult(
                    service_name="Google Places API",
                    status=HealthStatus.HEALTHY,
                    response_time=response_time,
                    message="API responding normally",
                    details={'results_count': len(data.get('results', []))}
                )
            elif data.get('status') == 'OVER_QUERY_LIMIT':
                return HealthCheckResult(
                    service_name="Google Places API",
                    status=HealthStatus.DEGRADED,
                    response_time=response_time,
                    message="Query limit exceeded",
                    details={'api_status': data.get('status')}
                )
            else:
                return HealthCheckResult(
                    service_name="Google Places API",
                    status=HealthStatus.UNHEALTHY,
                    response_time=response_time,
                    message=f"API error: {data.get('status')}",
                    details={'api_status': data.get('status')}
                )
        else:
            return HealthCheckResult(
                service_name="Google Places API",
                status=HealthStatus.UNHEALTHY,
                response_time=response_time,
                message=f"HTTP {response.status_code}",
                details={'status_code': response.status_code}
            )
    
    except requests.exceptions.Timeout:
        return HealthCheckResult(
            service_name="Google Places API",
            status=HealthStatus.UNHEALTHY,
            response_time=time.time() - start_time,
            message="Request timeout"
        )
    except requests.exceptions.ConnectionError:
        return HealthCheckResult(
            service_name="Google Places API",
            status=HealthStatus.UNHEALTHY,
            response_time=time.time() - start_time,
            message="Connection error"
        )
    except Exception as e:
        return HealthCheckResult(
            service_name="Google Places API",
            status=HealthStatus.UNHEALTHY,
            response_time=time.time() - start_time,
            message=f"Unexpected error: {str(e)}"
        )

def check_tmdb_api() -> HealthCheckResult:
    """
    Check TMDB API health.
    
    Returns:
        HealthCheckResult with API status
    """
    start_time = time.time()
    
    try:
        # Test with popular movies endpoint
        url = "https://api.themoviedb.org/3/movie/popular"
        params = {
            'api_key': settings.TMDB_API_KEY,
            'language': 'en-US',
            'page': 1
        }
        
        response = requests.get(url, params=params, timeout=10)
        response_time = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            return HealthCheckResult(
                service_name="TMDB API",
                status=HealthStatus.HEALTHY,
                response_time=response_time,
                message="API responding normally",
                details={'results_count': len(data.get('results', []))}
            )
        elif response.status_code == 429:
            return HealthCheckResult(
                service_name="TMDB API",
                status=HealthStatus.DEGRADED,
                response_time=response_time,
                message="Rate limit exceeded",
                details={'status_code': response.status_code}
            )
        else:
            return HealthCheckResult(
                service_name="TMDB API",
                status=HealthStatus.UNHEALTHY,
                response_time=response_time,
                message=f"HTTP {response.status_code}",
                details={'status_code': response.status_code}
            )
    
    except requests.exceptions.Timeout:
        return HealthCheckResult(
            service_name="TMDB API",
            status=HealthStatus.UNHEALTHY,
            response_time=time.time() - start_time,
            message="Request timeout"
        )
    except requests.exceptions.ConnectionError:
        return HealthCheckResult(
            service_name="TMDB API",
            status=HealthStatus.UNHEALTHY,
            response_time=time.time() - start_time,
            message="Connection error"
        )
    except Exception as e:
        return HealthCheckResult(
            service_name="TMDB API",
            status=HealthStatus.UNHEALTHY,
            response_time=time.time() - start_time,
            message=f"Unexpected error: {str(e)}"
        )

def check_openai_api() -> HealthCheckResult:
    """
    Check OpenAI API health (lightweight check).
    
    Returns:
        HealthCheckResult with API status
    """
    start_time = time.time()
    
    try:
        # Simple test - just check if we can make a basic request
        import openai
        from openai import OpenAI
        
        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        
        # Use a very simple completion to test connectivity
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "Hello"}],
            max_tokens=1,
            timeout=10
        )
        
        response_time = time.time() - start_time
        
        return HealthCheckResult(
            service_name="OpenAI API",
            status=HealthStatus.HEALTHY,
            response_time=response_time,
            message="API responding normally",
            details={'model': response.model}
        )
    
    except Exception as e:
        return HealthCheckResult(
            service_name="OpenAI API",
            status=HealthStatus.UNHEALTHY,
            response_time=time.time() - start_time,
            message=f"API error: {str(e)}"
        )

def check_email_smtp() -> HealthCheckResult:
    """
    Check Gmail SMTP connectivity.
    
    Returns:
        HealthCheckResult with SMTP status
    """
    start_time = time.time()
    
    try:
        import smtplib
        import ssl
        
        context = ssl.create_default_context()
        
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(settings.GMAIL_USERNAME, settings.GMAIL_APP_PASSWORD)
        
        response_time = time.time() - start_time
        
        return HealthCheckResult(
            service_name="Gmail SMTP",
            status=HealthStatus.HEALTHY,
            response_time=response_time,
            message="SMTP connection successful"
        )
    
    except smtplib.SMTPAuthenticationError:
        return HealthCheckResult(
            service_name="Gmail SMTP",
            status=HealthStatus.UNHEALTHY,
            response_time=time.time() - start_time,
            message="Authentication failed - check credentials"
        )
    except Exception as e:
        return HealthCheckResult(
            service_name="Gmail SMTP",
            status=HealthStatus.UNHEALTHY,
            response_time=time.time() - start_time,
            message=f"Connection error: {str(e)}"
        )

def check_memory_system() -> HealthCheckResult:
    """
    Check memory system health.
    
    Returns:
        HealthCheckResult with memory system status
    """
    start_time = time.time()
    
    try:
        from src.memory.recommendation_history import memory
        
        # Test basic memory operations
        summary = memory.get_memory_summary()
        recent = memory.get_recent_recommendations(7)
        
        response_time = time.time() - start_time
        
        return HealthCheckResult(
            service_name="Memory System",
            status=HealthStatus.HEALTHY,
            response_time=response_time,
            message="Memory system operational",
            details={
                'total_recommendations': summary.get('total_recommendations', 0),
                'recent_count': len(recent)
            }
        )
    
    except Exception as e:
        return HealthCheckResult(
            service_name="Memory System",
            status=HealthStatus.UNHEALTHY,
            response_time=time.time() - start_time,
            message=f"Memory system error: {str(e)}"
        )

def run_all_health_checks() -> Dict[str, HealthCheckResult]:
    """
    Run all health checks and return results.
    
    Returns:
        Dictionary mapping service names to health check results
    """
    logger.info("Starting comprehensive health checks...")
    
    checks = {
        'google_places': check_google_places_api,
        'tmdb': check_tmdb_api,
        'openai': check_openai_api,
        'email': check_email_smtp,
        'memory': check_memory_system
    }
    
    results = {}
    
    for check_name, check_func in checks.items():
        try:
            logger.info(f"Running health check: {check_name}")
            result = check_func()
            results[check_name] = result
            
            status_emoji = {
                HealthStatus.HEALTHY: "✅",
                HealthStatus.DEGRADED: "⚠️",
                HealthStatus.UNHEALTHY: "❌",
                HealthStatus.UNKNOWN: "❓"
            }.get(result.status, "❓")
            
            logger.info(f"{status_emoji} {result.service_name}: {result.status} ({result.response_time:.2f}s) - {result.message}")
        
        except Exception as e:
            logger.error(f"Health check {check_name} failed with error: {e}")
            results[check_name] = HealthCheckResult(
                service_name=check_name,
                status=HealthStatus.UNKNOWN,
                message=f"Check failed: {str(e)}"
            )
    
    return results

def get_overall_health_status(results: Dict[str, HealthCheckResult]) -> str:
    """
    Determine overall system health based on individual check results.
    
    Args:
        results: Dictionary of health check results
    
    Returns:
        Overall health status
    """
    if not results:
        return HealthStatus.UNKNOWN
    
    statuses = [result.status for result in results.values()]
    
    if all(status == HealthStatus.HEALTHY for status in statuses):
        return HealthStatus.HEALTHY
    elif any(status == HealthStatus.UNHEALTHY for status in statuses):
        return HealthStatus.UNHEALTHY
    elif any(status == HealthStatus.DEGRADED for status in statuses):
        return HealthStatus.DEGRADED
    else:
        return HealthStatus.UNKNOWN

def print_health_report(results: Dict[str, HealthCheckResult]) -> None:
    """
    Print a formatted health report.
    
    Args:
        results: Dictionary of health check results
    """
    overall_status = get_overall_health_status(results)
    
    print("\n" + "="*60)
    print("🏥 RANDY SYSTEM HEALTH REPORT")
    print("="*60)
    
    # Overall status
    status_emoji = {
        HealthStatus.HEALTHY: "✅",
        HealthStatus.DEGRADED: "⚠️",
        HealthStatus.UNHEALTHY: "❌",
        HealthStatus.UNKNOWN: "❓"
    }.get(overall_status, "❓")
    
    print(f"Overall Status: {status_emoji} {overall_status.upper()}")
    print(f"Check Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\nService Details:")
    print("-" * 60)
    
    for service_name, result in results.items():
        status_emoji = {
            HealthStatus.HEALTHY: "✅",
            HealthStatus.DEGRADED: "⚠️",
            HealthStatus.UNHEALTHY: "❌",
            HealthStatus.UNKNOWN: "❓"
        }.get(result.status, "❓")
        
        response_time_str = f"({result.response_time:.2f}s)" if result.response_time else ""
        print(f"{status_emoji} {result.service_name:<20} {result.status:<10} {response_time_str}")
        if result.message:
            print(f"   └─ {result.message}")
    
    print("="*60) 