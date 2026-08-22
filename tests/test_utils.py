"""
工具层测试

测试城市码管理和文件IO模块。
"""

import sys
sys.path.insert(0, '.')

import os
import json
import tempfile
import pytest

from src.utils.city_codes import (
    get_city_code, get_city_name, list_cities, list_cities_with_codes,
)
from src.utils.file_io import DataWriter


class TestCityCodes:
    """城市码管理测试"""

    def test_get_city_code_known(self):
        """测试已知城市的码查询"""
        assert get_city_code("北京") == "101010100"
        assert get_city_code("上海") == "101020100"
        assert get_city_code("深圳") == "101280100"

    def test_get_city_code_unknown(self):
        """测试未知城市的码查询"""
        assert get_city_code("火星") is None

    def test_get_city_name(self):
        """测试反向查询"""
        assert get_city_name("101010100") == "北京"
        assert get_city_name("101020100") == "上海"
        assert get_city_name("999999999") is None

    def test_list_cities_all(self):
        """测试列出所有城市"""
        cities = list_cities()
        assert len(cities) > 0
        assert "北京" in cities
        assert "上海" in cities

    def test_list_cities_with_codes(self):
        """测试带码的城市列表"""
        result = list_cities_with_codes()
        assert len(result) > 0
        assert all("city" in item and "code" in item for item in result)


class TestDataWriter:
    """数据写入测试"""

    @pytest.fixture
    def writer(self, tmp_path):
        """创建临时目录的 DataWriter"""
        return DataWriter(str(tmp_path))

    @pytest.fixture
    def sample_jobs(self):
        """测试用职位数据"""
        return [
            {
                "job_id": "j001",
                "job_name": "AI Engineer",
                "salary_desc": "30-60K",
                "city": "Shanghai",
                "skills": ["Python", "PyTorch"],
            },
            {
                "job_id": "j002",
                "job_name": "Frontend Dev",
                "salary_desc": "20-40K",
                "city": "Beijing",
                "skills": ["Vue", "React"],
            },
        ]

    def test_save_json(self, writer, sample_jobs):
        """测试 JSON 保存"""
        filepath = writer.save_json(sample_jobs, "test.json")
        assert os.path.exists(filepath)
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert len(data) == 2

    def test_save_json_dedup(self, writer, sample_jobs):
        """测试 JSON 去重"""
        # 第一次保存
        writer.save_json(sample_jobs, "test.json")
        # 第二次保存（含重复 job_id + 新数据）
        new_jobs = [
            {"job_id": "j001", "job_name": "Updated Title", "salary_desc": "50-100K"},
            {"job_id": "j003", "job_name": "New Job", "salary_desc": "15-25K"},
        ]
        writer.save_json(new_jobs, "test.json")

        loaded = DataWriter._load_json(
            os.path.join(writer.output_dir, "test.json")
        )
        # 应该有3条（j001被更新，j002保留，j003新增）
        assert len(loaded) == 3
        j001 = next(j for j in loaded if j["job_id"] == "j001")
        assert j001["job_name"] == "Updated Title"

    def test_save_csv(self, writer, sample_jobs):
        """测试 CSV 保存"""
        filepath = writer.save_csv(sample_jobs, "test.csv")
        assert os.path.exists(filepath)
        # CSV 应该有 header + 2 rows
        with open(filepath, "r", encoding="utf-8-sig") as f:
            lines = f.readlines()
        assert len(lines) == 3  # header + 2 data rows

    def test_load_json_nonexistent(self):
        """测试加载不存在的文件"""
        assert DataWriter._load_json("/nonexistent/path.json") == []

    def test_merge_files(self, writer, tmp_path):
        """测试文件合并去重"""
        file1 = tmp_path / "f1.json"
        file2 = tmp_path / "f2.json"
        output = tmp_path / "merged.json"

        with open(file1, "w", encoding="utf-8") as f:
            json.dump([{"job_id": "a", "job_name": "Job A"}], f)
        with open(file2, "w", encoding="utf-8") as f:
            json.dump([
                {"job_id": "a", "job_name": "Job A Updated"},
                {"job_id": "b", "job_name": "Job B"},
            ], f)

        writer.merge_files(str(file1), str(file2), str(output))
        merged = DataWriter._load_json(str(output))
        assert len(merged) == 2  # 去重后2条


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
