import json
import logging
import os
import re
from typing import AsyncGenerator, List, TypedDict

from langgraph.graph import END, StateGraph
from openai import AsyncOpenAI

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger("AIService")


class AgentState(TypedDict):
    clean_text: str
    draft_issues: List[dict]
    final_issues: List[dict]


class AIService:
    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=os.getenv("AI_API_KEY"),
            base_url=os.getenv("AI_BASE_URL"),
        )
        self.model = os.getenv("AI_MODEL_NAME", "deepseek-chat")

        # 初审：高召回，新增“无关词语/噪声数字”的删除规则。
        self.SCANNER_PROMPT = """
你是一名资深公文校对员。请逐段审查文本，并只输出“必须修改”的问题。

请重点识别以下 5 类问题：
1. 语义错误：逻辑冲突、语义不通、搭配不当。
2. 标点错误：标点缺失、误用、冗余。
3. 文字错误：错别字、漏字、多字。
4. 冗余无关词语：与所在句或段落主旨明显无关、插入性噪声词、无实际信息增益的残片。
5. 无意义数字：孤立数字串或噪声编号（如测试残留、随机数字），与上下文业务语义无关。

删除规则（非常重要）：
- 对第 4/5 类问题，suggestion 必须返回空字符串 ""，表示删除。
- original 必须是“最小可删除片段”，不要把整句都当作 original。
- 若数字有明确语义（日期、时间、金额、百分比、版本号、法规条款号、序号等），禁止误删。

输出要求：
- 仅返回 JSON 对象：{"issues": [...]}。
- 每个 issue 必须包含：original, suggestion, type, reason。
- 没有问题时返回：{"issues": []}。
""".strip()

        # 复核：高精度，显式允许并保留“删除建议”。
        self.VERIFIER_PROMPT = """
你是一名主审编辑，负责复核初审建议，只保留“必要且正确”的修改。

复核标准：
1. 准确性：original 必须与原文可精确匹配，且确有问题。
2. 上下文一致性：修改后句子/段落更通顺，不破坏原意。
3. 删除建议审查：
   - 对“冗余无关词语/无意义数字”可保留删除建议（suggestion = ""）。
   - 仅当该片段与上下文主旨明显无关时才保留。
   - 若数字承载时间/金额/比例/编号等关键信息，必须驳回删除。
4. 抑制过度修改：可改可不改的一律驳回。

输出要求：
- 仅返回 JSON 对象：{"approved_issues": [...]}。
- 字段结构保持为 original, suggestion, type, reason。
""".strip()

        self.VOCAB_IMPORT_PROMPT = """
你是“术语替换词库抽取助手”。任务是从文档中提炼高质量的“原词 -> 替换词”映射。

抽取原则（必须遵守）：
1) 只保留“明确表达替换关系”的内容，常见模式包括：
   - “将A改为B / A应为B / A统一为B / A替换为B / A（应改为B）”
   - 术语对照表、规范用语表、同义修正规则。
2) 仅当 A 和 B 都是具体词语/短语时才保留；排除解释性长句、无替换意图的定义句。
3) original_word 必须是被替换项，replacement_word 必须是替换后标准项，方向不能反。
4) 不要拆坏固定搭配；优先抽取“最小且完整”的术语片段。
5) 去重并清洗：
   - 去除前后空格、引号、项目符号、序号。
   - 删除 original_word == replacement_word 的项。
   - 同一 original_word 仅保留最可信的一条 replacement_word。
6) 忽略噪声：乱码、纯数字编号、日期/页码、无语义符号串。
7) 原子化要求（非常重要）：
   - 若 A/B 仅在短语局部不同，必须只输出最小可替换短语，不要输出整句或整个长定语。
   - 例如：
     输入语义：“关于XXX的处理建议 -> 关于XXX的处理问题”
     输出必须是：{"original_word":"处理建议","replacement_word":"处理问题"}
     不能输出整段“关于XXX的...”
8) 长度与歧义控制：
   - 尽量避免输出单字词对（如“的->地”这类孤立字）或过短、泛化词对。
   - 优先输出在语境中更不易误替换的短语（通常 >=3 个字）。
   - 仅在缩写/专有名词确有明确替换关系时，才允许较短词对。

输出要求：
- 仅输出 JSON 对象，不要 markdown，不要解释文字。
- 格式严格为：
  {"items":[{"original_word":"...","replacement_word":"..."}]}
- 无法提取时返回：
  {"items":[]}
""".strip()

        self.graph = self._build_workflow()

    async def analyze_stream(
        self,
        text_content: str,
        vocabularies: List[dict] = None,
    ) -> AsyncGenerator[dict, None]:
        logger.info("启动智能校阅工作流")
        yield {"step": "start", "desc": "正在启动 AI 校阅服务..."}

        clean_text = self._strip_html(text_content)
        if not clean_text.strip():
            yield {"step": "error", "desc": "文档内容为空"}
            return

        vocab_issues = self._build_vocab_issues(clean_text, vocabularies or [])

        initial_state: AgentState = {
            "clean_text": clean_text,
            "draft_issues": [],
            "final_issues": [],
        }

        try:
            async for event in self.graph.astream(initial_state):
                for node, output in event.items():
                    if node == "scanner":
                        count = len(output.get("draft_issues", []))
                        yield {
                            "step": "scanning",
                            "desc": f"初审完成，发现 {count} 处疑似问题，正在复核...",
                        }

                    elif node == "verifier":
                        ai_final = output.get("final_issues", [])
                        merged = self._dedup_issues(vocab_issues + ai_final)
                        yield {
                            "step": "verifying",
                            "desc": f"复核通过 {len(ai_final)} 处建议，词库命中 {len(vocab_issues)} 处，正在整理结果...",
                            "data": merged,
                        }

        except Exception as exc:
            logger.error("Workflow Error: %s", exc, exc_info=True)
            if vocab_issues:
                yield {
                    "step": "verifying",
                    "desc": f"AI 分析异常，词库命中 {len(vocab_issues)} 处",
                    "data": vocab_issues,
                }
            else:
                yield {"step": "error", "desc": f"分析服务异常: {str(exc)}"}

        yield {"step": "complete", "desc": "校阅完成"}

    async def scanner_node(self, state: AgentState):
        text = state["clean_text"]
        try:
            response = await self._call_llm(self.SCANNER_PROMPT, text, temperature=0.2)
            issues = self._normalize_issues(response.get("issues", []), text)
            return {"draft_issues": issues}
        except Exception:
            return {"draft_issues": []}

    async def verifier_node(self, state: AgentState):
        draft_issues = state.get("draft_issues", [])
        text = state["clean_text"]

        if not draft_issues:
            return {"final_issues": []}

        verify_input = json.dumps(
            {
                "original_text": text,
                "proposed_issues": draft_issues,
            },
            ensure_ascii=False,
        )

        try:
            response = await self._call_llm(self.VERIFIER_PROMPT, verify_input, temperature=0.1)
            final = response.get("approved_issues", response.get("issues", []))
            return {"final_issues": self._normalize_issues(final, text)}
        except Exception:
            logger.warning("复核节点异常，降级使用初审结果")
            return {"final_issues": self._normalize_issues(draft_issues, text)}

    async def _call_llm(self, sys_prompt: str, user_content: str, temperature: float = 0.1) -> dict:
        try:
            resp = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": sys_prompt},
                    {"role": "user", "content": user_content},
                ],
                response_format={"type": "json_object"},
                temperature=temperature,
                stream=False,
            )
            return json.loads(resp.choices[0].message.content)
        except Exception as exc:
            logger.error("LLM Call Error: %s", exc)
            raise

    async def extract_vocabulary_pairs(self, text_content: str) -> List[dict]:
        """从文档文本中抽取词库原词/替换词对。"""
        content = (text_content or "").strip()
        if not content:
            return []

        # 防止超长文本导致请求不稳定
        if len(content) > 20000:
            content = content[:20000]

        try:
            response = await self._call_llm(self.VOCAB_IMPORT_PROMPT, content, temperature=0.1)
        except Exception:
            return []

        raw_items = response.get("items", response.get("pairs", response.get("vocabularies", [])))
        if not isinstance(raw_items, list):
            return []

        normalized = []
        seen = set()
        for item in raw_items:
            if not isinstance(item, dict):
                continue
            original = str(item.get("original_word", "")).strip()
            replacement = str(item.get("replacement_word", "")).strip()
            if not original or not replacement:
                continue
            if original == replacement:
                continue
            key = (original, replacement)
            if key in seen:
                continue
            seen.add(key)
            normalized.append(
                {
                    "original_word": original,
                    "replacement_word": replacement,
                }
            )
        return normalized

    def _build_vocab_issues(self, clean_text: str, vocabularies: List[dict]) -> List[dict]:
        vocab_issues: List[dict] = []
        for entry in vocabularies:
            orig = str(entry.get("original_word", "")).strip()
            repl = str(entry.get("replacement_word", "")).strip()
            if orig and orig in clean_text:
                vocab_issues.append(
                    {
                        "original": orig,
                        "suggestion": repl,
                        "type": "词库",
                        "reason": f"词库命中：建议将“{orig}”替换为“{repl}”",
                        "source": "词库",
                    }
                )

        if vocab_issues:
            logger.info("词库匹配命中 %s 处", len(vocab_issues))

        return self._dedup_issues(vocab_issues)

    def _normalize_issues(self, issues: List[dict], clean_text: str) -> List[dict]:
        normalized: List[dict] = []
        for item in issues or []:
            if not isinstance(item, dict):
                continue

            original = str(item.get("original", "")).strip()
            suggestion = str(item.get("suggestion", ""))
            issue_type = str(item.get("type", "")).strip() or "其他"
            reason = str(item.get("reason", "")).strip() or "需要修正"

            if not original:
                continue
            if original not in clean_text:
                continue

            # 统一删除类建议输出：suggestion 为空字符串。
            delete_hint = any(key in issue_type + reason for key in ["冗余", "无关", "噪声", "删除"]) or self._is_noise_number(original)
            if delete_hint:
                suggestion = ""

            normalized.append(
                {
                    "original": original,
                    "suggestion": suggestion.strip(),
                    "type": issue_type,
                    "reason": reason,
                }
            )

        return self._dedup_issues(normalized)

    def _dedup_issues(self, issues: List[dict]) -> List[dict]:
        deduped: List[dict] = []
        seen = set()
        for issue in issues:
            key = (
                issue.get("original", ""),
                issue.get("suggestion", ""),
                issue.get("type", ""),
            )
            if key in seen:
                continue
            seen.add(key)
            deduped.append(issue)
        return deduped

    def _is_noise_number(self, text: str) -> bool:
        token = text.strip()
        if not re.fullmatch(r"[0-9０-９]+", token):
            return False

        # 常见有意义数字（年份、日期、金额等）避免误删
        if re.fullmatch(r"(19|20)\d{2}", token):
            return False
        if len(token) <= 2:
            return False

        # 纯数字且长度中等，通常是残留编号/噪声，倾向删除
        return 3 <= len(token) <= 12

    def _strip_html(self, html: str) -> str:
        text = re.sub(r"<[^>]+>", "", html)
        return re.sub(r"\n\s*\n", "\n", text).strip()

    def _build_workflow(self):
        wf = StateGraph(AgentState)
        wf.add_node("scanner", self.scanner_node)
        wf.add_node("verifier", self.verifier_node)

        wf.set_entry_point("scanner")
        wf.add_edge("scanner", "verifier")
        wf.add_edge("verifier", END)

        return wf.compile()


ai_service = AIService()
