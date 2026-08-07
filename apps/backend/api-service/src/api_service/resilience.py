import logging
import pybreaker
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

logger = logging.getLogger(__name__)

class RabbitMQPublishError(Exception):
    pass


rabbitmq_breaker = pybreaker.CircuitBreaker(
    fail_max=5,
    reset_timeout=30
)


@rabbitmq_breaker
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=8),
    retry=retry_if_exception_type(RabbitMQPublishError),
    reraise=True
)
async def publish_with_resilience(publish_func, payload: dict):
    try:
        logger.info(f"Publishing message with resilience: event_id={payload.get('event_id')}")
        await publish_func(payload)
        logger.info(f"Successfully published message: event_id={payload.get('event_id')}")
    except Exception as e:
        logger.error(f"Failed to publish message: event_id={payload.get('event_id')}, error={str(e)}")
        raise RabbitMQPublishError(str(e)) from e