"""
数据文件读写模块

支持 JSON / CSV 格式的数据写入、读取和合并。
核心特性：
- 按 job_id 去重（同ID覆盖更新）
- 增量写入（每页抓完立即保存，Ctrl+C 不丢数据）
- CSV 使用 UTF-8 BOM 编码（Excel 兼容）
"""

import json
import csv
import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

from src.config import settings


class DataWriter:
    """
    数据写入管理器

    支持 JSON / CSV 双格式输出，按 job_id 去重，增量写入。
    """

    def __init__(self, output_dir: Optional[str] = None):
        """
        初始化数据写入器。

        参数:
            output_dir: 输出目录，默认使用配置中的 JOB_RESULT_DIR
        """
        self.output_dir = Path(output_dir) if output_dir else settings.JOB_RESULT_DIR
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def save_json(
        self, jobs: List[Dict], filename: Optional[str] = None
    ) -> str:
        """
        保存职位数据为 JSON 文件，按 job_id 去重。

        参数:
            jobs: 职位数据列表
            filename: 文件名（不含路径），不传则自动生成时间戳文件名

        返回:
            保存的文件完整路径
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M")
            filename = f"boss_jobs_{timestamp}.json"
        filepath = self.output_dir / filename

        # 读取已有数据
        existing: Dict[str, Dict] = {}
        if filepath.exists():
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    for job in json.load(f):
                        jid = job.get("job_id")
                        if jid:
                            existing[jid] = job
            except (json.JSONDecodeError, IOError):
                pass

        # 合并新数据（同ID覆盖更新）
        for job in jobs:
            jid = job.get("job_id")
            if jid:
                existing[jid] = job

        merged = list(existing.values())

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(merged, f, ensure_ascii=False, indent=2)

        return str(filepath)

    def save_csv(
        self, jobs: List[Dict], filename: Optional[str] = None
    ) -> str:
        """
        保存职位数据为 CSV 文件（UTF-8 BOM 编码，Excel 兼容）。

        参数:
            jobs: 职位数据列表
            filename: 文件名（不含路径）

        返回:
            保存的文件完整路径
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M")
            filename = f"boss_jobs_{timestamp}.csv"
        filepath = self.output_dir / filename

        if not jobs:
            return str(filepath)

        fields = [
            "job_name", "salary_desc", "city", "area",
            "experience", "education", "company_name",
            "company_industry", "company_scale", "skills",
            "job_desc", "boss_name", "boss_active_status",
            "fetch_time",
        ]

        with open(filepath, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
            writer.writeheader()
            for job in jobs:
                row = dict(job)
                # 列表字段转为管道分隔字符串
                if isinstance(row.get("skills"), list):
                    row["skills"] = " | ".join(row["skills"])
                if isinstance(row.get("welfare"), list):
                    row["welfare"] = " | ".join(row["welfare"])
                writer.writerow(row)

        return str(filepath)

    def merge_files(self, file1: str, file2: str, output: str) -> str:
        """
        合并两个 JSON 文件，按 job_id 去重。

        参数:
            file1: 第一个 JSON 文件路径
            file2: 第二个 JSON 文件路径
            output: 合并后输出路径

        返回:
            输出文件路径
        """
        data1 = self._load_json(file1)
        data2 = self._load_json(file2)

        merged: Dict[str, Dict] = {}
        for job in data1 + data2:
            jid = job.get("job_id")
            if jid:
                merged[jid] = job

        result = list(merged.values())
        with open(output, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        return output

    def load_latest_json(self) -> List[Dict]:
        """
        加载输出目录中最新的 JSON 结果文件。

        返回:
            职位数据列表，无文件则返回空列表
        """
        json_files = sorted(
            self.output_dir.glob("boss_jobs_*.json"),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )
        if not json_files:
            return []
        return self._load_json(str(json_files[0]))

    @staticmethod
    def _load_json(filepath: str) -> List[Dict]:
        """加载 JSON 文件，文件不存在或解析失败返回空列表。"""
        if not os.path.exists(filepath):
            return []
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data if isinstance(data, list) else []
        except (json.JSONDecodeError, IOError):
            return []

