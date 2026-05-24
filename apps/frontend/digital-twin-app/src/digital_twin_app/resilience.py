from tenacity import retry, stop_after_attempt, wait_exponential
from pybreaker import CircuitBreaker


class BackendReadError(Exception):
    pass

# Initialize circuit breaker for backend API
backend_breaker = CircuitBreaker(
    fail_max=5,  # Open after 5 failures
    reset_timeout=60,  # Try to recover after 60 seconds
    exclude=[requests.exceptions.HTTPError],  # Don't break on 4xx errors
    listeners=[]  # Could add listeners for logging
)

# Function to fetch data from the backend API with error handling and logging
@backend_breaker
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=8),
    retry=retry_if_exception_type(BackendReadError),
    reraise=True
)
def fetch_backend_data(backend_api_url: str, timeout_s: int = 5):
    """Fetches data from the backend API with retries and exponential backoff for retryable errors.
    @param backend_api_url: URL of the backend API to fetch data from
    @param timeout_s: Timeout in seconds for the API request (default: 5)   
    @return: JSON response from the backend API
    @raises BackendReadError: If a retryable error occurs (e.g., 429, 500, 502, 503, 504)
    @raises requests.exceptions.RequestException: For non-retryable errors or if all retries fail
    """
    response = requests.get(backend_api_url, timeout=timeout_s)

    if response.status_code in [429, 500, 502, 503, 504]:
        raise BackendReadError(f"Retryable backend error: {response.status_code}")

    response.raise_for_status()
    return response.json()
