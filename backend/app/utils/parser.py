import mammoth
import os
import subprocess
import logging
import base64

# 配置日志审计
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("DocumentParser")

class DocumentParser:
    """
    公文解析器：负责将物理磁盘上的文档转换为富文本 HTML
    """

    @staticmethod
    def get_content(file_path: str) -> str:
        if not os.path.exists(file_path):
            logger.error(f"文件未找到: {file_path}")
            return "<p>错误：服务器找不到该物理文件。</p>"

        ext = file_path.split('.')[-1].lower()

        if ext == 'docx':
            return DocumentParser._parse_docx(file_path)
        elif ext == 'doc':
            return DocumentParser._parse_doc_via_conversion(file_path)
        else:
            return f"<p>不支持的格式: {ext}。请上传 docx 或 doc 文件。</p>"

    @staticmethod
    def _convert_image(image):
        """
        图片处理钩子：将图片转换为 Base64
        注意：生产环境建议这里将图片上传到对象存储(OSS/S3)，返回 URL，
        而不是返回 Base64，否则 HTML 会非常大。
        """
        with image.open() as image_bytes:
            encoded_src = base64.b64encode(image_bytes.read()).decode("ascii")

        return {
            "src": f"data:{image.content_type};base64,{encoded_src}"
        }

    @staticmethod
    def _parse_docx(file_path: str) -> str:
        """
        使用 Mammoth 解析 docx
        """
        try:
            with open(file_path, "rb") as docx_file:
                # 1. 定义样式映射 (Style Map)
                # Mammoth 默认有时候识别不出复杂的标题，这里强制映射
                # 还可以将 Word 中的特定样式映射为 HTML 的 class
                style_map = """
                p[style-name='Heading 1'] => h1
                p[style-name='Heading 2'] => h2
                p[style-name='Heading 3'] => h3
                p[style-name='Title'] => h1.doc-title
                p[style-name='Subtitle'] => h2.doc-subtitle
                table => table.table-wrapper
                """
                # 注意：mammoth 不太支持直接给 table 加 class，但可以尝试映射内容

                # 2. 执行转换
                result = mammoth.convert_to_html(
                    docx_file,
                    style_map=style_map,
                    convert_image=mammoth.images.img_element(DocumentParser._convert_image) # 显式处理图片
                )

                html = result.value

                # 3. 记录警告 (这对调试 Word 格式非常有用)
                if result.messages:
                    # 过滤掉一些无关痛痒的警告
                    warnings = [m.message for m in result.messages if "unknown" not in m.message]
                    if warnings:
                        logger.warning(f"解析警告: {warnings}")

                if not html.strip():
                    return "<p>该文档内容为空。</p>"

                logger.info(f"✅ 成功解析 docx: {file_path}")
                return html
        except Exception as e:
            logger.error(f"🔥 Mammoth 解析崩溃: {str(e)}")
            return f"<p>解析异常: {str(e)}</p>"

    @staticmethod
    def _parse_doc_via_conversion(file_path: str) -> str:
        # 这部分代码保持不变，逻辑没问题
        logger.info(f"🔄 检测到旧版格式，尝试转换: {file_path}")
        try:
            output_dir = os.path.dirname(file_path)
            # 使用 LibreOffice 转换
            process = subprocess.run([
                'libreoffice',
                '--headless',
                '--convert-to', 'docx',
                file_path,
                '--outdir', output_dir
            ], capture_output=True, text=True, check=True)

            base_name = os.path.splitext(os.path.basename(file_path))[0]
            new_docx_path = os.path.join(output_dir, f"{base_name}.docx")

            if os.path.exists(new_docx_path):
                content = DocumentParser._parse_docx(new_docx_path)
                # 可选：转换完删除临时文件
                # os.remove(new_docx_path)
                return content
            else:
                return "<p>格式转换失败：LibreOffice 未生成目标文件。</p>"

        except Exception as e:
            logger.error(f"转换过程发生错误: {str(e)}")
            return f"<p>转换异常: {str(e)}</p>"