import logging
import os
import aio_pika

logger = logging.getLogger(__name__)

class RabbitMQ:
    def __init__(self):
        self.host = os.getenv("RABBITMQ_HOST", "localhost")
        self.port = int(os.getenv("RABBITMQ_PORT", "5672"))
        self.user = os.getenv("RABBITMQ_USER", "admin")
        self.password = os.getenv("RABBITMQ_PASSWORD", "admin")

        self.connection = None
        self.channel = None
        logger.info(f"RabbitMQ initialized with host={self.host}, port={self.port}")

    async def connect(self):
        try:
            logger.info(f"Connecting to RabbitMQ at {self.host}:{self.port}")
            self.connection = await aio_pika.connect_robust(
                host=self.host,
                port=self.port,
                login=self.user,
                password=self.password,
            )

            self.channel = await self.connection.channel(publisher_confirms=True)
            await self.channel.set_qos(prefetch_count=10)
            logger.info("Successfully connected to RabbitMQ and initialized channel")
        except Exception as e:
            logger.error(f"Failed to connect to RabbitMQ: {str(e)}")
            raise

    async def close(self):
        logger.info("Closing RabbitMQ connection")
        if self.connection:
            await self.connection.close()
        logger.info("RabbitMQ connection closed")


rabbitmq = RabbitMQ()