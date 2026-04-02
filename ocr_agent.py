"""
AnatomySelf OCR Agent 模块
支持 PDF 和图片的医疗报告识别
依赖：pdfplumber, pytesseract, Pillow
系统依赖：Tesseract OCR（需单独安装）
"""
import re
import config
from datetime import datetime

# 检查 OCR 依赖可用性
try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False

try:
    import pytesseract
    from PIL import Image
    TESSERACT_AVAILABLE = True
    # 验证 Tesseract 系统程序是否已安装
    try:
        pytesseract.get_tesseract_version()
        TESSERACT_SYSTEM_OK = True
    except Exception:
        TESSERACT_SYSTEM_OK = False
except ImportError:
    TESSERACT_AVAILABLE = False
    TESSERACT_SYSTEM_OK = False


def get_ocr_status() -> dict:
    """返回 OCR 可用性状态"""
    return {
        "pdfplumber": PDFPLUMBER_AVAILABLE,
        "pytesseract_package": TESSERACT_AVAILABLE,
        "tesseract_system": TESSERACT_SYSTEM_OK,
        "fully_available": PDFPLUMBER_AVAILABLE and TESSERACT_AVAILABLE and TESSERACT_SYSTEM_OK
    }


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """从 PDF 文件中提取文本"""
    if not PDFPLUMBER_AVAILABLE:
        raise ImportError(
            "缺少 pdfplumber 依赖，请运行：pip install pdfplumber"
        )
    
    import io
    text_parts = []
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                text_parts.append(text)
    
    return "\n".join(text_parts)


def extract_text_from_image(file_bytes: bytes) -> str:
    """从图片文件中提取文本"""
    if not TESSERACT_AVAILABLE:
        raise ImportError(
            "缺少 pytesseract 依赖，请运行：pip install pytesseract Pillow"
        )
    
    if not TESSERACT_SYSTEM_OK:
        raise RuntimeError(
            "系统未安装 Tesseract OCR 程序。\n"
            "安装方法：\n"
            "  macOS: brew install tesseract tesseract-lang\n"
            "  Ubuntu/Debian: sudo apt-get install tesseract-ocr tesseract-ocr-chi-sim\n"
            "  Windows: 下载安装包 https://github.com/UB-Mannheim/tesseract/wiki"
        )
    
    import io
    image = Image.open(io.BytesIO(file_bytes))
    # 尝试中文+英文识别
    text = pytesseract.image_to_string(image, lang='chi_sim+eng')
    return text


def extract_indicators_via_ai(
    file_bytes: bytes,
    file_type: str = "pdf"
) -> tuple:
    """
    使用 AI 从医疗报告中提取指标
    返回 (indicators_list, report_date)
    """
    # 1. 提取原始文本
    try:
        if file_type.lower() in ("pdf",):
            raw_text = extract_text_from_pdf(file_bytes)
        else:
            raw_text = extract_text_from_image(file_bytes)
    except Exception as e:
        raise RuntimeError(f"文本提取失败：{str(e)}")
    
    if not raw_text.strip():
        raise ValueError("未能从文件中提取到文本内容，请确认文件格式正确。")
    
    # 2. 使用 AI 解析指标
    if not config.LLM_API_KEY:
        raise ValueError("❌ 未配置 LLM_API_KEY，无法使用 AI 解析功能。")
    
    from openai import OpenAI
    client = OpenAI(
        api_key=config.LLM_API_KEY,
        base_url=config.LLM_BASE_URL
    )
    
    prompt = f"""请从以下医疗报告文本中提取所有检验指标，并以 JSON 格式返回。

报告文本：
{raw_text[:3000]}

请返回如下格式的 JSON 数组：
[
  {{
    "indicator_name": "指标名称",
    "indicator_code": "指标代码（如WBC）",
    "value": 数值,
    "unit": "单位",
    "ref_low": 参考下限,
    "ref_high": 参考上限,
    "category": "类别（如血液检查、生化检查等）"
  }}
]

同时在 JSON 数组前面返回报告日期，格式：DATE:YYYY-MM-DD
如果无法确定日期，返回 DATE:{datetime.now().strftime('%Y-%m-%d')}

只返回 DATE 行和 JSON 数组，不要其他内容。"""
    
    resp = client.chat.completions.create(
        model=config.LLM_MODEL,
        messages=[
            {"role": "system", "content": "你是专业的医疗数据解析专家，擅长从体检报告中提取结构化数据。"},
            {"role": "user", "content": prompt}
        ],
        max_tokens=2000,
        temperature=0.1
    )
    
    content = resp.choices[0].message.content.strip()
    
    # 解析日期
    report_date = datetime.now().strftime('%Y-%m-%d')
    date_match = re.search(r'DATE:(\d{4}-\d{2}-\d{2})', content)
    if date_match:
        report_date = date_match.group(1)
    
    # 解析 JSON
    import json
    json_match = re.search(r'\[.*\]', content, re.DOTALL)
    if not json_match:
        raise ValueError("AI 未能返回有效的 JSON 格式数据。")
    
    indicators = json.loads(json_match.group())
    
    return indicators, report_date
