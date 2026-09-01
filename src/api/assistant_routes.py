"""
AI 助手 API 路由

提供以下接口：
- POST /api/assistant/chat        - 对话（SSE流式返回处理过程和分析结果）
- GET  /api/assistant/conversations - 获取对话列表
- GET  /api/assistant/conversation/{id} - 获取单个对话详情
- DELETE /api/assistant/conversation/{id} - 删除对话
- POST /api/assistant/new-chat    - 创建新对话
- GET  /api/assistant/check       - 检查AI助手服务状态
"""

import json
import time
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from src.models.database import get_db
from src.ai_assistant.assistant_service import AssistantService
from src.ai_assistant.mongo_manager import MongoManager
from src.services.login_manager import LoginManager

router = APIRouter(prefix="/api/assistant", tags=["ai-assistant"])


# ========== 请求/响应 Schema ==========

class ChatRequest(BaseModel):
    """对话请求"""
    message: str = Field(..., description="用户输入消息")
    conversation_id: Optional[str] = Field(None, description="对话ID，为空则创建新对话")
    user_id: str = Field(default="default_user", description="用户标识")


class NewChatRequest(BaseModel):
    """新建对话请求"""
    user_id: str = Field(default="default_user", description="用户标识")
    title: str = Field(default="新对话", description="对话标题")


class LoginConfirmRequest(BaseModel):
    """登录确认请求"""
    session_id: str = Field(..., description="登录会话ID")
    success: bool = Field(default=True, description="是否成功完成登录")


# ========== 对话接口 ==========

@router.post("/chat")
def chat(req: ChatRequest, db: Session = Depends(get_db)):
    """
    AI 助手对话接口（SSE 流式返回）。

    通过 Server-Sent Events 逐步返回处理过程和分析结果：
    - step: 处理步骤（解析需求、检查数据库、爬取、查询、分析）
    - content: LLM 流式输出的分析内容片段
    - done: 完成信号
    - error: 错误信号
    """
    service = AssistantService()

    def event_generator():
        try:
            for event in service.chat(
                user_input=req.message,
                db=db,
                conversation_id=req.conversation_id,
                user_id=req.user_id,
            ):
                yield f"data: {json.dumps(event, ensure_ascii=False)}\n\n"
        except Exception as e:
            error_event = {"type": "error", "message": f"服务异常: {e}"}
            yield f"data: {json.dumps(error_event, ensure_ascii=False)}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/conversations")
def list_conversations(user_id: str = "default_user", limit: int = 50):
    """获取用户的对话列表。"""
    try:
        conversations = MongoManager.list_conversations(user_id, limit)
        return {"conversations": conversations}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取对话列表失败: {e}")


@router.get("/conversation/{conversation_id}")
def get_conversation(conversation_id: str):
    """获取单个对话的完整内容。"""
    try:
        conv = MongoManager.get_conversation(conversation_id)
        if not conv:
            raise HTTPException(status_code=404, detail="对话不存在")
        return conv
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取对话失败: {e}")


@router.delete("/conversation/{conversation_id}")
def delete_conversation(conversation_id: str):
    """删除对话。"""
    try:
        success = MongoManager.delete_conversation(conversation_id)
        if not success:
            raise HTTPException(status_code=404, detail="对话不存在")
        return {"status": "success", "message": "对话已删除"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除对话失败: {e}")


@router.post("/new-chat")
def new_chat(req: NewChatRequest):
    """创建新对话。"""
    try:
        conversation_id = MongoManager.create_conversation(
            user_id=req.user_id, title=req.title
        )
        return {"conversation_id": conversation_id, "title": req.title}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建对话失败: {e}")


@router.post("/login-confirm")
def confirm_login(req: LoginConfirmRequest):
    """
    用户完成登录/验证后，前端调用此接口通知后端继续爬取。

    流程：
    1. 爬虫检测到未登录/风控 → SSE 推送 login_required 事件（含 session_id）
    2. 前端弹出对话框，引导用户在 Chrome 中完成登录/验证
    3. 用户完成后，前端调用此接口
    4. 后端解除爬虫线程的阻塞，继续采集
    """
    login_manager = LoginManager()
    if req.success:
        ok = login_manager.confirm_login(req.session_id)
        if not ok:
            raise HTTPException(status_code=404, detail="登录会话不存在或已过期")
        return {"status": "success", "message": "登录确认已收到，将继续采集"}
    else:
        login_manager.cancel_login(req.session_id)
        return {"status": "cancelled", "message": "已取消登录"}


@router.get("/check")
def check_service():
    """检查 AI 助手服务状态。"""
    from src.config import settings

    result = {
        "mongo_connected": False,
        "llm_configured": bool(settings.LLM_API_KEY),
        "llm_model": settings.LLM_MODEL,
        "llm_base_url": settings.LLM_BASE_URL,
    }

    try:
        result["mongo_connected"] = MongoManager.check_connection()
    except Exception as e:
        result["mongo_error"] = str(e)

    return result
