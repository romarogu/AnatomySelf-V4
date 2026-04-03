"""
utils.py — AnatomySelf V5.5 通用工具库
包含：医学维度定义、指标生理知识库、评分计算、Plotly 图表生成函数。
"""
from __future__ import annotations
from typing import Dict, List, Optional, Any
import plotly.graph_objects as go
import plotly.express as px

# ══════════════════════════════════════════════════════════════════════════════
# 1. 医学维度定义（六大维度）
# ══════════════════════════════════════════════════════════════════════════════

MEDICAL_DIMENSIONS: Dict[str, Dict] = {
    "代谢健康": {
        "icon": "🔥",
        "color": "#FF6B6B",
        "desc": "血糖、血脂、尿酸等代谢指标",
        "indicators": {
            "GLU":  {"weight": 2.0, "ref_low": 3.9, "ref_high": 6.1},
            "HBA1C": {"weight": 2.5, "ref_low": 4.0, "ref_high": 6.0},
            "TC":   {"weight": 1.5, "ref_low": 0.0, "ref_high": 5.2},
            "TG":   {"weight": 1.5, "ref_low": 0.0, "ref_high": 1.7},
            "LDL":  {"weight": 2.0, "ref_low": 0.0, "ref_high": 3.4},
            "HDL":  {"weight": 1.5, "ref_low": 1.0, "ref_high": 9.9},
            "UA":   {"weight": 1.5, "ref_low": 0.0, "ref_high": 420},
        },
    },
    "免疫力": {
        "icon": "🛡️",
        "color": "#4ECDC4",
        "desc": "白细胞、淋巴细胞等免疫指标",
        "indicators": {
            "WBC":  {"weight": 2.0, "ref_low": 4.0, "ref_high": 10.0},
            "LYMPH": {"weight": 1.5, "ref_low": 20.0, "ref_high": 40.0},
            "NEUT": {"weight": 1.5, "ref_low": 50.0, "ref_high": 70.0},
            "CRP":  {"weight": 2.0, "ref_low": 0.0, "ref_high": 10.0},
            "ESR":  {"weight": 1.0, "ref_low": 0.0, "ref_high": 20.0},
        },
    },
    "呼吸功能": {
        "icon": "🫁",
        "color": "#45B7D1",
        "desc": "血氧、血红蛋白等呼吸相关指标",
        "indicators": {
            "SPO2": {"weight": 2.5, "ref_low": 95.0, "ref_high": 100.0},
            "HGB":  {"weight": 2.0, "ref_low": 120.0, "ref_high": 160.0},
            "RBC":  {"weight": 1.5, "ref_low": 3.5, "ref_high": 5.5},
            "HCT":  {"weight": 1.0, "ref_low": 36.0, "ref_high": 50.0},
        },
    },
    "循环功能": {
        "icon": "❤️",
        "color": "#E74C3C",
        "desc": "血压、心率等循环系统指标",
        "indicators": {
            "SBP":  {"weight": 2.5, "ref_low": 90.0, "ref_high": 140.0},
            "DBP":  {"weight": 2.5, "ref_low": 60.0, "ref_high": 90.0},
            "HR":   {"weight": 1.5, "ref_low": 60.0, "ref_high": 100.0},
        },
    },
    "消化功能": {
        "icon": "🫀",
        "color": "#F39C12",
        "desc": "肝功能、肾功能等消化代谢指标",
        "indicators": {
            "ALT":  {"weight": 2.0, "ref_low": 0.0, "ref_high": 40.0},
            "AST":  {"weight": 2.0, "ref_low": 0.0, "ref_high": 40.0},
            "TBIL": {"weight": 1.5, "ref_low": 0.0, "ref_high": 21.0},
            "ALB":  {"weight": 1.5, "ref_low": 35.0, "ref_high": 55.0},
            "CREA": {"weight": 2.0, "ref_low": 44.0, "ref_high": 115.0},
            "BUN":  {"weight": 1.5, "ref_low": 2.9, "ref_high": 8.2},
        },
    },
    "骨骼健康": {
        "icon": "🦴",
        "color": "#9B59B6",
        "desc": "钙、磷、骨密度等骨骼相关指标",
        "indicators": {
            "CA":   {"weight": 2.0, "ref_low": 2.1, "ref_high": 2.6},
            "P":    {"weight": 1.5, "ref_low": 0.8, "ref_high": 1.6},
            "ALP":  {"weight": 1.5, "ref_low": 40.0, "ref_high": 150.0},
            "VD":   {"weight": 2.0, "ref_low": 50.0, "ref_high": 250.0},
        },
    },
}


