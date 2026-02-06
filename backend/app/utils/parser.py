import mammoth
import os
import subprocess
import logging

# 配置日志审计
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("DocumentParser")

class DocumentParser:
    """
    公文解析器：负责将物理磁盘上的文档转换为富文本 HTML
    """

    @staticmethod
    def get_content(file_path: str) -> str:
        """
        入口方法：自动识别格式并返回 HTML 字符串
        """
        if not os.path.exists(file_path):
            logger.error(f"文件未找到: {file_path}")
            return "<p>错误：服务器找不到该物理文件。</p>"

        # 获取后缀名
        ext = file_path.split('.')[-1].lower()

        if ext == 'docx':
            return DocumentParser._parse_docx(file_path)
        elif ext == 'doc':
            return DocumentParser._parse_doc_via_conversion(file_path)
        else:
            return f"<p>不支持的格式: {ext}。请上传 docx 或 doc 文件。</p>"

    @staticmethod
    def _parse_docx(file_path: str) -> str:
        """
        使用 Mammoth 解析 docx（保持 HTML 语义化）
        """
        try:
            with open(file_path, "rb") as docx_file:
                # 转换配置：我们可以根据公文特性自定义样式映射
                # 比如将 Word 的 'Title' 映射为 HTML 的 'h1'
                result = mammoth.convert_to_html(docx_file)
                html = result.value

                # 记录转换过程中的警告（如：未识别的样式）
                if result.messages:
                    logger.warning(f"解析警告: {result.messages}")

                if not html.strip():
                    return "<p>该文档内容为空。</p>"

                logger.info(f"✅ 成功解析 docx: {file_path}")
                return html
        except Exception as e:
            logger.error(f"🔥 Mammoth 解析崩溃: {str(e)}")
            return f"<p>解析异常: {str(e)}</p>"

    @staticmethod
    def _parse_doc_via_conversion(file_path: str) -> str:
        """
        处理老旧 .doc 格式：先调用 LibreOffice 转换为 .docx 再解析
        注意：生产环境需在服务器/Docker 中安装 libreoffice
        """
        logger.info(f"🔄 检测到旧版格式，尝试转换: {file_path}")

        try:
            # 1. 设置输出目录
            output_dir = os.path.dirname(file_path)

            # 2. 调用系统指令进行静默转换 (Headless Mode)
            # 命令示例: libreoffice --headless --convert-to docx test.doc --outdir ./uploads
            process = subprocess.run([
                'libreoffice',
                '--headless',
                '--convert-to', 'docx',
                file_path,
                '--outdir', output_dir
            ], capture_output=True, text=True, check=True)

            # 3. 构造转换后的新路径
            base_name = os.path.splitext(os.path.basename(file_path))[0]
            new_docx_path = os.path.join(output_dir, f"{base_name}.docx")

            # 4. 验证转换结果并递归解析
            if os.path.exists(new_docx_path):
                content = DocumentParser._parse_docx(new_docx_path)
                # 转换完后建议清理掉临时的 docx，或者保留作为缓存
                return content
            else:
                return "<p>格式转换失败：LibreOffice 未生成目标文件。</p>"

        except FileNotFoundError:
            logger.error("系统未安装 LibreOffice，无法解析 .doc 格式")
            return "<p>当前环境仅支持 .docx。如需解析 .doc，请联系管理员安装转换组件。</p>"
        except Exception as e:
            logger.error(f"转换过程发生错误: {str(e)}")
            return f"<p>转换异常: {str(e)}</p>"