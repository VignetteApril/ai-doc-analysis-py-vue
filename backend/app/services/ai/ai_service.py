import os
import json
import logging
import re
from typing import TypedDict, List, AsyncGenerator
from openai import AsyncOpenAI
from langgraph.graph import StateGraph, END

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger("AIService")

# 定义状态字典
class AgentState(TypedDict):
    clean_text: str
    draft_issues: List[dict] # 初审发现的问题
    final_issues: List[dict] # 复审通过的问题

class AIService:
    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=os.getenv("AI_API_KEY"),
            base_url=os.getenv("AI_BASE_URL")
        )
        self.model = os.getenv("AI_MODEL_NAME", "deepseek-chat")

        # =================PROMPT 提示词工程=================

        # 1. 初审提示词：高灵敏度，负责找出所有可能的错误
        self.SCANNER_PROMPT = """你是一名资深公文校对员。请仔细阅读文本，找出以下三类特定错误：
1. 【语义错误】：明显的逻辑矛盾、用词不当导致歧义。
2. 【标点错误】：标点符号使用不规范、缺失或多余。
3. 【文字错误】：多字、漏字、明显的错别字。

要求：
- 仅关注客观错误，不要修改作者的写作风格。
- 返回 JSON 格式，包含 `issues` 数组。
- 每个 issue 包含：original(原文), suggestion(建议), type(类型), reason(理由)。
- 如果没有错误，issues 数组为空。
"""

        # 2. 复审提示词：自我审查，保证通顺，拒绝过度修改
        self.VERIFIER_PROMPT = """你是一名主要责编。你的任务是审核“初审员”提出的修改建议。
请逐条评估建议，并执行以下过滤标准：

1. 【准确性检查】：原文真的错了吗？如果原文可改可不改，则**拒绝**修改（防止反复修改）。
2. 【通顺性检查】：修改后的句子是否通顺？如果修改后导致语序别扭，则**拒绝**。
3. 【完整性检查】：`original` 字段必须能与原文完全匹配。

输出要求：
- 返回 JSON 格式，包含 `approved_issues` 数组。
- 只保留你认为【必须修改】且【修改后更通顺】的建议。
- 字段结构保持不变。
"""

        self.graph = self._build_workflow()

    async def analyze_stream(self, text_content: str) -> AsyncGenerator[dict, None]:
        """生成器：流式返回处理状态和结果"""
        logger.info("启动智能校阅工作流...")

        yield {"step": "start", "desc": "正在初始化 AI 引擎..."}

        # 预处理
        clean_text = self._strip_html(text_content)
        if not clean_text.strip():
            yield {"step": "error", "desc": "文档内容为空"}
            return

        initial_state = {"clean_text": clean_text, "draft_issues": [], "final_issues": []}

        try:
            # 执行图流
            async for event in self.graph.astream(initial_state):
                for node, output in event.items():
                    if node == "scanner":
                        count = len(output.get("draft_issues", []))
                        yield {"step": "scanning", "desc": f"初审完成，发现 {count} 处疑似问题，正在进行复核..."}

                    elif node == "verifier":
                        final = output.get("final_issues", [])
                        yield {
                            "step": "verifying",
                            "desc": f"复核通过 {len(final)} 处建议，准备渲染...",
                            "data": final # 只有通过复核的数据才发给前端
                        }

        except Exception as e:
            logger.error(f"Workflow Error: {e}", exc_info=True)
            yield {"step": "error", "desc": f"分析服务异常: {str(e)}"}

        yield {"step": "complete", "desc": "校阅完成"}

    # ================= 核心节点逻辑 =================

    async def scanner_node(self, state: AgentState):
        """节点 1：初审（高召回）"""
        text = state["clean_text"]
        try:
            # 这里温度设稍微高一点点(0.2)，让它敢于找错
            response = await self._call_llm(self.SCANNER_PROMPT, text, temperature=0.2)
            return {"draft_issues": response.get("issues", [])}
        except Exception:
            return {"draft_issues": []}

    async def verifier_node(self, state: AgentState):
        """节点 2：复审（高精度，防幻觉）"""
        draft_issues = state.get("draft_issues", [])
        text = state["clean_text"]

        if not draft_issues:
            return {"final_issues": []}

        # 构造复审的输入：原文 + 初审建议
        verify_input = json.dumps({
            "original_text_snippet": text[:2000], # 截取部分原文作为上下文(避免token过长)
            "proposed_issues": draft_issues
        }, ensure_ascii=False)

        try:
            # 复审温度要低(0.1)，保持理性
            response = await self._call_llm(self.VERIFIER_PROMPT, verify_input, temperature=0.1)
            # 兼容模型可能返回 'issues' 或 'approved_issues'
            final = response.get("approved_issues", response.get("issues", []))
            return {"final_issues": final}
        except Exception:
            # 如果复审挂了，为了保底，返回初审结果（或者返回空，看策略）
            logger.warning("复审节点异常，降级使用初审结果")
            return {"final_issues": draft_issues}

    # ================= 辅助方法 =================

    async def _call_llm(self, sys_prompt, user_content, temperature=0.1) -> dict:
        try:
            resp = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": sys_prompt},
                    {"role": "user", "content": user_content}
                ],
                response_format={"type": "json_object"},
                temperature=temperature,
                stream=False
            )
            return json.loads(resp.choices[0].message.content)
        except Exception as e:
            logger.error(f"LLM Call Error: {e}")
            raise e

    def _strip_html(self, html: str) -> str:
        text = re.sub(r'<[^>]+>', '', html)
        return re.sub(r'\n\s*\n', '\n', text).strip()

    def _build_workflow(self):
        wf = StateGraph(AgentState)
        wf.add_node("scanner", self.scanner_node)
        wf.add_node("verifier", self.verifier_node)

        # 流程：Start -> Scanner -> Verifier -> End
        wf.set_entry_point("scanner")
        wf.add_edge("scanner", "verifier")
        wf.add_edge("verifier", END)

        return wf.compile()

ai_service = AIService()