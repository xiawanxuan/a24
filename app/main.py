from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.endpoints import router as guangyun_router
from app.database import engine
from app import models

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="《广韵》古汉语音韵学查询服务",
    description="""
基于 FastAPI + SQLite 的古汉语音韵学 RESTful API 服务。

## 主要功能

- **汉字音韵查询**：按汉字查询《广韵》反切、声母、韵母、声调、韵图位置
- **反切推导**：根据反切上字和下字推导可能的读音组合
- **音韵相似度计算**：基于韵图位置（等、呼、摄、声母、韵母、声调）计算音韵相似度
- **多条件搜索**：支持按声母、韵母、声调、韵摄、等呼等条件组合查询

## API 版本

当前版本：v1

## 数据说明

示例数据基于《广韵》音系，包含声母、韵母、声调、韵摄、等呼等韵图信息。
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(guangyun_router)


@app.get("/", summary="服务信息", tags=["系统"])
def root():
    return {
        "name": "《广韵》古汉语音韵学查询服务",
        "version": "1.0.0",
        "status": "running",
        "api_docs": "/docs",
        "redoc_docs": "/redoc",
        "openapi": "/openapi.json"
    }


@app.get("/health", summary="健康检查", tags=["系统"])
def health_check():
    return {"status": "healthy"}
