import os
import json
import re
import uuid
import logging
from typing import TypedDict, List, Dict, Optional, Tuple
from openai import AsyncOpenAI
from langgraph.graph import StateGraph, END

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger("泰山Agent")


class AgentState(TypedDict):
    html_content: str
    clean_text: str
    raw_issues: list
    final_issues: list
    final_html: str


class AIService:
    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=os.getenv("AI_API_KEY"),
            base_url=os.getenv("AI_BASE_URL")
        )
        self.model = os.getenv("AI_MODEL_NAME", "pro/deepseek-ai/DeepSeek-V3")

        self.SKELETON_CHAR_PATTERN = re.compile(r"[\u4e00-\u9fa5a-zA-Z0-9]")
        self.NON_SKELETON_PATTERN = re.compile(r"[^\u4e00-\u9fa5a-zA-Z0-9]")

        self.graph = self._build_workflow()
        logger.info(f"🚀 AI Service Ready | Model: {self.model}")

    # ====================== 节点逻辑 ======================

    async def preprocess_node(self, state: AgentState):
        logger.info("🟢 [1. 预处理] 提取纯文本...")
        text = re.sub(r'<[^>]+>', '', state.get("html_content", ""))
        return {"clean_text": text}

    async def scanner_node(self, state: AgentState):
        logger.info("🟡 [2. 初审] 扫描错误...")

        prompt = """你是一名资深公文校对员。请阅读原文，找出【错别字、标点错误、语病、敏感词、不规范表达】。

        ### 输出要求：
        返回严格的 JSON 对象（不要使用 Markdown 代码块），包含 `issues` 数组。

        ### 数组元素字段：
        1. `original`: 原文中错误的片段（必须与原文完全一致）
        2. `content`: 修改后的建议内容（如果是删除建议，请返回空字符串 ""）
        3. `type`: 错误类型（错别字、标点错误、语病等）
        4. `reason`: 修改理由（简洁清晰）

        ### 输出示例：
        {
            "issues": [
                {"original": "记要", "content": "纪要", "type": "错别字", "reason": "用词错误"},
                {"original": "，，", "content": "，", "type": "标点错误", "reason": "重复标点"}
            ]
        }
        """

        try:
            data = await self._call_ai("Scanner", prompt, state["clean_text"])
            issues = data.get("issues", []) if isinstance(data, dict) else data
            if not isinstance(issues, list):
                issues = []
            logger.info(f"✅ Scanner 发现 {len(issues)} 个问题")
            return {"raw_issues": issues}
        except Exception as e:
            logger.error(f"❌ Scanner 异常: {e}")
            return {"raw_issues": []}

    async def reviewer_node(self, state: AgentState):
        logger.info(f"🟠 [3. 复审] 处理建议 (共 {len(state['raw_issues'])} 条)...")
        if not state["raw_issues"]:
            return {"final_issues": []}

        approved = []
        for issue in state["raw_issues"]:
            issue_id = f"ai-{uuid.uuid4().hex[:10]}"
            approved.append({
                "id": issue_id,
                "original": issue.get("original", ""),
                "content": issue.get("content") or issue.get("suggestion", ""),
                "type": issue.get("type", "其他"),
                "message": issue.get("reason", issue.get("message", "")),   # 前端需要 message
                "reason": issue.get("reason", "")   # 保留兼容
            })
        return {"final_issues": approved}

    def finalizer_node(self, state: AgentState):
        logger.info("🔵 [4. 终审] 注入 AI 校阅标记...")

        current_html = state["html_content"]
        valid_issues = []

        for issue in state["final_issues"]:
            orig = issue.get("original", "").strip()
            if not orig:
                continue

            loc = self._get_python_indices(current_html, orig)
            if loc:
                start, end = loc
                issue_id = issue["id"]

                tag_start = (
                    f'<span class="ai-correction-mark" '
                    f'data-ai-id="{issue_id}" '
                    f'title="AI 建议：{issue.get("message", "")}">'
                )
                tag_end = '</span>'

                before = current_html[:start]
                target = current_html[start:end]
                after = current_html[end:]

                current_html = before + tag_start + target + tag_end + after

                valid_issues.append(issue)
                logger.debug(f"📍 注入成功: {orig} → data-ai-id={issue_id}")
            else:
                logger.warning(f"❌ 无法定位原文: '{orig}'")

        logger.info(f"🏁 注入完成，生效 {len(valid_issues)} 条标记")
        return {
            "final_issues": valid_issues,
            "final_html": current_html
        }

    # ====================== 定位算法 ======================

    def _get_python_indices(self, full_text: str, target: str) -> Optional[Tuple[int, int]]:
        """增强版定位：优先精确匹配 → 骨架匹配"""
        if not target or not full_text:
            return None

        idx = full_text.find(target)
        if idx != -1:
            return idx, idx + len(target)

        target_sk = self.NON_SKELETON_PATTERN.sub("", target)
        if len(target_sk) < 2:
            return None

        doc_sk = []
        doc_map = []

        is_in_tag = False
        for i, char in enumerate(full_text):
            if char == '<':
                is_in_tag = True
            elif char == '>':
                is_in_tag = False
            elif not is_in_tag and self.SKELETON_CHAR_PATTERN.match(char):
                doc_sk.append(char)
                doc_map.append(i)

        sk_str = "".join(doc_sk)
        sk_idx = sk_str.find(target_sk)

        if sk_idx != -1:
            real_start = doc_map[sk_idx]
            real_end = doc_map[sk_idx + len(target_sk) - 1] + 1
            return real_start, real_end

        return None

    # ====================== 辅助方法 ======================

    async def _call_ai(self, tag, sys_prompt, user_content):
        try:
            resp = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": sys_prompt},
                    {"role": "user", "content": user_content}
                ],
                response_format={"type": "json_object"},
                temperature=0.1,
                timeout=150
            )
            raw = resp.choices[0].message.content.strip()
            if "```" in raw:
                raw = re.sub(r"^```(?:json)?\s*", "", raw)
                raw = re.sub(r"\s*```$", "", raw)
            return json.loads(raw)
        except Exception as e:
            logger.error(f"[{tag}] AI 调用失败: {e}")
            raise

    def _build_workflow(self):
        wf = StateGraph(AgentState)
        wf.add_node("preprocess", self.preprocess_node)
        wf.add_node("scan", self.scanner_node)
        wf.add_node("review", self.reviewer_node)
        wf.add_node("finalize", self.finalizer_node)

        wf.set_entry_point("preprocess")
        wf.add_edge("preprocess", "scan")
        wf.add_edge("scan", "review")
        wf.add_edge("review", "finalize")
        wf.add_edge("finalize", END)
        return wf.compile()

    async def analyze_stream(self, html_content: str):
        # 关键修改：标准 SSE 格式，每条消息以 data: {json}\n\n 结束
        yield f"data: {json.dumps({'step': 'start', 'desc': 'AI 校审启动...'})}\n\n"

        initial_state = {
            "html_content": html_content,
            "clean_text": "",
            "raw_issues": [],
            "final_issues": [],
            "final_html": ""
        }

        final_result = {}
        async for event in self.graph.astream(initial_state):
            for node_name, output in event.items():
                if node_name == "finalize":
                    final_result = output
                desc_map = {
                    "preprocess": "提取纯文本",
                    "scan": "深度扫描问题",
                    "review": "复核建议",
                    "finalize": "注入校阅标记"
                }
                yield f"data: {json.dumps({'step': node_name, 'desc': desc_map.get(node_name, node_name)})}\n\n"

        payload = {
            "step": "complete",
            "results": {
                "final_issues": final_result.get("final_issues", []),
                "final_html": final_result.get("final_html", "")
            }
        }
        logger.info(f"📤 校审完成 | 发现 {len(payload['results']['final_issues'])} 个问题")
        yield f"data: {json.dumps(payload)}\n\n"


# 单例
ai_service = AIService()