# ══════════════════════════════════════════════════════════════════════════════
# 2. 指标生理知识库（INDICATOR_PHYSIOLOGY）
# ══════════════════════════════════════════════════════════════════════════════

INDICATOR_PHYSIOLOGY: Dict[str, Dict] = {
    # 血糖
    "GLU":   {"name": "空腹血糖",   "unit": "mmol/L", "organs": ["胰腺", "肝脏"], "ref_low": 3.9, "ref_high": 6.1},
    "HBA1C": {"name": "糖化血红蛋白", "unit": "%",      "organs": ["胰腺", "血液"], "ref_low": 4.0, "ref_high": 6.0},
    # 血脂
    "TC":    {"name": "总胆固醇",   "unit": "mmol/L", "organs": ["肝脏", "血管"], "ref_low": 0.0, "ref_high": 5.2},
    "TG":    {"name": "甘油三酯",   "unit": "mmol/L", "organs": ["肝脏", "脂肪组织"], "ref_low": 0.0, "ref_high": 1.7},
    "LDL":   {"name": "低密度脂蛋白", "unit": "mmol/L", "organs": ["肝脏", "血管"], "ref_low": 0.0, "ref_high": 3.4},
    "HDL":   {"name": "高密度脂蛋白", "unit": "mmol/L", "organs": ["肝脏", "血管"], "ref_low": 1.0, "ref_high": 9.9},
    # 尿酸
    "UA":    {"name": "尿酸",       "unit": "μmol/L", "organs": ["肾脏", "关节"], "ref_low": 0.0, "ref_high": 420},
    # 血常规
    "WBC":   {"name": "白细胞",     "unit": "×10⁹/L", "organs": ["骨髓", "免疫系统"], "ref_low": 4.0, "ref_high": 10.0},
    "RBC":   {"name": "红细胞",     "unit": "×10¹²/L","organs": ["骨髓", "血液"],  "ref_low": 3.5, "ref_high": 5.5},
    "HGB":   {"name": "血红蛋白",   "unit": "g/L",    "organs": ["骨髓", "血液"],  "ref_low": 120.0, "ref_high": 160.0},
    "HCT":   {"name": "红细胞压积", "unit": "%",      "organs": ["骨髓", "血液"],  "ref_low": 36.0, "ref_high": 50.0},
    "PLT":   {"name": "血小板",     "unit": "×10⁹/L", "organs": ["骨髓", "血液"],  "ref_low": 100.0, "ref_high": 300.0},
    "LYMPH": {"name": "淋巴细胞比例","unit": "%",      "organs": ["淋巴系统", "免疫系统"], "ref_low": 20.0, "ref_high": 40.0},
    "NEUT":  {"name": "中性粒细胞比例","unit": "%",    "organs": ["骨髓", "免疫系统"], "ref_low": 50.0, "ref_high": 70.0},
    # 炎症
    "CRP":   {"name": "C反应蛋白",  "unit": "mg/L",   "organs": ["肝脏", "免疫系统"], "ref_low": 0.0, "ref_high": 10.0},
    "ESR":   {"name": "血沉",       "unit": "mm/h",   "organs": ["血液", "免疫系统"], "ref_low": 0.0, "ref_high": 20.0},
    # 血压心率
    "SBP":   {"name": "收缩压",     "unit": "mmHg",   "organs": ["心脏", "血管"],  "ref_low": 90.0, "ref_high": 140.0},
    "DBP":   {"name": "舒张压",     "unit": "mmHg",   "organs": ["心脏", "血管"],  "ref_low": 60.0, "ref_high": 90.0},
    "HR":    {"name": "心率",       "unit": "次/分",  "organs": ["心脏"],          "ref_low": 60.0, "ref_high": 100.0},
    "SPO2":  {"name": "血氧饱和度", "unit": "%",      "organs": ["肺脏", "血液"],  "ref_low": 95.0, "ref_high": 100.0},
    # 肝功能
    "ALT":   {"name": "谷丙转氨酶", "unit": "U/L",    "organs": ["肝脏"],          "ref_low": 0.0, "ref_high": 40.0},
    "AST":   {"name": "谷草转氨酶", "unit": "U/L",    "organs": ["肝脏", "心肌"],  "ref_low": 0.0, "ref_high": 40.0},
    "TBIL":  {"name": "总胆红素",   "unit": "μmol/L", "organs": ["肝脏", "胆囊"],  "ref_low": 0.0, "ref_high": 21.0},
    "ALB":   {"name": "白蛋白",     "unit": "g/L",    "organs": ["肝脏"],          "ref_low": 35.0, "ref_high": 55.0},
    "GGT":   {"name": "谷氨酰转肽酶","unit": "U/L",   "organs": ["肝脏", "胆道"],  "ref_low": 0.0, "ref_high": 50.0},
    # 肾功能
    "CREA":  {"name": "肌酐",       "unit": "μmol/L", "organs": ["肾脏"],          "ref_low": 44.0, "ref_high": 115.0},
    "BUN":   {"name": "尿素氮",     "unit": "mmol/L", "organs": ["肾脏"],          "ref_low": 2.9, "ref_high": 8.2},
    # 骨骼
    "CA":    {"name": "血钙",       "unit": "mmol/L", "organs": ["骨骼", "肾脏"],  "ref_low": 2.1, "ref_high": 2.6},
    "P":     {"name": "血磷",       "unit": "mmol/L", "organs": ["骨骼", "肾脏"],  "ref_low": 0.8, "ref_high": 1.6},
    "ALP":   {"name": "碱性磷酸酶", "unit": "U/L",    "organs": ["骨骼", "肝脏"],  "ref_low": 40.0, "ref_high": 150.0},
    "VD":    {"name": "维生素D",    "unit": "nmol/L", "organs": ["骨骼", "免疫系统"], "ref_low": 50.0, "ref_high": 250.0},
    # 甲状腺
    "TSH":   {"name": "促甲状腺激素","unit": "mIU/L", "organs": ["甲状腺", "垂体"], "ref_low": 0.27, "ref_high": 4.2},
    "FT4":   {"name": "游离甲状腺素","unit": "pmol/L","organs": ["甲状腺"],         "ref_low": 12.0, "ref_high": 22.0},
    "FT3":   {"name": "游离三碘甲状腺原氨酸","unit": "pmol/L","organs": ["甲状腺"], "ref_low": 3.1, "ref_high": 6.8},
    # 体重相关
    "BMI":   {"name": "体质指数",   "unit": "kg/m²",  "organs": ["全身"],          "ref_low": 18.5, "ref_high": 24.0},
    "WEIGHT":{"name": "体重",       "unit": "kg",     "organs": ["全身"],          "ref_low": None, "ref_high": None},
    "HEIGHT":{"name": "身高",       "unit": "cm",     "organs": ["骨骼"],          "ref_low": None, "ref_high": None},
}


