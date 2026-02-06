from html2docx import html2docx
import io

class DocumentExporter:
    @staticmethod
    def html_to_docx(html_content: str, output_path: str) -> bool:
        """
        核心逻辑：将 HTML 字符串转换为物理 .docx 文件
        """
        try:
            # html2docx 接收 HTML 字符串并返回 BytesIO 流
            buf = html2docx(html_content)
            with open(output_path, 'wb') as f:
                f.write(buf.getvalue())
            return True
        except Exception as e:
            print(f"导出错误: {str(e)}")
            return False