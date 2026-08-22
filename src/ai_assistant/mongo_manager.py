"""
MongoDB 对话记录管理模块

使用 MongoDB 存储用户的对话记录，实现上下文功能。
每个会话(conversation)包含多条消息(message)。
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from bson import ObjectId

from src.config import settings


class MongoManager:
    """
    MongoDB 连接与对话记录管理

    数据结构:
    - conversations 集合:
      {
        "_id": ObjectId,
        "user_id": "default_user",         # 用户标识
        "title": "对话标题",                # 取自用户第一条消息摘要
        "created_at": datetime,
        "updated_at": datetime,
        "messages": [                       # 消息列表（内嵌）
          {
            "role": "user",                 # user / assistant
            "content": "用户输入内容",
            "timestamp": datetime,
            "process_steps": [],            # 助手处理步骤（仅 assistant 消息）
            "parsed_keywords": {...},       # 解析出的关键词组（仅 user 消息）
          },
          ...
        ]
      }
    """

    _client = None
    _db = None

    @classmethod
    def _get_client(cls):
        """懒加载 MongoDB 客户端（单例）。"""
        if cls._client is None:
            from pymongo import MongoClient
            cls._client = MongoClient(settings.MONGO_URL, serverSelectionTimeoutMS=5000)
            # 测试连接
            cls._client.admin.command("ping")
            cls._db = cls._client[settings.MONGO_DB]
            # 创建索引
            cls._db.conversations.create_index("user_id")
            cls._db.conversations.create_index([("updated_at", -1)])
        return cls._db

    @classmethod
    def get_db(cls):
        """获取数据库实例。"""
        return cls._get_client()

    @classmethod
    def check_connection(cls) -> bool:
        """检查 MongoDB 连接是否正常。"""
        try:
            cls._get_client()
            return True
        except Exception as e:
            print(f"[MongoManager] Connection failed: {e}")
            return False

    # ========== 对话管理 ==========

    @classmethod
    def create_conversation(cls, user_id: str = "default_user", title: str = "新对话") -> str:
        """创建新对话，返回对话ID。"""
        db = cls.get_db()
        now = datetime.utcnow()
        result = db.conversations.insert_one({
            "user_id": user_id,
            "title": title,
            "created_at": now,
            "updated_at": now,
            "messages": [],
        })
        return str(result.inserted_id)

    @classmethod
    def list_conversations(cls, user_id: str = "default_user", limit: int = 50) -> List[Dict]:
        """列出用户的所有对话（按更新时间倒序）。"""
        db = cls.get_db()
        cursor = db.conversations.find(
            {"user_id": user_id},
            {
                "title": 1,
                "created_at": 1,
                "updated_at": 1,
                "message_count": {"$size": "$messages"},
            }
        ).sort("updated_at", -1).limit(limit)
        conversations = []
        for conv in cursor:
            conversations.append({
                "id": str(conv["_id"]),
                "title": conv.get("title", "新对话"),
                "created_at": conv["created_at"].isoformat() if conv.get("created_at") else None,
                "updated_at": conv["updated_at"].isoformat() if conv.get("updated_at") else None,
                "message_count": conv.get("message_count", 0),
            })
        return conversations

    @classmethod
    def get_conversation(cls, conversation_id: str) -> Optional[Dict]:
        """获取单个对话的完整内容（含所有消息）。"""
        db = cls.get_db()
        conv = db.conversations.find_one({"_id": ObjectId(conversation_id)})
        if not conv:
            return None
        # 序列化
        messages = []
        for msg in conv.get("messages", []):
            messages.append({
                "role": msg.get("role", ""),
                "content": msg.get("content", ""),
                "timestamp": msg["timestamp"].isoformat() if msg.get("timestamp") else None,
                "process_steps": msg.get("process_steps", []),
                "parsed_keywords": msg.get("parsed_keywords"),
                "logs": msg.get("logs", []),
            })
        return {
            "id": str(conv["_id"]),
            "title": conv.get("title", "新对话"),
            "messages": messages,
        }

    @classmethod
    def add_message(
        cls,
        conversation_id: str,
        role: str,
        content: str,
        process_steps: Optional[List[Dict]] = None,
        parsed_keywords: Optional[Dict] = None,
        logs: Optional[List[Dict]] = None,
    ) -> bool:
        """
        向对话中追加一条消息。

        参数:
            conversation_id: 对话ID
            role: 消息角色 (user / assistant)
            content: 消息内容
            process_steps: 处理步骤列表（仅 assistant 消息）
            parsed_keywords: 解析出的关键词组（仅 user 消息）
            logs: 运行日志列表（仅 assistant 消息，爬虫日志等）
        """
        db = cls.get_db()
        now = datetime.utcnow()
        message = {
            "role": role,
            "content": content,
            "timestamp": now,
        }
        if process_steps:
            message["process_steps"] = process_steps
        if parsed_keywords:
            message["parsed_keywords"] = parsed_keywords
        if logs:
            message["logs"] = logs

        result = db.conversations.update_one(
            {"_id": ObjectId(conversation_id)},
            {
                "$push": {"messages": message},
                "$set": {"updated_at": now},
            }
        )
        return result.modified_count > 0

    @classmethod
    def update_message(
        cls,
        conversation_id: str,
        message_index: int,
        content: Optional[str] = None,
        process_steps: Optional[List[Dict]] = None,
    ) -> bool:
        """更新对话中指定位置的消息（用于流式更新 assistant 回复）。"""
        db = cls.get_db()
        update_fields = {}
        if content is not None:
            update_fields[f"messages.{message_index}.content"] = content
        if process_steps is not None:
            update_fields[f"messages.{message_index}.process_steps"] = process_steps
        update_fields["updated_at"] = datetime.utcnow()
        if not update_fields:
            return False
        result = db.conversations.update_one(
            {"_id": ObjectId(conversation_id)},
            {"$set": update_fields}
        )
        return result.modified_count > 0

    @classmethod
    def delete_conversation(cls, conversation_id: str) -> bool:
        """删除对话。"""
        db = cls.get_db()
        result = db.conversations.delete_one({"_id": ObjectId(conversation_id)})
        return result.deleted_count > 0

    @classmethod
    def get_context_messages(
        cls,
        conversation_id: str,
        max_messages: int = 10,
    ) -> List[Dict]:
        """
        获取对话上下文消息（用于 LLM 上下文）。

        返回最近的消息列表，格式兼容 OpenAI API:
        [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]
        """
        conv = cls.get_conversation(conversation_id)
        if not conv:
            return []
        messages = conv.get("messages", [])
        # 取最近的消息
        recent = messages[-max_messages:] if len(messages) > max_messages else messages
        context = []
        for msg in recent:
            context.append({
                "role": msg.get("role", "user"),
                "content": msg.get("content", ""),
            })
        return context

    @classmethod
    def update_conversation_title(cls, conversation_id: str, title: str) -> bool:
        """更新对话标题。"""
        db = cls.get_db()
        result = db.conversations.update_one(
            {"_id": ObjectId(conversation_id)},
            {"$set": {"title": title, "updated_at": datetime.utcnow()}}
        )
        return result.modified_count > 0