# ══════════════════════════════════════════════════════════════════════════════
# 3. 工具函数
# ══════════════════════════════════════════════════════════════════════════════

def get_indicator_info(code: str) -> Optional[Dict]:
    """根据指标代码获取生理知识库信息，不区分大小写。"""
    if not code:
        return None
    return INDICATOR_PHYSIOLOGY.get(code.upper())


def get_dimension_grade(score: float) -> tuple[str, str]:
    """
    根据评分（0-100）返回 (等级文字, 颜色) 元组。
    """
    if score >= 90:
        return "优秀", "#2ECC71"
    elif score >= 75:
        return "良好", "#3498DB"
    elif score >= 60:
        return "一般", "#F39C12"
    elif score >= 40:
        return "偏差", "#E67E22"
    else:
        return "异常", "#E74C3C"


def _score_single_indicator(value: float, ref_low: float, ref_high: float) -> float:
    """
    对单个指标计算 0-100 分：
    - 在参考范围内：100 分
    - 超出范围：按偏差比例线性扣分，最低 0 分
    """
    if ref_low is None or ref_high is None:
        return 80.0  # 无参考范围时给默认分
    ref_range = ref_high - ref_low
    if ref_range <= 0:
        return 80.0
    if ref_low <= value <= ref_high:
        return 100.0
    if value < ref_low:
        deviation = (ref_low - value) / ref_range
    else:
        deviation = (value - ref_high) / ref_range
    score = max(0.0, 100.0 - deviation * 80.0)
    return round(score, 1)


