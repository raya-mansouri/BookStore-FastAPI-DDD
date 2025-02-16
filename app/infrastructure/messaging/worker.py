import asyncio
from application.events.reservation_event import consume_event

async def main():
    await consume_event()

if __name__ == "__main__":
    asyncio.run(main())


# services:
#   worker:
#     build: .
#     command: python -m application.events.reservation_event
#     depends_on:
#       - rabbitmq

# docker-compose up -d worker
