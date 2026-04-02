"""
AnatomySelf 统一配置文件
支持从环境变量、Streamlit secrets 或默认值读取配置
"""
import os
import streamlit as st


def get_config(key: str, default: str = "") -> str:
    """
    统一配置读取函数
    优先级：st.secrets > 环境变量 > 默认值
    """
    # 1. 优先从 Streamlit secrets 读取
    try:
        if hasattr(st, 'secrets') and key in st.secrets:
            return st.secrets[key]
    except Exception:
        pass
    
    # 2. 从环境变量读取
    value = os.getenv(key)
    if value:
        return value
    
    # 3. 返回默认值
    return default


# ========== AI 配置 ==========
LLM_API_KEY = get_config("LLM_API_KEY", "")
LLM_BASE_URL = get_config("LLM_BASE_URL", "https://api.openai.com/v1")
LLM_MODEL = get_config("LLM_MODEL", "gpt-4.1-mini")
LLM_TEMPERATURE = float(get_config("LLM_TEMPERATURE", "0.7"))

# ========== 环境配置 ==========
DEFAULT_CITY = get_config("DEFAULT_CITY", "Beijing")

# ========== 数据库配置 ==========
DATABASE_PATH = get_config("DATABASE_PATH", "./anatomy_self.db")

# ========== OCR 配置 ==========
OCR_ENABLED = get_config("OCR_ENABLED", "true").lower() in ("true", "1", "yes")

# ========== 调试模式 ==========
DEBUG_MODE = get_config("DEBUG_MODE", "false").lower() in ("true", "1", "yes")


def validate_config():
    """
    验证必需配置项是否已设置
    返回 (is_valid, error_message)
    """
    if not LLM_API_KEY:
        return False, "❌ 缺少必需配置：LLM_API_KEY\n\n请设置环境变量或在 .streamlit/secrets.toml 中配置。"
    
    return True, ""
