import base64
import logging
import os
import re
import subprocess
import zipfile
from html import escape

import mammoth

try:
    from docx import Document as DocxDocument
    from docx.table import Table as DocxTable
    from docx.text.paragraph import Paragraph as DocxParagraph
except Exception:  # pragma: no cover - optional runtime dependency
    DocxDocument = None
    DocxTable = None
    DocxParagraph = None

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("DocumentParser")


class DocumentParser:
    """将上传文档转换为编辑器可用的 HTML。"""

    @staticmethod
    def get_content(file_path: str) -> str:
        if not os.path.exists(file_path):
            logger.error("文件未找到: %s", file_path)
            return "<p>错误：服务器找不到该物理文件。</p>"

        ext = os.path.splitext(file_path)[1].lower()

        if ext == ".docx":
            return DocumentParser._parse_docx(file_path)
        if ext == ".doc":
            return DocumentParser._parse_doc_via_conversion(file_path)

        return f"<p>暂不支持的格式: {escape(ext)}。请上传 docx 或 doc 文件。</p>"

    @staticmethod
    def _convert_image(image):
        with image.open() as image_bytes:
            encoded_src = base64.b64encode(image_bytes.read()).decode("ascii")
        return {"src": f"data:{image.content_type};base64,{encoded_src}"}

    @staticmethod
    def _parse_docx(file_path: str) -> str:
        """
        主路径：Mammoth 转 HTML。
        兜底：若 Word 含表格但 Mammoth 输出无 table，则用 python-docx 重建结构。
        """
        try:
            with open(file_path, "rb") as docx_file:
                style_map = """
                p[style-name='Heading 1'] => h1
                p[style-name='Heading 2'] => h2
                p[style-name='Heading 3'] => h3
                p[style-name='Title'] => h1.doc-title
                p[style-name='Subtitle'] => h2.doc-subtitle
                """

                result = mammoth.convert_to_html(
                    docx_file,
                    style_map=style_map,
                    convert_image=mammoth.images.img_element(DocumentParser._convert_image),
                )

            html = (result.value or "").strip()
            if result.messages:
                warnings = [m.message for m in result.messages if "unknown" not in m.message.lower()]
                if warnings:
                    logger.warning("Mammoth 解析警告: %s", warnings)

            has_doc_table = DocumentParser._docx_contains_table(file_path)
            has_html_table = "<table" in html.lower()

            # 关键兜底：文档有表格，但解析结果没有 table 结构。
            if has_doc_table and not has_html_table:
                logger.warning("检测到 DOCX 含表格，但 Mammoth 输出无 <table>，启用 python-docx 兜底")
                fallback_html = DocumentParser._parse_docx_with_python_docx(file_path)
                if fallback_html.strip():
                    return fallback_html

            if html:
                return html

            # Mammoth 为空时兜底
            fallback_html = DocumentParser._parse_docx_with_python_docx(file_path)
            if fallback_html.strip():
                return fallback_html

            return "<p>该文档内容为空。</p>"

        except Exception as exc:
            logger.error("DOCX 解析异常: %s", exc)
            fallback_html = DocumentParser._parse_docx_with_python_docx(file_path)
            if fallback_html.strip():
                return fallback_html
            return f"<p>解析异常: {escape(str(exc))}</p>"

    @staticmethod
    def _docx_contains_table(file_path: str) -> bool:
        try:
            with zipfile.ZipFile(file_path) as zf:
                xml = zf.read("word/document.xml").decode("utf-8", errors="ignore")
                return "<w:tbl" in xml
        except Exception:
            return False

    @staticmethod
    def _parse_docx_with_python_docx(file_path: str) -> str:
        if DocxDocument is None:
            logger.warning("python-docx 不可用，无法执行 DOCX 结构化兜底")
            return ""

        try:
            doc = DocxDocument(file_path)
            blocks = []

            for block in DocumentParser._iter_block_items(doc):
                if DocxParagraph is not None and isinstance(block, DocxParagraph):
                    blocks.append(DocumentParser._paragraph_to_html(block))
                elif DocxTable is not None and isinstance(block, DocxTable):
                    blocks.append(DocumentParser._table_to_html(block))

            html = "\n".join(part for part in blocks if part)
            return html or ""
        except Exception as exc:
            logger.error("python-docx 兜底解析失败: %s", exc)
            return ""

    @staticmethod
    def _iter_block_items(document):
        if DocxParagraph is None or DocxTable is None:
            return []

        body = document.element.body
        for child in body.iterchildren():
            tag = child.tag.rsplit("}", 1)[-1]
            if tag == "p":
                yield DocxParagraph(child, document)
            elif tag == "tbl":
                yield DocxTable(child, document)

    @staticmethod
    def _paragraph_to_html(paragraph) -> str:
        text = (paragraph.text or "").strip()
        style_name = (getattr(paragraph.style, "name", "") or "").lower()

        if not text:
            return "<p><br/></p>"

        if "heading 1" in style_name:
            tag = "h1"
        elif "heading 2" in style_name:
            tag = "h2"
        elif "heading 3" in style_name:
            tag = "h3"
        else:
            tag = "p"

        run_html = []
        for run in paragraph.runs:
            run_text = escape(run.text or "")
            if not run_text:
                continue
            if run.bold:
                run_text = f"<strong>{run_text}</strong>"
            if run.italic:
                run_text = f"<em>{run_text}</em>"
            if run.underline:
                run_text = f"<u>{run_text}</u>"
            run_html.append(run_text)

        content = "".join(run_html) if run_html else escape(text)
        return f"<{tag}>{content}</{tag}>"

    @staticmethod
    def _table_to_html(table) -> str:
        rows_html = []
        for row in table.rows:
            cells_html = []
            for cell in row.cells:
                paragraphs = [
                    DocumentParser._paragraph_to_html(p)
                    for p in cell.paragraphs
                    if (p.text or "").strip() or len(p.runs) > 0
                ]
                cell_content = "".join(paragraphs) if paragraphs else "<p><br/></p>"
                cells_html.append(f"<td>{cell_content}</td>")
            rows_html.append(f"<tr>{''.join(cells_html)}</tr>")

        return f"<table><tbody>{''.join(rows_html)}</tbody></table>"

    @staticmethod
    def _parse_doc_via_conversion(file_path: str) -> str:
        logger.info("检测到 .doc，尝试先转 docx: %s", file_path)
        try:
            output_dir = os.path.dirname(file_path)
            subprocess.run(
                [
                    "libreoffice",
                    "--headless",
                    "--convert-to",
                    "docx",
                    file_path,
                    "--outdir",
                    output_dir,
                ],
                capture_output=True,
                text=True,
                check=True,
            )

            base_name = os.path.splitext(os.path.basename(file_path))[0]
            new_docx_path = os.path.join(output_dir, f"{base_name}.docx")

            if os.path.exists(new_docx_path):
                return DocumentParser._parse_docx(new_docx_path)

            return "<p>格式转换失败：LibreOffice 未生成目标 docx 文件。</p>"
        except Exception as exc:
            logger.error("DOC 转换异常: %s", exc)
            return f"<p>转换异常: {escape(str(exc))}</p>"