def compute_dimension_scores(records: List[Dict]) -> Dict[str, float]:
    """
    根据体检记录列表计算六大维度评分（0-100）。
    每个维度取其包含指标的加权平均分。
    若某维度无任何数据，默认给 75 分。
    """
    # 建立 code -> record 映射（取最新一条）
    code_map: Dict[str, Dict] = {}
    for rec in records:
        code = (rec.get("indicator_code") or "").upper()
        if code:
            # 保留最新日期的记录
            existing = code_map.get(code)
            if not existing or rec.get("record_date", "") >= existing.get("record_date", ""):
                code_map[code] = rec

    result: Dict[str, float] = {}
    for dim_name, dim_cfg in MEDICAL_DIMENSIONS.items():
        total_weight = 0.0
        weighted_score = 0.0
        for code, ind_cfg in dim_cfg["indicators"].items():
            rec = code_map.get(code)
            if rec is None:
                continue
            value = rec.get("value")
            if value is None:
                continue
            ref_low  = rec.get("ref_low")  or ind_cfg.get("ref_low")
            ref_high = rec.get("ref_high") or ind_cfg.get("ref_high")
            weight = ind_cfg.get("weight", 1.0)
            score = _score_single_indicator(float(value), ref_low, ref_high)
            weighted_score += score * weight
            total_weight += weight
        if total_weight > 0:
            result[dim_name] = round(weighted_score / total_weight, 1)
        else:
            result[dim_name] = 75.0
    return result


def calculate_health_scores(records: List[Dict]) -> Dict[str, float]:
    """
    calculate_health_scores 是 compute_dimension_scores 的别名，
    供 module_d_weekly.py 调用。
    """
    return compute_dimension_scores(records)


# ══════════════════════════════════════════════════════════════════════════════
# 4. Plotly 图表函数
# ══════════════════════════════════════════════════════════════════════════════

_DARK_BG  = "#0E1117"
_CARD_BG  = "#21253A"
_GRID_CLR = "#2E3250"
_TEXT_CLR = "#E8EAF0"
_SUB_CLR  = "#8892B0"


def _base_layout(**kwargs) -> dict:
    """返回统一的深色主题 Plotly layout 字典。"""
    base = dict(
        paper_bgcolor=_DARK_BG,
        plot_bgcolor=_CARD_BG,
        font=dict(color=_TEXT_CLR, family="JetBrains Mono, Courier New, monospace"),
        margin=dict(l=20, r=20, t=40, b=20),
    )
    base.update(kwargs)
    return base


