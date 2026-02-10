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
    issues: List[dict]

class AIService:
    def __init__(self):
        # 初始化 OpenAI 客户端
        self.client = AsyncOpenAI(
            api_key=os.getenv("AI_API_KEY"),
            base_url=os.getenv("AI_BASE_URL")
        )
        self.model = os.getenv("AI_MODEL_NAME", "deepseek-chat")

        # 核心提示词：强制返回 JSON 且包含上下文辅助定位
        self.PROMPT = """你是一个专业的公文校对助手。请分析文本中的【错别字、标点错误、语病、敏感词、不规范表达】。

        ### 输出要求：
        1. 按文本在原文中出现的顺序输出问题。
        2. 必须返回合法的 JSON 格式。
        3. JSON 根对象必须包含 `issues` 数组。

        ### Issue 结构：
        - `original`: 原文片段（必须与原文完全一致，不要带标点，除非标点是错误的一部分）。
        - `suggestion`: 修改建议。
        - `type`: 错误类型（如：错别字、语法错误、敏感词）。
        - `reason`: 简短的修改理由。

        ### 示例：
        {
            "issues": [
                {"original": "记要", "suggestion": "纪要", "type": "错别字", "reason": "固定搭配错误"},
                {"original": "不但...而且", "suggestion": "不仅...而且", "type": "关联词", "reason": "搭配不当"}
            ]
        }
        """

        # 构建 LangGraph 工作流
        self.graph = self._build_workflow()

    async def analyze_stream(self, text_content: str) -> AsyncGenerator[dict, None]:
        """
        生成器：流式返回处理状态和结果
        """
        logger.info("启动流式校阅...")

        # 1. 发送开始信号
        yield {"step": "start", "desc": "正在连接 AI 服务..."}

        # 2. 预处理：提取纯文本 (简单去除 HTML 标签，保留换行)
        clean_text = self._strip_html(text_content)
        if not clean_text.strip():
            yield {"step": "error", "desc": "文档内容为空"}
            return

        yield {"step": "thinking", "desc": "AI 正在深度分析文本..."}

        # 3. 初始化状态
        initial_state = {"clean_text": clean_text, "issues": []}

        # 4. 执行工作流并流式输出
        try:
            async for event in self.graph.astream(initial_state):
                for node, output in event.items():
                    if node == "scanner":
                        issues = output.get("issues", [])
                        if issues:
                            # 分批发送问题，前端收到后立即渲染
                            yield {
                                "step": "scanning",
                                "desc": f"发现 {len(issues)} 处建议...",
                                "data": issues
                            }
                        else:
                            yield {"step": "scanning", "desc": "未发现明显问题"}
        except Exception as e:
            logger.error(f"AI Service Error: {e}")
            yield {"step": "error", "desc": f"分析中断: {str(e)}"}

        # 5. 完成信号
        yield {"step": "complete", "desc": "校阅完成"}

    # --- LangGraph 节点 ---

    async def scanner_node(self, state: AgentState):
        text = state["clean_text"]
        try:
            # 调用大模型
            response_data = await self._call_llm(text)
            return {"issues": response_data.get("issues", [])}
        except Exception as e:
            logger.error(f"LLM Call Failed: {e}")
            return {"issues": []}

    # --- 辅助方法 ---

    async def _call_llm(self, text: str) -> dict:
        """封装 AI 调用逻辑，处理 JSON 解析"""
        try:
            resp = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.PROMPT},
                    {"role": "user", "content": text}
                ],
                response_format={"type": "json_object"},
                temperature=0.1, # 低温度保证准确性
                stream=False     # 这里不用 stream，因为我们需要完整的 JSON 结构
            )
            content = resp.choices[0].message.content
            return json.loads(content)
        except json.JSONDecodeError:
            logger.error("AI 返回了非法的 JSON")
            return {"issues": []}
        except Exception as e:
            raise e

    def _strip_html(self, html: str) -> str:
        """移除 HTML 标签，保留文本内容"""
        # 简单的正则去除，生产环境建议使用 BeautifulSoup
        text = re.sub(r'<[^>]+>', '', html)
        # 去除多余的空行，但保留段落感
        return re.sub(r'\n\s*\n', '\n', text).strip()

    def _build_workflow(self):
        """构建简单的图结构"""
        wf = StateGraph(AgentState)
        wf.add_node("scanner", self.scanner_node)
        wf.set_entry_point("scanner")
        wf.add_edge("scanner", END)
        return wf.compile()

# 单例模式
ai_service = AIService()