"""
AnatomySelf AI Agent 模块
统一 AI 调用接口，使用 config.py 配置
"""
import config
from openai import OpenAI


def _get_ai_client():
    """获取 AI 客户端实例"""
    if not config.LLM_API_KEY:
        raise ValueError("❌ 未配置 LLM_API_KEY，请在环境变量或 .streamlit/secrets.toml 中设置。")
    
    return OpenAI(
        api_key=config.LLM_API_KEY,
        base_url=config.LLM_BASE_URL
    )


def analyze_indicator(
    indicator_name: str,
    indicator_code: str,
    value: float,
    unit: str,
    ref_low: float,
    ref_high: float,
    age: int = 0,
    gender: str = ""
) -> str:
    """
    分析单个指标的健康状况
    """
    try:
        client = _get_ai_client()
        
        status = "正常"
        if value < ref_low:
            status = "偏低"
        elif value > ref_high:
            status = "偏高"
        
        prompt = f"""请作为专业医学顾问，分析以下体检指标：

指标名称：{indicator_name} ({indicator_code})
检测值：{value} {unit}
参考范围：{ref_low} - {ref_high} {unit}
状态：{status}
年龄：{age}岁
性别：{gender}

请给出：
1. 该指标的生理意义
2. 当前状态的健康影响
3. 具体的改善建议（饮食、运动、生活习惯）

请用简洁专业的语言，200字以内。"""

        resp = client.chat.completions.create(
            model=config.LLM_MODEL,
            messages=[
                {"role": "system", "content": "你是一位资深医学顾问，擅长解读体检报告并给出实用建议。"},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=config.LLM_TEMPERATURE
        )
        
        return resp.choices[0].message.content
    
    except Exception as e:
        return f"AI 分析暂时不可用：{str(e)}"


def analyze_symptom(
    symptom_text: str,
    body_location: str,
    profile: dict,
    recent_records: list,
    environmental_data: dict = None
) -> dict:
    """
    分析症状并给出健康建议
    """
    try:
        client = _get_ai_client()
        
        age = profile.get("age", 0)
        gender = profile.get("gender", "")
        allergies = profile.get("allergies", "")
        chronic = profile.get("chronic_diseases", "")
        
        env_info = ""
        if environmental_data:
            env_info = f"\n环境信息：温度 {environmental_data.get('temp', 'N/A')}°C，湿度 {environmental_data.get('humidity', 'N/A')}%，PM2.5: {environmental_data.get('pm25', 'N/A')}"
        
        prompt = f"""请作为专业医学顾问，分析以下症状：

症状描述：{symptom_text}
部位：{body_location}
年龄：{age}岁
性别：{gender}
过敏史：{allergies or '无'}
慢性病史：{chronic or '无'}{env_info}

请给出：
1. 可能的原因分析
2. 严重程度评估
3. 建议的处理方式
4. 是否需要就医

请用简洁专业的语言，300字以内。"""

        resp = client.chat.completions.create(
            model=config.LLM_MODEL,
            messages=[
                {"role": "system", "content": "你是一位资深医学顾问，擅长症状分析和健康建议。"},
                {"role": "user", "content": prompt}
            ],
            max_tokens=800,
            temperature=config.LLM_TEMPERATURE
        )
        
        return {
            "analysis": resp.choices[0].message.content,
            "timestamp": str(profile.get("timestamp", ""))
        }
    
    except Exception as e:
        return {
            "analysis": f"AI 分析暂时不可用：{str(e)}",
            "timestamp": ""
        }


def generate_weekly_report_v2(
    profile: dict,
    week_start: str,
    week_end: str,
    records: list,
    symptoms: list,
    options: dict
) -> dict:
    """
    生成周报
    """
    try:
        client = _get_ai_client()
        
        age = profile.get("age", 0)
        gender = profile.get("gender", "")
        
        records_summary = f"共 {len(records)} 条体检记录"
        symptoms_summary = f"共 {len(symptoms)} 条症状记录"
        
        prompt = f"""请作为专业健康顾问，生成本周健康周报：

时间范围：{week_start} 至 {week_end}
用户信息：{age}岁，{gender}
体检数据：{records_summary}
症状记录：{symptoms_summary}

请生成包含以下内容的周报：
1. 本周健康概况
2. 关键指标变化趋势
3. 需要关注的健康问题
4. 下周健康建议

请用专业但易懂的语言，500字以内。"""

        resp = client.chat.completions.create(
            model=config.LLM_MODEL,
            messages=[
                {"role": "system", "content": "你是一位资深健康顾问，擅长生成个性化健康报告。"},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1500,
            temperature=config.LLM_TEMPERATURE
        )
        
        return {
            "content": resp.choices[0].message.content,
            "week_start": week_start,
            "week_end": week_end
        }
    
    except Exception as e:
        return {
            "content": f"AI 生成周报暂时不可用：{str(e)}",
            "week_start": week_start,
            "week_end": week_end
        }