def plot_health_radar(records: List[Dict], member_name: str = "") -> go.Figure:
    """
    绘制六维健康雷达图。
    """
    scores = compute_dimension_scores(records)
    dims   = list(scores.keys())
    values = list(scores.values())
    # 闭合雷达图
    dims_closed   = dims + [dims[0]]
    values_closed = values + [values[0]]

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=values_closed,
        theta=dims_closed,
        fill="toself",
        fillcolor="rgba(74, 158, 255, 0.15)",
        line=dict(color="#4A9EFF", width=2),
        name=member_name or "健康评分",
    ))
    fig.update_layout(
        **_base_layout(title=dict(text=f"{member_name} 六维健康雷达", font=dict(size=14))),
        polar=dict(
            bgcolor=_CARD_BG,
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                tickfont=dict(size=9, color=_SUB_CLR),
                gridcolor=_GRID_CLR,
            ),
            angularaxis=dict(
                tickfont=dict(size=11, color=_TEXT_CLR),
                gridcolor=_GRID_CLR,
            ),
        ),
        showlegend=False,
    )
    return fig


def plot_indicator_trend(
    history: List[Dict],
    indicator_name: str = "",
    unit: str = "",
) -> go.Figure:
    """
    绘制单个指标的历史趋势折线图，含参考范围带。
    """
    dates  = [r.get("record_date", "") for r in history]
    values = [r.get("value") for r in history]
    ref_low  = history[-1].get("ref_low")
    ref_high = history[-1].get("ref_high")

    fig = go.Figure()
    # 参考范围填充
    if ref_low is not None and ref_high is not None:
        fig.add_hrect(
            y0=ref_low, y1=ref_high,
            fillcolor="rgba(46, 204, 113, 0.08)",
            line_width=0,
            annotation_text="参考范围",
            annotation_position="top right",
            annotation_font=dict(size=9, color="#2ECC71"),
        )
        fig.add_hline(y=ref_low,  line=dict(color="#2ECC71", width=1, dash="dot"))
        fig.add_hline(y=ref_high, line=dict(color="#2ECC71", width=1, dash="dot"))

    # 趋势线
    fig.add_trace(go.Scatter(
        x=dates, y=values,
        mode="lines+markers",
        line=dict(color="#4A9EFF", width=2),
        marker=dict(size=7, color="#4A9EFF"),
        name=indicator_name,
    ))
    fig.update_layout(
        **_base_layout(
            title=dict(text=f"{indicator_name}（{unit}）趋势", font=dict(size=13)),
            xaxis=dict(gridcolor=_GRID_CLR, showgrid=True),
            yaxis=dict(gridcolor=_GRID_CLR, showgrid=True,
                       title=dict(text=unit, font=dict(size=11))),
        )
    )
    return fig


def plot_indicator_gauge(
    indicator_name: str,
    value: float,
    unit: str,
    ref_low: float,
    ref_high: float,
) -> go.Figure:
    """
    绘制单个指标的仪表盘图。
    """
    # 仪表盘范围：参考范围的 0.5x ~ 1.8x
    gauge_min = min(ref_low * 0.5, value * 0.8) if ref_low > 0 else 0
    gauge_max = max(ref_high * 1.5, value * 1.2)

    if value < ref_low:
        bar_color = "#3498DB"
    elif value > ref_high:
        bar_color = "#E74C3C"
    else:
        bar_color = "#2ECC71"

    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=value,
        delta={"reference": (ref_low + ref_high) / 2, "valueformat": ".1f"},
        title={"text": f"{indicator_name}<br><span style='font-size:11px;color:{_SUB_CLR}'>{unit}</span>"},
        gauge={
            "axis": {"range": [gauge_min, gauge_max], "tickcolor": _SUB_CLR},
            "bar": {"color": bar_color},
            "bgcolor": _CARD_BG,
            "bordercolor": _GRID_CLR,
            "steps": [
                {"range": [gauge_min, ref_low],  "color": "rgba(52,152,219,0.15)"},
                {"range": [ref_low, ref_high],   "color": "rgba(46,204,113,0.15)"},
                {"range": [ref_high, gauge_max], "color": "rgba(231,76,60,0.15)"},
            ],
            "threshold": {
                "line": {"color": "#F39C12", "width": 3},
                "thickness": 0.75,
                "value": value,
            },
        },
        number={"font": {"color": bar_color, "size": 28}},
    ))
    fig.update_layout(**_base_layout(height=220, margin=dict(l=20, r=20, t=50, b=10)))
    return fig


