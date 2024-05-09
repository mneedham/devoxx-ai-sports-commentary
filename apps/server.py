from aiokafka import AIOKafkaConsumer
import asyncio
from fastapi import FastAPI, Request
from sse_starlette.sse import EventSourceResponse
import uvicorn
from uuid import uuid4

STREAM_DELAY = 1

app = FastAPI()

# @app.on_event("startup")
# async def startup_event():
#   global consumer
#   consumer = AIOKafkaConsumer(
#     'livetext',
#     bootstrap_servers='localhost:9092',
#     group_id="demo-dunith-mark2",
#     auto_offset_reset='earliest',
#     value_deserializer=lambda x: x.decode('utf-8')
#   )
#   await consumer.start()

# @app.on_event("shutdown")
# async def shutdown_event():
#   await consumer.stop()

# @app.get("/livetext")
# async def livetext(request: Request):
#   async def event_generator():
#     while True:
#       if await request.is_disconnected():
#         break
#       try:
#         async for msg in consumer:
#           yield f"{msg.value}\n\n"
#         await asyncio.sleep(STREAM_DELAY)
#       except Exception as e:
#         yield f"data: Error - {str(e)}\n\n"
#         break

#   return EventSourceResponse(event_generator())

@app.get("/livetext")
async def livetext(request: Request):
    async def event_generator():
        # Create a unique group_id for each consumer
        group_id = f"demo-dunith-mark-{uuid4()}"
        consumer = AIOKafkaConsumer(
            'livetext',
            bootstrap_servers='localhost:9092',
            group_id=group_id,
            auto_offset_reset='earliest',
            value_deserializer=lambda x: x.decode('utf-8')
        )
        await consumer.start()
        try:
            while True:
                if await request.is_disconnected():
                    break
                async for msg in consumer:
                    yield f"{msg.value}\n\n"
                await asyncio.sleep(STREAM_DELAY)
        except Exception as e:
            yield f"data: Error - {str(e)}\n\n"
        finally:
            await consumer.stop()
    return EventSourceResponse(event_generator())

if __name__ == "__main__":
  uvicorn.run(app, host="0.0.0.0", port=8000)
