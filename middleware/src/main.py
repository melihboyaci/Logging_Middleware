from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
import uvicorn

from middleware.src.api.routes import router
from middleware.src.config import MiddlewareConfig
from middleware.src.pipeline.pipeline_builder import build_pipeline
from middleware.src.transport.consumer import RabbitConsumer


@asynccontextmanager
async def lifespan(app: FastAPI):  # type: ignore[no-untyped-def]
    config = MiddlewareConfig()
    pipeline = build_pipeline()
    consumer = RabbitConsumer(config=config, process_log=pipeline.handle)
    app.state.consumer = consumer
    await consumer.start()
    try:
        yield
    finally:
        await consumer.stop()


def create_app() -> FastAPI:
    app = FastAPI(title="Logging Middleware", lifespan=lifespan)
    app.include_router(router)
    return app


def main() -> None:
    config = MiddlewareConfig()
    uvicorn.run(
        "middleware.src.main:create_app",
        host=config.host,
        port=config.port,
        factory=True,
    )


if __name__ == "__main__":
    main()