def plot_family_comparison(family_data: Dict[str, List[Dict]]) -> go.Figure:
    """
    绘制家庭成员健康对比雷达图（多成员叠加）。
    family_data: {成员名: [records]}
    """
    colors = ["#4A9EFF", "#2ECC71", "#F39C12", "#E74C3C", "#9B59B6", "#1ABC9C"]
    dims = list(MEDICAL_DIMENSIONS.keys())
    dims_closed = dims + [dims[0]]

    fig = go.Figure()
    for idx, (member_name, records) in enumerate(family_data.items()):
        scores = compute_dimension_scores(records)
        values = [scores.get(d, 75.0) for d in dims]
        values_closed = values + [values[0]]
        color = colors[idx % len(colors)]
        fig.add_trace(go.Scatterpolar(
            r=values_closed,
            theta=dims_closed,
            fill="toself",
            fillcolor=f"rgba{tuple(int(color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4)) + (0.08,)}",
            line=dict(color=color, width=2),
            name=member_name,
        ))
    fig.update_layout(
        **_base_layout(title=dict(text="家庭健康对比", font=dict(size=14))),
        polar=dict(
            bgcolor=_CARD_BG,
            radialaxis=dict(
                visible=True, range=[0, 100],
                tickfont=dict(size=9, color=_SUB_CLR),
                gridcolor=_GRID_CLR,
            ),
            angularaxis=dict(tickfont=dict(size=11, color=_TEXT_CLR), gridcolor=_GRID_CLR),
        ),
        showlegend=True,
        legend=dict(font=dict(color=_TEXT_CLR, size=11), bgcolor="rgba(0,0,0,0)"),
    )
    return fig


def plot_symptom_calendar(symptoms: List[Dict]) -> Optional[go.Figure]:
    """
    绘制症状日历热力图（按日期 × 严重度）。
    """
    if not symptoms:
        return None
    import pandas as pd

    try:
        df = pd.DataFrame(symptoms)
        df["log_date"] = pd.to_datetime(df["log_date"], errors="coerce")
        df = df.dropna(subset=["log_date"])
        df["severity"] = pd.to_numeric(df.get("severity", 0), errors="coerce").fillna(0)
        df["date_str"] = df["log_date"].dt.strftime("%Y-%m-%d")
        daily = df.groupby("date_str")["severity"].mean().reset_index()
        daily.columns = ["date", "avg_severity"]

        fig = go.Figure(go.Bar(
            x=daily["date"],
            y=daily["avg_severity"],
            marker=dict(
                color=daily["avg_severity"],
                colorscale=[[0, "#2ECC71"], [0.5, "#F39C12"], [1.0, "#E74C3C"]],
                cmin=0, cmax=10,
                colorbar=dict(title="严重度", tickfont=dict(color=_SUB_CLR)),
            ),
            name="平均严重度",
        ))
        fig.update_layout(
            **_base_layout(
                title=dict(text="症状记录日历", font=dict(size=13)),
                xaxis=dict(gridcolor=_GRID_CLR, title="日期"),
                yaxis=dict(gridcolor=_GRID_CLR, title="平均严重度", range=[0, 10]),
            )
        )
        return fig
    except Exception:
        return None
