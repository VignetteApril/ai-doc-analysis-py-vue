import os, json, re, uuid, logging, asyncio, time
from typing import List, Dict, Tuple, Optional, Annotated, TypedDict
from openai import AsyncOpenAI
from langgraph.graph import StateGraph, END

# --- 日志配置 ---
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
    iteration: int

class AIService:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=os.getenv("AI_API_KEY"), base_url=os.getenv("AI_BASE_URL"))
        self.model = os.getenv("AI_MODEL_NAME", "pro/deepseek-ai/DeepSeek-V3")
        self.SKELETON_CHAR_PATTERN = re.compile(r"[\u4e00-\u9fa5a-zA-Z0-9]")
        self.NON_SKELETON_PATTERN = re.compile(r"[^\u4e00-\u9fa5a-zA-Z0-9]")
        self.graph = self._build_workflow()

    # --- 1. 节点逻辑 ---

    async def preprocess_node(self, state: AgentState):
        logger.info("🟢 [1. 预处理] 提取纯文本...")
        html = state["html_content"]
        # 简单剥离标签，保留文本用于分析
        clean_text = re.sub(r'<[^>]+>', '', html)
        return {"clean_text": clean_text}

    async def scanner_node(self, state: AgentState):
        logger.info("🟡 [2. 初审] 正在寻找错误并锁定上下文...")
        # 🚀 关键 Prompt：要求包含上下文，确保 find() 唯一
        prompt = """你是一名资深公文校对员。
        ### 核心规则：
        1. 'original' 必须包含错误字符及其【左右各1-2个字符】的上下文。
           - 错误示例：original: "”" (无法定位)
           - 正确示例：original: "识别””" (包含左侧上下文)
        2. 如果是删除操作，'content' 设为 ""。
        3. 仅关注错别字、标点错误、语病。
        输出 JSON: {"issues": [{"type": "...", "original": "...", "content": "...", "reason": "..."}]}"""

        issues = await self._call_ai("Scanner", prompt, f"待审内容：\n{state['clean_text']}")
        return {"raw_issues": issues}

    async def reviewer_node(self, state: AgentState):
        logger.info("🟠 [3. 复审] 过滤幻觉与误判...")
        if not state["raw_issues"]: return {"final_issues": []}

        prompt = f"""你是一名高级主编。请审核以下建议：{json.dumps(state['raw_issues'], ensure_ascii=False)}
        任务：
        1. 剔除导致语句不通顺的修改。
        2. 剔除对专业术语的错误修改。
        3. 确保标点符号修改后是成对/规范的。
        输出 JSON 数组：{{"issues": [...]}}"""

        verified = await self._call_ai("Reviewer", prompt, f"全文背景：\n{state['clean_text']}")
        return {"final_issues": verified}

    def finalizer_node(self, state: AgentState):
        logger.info("🔵 [4. 终审] 生成唯一 ID 与坐标...")
        results = []
        html_len = len(state["html_content"])

        for it in state["final_issues"]:
            orig = it.get("original", "")
            # 计算在 HTML 源码中的 start/end 索引
            start_js, end_js = self._smart_reanchor(state["html_content"], orig)

            # 🟢 核心：生成唯一 ID
            # 这个 ID 将被注入到 HTML 标签中，作为 DOM 操作的锚点
            issue_id = f"issue-{uuid.uuid4().hex[:8]}"

            if start_js is not None and start_js != -1:
                results.append({
                    "id": issue_id,
                    "start": start_js,
                    "end": end_js,
                    "original": orig,
                    "content": it.get("content", ""),
                    "type": it.get("type", "建议"),
                    "message": it.get("reason", "建议修改")
                })
            else:
                logger.warning(f"❌ 无法回钉: {orig}")

        logger.info(f"🏁 任务完成，生成 {len(results)} 个锚点")
        return {"final_issues": results}

    # --- 2. 核心辅助方法 ---

    def _smart_reanchor(self, full_text, target):
        """
        利用上下文进行精准定位。
        因为 target 包含了上下文（如 '识别””'），所以在全文中通常是唯一的。
        """
        if not target: return None, None

        # 1. 优先尝试精确查找
        idx = full_text.find(target)
        if idx != -1:
            return self._py_to_js(full_text, idx), self._py_to_js(full_text, idx + len(target))

        # 2. 骨架匹配兜底 (处理 HTML 标签切断的情况)
        target_sk = self.NON_SKELETON_PATTERN.sub("", target)
        if len(target_sk) < 2: return None, None

        doc_sk, doc_map = [], []
        for m in self.SKELETON_CHAR_PATTERN.finditer(full_text):
            doc_sk.append(m.group()); doc_map.append(m.start())

        sk_str = "".join(doc_sk)
        sk_idx = sk_str.find(target_sk)
        if sk_idx != -1:
            real_start = doc_map[sk_idx]
            # 计算结束位置
            real_end = doc_map[sk_idx + len(target_sk) - 1] + 1
            # 向后扩展直到找到非骨架字符的边界（简单处理）
            return self._py_to_js(full_text, real_start), self._py_to_js(full_text, real_end)

        return None, None

    async def _call_ai(self, tag, sys_prompt, user_content):
        try:
            resp = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "system", "content": sys_prompt}, {"role": "user", "content": user_content}],
                response_format={"type": "json_object"},
                temperature=0.1, timeout=300.0
            )
            data = json.loads(resp.choices[0].message.content)
            for key in ['issues', 'suggestions', 'data']:
                if key in data: return data[key]
            return [data] if isinstance(data, dict) else []
        except Exception as e:
            logger.error(f"AI Error ({tag}): {e}")
            return []

    def _build_workflow(self):
        wf = StateGraph(AgentState)
        wf.add_node("preprocess", self.preprocess_node)
        wf.add_node("scan", self.scanner_node)
        wf.add_node("review", self.reviewer_node)
        wf.add_node("finalize", self.finalizer_node)
        wf.set_entry_point("preprocess")
        wf.add_edge("preprocess", "scan"); wf.add_edge("scan", "review"); wf.add_edge("review", "finalize"); wf.add_edge("finalize", END)
        return wf.compile()

    async def analyze_document(self, content):
        final_state = await self.graph.ainvoke({"html_content": content, "raw_issues": [], "final_issues": []})
        return final_state["final_issues"]

    def _py_to_js(self, text, py_idx):
        return len(text[:py_idx].encode('utf-16-le')) // 2

ai_service = AIService()