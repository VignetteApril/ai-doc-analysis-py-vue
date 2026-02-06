import httpx
import json
import os
from typing import List, Dict

class AIService:
    def __init__(self):
        self.api_key = os.getenv("ARK_API_KEY")
        self.endpoint = os.getenv("ARK_ENDPOINT")
        self.model = os.getenv("ARK_MODEL")

        # [DEBUG] 初始化检查
        print("\n" + "="*50)
        print("[DEBUG] AIService 初始化中...")
        print(f"[DEBUG] Endpoint: {self.endpoint}")
        print(f"[DEBUG] Model: {self.model}")
        print(f"[DEBUG] API Key (前4位): {self.api_key[:4] if self.api_key else 'None'}")
        print("="*50 + "\n")

    async def analyze_document(self, content: str) -> List[Dict]:
        """调用豆包模型进行公文校审 [cite: 2026-02-05]"""

        # [DEBUG] 输入内容检查
        print(f"[DEBUG] 接收到待分析文本，长度: {len(content)} 字符")
        if len(content) < 5:
            print("[DEBUG] 文本过短，跳过分析")
            return []

        system_prompt = """
        你是一名专业的公文校对专家。请分析用户提供的公文文本，识别错误。
        请严格按以下 JSON 数组格式输出，不要包含任何多余的解释：
        [
          {"type": "错误类型", "original": "原文内容", "content": "建议修改后的内容", "source": "AI分析"}
        ]
        """

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"请对以下公文内容进行校对：\n\n{content}"}
            ],
            # 💡 注意：有些模型在 response_format 为 json_object 时要求 Prompt 里必须包含 "json" 关键字
            "response_format": {"type": "json_object"}
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                print(f"[DEBUG] 正在向 {self.endpoint} 发送请求...")
                response = await client.post(self.endpoint, headers=headers, json=payload)

                # [DEBUG] HTTP 状态码
                print(f"[DEBUG] HTTP 状态码: {response.status_code}")

                if response.status_code != 200:
                    print(f"[DEBUG] 响应错误内容: {response.text}")

                response.raise_for_status()
                result = response.json()

                # [DEBUG] 获取模型返回的原始字符串
                ai_message = result['choices'][0]['message']['content']
                print(f"[DEBUG] AI 返回的原始字符串: {ai_message}")

                # [DEBUG] 尝试解析 JSON
                parsed_data = json.loads(ai_message)

                # 兼容处理：有些模型会返回 {"suggestions": [...]} 而不是直接返回数组
                if isinstance(parsed_data, dict):
                    # 尝试从字典中提取数组，常见的 key 有 'choices', 'suggestions', 'data'
                    for key in ['items', 'suggestions', 'data']:
                        if key in parsed_data:
                            print(f"[DEBUG] 从字典 Key '{key}' 中提取数组")
                            return parsed_data[key]
                    # 如果就是一个对象且没有明显数组，封装进列表
                    if not isinstance(parsed_data, list):
                         print(f"[DEBUG] 返回内容为单对象 JSON，已转换为列表")
                         return [parsed_data]

                print(f"[DEBUG] 成功解析 {len(parsed_data)} 条建议")
                return parsed_data

            except json.JSONDecodeError as je:
                print(f"[DEBUG] JSON 解析失败! 原始文本不是合法的 JSON 格式。")
                print(f"[DEBUG] 错误位置: {str(je)}")
                return []
            except KeyError as ke:
                print(f"[DEBUG] 响应结构异常! 找不到 Key: {str(ke)}")
                print(f"[DEBUG] 完整响应: {result}")
                return []
            except Exception as e:
                print(f"[DEBUG] AI 调用过程中发生异常: {type(e).__name__} - {str(e)}")
                return []