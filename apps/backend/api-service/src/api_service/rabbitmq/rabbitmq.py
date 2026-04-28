import os
import aio_pika

class RabbitMQ:
    def __init__(self):
        self.host = os.getenv("RABBITMQ_HOST", "localhost")
        self.port = int(os.getenv("RABBITMQ_PORT", "5672"))
        self.user = os.getenv("RABBITMQ_USER", "admin")
        self.password = os.getenv("RABBITMQ_PASSWORD", "admin")

        self.connection = None
        self.channel = None

    async def connect(self):
        self.connection = await aio_pika.connect_robust(
            host=self.host,
            port=self.port,
            login=self.user,
            password=self.password,
        )

        self.channel = await self.connection.channel()
        await self.channel.set_qos(prefetch_count=10)

    async def close(self):
        if self.connection:
            await self.connection.close()


rabbitmq = RabbitMQ()