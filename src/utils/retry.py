"""
Retry utilities with exponential backoff for robust API calls.
"""
import time
import random
import logging
import functools
from typing import Callable, Any, Optional, List, Type
import requests

logger = logging.getLogger('Randy.Retry')

class RetryError(Exception):
    """Raised when all retry attempts are exhausted."""
    pass

class APIHealthError(Exception):
    """Raised when API appears to be down or unhealthy.""" 
    pass

def exponential_backoff(attempt: int, base_delay: float = 1.0, max_delay: float = 60.0, jitter: bool = True) -> float:
    """
    Calculate exponential backoff delay with optional jitter.
    
    Args:
        attempt: Current attempt number (starting from 0)
        base_delay: Base delay in seconds
        max_delay: Maximum delay in seconds
        jitter: Whether to add random jitter to prevent thundering herd
    
    Returns:
        Delay in seconds
    """
    delay = min(base_delay * (2 ** attempt), max_delay)
    
    if jitter:
        # Add ±25% jitter
        jitter_range = delay * 0.25
        delay += random.uniform(-jitter_range, jitter_range)
    
    return max(0, delay)

def should_retry_error(exception: Exception, retryable_errors: List[Type[Exception]] = None) -> bool:
    """
    Determine if an error should trigger a retry.
    
    Args:
        exception: The exception that occurred
        retryable_errors: List of exception types that should trigger retries
    
    Returns:
        True if the error should trigger a retry
    """
    if retryable_errors is None:
        retryable_errors = [
            requests.exceptions.ConnectionError,
            requests.exceptions.Timeout,
            ConnectionError,
            TimeoutError,
        ]
    
    # Check HTTP status codes for requests exceptions FIRST
    if hasattr(exception, 'response') and exception.response is not None:
        status_code = exception.response.status_code
        # Retry on server errors (5xx) and some client errors
        retryable_status_codes = [429, 500, 502, 503, 504, 520, 521, 522, 523, 524]
        return status_code in retryable_status_codes
    
    # Check if it's a retryable error type (non-HTTP errors)
    if any(isinstance(exception, error_type) for error_type in retryable_errors):
        return True
    
    return False

def retry_with_backoff(
    max_attempts: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    retryable_errors: List[Type[Exception]] = None,
    on_retry: Optional[Callable] = None
):
    """
    Decorator for retrying functions with exponential backoff.
    
    Args:
        max_attempts: Maximum number of attempts (including first attempt)
        base_delay: Base delay for exponential backoff
        max_delay: Maximum delay between retries
        retryable_errors: List of exception types that should trigger retries
        on_retry: Optional callback function called on each retry attempt
    
    Returns:
        Decorated function with retry logic
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            
            for attempt in range(max_attempts):
                try:
                    result = func(*args, **kwargs)
                    
                    # Log successful retry if this wasn't the first attempt
                    if attempt > 0:
                        logger.info(f"{func.__name__} succeeded on attempt {attempt + 1}")
                    
                    return result
                    
                except Exception as e:
                    last_exception = e
                    
                    # Check if we should retry this error
                    if not should_retry_error(e, retryable_errors):
                        logger.warning(f"{func.__name__} failed with non-retryable error: {e}")
                        raise e
                    
                    # If this was the last attempt, raise the error
                    if attempt == max_attempts - 1:
                        logger.error(f"{func.__name__} failed after {max_attempts} attempts: {e}")
                        raise RetryError(f"Function {func.__name__} failed after {max_attempts} attempts. Last error: {e}")
                    
                    # Calculate delay and wait
                    delay = exponential_backoff(attempt, base_delay, max_delay)
                    logger.warning(f"{func.__name__} attempt {attempt + 1} failed: {e}. Retrying in {delay:.2f}s...")
                    
                    # Call retry callback if provided
                    if on_retry:
                        try:
                            on_retry(attempt + 1, e, delay)
                        except Exception as callback_error:
                            logger.warning(f"Retry callback failed: {callback_error}")
                    
                    time.sleep(delay)
            
            # This should never be reached, but just in case
            raise last_exception
        
        return wrapper
    return decorator

def circuit_breaker(failure_threshold: int = 5, recovery_timeout: float = 60.0):
    """
    Simple circuit breaker pattern to prevent cascading failures.
    
    Args:
        failure_threshold: Number of failures before opening circuit
        recovery_timeout: Time to wait before attempting recovery
    
    Returns:
        Decorated function with circuit breaker logic
    """
    def decorator(func: Callable) -> Callable:
        # Circuit breaker state
        state = {
            'failures': 0,
            'last_failure_time': 0,
            'is_open': False
        }
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            current_time = time.time()
            
            # Check if circuit is open and if recovery timeout has passed
            if state['is_open']:
                if current_time - state['last_failure_time'] > recovery_timeout:
                    logger.info(f"Circuit breaker for {func.__name__} attempting recovery")
                    state['is_open'] = False
                    state['failures'] = 0
                else:
                    raise APIHealthError(f"Circuit breaker is open for {func.__name__}. Service appears unhealthy.")
            
            try:
                result = func(*args, **kwargs)
                
                # Reset failure count on success
                if state['failures'] > 0:
                    logger.info(f"Circuit breaker for {func.__name__} recovered after {state['failures']} failures")
                    state['failures'] = 0
                
                return result
                
            except Exception as e:
                state['failures'] += 1
                state['last_failure_time'] = current_time
                
                # Open circuit if failure threshold is reached
                if state['failures'] >= failure_threshold:
                    state['is_open'] = True
                    logger.error(f"Circuit breaker opened for {func.__name__} after {failure_threshold} failures")
                
                raise e
        
        return wrapper
    return decorator

# Specialized retry configurations for different API types

# Google Places API - more aggressive retries due to quota limits
google_places_retry = retry_with_backoff(
    max_attempts=4,
    base_delay=2.0,
    max_delay=30.0
)

# TMDB API - lighter retries, usually more reliable
tmdb_retry = retry_with_backoff(
    max_attempts=3,
    base_delay=1.0,
    max_delay=15.0
)

# Email SMTP - conservative retries
email_retry = retry_with_backoff(
    max_attempts=2,
    base_delay=5.0,
    max_delay=30.0,
    retryable_errors=[
        ConnectionError,
        TimeoutError,
        # Note: SMTP errors are handled separately in email_tool.py
    ]
)

# OpenAI API - moderate retries
openai_retry = retry_with_backoff(
    max_attempts=3,
    base_delay=2.0,
    max_delay=45.0
) 