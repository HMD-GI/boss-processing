"""
简历 PDF 解析服务

支持两种解析模式：
1. AI 大模型解析（推荐）：使用 DeepSeek API 将 PDF 文本智能解析为结构化 JSON
2. 正则规则解析（兜底）：当未配置 API Key 时使用正则+模式匹配

还支持从 PDF 中提取图片（用于头像）。
"""

import re
import io
import os
import json
import base64
import time
import pdfplumber


class ResumeParser:
    """简历 PDF 解析器"""

    # 正则模式定义
    PHONE_RE = re.compile(r'1[3-9]\d[-\s]?\d{4}[-\s]?\d{4}')
    EMAIL_RE = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
    GITHUB_RE = re.compile(r'github\.com/[\w-]+', re.IGNORECASE)
    DATE_RE = re.compile(r'(\d{4})[.\-/年](\d{1,2})[.\-/月]?')
    GPA_RE = re.compile(r'GPA[:\s]*([0-9.]+/[0-9.]+|[0-9.]+)', re.IGNORECASE)
    RANK_RE = re.compile(r'(?:排名|Rank)[:\s]*([^\s,，]+)', re.IGNORECASE)

    SECTION_KEYWORDS = {
        'education': ['教育经历', '教育背景', '学历', '教育', 'Education'],
        'work': ['工作经历', '工作背景', '实习经历', '实习', '工作', 'Work', 'Experience', '职业经历'],
        'project': ['项目经历', '项目经验', '项目', 'Project', 'Projects'],
        'skill': ['专业技能', '技能', '技术栈', 'Skill', 'Skills', 'Technology'],
        'award': ['奖项荣誉', '荣誉奖项', '获奖', '奖项', '荣誉', 'Award', 'Awards', 'Honor'],
        'self': ['自我评价', '个人简介', '自我介绍', '个人总结', 'Summary', 'Profile', 'About'],
    }

    # AI 解析的系统提示词
    AI_SYSTEM_PROMPT = """你是一个专业的简历解析助手。用户会提供从 PDF 中提取的简历文本，你需要将其解析为结构化的 JSON 数据。

请严格按照以下 JSON 格式输出，所有字段如果简历中未提及则留空字符串或空数组：

{
  "personal": {
    "name": "姓名",
    "phone": "手机号",
    "email": "邮箱",
    "wechat": "微信号",
    "github": "GitHub地址",
    "blog": "博客地址",
    "jobIntention": "求职意向/目标职位",
    "gpa": "GPA",
    "rank": "排名",
    "selfEvaluation": "自我评价/个人简介"
  },
  "education": [
    {
      "school": "学校名称",
      "degree": "学位（大专/本科/硕士/博士）",
      "major": "专业",
      "gpa": "GPA",
      "rank": "排名",
      "courses": "主修课程",
      "startDate": "开始时间，格式 YYYY-MM",
      "endDate": "结束时间，格式 YYYY-MM"
    }
  ],
  "workExperience": [
    {
      "company": "公司名称",
      "department": "部门",
      "position": "职位",
      "startDate": "开始时间，格式 YYYY-MM",
      "endDate": "结束时间，格式 YYYY-MM 或 至今",
      "type": "工作或实习",
      "description": ["工作内容描述1", "工作内容描述2"]
    }
  ],
  "projects": [
    {
      "name": "项目名称",
      "role": "担任角色",
      "techStack": "技术栈",
      "description": "项目描述",
      "achievements": "项目成果"
    }
  ],
  "awards": [
    {
      "name": "奖项名称",
      "organization": "颁发机构",
      "level": "等级（如：国家级/省级/校级）",
      "category": "类别",
      "date": "获奖时间，格式 YYYY-MM"
    }
  ],
  "skills": [
    {"name": "技能名称"}
  ],
  "suggestedTemplate": "根据简历的排版风格推荐最匹配的模板ID，可选值：simple(经典简约)、modern(现代简约)、sidebar(侧边栏风格)、professional(商务专业)、creative(创意风格)、elegant(雅致风格)、classic(经典横幅)、darksidebar(深色侧栏)、minimal(极简留白)"
}

【重要解析规则】：
1. 日期统一格式为 YYYY-MM，如 2019-09。如果只有年份如 2019.09 或 2019年9月，也转为 2019-09。
2. 如果某个信息无法确定，留空字符串。
3. 技能只需要 name 字段，不需要 level。每条技能可以是一句话，如 "熟悉Python及Django框架" 或 "3年Java后端开发经验"。
4. 工作经历的 description 是字符串数组，每条描述是工作中的一项职责或成就。
5. suggestedTemplate 根据简历整体风格判断：简洁单栏选simple/modern/minimal，有侧边栏选sidebar/darksidebar，商务正式选professional/classic，创意设计选creative，优雅排版选elegant。

【工作经历解析要点 - 非常重要】：
- 必须提取简历中的【每一份】工作/实习经历，不能遗漏任何一段。
- 每段工作经历应包含：公司名称(company)、职位(position)、起止时间(startDate/endDate)。
- 部门(department)如果简历中有则提取，没有则留空。
- 工作内容描述(description)：把该段工作下的所有职责描述、项目内容、工作成果都提取为字符串数组中的独立条目，每条描述尽量保持原文的完整性，不要遗漏。
- 如果一段工作下有多条描述（如用 •、-、数字序号等列出的），每一条都应作为数组中的独立元素。
- 类型(type)：如果是实习标注为"实习"，否则为"工作"。
- 仔细区分不同公司/不同时间段的工作经历，不要把多段工作合并为一段。

【项目经历解析要点 - 非常重要】：
- 必须提取简历中的【每一个】项目，不能遗漏。
- 每个项目应包含：项目名称(name)、角色(role)、技术栈(techStack)、项目描述(description)、项目成果(achievements)。
- 项目描述(description)：尽量完整地描述项目背景、功能、规模等信息，不要只提取一句话。如果有多段描述，合并为一个完整的字符串。
- 项目成果(achievements)：提取项目取得的成果、业绩、量化数据等。如果没有则留空。
- 技术栈(techStack)：提取项目使用的技术、框架、工具等，用逗号分隔。
- 不要把工作经历中的项目混淆为独立的项目经历，除非简历中有单独的"项目经历"板块。
- 如果简历中没有明确的项目经历板块，但有项目相关描述，可以根据内容判断是否为独立项目。

【教育经历解析要点】：
- 提取每一段教育经历，包括学校、专业、学位、起止时间、GPA、排名、主修课程。

必须输出合法的 JSON，不要包含任何注释或额外文本。"""

    def parse(self, pdf_bytes: bytes) -> dict:
        """
        解析 PDF 文件，返回标准化简历数据。

        优先使用 AI 大模型解析，未配置 API Key 时回退到正则解析。
        """
        # 1. 提取文本
        text = self._extract_text(pdf_bytes)
        if not text.strip():
            return self._empty_result()

        # 2. 提取图片（用于头像）
        avatar_base64 = self._extract_avatar_image(pdf_bytes)

        # 3. 尝试 AI 解析（从 .env 读取大模型配置）
        api_key = os.getenv('LLM_API_KEY', '') or os.getenv('DEEPSEEK_API_KEY', '')  # 兼容旧配置
        if api_key:
            try:
                result = self._parse_with_ai(text, api_key)
                if avatar_base64:
                    result['personal']['avatar'] = avatar_base64
                result['parseMethod'] = 'ai'
                return result
            except Exception as e:
                print(f"[ResumeParser] AI parse failed, falling back to regex: {e}")

        # 4. 正则解析（兜底）
        result = self._parse_with_regex(text)
        if avatar_base64:
            result['personal']['avatar'] = avatar_base64
        result['parseMethod'] = 'regex'
        return result

    def _extract_text(self, pdf_bytes: bytes) -> str:
        """使用 pdfplumber 提取 PDF 全文文本。"""
        text_parts = []
        try:
            with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text() or ''
                    text_parts.append(page_text)
        except Exception as e:
            print(f"[ResumeParser] PDF extraction error: {e}")
        return '\n'.join(text_parts)

    def _extract_avatar_image(self, pdf_bytes: bytes) -> str:
        """
        从 PDF 中提取可能的头像图片。

        策略：提取所有图片，选择最接近证件照比例（宽高比 0.65~0.8）的较大图片。
        返回 base64 编码的 data URL。
        """
        try:
            with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
                for page in pdf.pages[:2]:  # 只看前两页
                    images = page.images
                    if not images:
                        continue

                    best_img = None
                    best_score = 0

                    for img_info in images:
                        w = img_info.get('width', 0)
                        h = img_info.get('height', 0)
                        if w < 30 or h < 40:
                            continue

                        ratio = w / h if h > 0 else 0
                        # 证件照比例约 0.65~0.8（一寸 25×35=0.714）
                        if 0.5 < ratio < 0.9:
                            score = w * h  # 面积越大优先
                            if score > best_score:
                                best_score = score
                                best_img = img_info

                    if best_img:
                        # 尝试从页面中裁剪图片区域
                        try:
                            # pdfplumber 的 image 提取需要用 page.crop
                            bbox = (
                                best_img['x0'],
                                best_img['top'],
                                best_img['x1'],
                                best_img['bottom'],
                            )
                            cropped = page.crop(bbox)
                            im = cropped.to_image(resolution=150)
                            buf = io.BytesIO()
                            im.original.save(buf, format='PNG')
                            img_data = base64.b64encode(buf.getvalue()).decode('utf-8')
                            return f"data:image/png;base64,{img_data}"
                        except Exception as e:
                            print(f"[ResumeParser] Image crop failed: {e}")
                            continue
        except Exception as e:
            print(f"[ResumeParser] Avatar extraction error: {e}")

        return ''

    def _parse_with_ai(self, text: str, api_key: str) -> dict:
        """使用 AI 大模型解析简历文本。

        大模型配置从 .env 文件读取：
        - LLM_API_KEY: API Key
        - LLM_BASE_URL: API Base URL（如 https://api.deepseek.com）
        - LLM_MODEL: 模型名称（如 deepseek-chat）
        """
        from openai import OpenAI

        # 从环境变量读取大模型配置，兼容旧版 DEEPSEEK_* 变量
        base_url = os.getenv('LLM_BASE_URL', '') or os.getenv('DEEPSEEK_BASE_URL', 'https://api.deepseek.com')
        model_name = os.getenv('LLM_MODEL', '') or os.getenv('DEEPSEEK_MODEL', 'deepseek-chat')

        client = OpenAI(
            api_key=api_key,
            base_url=base_url,
        )

        # 截断过长的文本（防止超出 token 限制）
        max_chars = 12000
        user_text = text[:max_chars] if len(text) > max_chars else text

        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": self.AI_SYSTEM_PROMPT},
                {"role": "user", "content": f"请仔细解析以下简历文本，务必提取所有工作经历和项目经历，不要遗漏任何条目。输出 JSON：\n\n{user_text}"},
            ],
            response_format={'type': 'json_object'},
            max_tokens=8192,
            temperature=0.1,
        )

        content = response.choices[0].message.content
        if not content or not content.strip():
            raise ValueError("AI 返回了空内容")

        parsed = json.loads(content)

        # 确保数据结构完整
        result = self._empty_result()

        # 合并 AI 解析结果
        if 'personal' in parsed:
            result['personal'].update(parsed['personal'])

        for field in ['education', 'workExperience', 'projects', 'awards', 'skills']:
            if field in parsed and isinstance(parsed[field], list):
                # 为每条数据添加 id
                for i, item in enumerate(parsed[field]):
                    if isinstance(item, dict):
                        if 'id' not in item:
                            item['id'] = int(time.time() * 1000) + i
                        result[field].append(item)

        # 确保 skills 只有 name 字段
        for skill in result['skills']:
            if 'level' in skill:
                del skill['level']
            if not skill.get('name', '').strip():
                result['skills'] = [s for s in result['skills'] if s is not skill]
        result['skills'] = [s for s in result['skills'] if s.get('name', '').strip()]

        # 确保 workExperience 的 description 是列表，并过滤空条目
        for work in result['workExperience']:
            if 'description' in work and isinstance(work['description'], str):
                work['description'] = [work['description']]
            elif 'description' not in work:
                work['description'] = []
            # 过滤空描述
            work['description'] = [d.strip() for d in work['description'] if d and d.strip()]
        # 过滤掉没有公司名的工作经历
        result['workExperience'] = [w for w in result['workExperience'] if w.get('company', '').strip()]

        # 确保项目经历字段完整，过滤空条目
        for proj in result['projects']:
            if 'description' not in proj:
                proj['description'] = ''
            if 'achievements' not in proj:
                proj['achievements'] = ''
            if 'techStack' not in proj:
                proj['techStack'] = ''
            if 'role' not in proj:
                proj['role'] = ''
        result['projects'] = [p for p in result['projects'] if p.get('name', '').strip()]

        # 过滤空奖项
        result['awards'] = [a for a in result['awards'] if a.get('name', '').strip()]

        # 过滤空教育经历
        result['education'] = [e for e in result['education'] if e.get('school', '').strip()]

        # 应用建议的模板
        suggested = parsed.get('suggestedTemplate', '')
        if suggested and suggested in ['simple', 'modern', 'sidebar', 'professional', 'creative', 'elegant', 'classic', 'darksidebar', 'minimal']:
            result['templateId'] = suggested
            result['suggestedTemplate'] = suggested

        return result

    # ========== 正则解析（兜底方案） ==========

    def _parse_with_regex(self, text: str) -> dict:
        """使用正则+模式匹配解析简历文本。"""
        sections = self._split_sections(text)
        result = self._empty_result()

        self._parse_personal(result, text, sections)
        self._parse_education(result, sections.get('education', ''))
        self._parse_work(result, sections.get('work', ''))
        self._parse_projects(result, sections.get('project', ''))
        self._parse_skills(result, sections.get('skill', ''))
        self._parse_awards(result, sections.get('award', ''))
        self._parse_self_evaluation(result, sections.get('self', ''))

        return result

    def _split_sections(self, text: str) -> dict:
        lines = text.split('\n')
        sections = {}
        current_section = None
        current_lines = []

        for line in lines:
            stripped = line.strip()
            if not stripped:
                if current_section:
                    current_lines.append('')
                continue

            matched_section = self._match_section_title(stripped)
            if matched_section:
                if current_section:
                    sections[current_section] = '\n'.join(current_lines).strip()
                current_section = matched_section
                current_lines = []
            else:
                if current_section:
                    current_lines.append(stripped)
                else:
                    if 'header' not in sections:
                        sections['header'] = []
                    if isinstance(sections['header'], list):
                        sections['header'].append(stripped)

        if current_section:
            sections[current_section] = '\n'.join(current_lines).strip()

        if 'header' in sections and isinstance(sections['header'], list):
            sections['header'] = '\n'.join(sections['header'])

        return sections

    def _match_section_title(self, line: str) -> str:
        clean = re.sub(r'[【】\[\]|\-—·•►▸■◆☆★\s]+', '', line)
        if not clean or len(clean) > 20:
            return None
        for section, keywords in self.SECTION_KEYWORDS.items():
            for kw in keywords:
                if kw in clean:
                    return section
        return None

    def _parse_personal(self, result, full_text, sections):
        header = sections.get('header', '')
        header_lines = header.split('\n')[:10] if header else full_text.split('\n')[:5]

        for line in header_lines:
            clean = line.strip()
            if clean and not re.search(r'[\d@]', clean) and 2 <= len(clean) <= 10:
                result['personal']['name'] = clean
                break

        phone_match = self.PHONE_RE.search(full_text)
        if phone_match:
            result['personal']['phone'] = phone_match.group()

        email_match = self.EMAIL_RE.search(full_text)
        if email_match:
            result['personal']['email'] = email_match.group()

        github_match = self.GITHUB_RE.search(full_text)
        if github_match:
            result['personal']['github'] = github_match.group()

        intention_match = re.search(r'(?:求职意向|意向|目标职位|求职目标)[:\s]*([^\n]+)', full_text)
        if intention_match:
            result['personal']['jobIntention'] = intention_match.group(1).strip()

        gpa_match = self.GPA_RE.search(full_text)
        if gpa_match:
            result['personal']['gpa'] = gpa_match.group(1)

        rank_match = self.RANK_RE.search(full_text)
        if rank_match:
            result['personal']['rank'] = rank_match.group(1)

    def _parse_education(self, result, text):
        if not text:
            return
        entries = self._split_entries(text)
        for entry_text in entries:
            entry = {
                'id': int(time.time() * 1000) + len(result['education']),
                'school': '', 'degree': '', 'major': '', 'gpa': '', 'rank': '',
                'courses': '', 'startDate': '', 'endDate': '',
            }
            lines = [l.strip() for l in entry_text.split('\n') if l.strip()]
            if not lines:
                continue
            entry['school'] = lines[0].split('  ')[0].strip()
            for line in lines:
                if any(kw in line for kw in ['硕士', '本科', '博士', '大专', 'Master', 'Bachelor', 'PhD']):
                    entry['degree'] = self._extract_keyword(line, ['硕士', '本科', '博士', '大专', 'Master', 'Bachelor', 'PhD'])
                dates = self.DATE_RE.findall(line)
                if len(dates) >= 2:
                    entry['startDate'] = f"{dates[0][0]}-{int(dates[0][1]):02d}"
                    entry['endDate'] = f"{dates[1][0]}-{int(dates[1][1]):02d}"
            if entry['school']:
                result['education'].append(entry)

    def _parse_work(self, result, text):
        if not text:
            return
        entries = self._split_entries(text)
        for entry_text in entries:
            entry = {
                'id': int(time.time() * 1000) + len(result['workExperience']),
                'company': '', 'department': '', 'position': '',
                'startDate': '', 'endDate': '', 'type': '工作', 'description': [],
            }
            lines = [l.strip() for l in entry_text.split('\n') if l.strip()]
            if not lines:
                continue
            first_line = lines[0]
            dates = self.DATE_RE.findall(first_line)
            company_text = self.DATE_RE.sub('', first_line).strip()
            # 去除常见分隔符
            company_text = re.sub(r'[|｜/\s]+', ' ', company_text).strip()
            if company_text:
                entry['company'] = company_text.split()[0] if company_text else ''
            if len(dates) >= 2:
                entry['startDate'] = f"{dates[0][0]}-{int(dates[0][1]):02d}"
                entry['endDate'] = f"{dates[1][0]}-{int(dates[1][1]):02d}"
            elif len(dates) == 1:
                entry['startDate'] = f"{dates[0][0]}-{int(dates[0][1]):02d}"
                entry['endDate'] = '至今'
            position_found = False
            desc_lines = []
            for line in lines[1:]:
                clean = re.sub(r'^[•·\-—►▸■◆\d.\s]+', '', line).strip()
                if not clean:
                    continue
                # 职位通常在第一行或第二行，短文本且无日期
                if not position_found and len(clean) < 20 and not re.search(r'\d{4}', clean):
                    # 检查是否看起来像职位名
                    if any(kw in clean for kw in ['工程师', '开发', '经理', '主管', '总监', '实习', '助理',
                                                            '专员', '设计师', '分析师', '架构师', '顾问', '员',
                                                            'Engineer', 'Developer', 'Manager', 'Intern', 'Lead']):
                        entry['position'] = clean
                        position_found = True
                        continue
                    else:
                        entry['position'] = clean
                        position_found = True
                        continue
                desc_lines.append(clean)
            entry['description'] = desc_lines
            if entry['company']:
                result['workExperience'].append(entry)

    def _parse_projects(self, result, text):
        if not text:
            return
        entries = self._split_entries(text)
        for entry_text in entries:
            entry = {
                'id': int(time.time() * 1000) + len(result['projects']),
                'name': '', 'role': '', 'techStack': '', 'description': '', 'achievements': '',
            }
            lines = [l.strip() for l in entry_text.split('\n') if l.strip()]
            if not lines:
                continue
            entry['name'] = lines[0].split('  ')[0].strip()
            for line in lines[1:]:
                clean = re.sub(r'^[•·\-—►▸■◆\d.\s]+', '', line).strip()
                if clean:
                    if entry['description']:
                        entry['description'] += ' ' + clean
                    else:
                        entry['description'] = clean
            if entry['name']:
                result['projects'].append(entry)

    def _parse_skills(self, result, text):
        if not text:
            return
        for line in text.split('\n'):
            clean = re.sub(r'^[•·\-—►▸■◆\d.\s]+', '', line.strip())
            if not clean:
                continue
            parts = re.split(r'[,，、；;/]+', clean)
            for part in parts:
                part = part.strip()
                if part and len(part) >= 1:
                    result['skills'].append({'id': len(result['skills']) + 1, 'name': part})

    def _parse_awards(self, result, text):
        if not text:
            return
        entries = self._split_entries(text)
        for entry_text in entries:
            entry = {
                'id': int(time.time() * 1000) + len(result['awards']),
                'name': '', 'organization': '', 'level': '', 'category': '', 'date': '',
            }
            lines = [l.strip() for l in entry_text.split('\n') if l.strip()]
            if not lines:
                continue
            full_line = lines[0]
            dates = self.DATE_RE.findall(full_line)
            if dates:
                entry['date'] = f"{dates[-1][0]}-{int(dates[-1][1]):02d}"
                full_line = self.DATE_RE.sub('', full_line).strip()
            entry['name'] = full_line
            if entry['name']:
                result['awards'].append(entry)

    def _parse_self_evaluation(self, result, text):
        if not text:
            return
        clean = re.sub(r'\s+', ' ', text).strip()
        if clean:
            result['personal']['selfEvaluation'] = clean

    def _split_entries(self, text: str) -> list:
        lines = text.split('\n')
        entries = []
        current_lines = []
        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue
            is_new_entry = False
            if self.DATE_RE.match(stripped):
                is_new_entry = True
            elif self.DATE_RE.search(stripped) and current_lines:
                if len(stripped) < 80 and not stripped.startswith('-') and not stripped.startswith('•'):
                    is_new_entry = True
            elif re.match(r'^[•·►▸■◆]\s*\S', stripped) and not current_lines:
                is_new_entry = True
            elif any(kw in stripped for kw in ['大学', '学院', 'University', '公司', '科技', '有限']) and current_lines:
                is_new_entry = True
            if is_new_entry and current_lines:
                entries.append('\n'.join(current_lines))
                current_lines = []
            current_lines.append(stripped)
        if current_lines:
            entries.append('\n'.join(current_lines))
        if not entries and text.strip():
            entries = [text.strip()]
        return entries

    def _extract_keyword(self, text, keywords):
        for kw in keywords:
            if kw in text:
                return kw
        return ''

    def _empty_result(self) -> dict:
        return {
            'templateId': 'modern',
            'themeColor': '#4361ee',
            'personal': {
                'name': '', 'avatar': '', 'phone': '', 'email': '', 'wechat': '',
                'github': '', 'blog': '', 'jobIntention': '', 'gpa': '', 'rank': '',
                'selfEvaluation': '',
            },
            'education': [],
            'workExperience': [],
            'projects': [],
            'awards': [],
            'skills': [],
        }
