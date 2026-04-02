"""
AnatomySelf V4.0 - 健康洞察引擎 (Insight Engine)
八字核心算法升级：
  - 天干生克（十天干完整生克体系）
  - 地支刑冲破害合会（六冲、六合、三合、三会、六害、三刑）
  - 十二长生（长生/沐浴/冠带/临官/帝旺/衰/病/死/墓/绝/胎/养）
  - 旺相休囚死（五行季节强弱）
  - 核心神煞（天乙贵人、文昌、驿马、桃花、羊刃、魁罡）
  - 弱关联医学对撞分析（五行承压 → 脏腑 → 体检指标）
"""

import streamlit as st
import json
import math
from datetime import datetime
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
import database as db
import auth

try:
    import plotly.graph_objects as go
    import plotly.express as px
    import numpy as np
    import pandas as pd
    PLOTLY_OK = True
except ImportError:
    PLOTLY_OK = False

# ═══════════════════════════════════════════════════════════════════════════════
# 八字核心数据表
# ═══════════════════════════════════════════════════════════════════════════════

TIANGAN = ["甲","乙","丙","丁","戊","己","庚","辛","壬","癸"]
DIZHI   = ["子","丑","寅","卯","辰","巳","午","未","申","酉","戌","亥"]

# 天干五行属性
TIANGAN_WX = {
    "甲":"木","乙":"木","丙":"火","丁":"火","戊":"土",
    "己":"土","庚":"金","辛":"金","壬":"水","癸":"水"
}
# 天干阴阳
TIANGAN_YY = {
    "甲":"阳","乙":"阴","丙":"阳","丁":"阴","戊":"阳",
    "己":"阴","庚":"阳","辛":"阴","壬":"阳","癸":"阴"
}
# 地支五行属性
DIZHI_WX = {
    "子":"水","丑":"土","寅":"木","卯":"木","辰":"土",
    "巳":"火","午":"火","未":"土","申":"金","酉":"金","戌":"土","亥":"水"
}
# 地支藏干（主气）
DIZHI_CANG = {
    "子":["壬","癸"],"丑":["己","癸","辛"],"寅":["甲","丙","戊"],
    "卯":["甲","乙"],"辰":["戊","乙","癸"],"巳":["丙","庚","戊"],
    "午":["丙","丁","己"],"未":["己","丁","乙"],"申":["庚","壬","戊"],
    "酉":["庚","辛"],"戌":["戊","辛","丁"],"亥":["壬","甲"]
}

# 五行生克
WX_SHENG = {"木":"火","火":"土","土":"金","金":"水","水":"木"}
WX_KE    = {"木":"土","火":"金","土":"水","金":"木","水":"火"}
WX_BEI_KE = {"土":"木","金":"火","水":"土","木":"金","火":"水"}  # 被克

# 五行对应人体
WX_BODY = {
    "木": {"organ":"肝胆","system":"神经/眼睛/筋腱","color":"#2ECC71","emotion":"怒",
           "indicators":["ALT","AST","GGT","ALP","TBIL"]},
    "火": {"organ":"心小肠","system":"循环/舌/血脉","color":"#E74C3C","emotion":"喜",
           "indicators":["CRP","LDL","TC","TG","HDL","HCY"]},
    "土": {"organ":"脾胃","system":"消化/肌肉/口腔","color":"#F39C12","emotion":"思",
           "indicators":["GLU","HBA1C","AMY","TP","ALB"]},
    "金": {"organ":"肺大肠","system":"呼吸/皮肤/鼻腔","color":"#BDC3C7","emotion":"悲",
           "indicators":["IgE","EOS","EOS%","WBC","NEU","NEU%"]},
    "水": {"organ":"肾膀胱","system":"泌尿/骨骼/耳朵","color":"#3498DB","emotion":"恐",
           "indicators":["CREA","BUN","UA","eGFR","K","NA"]},
}

# ─── 天干十神关系 ────────────────────────────────────────────────────────────
# 以日主天干为基准，计算其他天干的十神
SHISHEN_TABLE = {
    # (日主, 他干) -> 十神
    # 甲日主
    ("甲","甲"):"比肩",("甲","乙"):"劫财",("甲","丙"):"食神",("甲","丁"):"伤官",
    ("甲","戊"):"偏财",("甲","己"):"正财",("甲","庚"):"七杀",("甲","辛"):"正官",
    ("甲","壬"):"偏印",("甲","癸"):"正印",
    # 乙日主
    ("乙","乙"):"比肩",("乙","甲"):"劫财",("乙","丁"):"食神",("乙","丙"):"伤官",
    ("乙","己"):"偏财",("乙","戊"):"正财",("乙","辛"):"七杀",("乙","庚"):"正官",
    ("乙","癸"):"偏印",("乙","壬"):"正印",
    # 丙日主
    ("丙","丙"):"比肩",("丙","丁"):"劫财",("丙","戊"):"食神",("丙","己"):"伤官",
    ("丙","庚"):"偏财",("丙","辛"):"正财",("丙","壬"):"七杀",("丙","癸"):"正官",
    ("丙","甲"):"偏印",("丙","乙"):"正印",
    # 丁日主
    ("丁","丁"):"比肩",("丁","丙"):"劫财",("丁","己"):"食神",("丁","戊"):"伤官",
    ("丁","辛"):"偏财",("丁","庚"):"正财",("丁","癸"):"七杀",("丁","壬"):"正官",
    ("丁","乙"):"偏印",("丁","甲"):"正印",
    # 戊日主
    ("戊","戊"):"比肩",("戊","己"):"劫财",("戊","庚"):"食神",("戊","辛"):"伤官",
    ("戊","壬"):"偏财",("戊","癸"):"正财",("戊","甲"):"七杀",("戊","乙"):"正官",
    ("戊","丙"):"偏印",("戊","丁"):"正印",
    # 己日主
    ("己","己"):"比肩",("己","戊"):"劫财",("己","辛"):"食神",("己","庚"):"伤官",
    ("己","癸"):"偏财",("己","壬"):"正财",("己","乙"):"七杀",("己","甲"):"正官",
    ("己","丁"):"偏印",("己","丙"):"正印",
    # 庚日主
    ("庚","庚"):"比肩",("庚","辛"):"劫财",("庚","壬"):"食神",("庚","癸"):"伤官",
    ("庚","甲"):"偏财",("庚","乙"):"正财",("庚","丙"):"七杀",("庚","丁"):"正官",
    ("庚","戊"):"偏印",("庚","己"):"正印",
    # 辛日主
    ("辛","辛"):"比肩",("辛","庚"):"劫财",("辛","癸"):"食神",("辛","壬"):"伤官",
    ("辛","乙"):"偏财",("辛","甲"):"正财",("辛","丁"):"七杀",("辛","丙"):"正官",
    ("辛","己"):"偏印",("辛","戊"):"正印",
    # 壬日主
    ("壬","壬"):"比肩",("壬","癸"):"劫财",("壬","甲"):"食神",("壬","乙"):"伤官",
    ("壬","丙"):"偏财",("壬","丁"):"正财",("壬","戊"):"七杀",("壬","己"):"正官",
    ("壬","庚"):"偏印",("壬","辛"):"正印",
    # 癸日主
    ("癸","癸"):"比肩",("癸","壬"):"劫财",("癸","乙"):"食神",("癸","甲"):"伤官",
    ("癸","丁"):"偏财",("癸","丙"):"正财",("癸","己"):"七杀",("癸","戊"):"正官",
    ("癸","辛"):"偏印",("癸","庚"):"正印",
}

# ─── 地支六冲 ────────────────────────────────────────────────────────────────
DIZHI_CHONG = {
    "子":"午","午":"子","丑":"未","未":"丑",
    "寅":"申","申":"寅","卯":"酉","酉":"卯",
    "辰":"戌","戌":"辰","巳":"亥","亥":"巳"
}

# ─── 地支六合 ────────────────────────────────────────────────────────────────
DIZHI_LIUHE = {
    "子":"丑","丑":"子","寅":"亥","亥":"寅","卯":"戌","戌":"卯",
    "辰":"酉","酉":"辰","巳":"申","申":"巳","午":"未","未":"午"
}
DIZHI_LIUHE_WX = {
    ("子","丑"):"土",("寅","亥"):"木",("卯","戌"):"火",
    ("辰","酉"):"金",("巳","申"):"水",("午","未"):"土"
}

# ─── 地支三合局 ──────────────────────────────────────────────────────────────
DIZHI_SANHE = [
    ({"申","子","辰"},"水局"),
    ({"寅","午","戌"},"火局"),
    ({"巳","酉","丑"},"金局"),
    ({"亥","卯","未"},"木局"),
]

# ─── 地支三会方 ──────────────────────────────────────────────────────────────
DIZHI_SANHUI = [
    ({"寅","卯","辰"},"木方"),
    ({"巳","午","未"},"火方"),
    ({"申","酉","戌"},"金方"),
    ({"亥","子","丑"},"水方"),
]

# ─── 地支六害 ────────────────────────────────────────────────────────────────
DIZHI_LIUHAI = {
    "子":"未","未":"子","丑":"午","午":"丑",
    "寅":"巳","巳":"寅","卯":"辰","辰":"卯",
    "申":"亥","亥":"申","酉":"戌","戌":"酉"
}

# ─── 地支三刑 ────────────────────────────────────────────────────────────────
# 无礼之刑、无恩之刑、持势之刑、自刑
DIZHI_SANXING = {
    "寅":{"刑":"巳","type":"无恩之刑"},
    "巳":{"刑":"申","type":"无恩之刑"},
    "申":{"刑":"寅","type":"无恩之刑"},
    "丑":{"刑":"戌","type":"无礼之刑"},
    "戌":{"刑":"未","type":"无礼之刑"},
    "未":{"刑":"丑","type":"无礼之刑"},
    "子":{"刑":"卯","type":"持势之刑"},
    "卯":{"刑":"子","type":"持势之刑"},
    "辰":{"刑":"辰","type":"自刑"},
    "午":{"刑":"午","type":"自刑"},
    "酉":{"刑":"酉","type":"自刑"},
    "亥":{"刑":"亥","type":"自刑"},
}

# ─── 十二长生（以天干为基准，地支为状态）────────────────────────────────────
# 阳干顺行，阴干逆行
CHANG_SHENG_YANG = ["长生","沐浴","冠带","临官","帝旺","衰","病","死","墓","绝","胎","养"]
CHANG_SHENG_START = {
    # 阳干起始地支（长生之地）
    "甲":"亥","丙":"寅","戊":"寅","庚":"巳","壬":"申",
    # 阴干起始地支（长生之地，逆行）
    "乙":"午","丁":"酉","己":"酉","辛":"子","癸":"卯"
}

def get_changsheng(tg: str, dz: str) -> str:
    """计算天干在某地支的十二长生状态"""
    if tg not in CHANG_SHENG_START:
        return "未知"
    start_dz = CHANG_SHENG_START[tg]
    start_idx = DIZHI.index(start_dz)
    curr_idx  = DIZHI.index(dz)
    yy = TIANGAN_YY.get(tg, "阳")
    if yy == "阳":
        step = (curr_idx - start_idx) % 12
    else:
        step = (start_idx - curr_idx) % 12
    return CHANG_SHENG_YANG[step]

# 十二长生强弱评分
CHANGSHENG_SCORE = {
    "长生":8,"沐浴":4,"冠带":6,"临官":9,"帝旺":10,
    "衰":5,"病":3,"死":2,"墓":4,"绝":1,"胎":2,"养":5
}

# ─── 旺相休囚死（五行在四季的强弱）─────────────────────────────────────────
# 月份 -> 当令五行（旺）
MONTH_WANG = {
    1:"水",2:"水",3:"木",4:"木",5:"木",6:"火",
    7:"火",8:"火",9:"土",10:"金",11:"金",12:"水"
}
WANGXIANG_TABLE = {
    # (当令五行, 测算五行) -> 状态
    "木":{"木":"旺","火":"相","土":"死","金":"囚","水":"休"},
    "火":{"火":"旺","土":"相","金":"死","水":"囚","木":"休"},
    "土":{"土":"旺","金":"相","水":"死","木":"囚","火":"休"},
    "金":{"金":"旺","水":"相","木":"死","火":"囚","土":"休"},
    "水":{"水":"旺","木":"相","火":"死","土":"囚","金":"休"},
}
WANGXIANG_SCORE = {"旺":10,"相":8,"休":5,"囚":3,"死":1}

# ─── 核心神煞 ────────────────────────────────────────────────────────────────
# 天乙贵人（以日干查）
TIANYI_GUIREN = {
    "甲":["丑","未"],"乙":["子","申"],"丙":["亥","酉"],"丁":["亥","酉"],
    "戊":["丑","未"],"己":["子","申"],"庚":["丑","未"],"辛":["寅","午"],
    "壬":["卯","巳"],"癸":["卯","巳"]
}
# 文昌贵人（以日干查）
WENCHANG = {
    "甲":"巳","乙":"午","丙":"申","丁":"酉","戊":"申",
    "己":"酉","庚":"亥","辛":"子","壬":"寅","癸":"卯"
}
# 驿马（以年支/日支查三合局冲）
YIMA = {"申":"寅","子":"寅","辰":"寅","寅":"申","午":"申","戌":"申",
        "亥":"巳","卯":"巳","未":"巳","巳":"亥","酉":"亥","丑":"亥"}
# 桃花（以年支/日支查）
TAOHUA = {"申":"酉","子":"酉","辰":"酉","寅":"卯","午":"卯","戌":"卯",
          "亥":"子","卯":"子","未":"子","巳":"午","酉":"午","丑":"午"}
# 羊刃（以日干查）
YANGREN = {
    "甲":"卯","乙":"寅","丙":"午","丁":"巳","戊":"午",
    "己":"巳","庚":"酉","辛":"申","壬":"子","癸":"亥"
}
# 魁罡（特定干支组合）
KUIGANG = {"庚辰","庚戌","壬辰","戊戌"}


# ═══════════════════════════════════════════════════════════════════════════════
# 实验定义
# ═══════════════════════════════════════════════════════════════════════════════
EXPERIMENTS = [
    {"id":"cbc_analysis","icon":"🔬","title":"血常规智能解读",
     "desc":"自动分析最新血常规数据，识别异常模式，评估免疫状态与贫血风险。",
     "tags":["血液","免疫","贫血"],"color":"#4F8EF7"},
    {"id":"trend_12m","icon":"📈","title":"12个月健康趋势分析",
     "desc":"对比过去12个月的关键指标变化，识别上升/下降趋势，预测潜在风险。",
     "tags":["趋势","预测","时序"],"color":"#2ECC71"},
    {"id":"allergy_correlation","icon":"🌿","title":"过敏原与指标相关性",
     "desc":"分析 IgE、EOS% 等过敏相关指标与症状日志的时间相关性，绘制过敏负荷曲线。",
     "tags":["过敏","IgE","EOS"],"color":"#F39C12"},
    {"id":"bazi_health","icon":"🔮","title":"干支五行健康对撞引擎",
     "desc":"基于完整八字算法（天干生克、地支刑冲、十二长生、神煞），分析五脏系统潜在影响。",
     "tags":["干支","五行","中医"],"color":"#9B59B6"},
    {"id":"intervention_eval","icon":"💊","title":"干预效果追踪评估",
     "desc":"评估用药/饮食/运动干预前后的指标变化，量化干预效果，生成改善报告。",
     "tags":["干预","评估","对比"],"color":"#E74C3C"},
]


def _hex_to_rgb(h: str) -> str:
    h = h.lstrip("#")
    return ",".join(str(int(h[i:i+2], 16)) for i in (0, 2, 4))


def get_ganzhi(year: int):
    base = 1984  # 甲子年
    off = year - base
    return TIANGAN[off % 10], DIZHI[off % 12]


# ═══════════════════════════════════════════════════════════════════════════════
# 深度八字分析核心算法
# ═══════════════════════════════════════════════════════════════════════════════

def deep_bazi_analysis(birth_year: int, curr_year: int, curr_month: int = None,
                        birth_month: int = None, gender: str = "M") -> dict:
    """
    V5.5 三合参完整八字分析（年柱为主，结合当前年月）
    支持：本命原局 + 大运推算 + 流年丙午 三位一体
    返回包含所有分析结果的字典
    """
    if curr_month is None:
        curr_month = datetime.now().month

    b_tg, b_dz = get_ganzhi(birth_year)
    c_tg, c_dz = get_ganzhi(curr_year)

    result = {
        "birth_year": birth_year,
        "curr_year": curr_year,
        "birth_gz": f"{b_tg}{b_dz}",
        "curr_gz": f"{c_tg}{c_dz}",
        "b_tg": b_tg, "b_dz": b_dz,
        "c_tg": c_tg, "c_dz": c_dz,
        "b_wx": TIANGAN_WX[b_tg],
        "c_wx": TIANGAN_WX[c_tg],
    }

    # ── 1. 天干关系分析 ──────────────────────────────────────────────────────
    b_wx = TIANGAN_WX[b_tg]
    c_wx = TIANGAN_WX[c_tg]

    tg_relation = "无特殊关系"
    tg_detail   = ""
    if b_wx == c_wx:
        tg_relation = "比和"
        tg_detail   = f"本命{b_tg}({b_wx})与流年{c_tg}({c_wx})五行相同，比和助旺，精力充沛但需防过亢。"
    elif WX_SHENG[b_wx] == c_wx:
        tg_relation = "本命生流年（泄气）"
        tg_detail   = f"本命{b_tg}({b_wx})生流年{c_tg}({c_wx})，本命元气有所消耗，需注意体力储备。"
    elif WX_SHENG[c_wx] == b_wx:
        tg_relation = "流年生本命（得生）"
        tg_detail   = f"流年{c_tg}({c_wx})生本命{b_tg}({b_wx})，本命得到滋养，整体健康状态有所提升。"
    elif WX_KE[b_wx] == c_wx:
        tg_relation = "本命克流年（耗力）"
        tg_detail   = f"本命{b_tg}({b_wx})克流年{c_tg}({c_wx})，主动消耗，需防过劳伤身。"
    elif WX_KE[c_wx] == b_wx:
        tg_relation = "流年克本命（受克）⚠️"
        tg_detail   = f"流年{c_tg}({c_wx})克本命{b_tg}({b_wx})，本命受压制，是健康风险最高的关系，需重点关注{WX_BODY[b_wx]['organ']}系统。"

    result["tg_relation"] = tg_relation
    result["tg_detail"]   = tg_detail

    # ── 2. 地支关系分析 ──────────────────────────────────────────────────────
    dz_relations = []

    # 六冲
    if DIZHI_CHONG.get(b_dz) == c_dz:
        dz_relations.append({
            "type": "六冲 ⚡",
            "desc": f"本命地支{b_dz}与流年地支{c_dz}相冲，主动荡不安，健康上易有急性变化，需防意外伤病。",
            "severity": "高"
        })

    # 六合
    if DIZHI_LIUHE.get(b_dz) == c_dz:
        he_key = tuple(sorted([b_dz, c_dz]))
        he_wx = next((v for k, v in DIZHI_LIUHE_WX.items() if set(k) == set([b_dz, c_dz])), "")
        dz_relations.append({
            "type": "六合 ✨",
            "desc": f"本命地支{b_dz}与流年地支{c_dz}相合，化{he_wx}，主和谐顺遂，健康状态相对稳定。",
            "severity": "低"
        })

    # 三刑
    xing_info = DIZHI_SANXING.get(b_dz)
    if xing_info and xing_info["刑"] == c_dz:
        dz_relations.append({
            "type": f"三刑（{xing_info['type']}）⚠️",
            "desc": f"本命地支{b_dz}刑流年地支{c_dz}（{xing_info['type']}），主暗疾隐患，易有慢性病发作或手术之象。",
            "severity": "高"
        })

    # 六害
    if DIZHI_LIUHAI.get(b_dz) == c_dz:
        dz_relations.append({
            "type": "六害 ⚠️",
            "desc": f"本命地支{b_dz}与流年地支{c_dz}相害，主暗中受损，健康上需防慢性消耗性疾病。",
            "severity": "中"
        })

    if not dz_relations:
        dz_relations.append({
            "type": "无特殊刑冲",
            "desc": f"本命地支{b_dz}与流年地支{c_dz}无明显刑冲破害关系，地支层面较为平稳。",
            "severity": "低"
        })

    result["dz_relations"] = dz_relations

    # ── 3. 十二长生分析 ──────────────────────────────────────────────────────
    # 以本命天干在流年地支的长生状态
    b_changsheng_in_curr = get_changsheng(b_tg, c_dz)
    b_cs_score = CHANGSHENG_SCORE.get(b_changsheng_in_curr, 5)

    # 以流年天干在本命地支的长生状态
    c_changsheng_in_birth = get_changsheng(c_tg, b_dz)
    c_cs_score = CHANGSHENG_SCORE.get(c_changsheng_in_birth, 5)

    result["b_changsheng"] = b_changsheng_in_curr
    result["b_cs_score"]   = b_cs_score
    result["c_changsheng"] = c_changsheng_in_birth
    result["c_cs_score"]   = c_cs_score

    cs_health_map = {
        "长生": "生命力旺盛，免疫系统较强，适合积极调理。",
        "沐浴": "身体处于更新期，免疫力波动，需防外感。",
        "冠带": "体力充沛，但需防过度消耗。",
        "临官": "精力达到高峰，工作压力大，需防肝火旺盛。",
        "帝旺": "体力最旺，但物极必反，需防心脑血管压力。",
        "衰":   "精力开始下降，需注重补充营养和休息。",
        "病":   "身体较弱，免疫力下降，需积极预防疾病。",
        "死":   "元气最低，需重点调养，避免过度劳累。",
        "墓":   "气机收藏，适合静养，不宜大动。",
        "绝":   "生命力最弱，需格外注意健康，定期体检。",
        "胎":   "处于转变期，新旧交替，健康状态不稳定。",
        "养":   "恢复期，适合调养生息，增强体质。",
    }
    result["cs_health_advice"] = cs_health_map.get(b_changsheng_in_curr, "")

    # ── 4. 旺相休囚死 ────────────────────────────────────────────────────────
    wang_wx = MONTH_WANG.get(curr_month, "水")
    b_wangxiang = WANGXIANG_TABLE.get(wang_wx, {}).get(b_wx, "休")
    b_wx_score  = WANGXIANG_SCORE.get(b_wangxiang, 5)

    result["curr_month_wang"] = wang_wx
    result["b_wangxiang"]     = b_wangxiang
    result["b_wx_score"]      = b_wx_score

    # ── 5. 核心神煞 ──────────────────────────────────────────────────────────
    shensha = []

    # 天乙贵人
    if c_dz in TIANYI_GUIREN.get(b_tg, []):
        shensha.append({"name":"天乙贵人","dz":c_dz,"type":"吉","desc":"流年逢天乙贵人，贵人运强，健康上易得良医良药，利于就医问诊。"})

    # 文昌贵人
    if WENCHANG.get(b_tg) == c_dz:
        shensha.append({"name":"文昌贵人","dz":c_dz,"type":"吉","desc":"流年逢文昌，思维清晰，适合系统学习医学知识，理解力强。"})

    # 驿马
    if YIMA.get(b_dz) == c_dz:
        shensha.append({"name":"驿马","dz":c_dz,"type":"中","desc":"流年逢驿马，主奔波劳碌，需防旅途劳累导致免疫力下降。"})

    # 桃花
    if TAOHUA.get(b_dz) == c_dz:
        shensha.append({"name":"桃花","dz":c_dz,"type":"中","desc":"流年逢桃花，情绪波动较大，需防因情绪影响内分泌系统。"})

    # 羊刃
    if YANGREN.get(b_tg) == c_dz:
        shensha.append({"name":"羊刃","dz":c_dz,"type":"凶","desc":"流年逢羊刃，主刚烈冲动，需防意外伤害、手术、血光之灾，注意安全。"})

    # 魁罡
    gz_str = f"{b_tg}{b_dz}"
    if gz_str in KUIGANG:
        shensha.append({"name":"魁罡","dz":b_dz,"type":"中","desc":"本命坐魁罡，性格刚毅，健康上需防过度劳累和神经系统紧张。"})

    result["shensha"] = shensha

    # ── 6. 综合五行权重计算 ──────────────────────────────────────────────────
    w = {k: 20.0 for k in WX_BODY}

    # 本命天干 +15，地支 +10
    w[b_wx] += 15
    w[DIZHI_WX[b_dz]] += 10

    # 流年天干 +20，地支 +15（流年影响最大）
    w[c_wx] += 20
    w[DIZHI_WX[c_dz]] += 15

    # 流年生本命：被生者 +5
    if WX_SHENG[c_wx] == b_wx:
        w[b_wx] += 5

    # 流年克本命：被克者 -8
    if WX_KE[c_wx] == b_wx:
        w[b_wx] = max(5, w[b_wx] - 8)

    # 长生加权
    w[b_wx] += (b_cs_score - 5) * 0.5

    # 旺相休囚死加权
    w[b_wx] += (b_wx_score - 5) * 0.5

    # 归一化为百分比
    total = sum(w.values())
    w_pct = {k: round(v / total * 100, 1) for k, v in w.items()}
    result["wuxing_weights"] = w_pct

    # ── 7. 承压系统识别 ──────────────────────────────────────────────────────
    # 被克最严重的五行 = 流年克的五行
    ke_wx = WX_KE[c_wx]
    result["dominant_wx"]   = c_wx
    result["ke_wx"]         = ke_wx
    result["ke_body"]       = WX_BODY[ke_wx]
    result["dominant_body"] = WX_BODY[c_wx]

    # ── 8. 十神关系（年干对年干）────────────────────────────────────────────
    shishen = SHISHEN_TABLE.get((b_tg, c_tg), "未知")
    result["shishen"] = shishen
    shishen_health = {
        "比肩": "比肩年：竞争压力大，需防肝气郁结，注意情绪管理。",
        "劫财": "劫财年：财运波动，压力增大，需防脾胃消化问题。",
        "食神": "食神年：饮食旺盛，需防消化系统负担过重，控制饮食。",
        "伤官": "伤官年：思维活跃但易焦虑，需防神经系统紧张和失眠。",
        "偏财": "偏财年：奔波劳碌，需防过度疲劳影响免疫功能。",
        "正财": "正财年：工作稳定，健康状态较好，适合系统调理。",
        "七杀": "七杀年：压力最大，需防心脑血管问题和免疫力下降。",
        "正官": "正官年：责任重大，需防过度劳累，注意肝肾保养。",
        "偏印": "偏印年：思虑过多，需防神经衰弱和消化功能减弱。",
        "正印": "正印年：贵人相助，健康状态较好，适合休养生息。",
    }
    result["shishen_health"] = shishen_health.get(shishen, "")

    # ── 9. 大运推算（V5.5 新增：本命+大运+流年 三位一体）────────────────────
    # 起运岁数：简化统一3岁起运（实际应以节气日数除以三计算）
    qiyun_age = 3
    curr_age = curr_year - birth_year
    b_tg_yy = TIANGAN_YY.get(b_tg, "阳")
    # 阳男阴女顺行，阴男阳女逆行
    is_shun = (gender == "M" and b_tg_yy == "阳") or (gender == "F" and b_tg_yy == "阴")
    dayun_step = (curr_age - qiyun_age) // 10 if curr_age >= qiyun_age else -1

    if dayun_step >= 0:
        # 月令天干索引（简化：以年干天干为基准向后推）
        b_tg_idx = TIANGAN.index(b_tg)
        # 年干对应的月令天干：甲己年正月为丙寅，以年干序号循环推算
        month_tg_base = (b_tg_idx * 2) % 10  # 简化月令天干起始点
        bm = (birth_month or 1) - 1  # 0-based
        if is_shun:
            dy_tg_idx = (month_tg_base + bm + dayun_step + 1) % 10
            dy_dz_idx = (bm + dayun_step + 3) % 12  # 寅月对应地支索引
        else:
            dy_tg_idx = (month_tg_base + bm - dayun_step - 1) % 10
            dy_dz_idx = (bm - dayun_step + 1) % 12
        dayun_tg = TIANGAN[dy_tg_idx]
        dayun_dz = DIZHI[dy_dz_idx]
        dayun_gz = f"{dayun_tg}{dayun_dz}"
        dayun_wx = TIANGAN_WX[dayun_tg]
        dayun_dz_wx = DIZHI_WX[dayun_dz]
        dayun_start = qiyun_age + dayun_step * 10
        dayun_end   = dayun_start + 9

        # 大运对本命的影响
        if WX_KE.get(dayun_wx) == b_wx:
            dayun_impact = "大运克本命（高压山大运）"
        elif WX_SHENG.get(dayun_wx) == b_wx:
            dayun_impact = "大运生本命（得生大运）"
        elif WX_SHENG.get(b_wx) == dayun_wx:
            dayun_impact = "本命生大运（活跃消耗）"
        elif WX_KE.get(b_wx) == dayun_wx:
            dayun_impact = "本命克大运（主动控制）"
        else:
            dayun_impact = "大运与本命同气（比肩大运）"

        result["has_dayun"] = True
        result["dayun_gz"] = dayun_gz
        result["dayun_tg"] = dayun_tg
        result["dayun_dz"] = dayun_dz
        result["dayun_wx"] = dayun_wx
        result["dayun_dz_wx"] = dayun_dz_wx
        result["dayun_impact"] = dayun_impact
        result["dayun_age_range"] = f"{dayun_start}–{dayun_end}岁"
        result["dayun_body"] = WX_BODY.get(dayun_wx, {})
    else:
        result["has_dayun"] = False
        result["dayun_gz"] = "未起运"
        result["dayun_age_range"] = f"将于{qiyun_age}岁起运"
        result["dayun_impact"] = ""

    return result


def compute_collision_risks(result: dict, records: list) -> list:
    """计算体检指标与五行对撞风险"""
    if not records:
        return []

    ke_wx   = result["ke_wx"]
    ke_body = WX_BODY[ke_wx]
    dom_wx  = result["dominant_wx"]

    # 获取最新异常记录
    latest_date = max((r.get("record_date","") for r in records), default="")
    latest = [r for r in records if r.get("record_date") == latest_date]
    abnormal = [r for r in latest if r.get("status") in ("偏高","偏低")]

    risks = []
    for r in abnormal:
        code = r.get("indicator_code","").upper()
        # 找到该指标属于哪个五行
        r_wx = None
        for wx, body_info in WX_BODY.items():
            if code in body_info["indicators"]:
                r_wx = wx
                break

        if r_wx is None:
            continue

        # 风险评级
        if r_wx == ke_wx:
            risk = "🔴 高风险"
            risk_color = "#E74C3C"
            risk_reason = f"该指标属{r_wx}（{WX_BODY[r_wx]['organ']}），正是流年{dom_wx}克{ke_wx}的承压系统"
        elif r_wx == dom_wx:
            risk = "🟡 需关注"
            risk_color = "#F39C12"
            risk_reason = f"该指标属{r_wx}（{WX_BODY[r_wx]['organ']}），与流年旺盛之气同属，需防过亢"
        elif WX_SHENG[r_wx] == ke_wx:
            risk = "🟠 中等风险"
            risk_color = "#E67E22"
            risk_reason = f"该指标属{r_wx}，生{ke_wx}（承压系统），间接影响承压系统"
        else:
            risk = "🟢 低风险"
            risk_color = "#2ECC71"
            risk_reason = f"该指标与当前五行对撞关系较弱"

        risks.append({
            "name": r.get("indicator_name", code),
            "code": code,
            "value": r.get("value"),
            "status": r.get("status",""),
            "wuxing": r_wx or "未知",
            "risk": risk,
            "risk_color": risk_color,
            "risk_reason": risk_reason,
        })

    # 按风险等级排序
    risk_order = {"🔴 高风险":0,"🟠 中等风险":1,"🟡 需关注":2,"🟢 低风险":3}
    risks.sort(key=lambda x: risk_order.get(x["risk"], 4))
    return risks


# ═══════════════════════════════════════════════════════════════════════════════
# 主渲染
# ═══════════════════════════════════════════════════════════════════════════════

def render():
    st.markdown("""
    <div style="display:flex;align-items:center;justify-content:space-between;
         margin-bottom:24px;padding-bottom:16px;border-bottom:1px solid rgba(155,89,182,0.2);">
      <div>
        <div style="font-size:11px;text-transform:uppercase;letter-spacing:0.1em;color:#8892B0;margin-bottom:4px;">LIFE INSIGHT ENGINE</div>
        <div style="font-size:22px;font-weight:700;color:#E8EAF6;">生命洞察引擎</div>
      </div>
      <div style="font-size:11px;color:#9B59B6;letter-spacing:0.05em;">BaZi · Five Elements · AI</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown(
        "<p style='color:#8892B0;margin-top:-10px;'>"
        "Insight Engine — 一键式健康数据深度分析实验室</p>",
        unsafe_allow_html=True,
    )

    tab_lab, tab_bazi, tab_chat, tab_csv, tab_guide = st.tabs([
        "⬡ 一键实验室", "◉ 干支五行对撞", "◎ AI 命理对话", "⊞ CSV 工作台", "⊟ 使用指南"
    ])

    with tab_lab:
        _render_lab()
    with tab_bazi:
        _render_bazi_engine()
    with tab_chat:
        _render_ai_chat()
    with tab_csv:
        _render_csv_workbench()
    with tab_guide:
        _render_guide()


# ─────────────────────────────────────────────────────────────────────────────
# Tab 1：一键实验室
# ─────────────────────────────────────────────────────────────────────────────
def _render_lab():
    user_id = st.session_state.get("auth_user_id")
    profiles = db.get_all_profiles(user_id=user_id) if user_id else []
    if not profiles:
        st.warning("请先在「家庭成员驾驶舱」中添加成员档案。")
        return

    global_pid = st.session_state.get("selected_profile_id")
    default_idx = next((i for i, p in enumerate(profiles) if p["id"] == global_pid), 0)
    profile_labels = [f"{p.get('avatar_emoji','👤')} {p['name']}" for p in profiles]
    sel_label = st.selectbox("分析对象", profile_labels, index=default_idx, key="e_profile_sel")
    profile = next(p for p in profiles if f"{p.get('avatar_emoji','👤')} {p['name']}" == sel_label)
    st.session_state["selected_profile_id"] = profile["id"]

    st.markdown("---")
    st.markdown("#### 选择研究实验")

    cols = st.columns(len(EXPERIMENTS))
    sel_exp_id = st.session_state.get("e_selected_exp", EXPERIMENTS[0]["id"])

    for i, exp in enumerate(EXPERIMENTS):
        with cols[i]:
            is_sel = (exp["id"] == sel_exp_id)
            bc = exp["color"] if is_sel else "#2E3250"
            rgb = _hex_to_rgb(exp["color"])
            bg = f"rgba({rgb},0.10)" if is_sel else "#21253A"
            tags_html = "".join(
                f"<span style='background:rgba({rgb},0.15);color:{exp['color']};"
                f"border-radius:20px;padding:2px 8px;font-size:10px;margin-right:4px;'>{t}</span>"
                for t in exp["tags"]
            )
            st.markdown(
                f"""<div style='background:{bg};border:1.5px solid {bc};border-radius:12px;
                    padding:14px;min-height:150px;'>
                    <div style='font-size:24px;margin-bottom:6px;'>{exp["icon"]}</div>
                    <div style='color:#E8EAF6;font-size:12px;font-weight:700;margin-bottom:6px;'>
                        {exp["title"]}</div>
                    <div style='color:#8892B0;font-size:10px;margin-bottom:8px;line-height:1.4;'>
                        {exp["desc"]}</div>
                    <div>{tags_html}</div>
                </div>""",
                unsafe_allow_html=True,
            )
            if st.button(
                "✓ 已选" if is_sel else "选择",
                key=f"e_sel_{exp['id']}",
                use_container_width=True,
                type="primary" if is_sel else "secondary",
            ):
                st.session_state["e_selected_exp"] = exp["id"]
                for k in ("e_result_text","e_result_figs","e_ai_interp"):
                    st.session_state.pop(k, None)
                st.rerun()

    st.markdown("---")
    cur_exp = next((e for e in EXPERIMENTS if e["id"] == sel_exp_id), EXPERIMENTS[0])
    rgb_cur = _hex_to_rgb(cur_exp["color"])
    st.markdown(
        f"""<div style='background:#21253A;border:1px solid rgba({rgb_cur},0.3);
            border-radius:12px;padding:16px;margin-bottom:16px;'>
            <span style='font-size:20px;'>{cur_exp["icon"]}</span>
            <span style='color:{cur_exp["color"]};font-size:14px;font-weight:700;margin-left:8px;'>
                {cur_exp["title"]}</span>
            <div style='color:#8892B0;font-size:12px;margin-top:6px;'>{cur_exp["desc"]}</div>
        </div>""",
        unsafe_allow_html=True,
    )

    col_run, col_clr = st.columns([3, 1])
    with col_run:
        run_btn = st.button(f"⚗️ 运行：{cur_exp['title']}", type="primary",
                            use_container_width=True, key="e_run_btn")
    with col_clr:
        if st.button("🗑️ 清除", use_container_width=True, key="e_clear"):
            for k in ("e_result_text","e_result_figs","e_ai_interp"):
                st.session_state.pop(k, None)
            st.rerun()

    if run_btn:
        with st.spinner(f"⚗️ 正在执行「{cur_exp['title']}」..."):
            result_text, result_figs = _execute_experiment(sel_exp_id, profile)
        st.session_state["e_result_text"] = result_text
        st.session_state["e_result_figs"] = result_figs
        st.session_state.pop("e_ai_interp", None)
        st.rerun()

    result_text = st.session_state.get("e_result_text")
    result_figs = st.session_state.get("e_result_figs", [])

    if result_text:
        st.markdown("#### 📊 实验结果")
        st.markdown(
            f"""<div style='background:linear-gradient(135deg,#1a2744,#21253A);
                border:1px solid #2E3250;border-radius:12px;padding:20px;margin-bottom:16px;'>
                <div style='color:{cur_exp["color"]};font-size:12px;font-weight:700;
                    letter-spacing:1px;margin-bottom:12px;'>
                    {cur_exp["icon"]} {cur_exp["title"]} — 分析报告</div>""",
            unsafe_allow_html=True,
        )
        st.markdown(result_text)
        st.markdown("</div>", unsafe_allow_html=True)

        if result_figs and PLOTLY_OK:
            for fig in result_figs:
                try:
                    st.plotly_chart(fig, use_container_width=True)
                except Exception:
                    pass

        ai_interp = st.session_state.get("e_ai_interp")
        if st.button("🤖 AI 深度解读结果", type="secondary",
                     use_container_width=True, key="e_ai_btn"):
            with st.spinner("🧠 AI 正在深度解读实验结果...（约 15 秒）"):
                try:
                    from openai import OpenAI
                    if not config.LLM_API_KEY:
                        st.error("❌ 未配置 LLM_API_KEY，请在环境变量或 .streamlit/secrets.toml 中设置。")
                        return
                    client = OpenAI(
                        api_key=config.LLM_API_KEY,
                        base_url=config.LLM_BASE_URL
                    )
                    resp = client.chat.completions.create(
                        model=config.LLM_MODEL,
                        messages=[
                            {"role":"system","content":
                             "你是一位资深医学数据科学家和健康顾问，擅长将数据分析结果转化为通俗易懂的健康洞察。"},
                            {"role":"user","content":
                             f"请对以下健康数据分析结果进行深度解读，给出具体的健康建议和注意事项：\n\n{result_text[:2000]}"}
                        ],
                        max_tokens=1000, temperature=config.LLM_TEMPERATURE,
                    )
                    ai_interp = resp.choices[0].message.content
                    st.session_state["e_ai_interp"] = ai_interp
                except Exception as e:
                    ai_interp = f"AI 解读暂时不可用：{e}"
                    st.session_state["e_ai_interp"] = ai_interp
                st.rerun()

        if ai_interp:
            st.markdown(
                """<div style='background:#1A2744;border:1px solid #4F8EF744;
                    border-radius:12px;padding:20px;margin-top:12px;'>
                    <div style='color:#4F8EF7;font-size:12px;font-weight:700;
                        margin-bottom:12px;'>🤖 AI 深度解读</div>""",
                unsafe_allow_html=True,
            )
            st.markdown(ai_interp)
            st.markdown("</div>", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# Tab 2：干支五行对撞引擎（深度版）
# ─────────────────────────────────────────────────────────────────────────────
def _render_bazi_engine():
    st.markdown("""
    <div style='margin-bottom:20px;'>
      <div style='font-size:11px;text-transform:uppercase;letter-spacing:0.12em;
           color:#8892B0;margin-bottom:4px;'>BAZI ENGINE V5.5</div>
      <div style='font-size:20px;font-weight:700;color:#E8EAF6;
           letter-spacing:0.02em;'>干支五行健康对撞引擎</div>
      <div style='font-size:12px;color:#6B7280;margin-top:4px;'>
        本命原局 · 大运推算 · 流年丙午 — 三位一体分析</div>
    </div>
    """, unsafe_allow_html=True)

    user_id = st.session_state.get("auth_user_id")
    profiles = db.get_all_profiles(user_id=user_id) if user_id else []
    if not profiles:
        st.warning("请先添加成员档案。")
        return

    global_pid = st.session_state.get("selected_profile_id")
    default_idx = next((i for i, p in enumerate(profiles) if p["id"] == global_pid), 0)
    profile_labels = [f"{p.get('avatar_emoji','👤')} {p['name']}" for p in profiles]
    sel_label = st.selectbox("分析对象", profile_labels, index=default_idx, key="bazi_profile_sel")
    profile = next(p for p in profiles if f"{p.get('avatar_emoji','👤')} {p['name']}" == sel_label)

    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        birth_year = st.number_input("出生年份", min_value=1900, max_value=2010,
                                     value=int(profile.get("birth_year") or 1985),
                                     step=1, key="bazi_birth_year")
    with col2:
        birth_month = st.selectbox("出生月份",
                                   list(range(1,13)),
                                   index=0, key="bazi_birth_month")
    with col3:
        gender_sel = st.selectbox("性别",
                                  ["男", "女"],
                                  index=0 if (profile.get("gender") or "M") == "M" else 1,
                                  key="bazi_gender")
        gender = "M" if gender_sel == "男" else "F"
    with col4:
        curr_year = st.number_input("流年（当前年）", min_value=2020, max_value=2050,
                                    value=datetime.now().year, step=1, key="bazi_curr_year")
    with col5:
        curr_month = st.selectbox("当前月份",
                                  list(range(1,13)),
                                  index=datetime.now().month - 1,
                                  key="bazi_curr_month")

    col_run, col_clr = st.columns([3, 1])
    with col_run:
        run_bazi = st.button("执行完整八字健康分析", type="primary",
                             use_container_width=True, key="bazi_run")
    with col_clr:
        if st.button("清除结果", use_container_width=True, key="bazi_clear"):
            for k in ("bazi_result","bazi_risks","bazi_ai"):
                st.session_state.pop(k, None)
            st.rerun()

    if run_bazi:
        with st.spinner("正在执行三合参八字分析..."):
            records = db.get_records(profile["id"]) or []
            result = deep_bazi_analysis(
                int(birth_year), int(curr_year), int(curr_month),
                birth_month=int(birth_month), gender=gender
            )
            risks  = compute_collision_risks(result, records)
            st.session_state["bazi_result"] = result
            st.session_state["bazi_risks"]  = risks
            st.session_state.pop("bazi_ai", None)
        st.rerun()

    result = st.session_state.get("bazi_result")
    if not result:
        st.info("请设置出生年份和当前年份，点击「执行完整八字健康分析」开始分析。")
        return

    risks = st.session_state.get("bazi_risks", [])

    # ── 基本信息卡 ──────────────────────────────────────────────────────────
    b_body = WX_BODY[result["b_wx"]]
    c_body = WX_BODY[result["c_wx"]]
    ke_body = result["ke_body"]

    st.markdown(
        f"""<div style='background:linear-gradient(135deg,#1a1d27,#21253A);
            border:1px solid #9B59B6;border-radius:14px;padding:20px;margin-bottom:16px;'>
            <div style='display:grid;grid-template-columns:1fr 1fr 1fr;gap:16px;'>
                <div style='text-align:center;'>
                    <div style='color:#8892B0;font-size:11px;margin-bottom:4px;'>本命年柱</div>
                    <div style='color:#E8EAF6;font-size:28px;font-weight:700;'>{result["birth_gz"]}</div>
                    <div style='color:{b_body["color"]};font-size:13px;'>
                        {result["b_wx"]} · {b_body["organ"]}</div>
                    <div style='color:#8892B0;font-size:11px;margin-top:4px;'>
                        长生：{result["b_changsheng"]}（{result["b_cs_score"]}分）</div>
                    <div style='color:#8892B0;font-size:11px;'>
                        旺相：{result["b_wangxiang"]}（{result["b_wx_score"]}分）</div>
                </div>
                <div style='text-align:center;border-left:1px solid #2E3250;border-right:1px solid #2E3250;'>
                    <div style='color:#8892B0;font-size:11px;margin-bottom:4px;'>天干关系</div>
                    <div style='color:#F39C12;font-size:16px;font-weight:700;margin-bottom:4px;'>
                        {result["tg_relation"]}</div>
                    <div style='color:#8892B0;font-size:11px;margin-bottom:8px;'>
                        十神：{result["shishen"]}</div>
                    <div style='color:#8892B0;font-size:11px;margin-bottom:4px;'>承压系统</div>
                    <div style='color:{ke_body["color"]};font-size:16px;font-weight:700;'>
                        {result["ke_wx"]} · {ke_body["organ"]}</div>
                </div>
                <div style='text-align:center;'>
                    <div style='color:#8892B0;font-size:11px;margin-bottom:4px;'>流年年柱</div>
                    <div style='color:#E8EAF6;font-size:28px;font-weight:700;'>{result["curr_gz"]}</div>
                    <div style='color:{c_body["color"]};font-size:13px;'>
                        {result["c_wx"]} · {c_body["organ"]}</div>
                    <div style='color:#8892B0;font-size:11px;margin-top:4px;'>
                        长生：{result["c_changsheng"]}（{result["c_cs_score"]}分）</div>
                    <div style='color:#8892B0;font-size:11px;'>
                        当月令：{result["curr_month_wang"]}旺</div>
                </div>
            </div>
        </div>""",
        unsafe_allow_html=True,
    )

    # ── 大运信息卡（V5.5 新增）────────────────────────────────────────────
    if result.get("has_dayun"):
        dy_body = result.get("dayun_body", {})
        st.markdown(
            f"""
            <div style='background:#161618;border:1px solid #2D2D30;border-radius:12px;
                 padding:16px 20px;margin-bottom:16px;'>
              <div style='display:flex;align-items:center;gap:16px;flex-wrap:wrap;'>
                <div style='min-width:120px;'>
                  <div style='font-size:10px;text-transform:uppercase;letter-spacing:0.1em;
                       color:#6B7280;margin-bottom:4px;'>CURRENT MAJOR LUCK</div>
                  <div style='font-size:26px;font-weight:700;color:#E8EAF6;
                       font-family:"JetBrains Mono",monospace;letter-spacing:0.05em;'>
                       {result["dayun_gz"]}</div>
                  <div style='font-size:11px;color:#8892B0;margin-top:2px;'>
                       {result["dayun_age_range"]}</div>
                </div>
                <div style='flex:1;border-left:1px solid #2D2D30;padding-left:16px;'>
                  <div style='font-size:11px;color:#6B7280;margin-bottom:6px;'>大运五行</div>
                  <div style='font-size:14px;color:{dy_body.get("color","#E8EAF6")};
                       font-weight:600;'>{result["dayun_wx"]} • {dy_body.get("organ","")}</div>
                  <div style='font-size:12px;color:#8892B0;margin-top:4px;'>{result["dayun_impact"]}</div>
                </div>
              </div>
            </div>""",
            unsafe_allow_html=True,
        )

    # ── 五行权重可视化 ───────────────────────────────────────────────────
    st.markdown("#### 五行能量权重分布")
    if PLOTLY_OK:
        w = result["wuxing_weights"]
        wx_list = list(w.keys())
        wx_vals = list(w.values())
        wx_colors = [WX_BODY[wx]["color"] for wx in wx_list]

        col_radar, col_bar = st.columns(2)
        with col_radar:
            fig_r = go.Figure(go.Scatterpolar(
                r=wx_vals + [wx_vals[0]],
                theta=[f"{wx}\n{WX_BODY[wx]['organ']}" for wx in wx_list] + [f"{wx_list[0]}\n{WX_BODY[wx_list[0]]['organ']}"],
                fill="toself",
                fillcolor="rgba(155,89,182,0.15)",
                line=dict(color="#9B59B6", width=2),
                marker=dict(size=6, color="#9B59B6"),
            ))
            fig_r.update_layout(
                polar=dict(
                    radialaxis=dict(visible=True, range=[0,50], tickfont=dict(color="#8892B0",size=9),
                                   gridcolor="#2E3250"),
                    angularaxis=dict(tickfont=dict(color="#E8EAF6",size=10), gridcolor="#2E3250"),
                    bgcolor="#1A1D27",
                ),
                paper_bgcolor="#1A1D27", height=280,
                margin=dict(l=30,r=30,t=20,b=20),
                showlegend=False,
            )
            st.plotly_chart(fig_r, use_container_width=True)

        with col_bar:
            fig_b = go.Figure(go.Bar(
                x=wx_list, y=wx_vals,
                marker_color=wx_colors,
                text=[f"{v}%" for v in wx_vals],
                textposition="outside",
                textfont=dict(color="#E8EAF6", size=11),
            ))
            fig_b.update_layout(
                paper_bgcolor="#1A1D27", plot_bgcolor="#1A1D27",
                xaxis=dict(tickfont=dict(color="#E8EAF6",size=12), gridcolor="#2E3250"),
                yaxis=dict(tickfont=dict(color="#8892B0",size=9), gridcolor="#2E3250",
                           title="能量权重 %"),
                height=280, margin=dict(l=20,r=20,t=20,b=20),
                showlegend=False,
            )
            st.plotly_chart(fig_b, use_container_width=True)

    # ── 天干关系详解 ─────────────────────────────────────────────────────────
    st.markdown("#### 天干生克关系")
    tg_color = "#E74C3C" if "受克" in result["tg_relation"] or "耗力" in result["tg_relation"] else \
               "#2ECC71" if "得生" in result["tg_relation"] else "#F39C12"
    st.markdown(
        f"""<div style='background:#21253A;border-left:4px solid {tg_color};
            border-radius:0 10px 10px 0;padding:14px 18px;margin-bottom:12px;'>
            <div style='color:{tg_color};font-weight:700;margin-bottom:6px;'>
                {result["tg_relation"]} · 十神：{result["shishen"]}</div>
            <div style='color:#8892B0;font-size:13px;line-height:1.6;'>{result["tg_detail"]}</div>
            <div style='color:#8892B0;font-size:12px;margin-top:6px;'>{result["shishen_health"]}</div>
        </div>""",
        unsafe_allow_html=True,
    )

    # ── 地支刑冲破害 ─────────────────────────────────────────────────────────
    st.markdown("#### 地支刑冲破害合")
    for rel in result["dz_relations"]:
        sev_color = "#E74C3C" if rel["severity"]=="高" else \
                    "#F39C12" if rel["severity"]=="中" else "#2ECC71"
        st.markdown(
            f"""<div style='background:#21253A;border-left:4px solid {sev_color};
                border-radius:0 10px 10px 0;padding:12px 16px;margin-bottom:8px;'>
                <div style='color:{sev_color};font-weight:700;margin-bottom:4px;'>
                    {rel["type"]} · 风险：{rel["severity"]}</div>
                <div style='color:#8892B0;font-size:13px;'>{rel["desc"]}</div>
            </div>""",
            unsafe_allow_html=True,
        )

    # ── 十二长生与旺相休囚 ───────────────────────────────────────────────────
    st.markdown("#### 十二长生 · 旺相休囚死")
    cs_color = "#2ECC71" if result["b_cs_score"] >= 7 else \
               "#F39C12" if result["b_cs_score"] >= 4 else "#E74C3C"
    wx_color = "#2ECC71" if result["b_wx_score"] >= 8 else \
               "#F39C12" if result["b_wx_score"] >= 5 else "#E74C3C"
    col_cs, col_wx = st.columns(2)
    with col_cs:
        st.markdown(
            f"""<div style='background:#21253A;border-radius:10px;padding:14px;text-align:center;'>
                <div style='color:#8892B0;font-size:11px;margin-bottom:4px;'>本命天干在流年地支</div>
                <div style='color:{cs_color};font-size:22px;font-weight:700;'>
                    {result["b_changsheng"]}</div>
                <div style='color:#8892B0;font-size:12px;margin-top:6px;'>
                    {result["cs_health_advice"]}</div>
            </div>""",
            unsafe_allow_html=True,
        )
    with col_wx:
        st.markdown(
            f"""<div style='background:#21253A;border-radius:10px;padding:14px;text-align:center;'>
                <div style='color:#8892B0;font-size:11px;margin-bottom:4px;'>本命五行当月旺相状态</div>
                <div style='color:{wx_color};font-size:22px;font-weight:700;'>
                    {result["b_wangxiang"]}</div>
                <div style='color:#8892B0;font-size:12px;margin-top:6px;'>
                    当月令：{result["curr_month_wang"]}旺，本命{result["b_wx"]}处于{result["b_wangxiang"]}状态</div>
            </div>""",
            unsafe_allow_html=True,
        )

    # ── 核心神煞 ─────────────────────────────────────────────────────────────
    if result["shensha"]:
        st.markdown("#### 核心神煞")
        shensha_cols = st.columns(min(len(result["shensha"]), 4))
        for i, ss in enumerate(result["shensha"]):
            ss_color = "#2ECC71" if ss["type"]=="吉" else \
                       "#E74C3C" if ss["type"]=="凶" else "#F39C12"
            with shensha_cols[i % len(shensha_cols)]:
                st.markdown(
                    f"""<div style='background:#21253A;border:1px solid {ss_color}44;
                        border-radius:10px;padding:12px;text-align:center;margin-bottom:8px;'>
                        <div style='color:{ss_color};font-size:14px;font-weight:700;'>
                            {ss["name"]}</div>
                        <div style='color:#8892B0;font-size:10px;margin-top:4px;'>
                            {ss["type"]} · {ss["dz"]}</div>
                        <div style='color:#8892B0;font-size:10px;margin-top:6px;line-height:1.4;'>
                            {ss["desc"]}</div>
                    </div>""",
                    unsafe_allow_html=True,
                )

    # ── 体检指标对撞风险 ─────────────────────────────────────────────────────
    st.markdown("#### 体检指标五行对撞风险")
    if risks:
        for r in risks:
            st.markdown(
                f"""<div style='background:#21253A;border-left:4px solid {r["risk_color"]};
                    border-radius:0 10px 10px 0;padding:12px 16px;margin-bottom:8px;'>
                    <div style='display:flex;justify-content:space-between;align-items:center;'>
                        <div>
                            <span style='color:#E8EAF6;font-weight:700;'>{r["name"]}</span>
                            <span style='color:#8892B0;font-size:12px;margin-left:8px;'>
                                ({r["code"]}) · {r["status"]}</span>
                        </div>
                        <span style='background:rgba(0,0,0,0.3);color:{r["risk_color"]};
                            border-radius:20px;padding:3px 12px;font-size:12px;font-weight:700;'>
                            {r["risk"]}</span>
                    </div>
                    <div style='color:#8892B0;font-size:12px;margin-top:4px;'>
                        五行：{r["wuxing"]} — {WX_BODY.get(r["wuxing"],{}).get("organ","未知")}系统</div>
                    <div style='color:#8892B0;font-size:11px;margin-top:2px;'>
                        {r["risk_reason"]}</div>
                </div>""",
                unsafe_allow_html=True,
            )
    else:
        st.info("当前无异常指标，或暂无体检数据。请先录入体检记录。")

    # ── AI 深度解读 ──────────────────────────────────────────────────────────
    st.markdown("---")
    col_ai, col_regen = st.columns([3, 1])
    with col_ai:
        ai_run = st.button("DeepSeek 三合参健康深度解读", type="primary",
                           use_container_width=True, key="bazi_ai_run")
    with col_regen:
        if st.button("重新生成", use_container_width=True, key="bazi_ai_regen"):
            st.session_state.pop("bazi_ai", None)
            st.rerun()

    cached_ai = st.session_state.get("bazi_ai")

    if ai_run and not cached_ai:
        age = datetime.now().year - int(result.get("birth_year") or 1985)
        gender_str = "男" if profile.get("gender") == "M" else "女"
        dayun_info = ""
        if result.get("has_dayun"):
            dayun_info = (
                f"当前大运：{result['dayun_gz']}（{result['dayun_age_range']}）\n"
                f"大运五行：{result['dayun_wx']} · {result.get('dayun_dz_wx','')}\n"
                f"大运影响：{result['dayun_impact']}\n"
            )
        with st.spinner("DeepSeek 正在融合三合参（本命+大运+流年）进行深度分析...（约 20 秒）"):
            try:
                from openai import OpenAI
                if not config.LLM_API_KEY:
                    st.error("❌ 未配置 LLM_API_KEY，请在环境变量或 .streamlit/secrets.toml 中设置。")
                    return
                client = OpenAI(
                    api_key=config.LLM_API_KEY,
                    base_url=config.LLM_BASE_URL
                )
                risks_summary = json.dumps(
                    [{"\u6307\u6807":r["name"],"\u72b6\u6001":r["status"],"\u4e94\u884c":r["wuxing"],"\u98ce\u9669":r["risk"]} for r in risks],
                    ensure_ascii=False
                )
                prompt = (
                    f"请以子平八字三合参理论结合现代医学，为以下用户生成完整健康分析报告：\n\n"
                    f"【本命原局】年柱：{result['birth_gz']}（{result['b_wx']}，{b_body['organ']}）\n"
                    f"用户：{profile.get('name')}，{age}岁，{gender_str}\n\n"
                    f"【当前大运】{dayun_info or '未起运'}\n\n"
                    f"【流年丙午】年柱：{result['curr_gz']}（{result['c_wx']}，{c_body['organ']}）\n"
                    f"天干关系：{result['tg_relation']}（十神：{result['shishen']}）\n"
                    f"地支关系：{'; '.join(r['type'] for r in result['dz_relations'])}\n"
                    f"十二长生：本命天干在流年地支为「{result['b_changsheng']}」\n"
                    f"旺相休囚：本命五行当月为「{result['b_wangxiang']}」\n"
                    f"神煞：{', '.join(ss['name'] for ss in result['shensha']) or '无特殊神煞'}\n"
                    f"承压系统：{result['ke_wx']}（{ke_body['organ']}）\n\n"
                    f"【体检异常指标】{risks_summary}\n\n"
                    f"请输出：\n"
                    f"1. 本命+大运+流年三合参综合健康判断\n"
                    f"2. 流年丙午火旺，对本命五行的具体充冲（呼吸系统、心脏负荷等）\n"
                    f"3. 承压脏腔系统的具体风险（结合异常指标）\n"
                    f"4. 饮食/作息/运动的个性化建议（五行补泻原则）\n"
                    f"5. 现代医学视角的补充建议\n"
                    f"语言专业但通俗，避免过度玄学化。"
                )
                resp = client.chat.completions.create(
                    model="deepseek-chat",
                    messages=[
                        {"role":"system","content":
                         "你是一位精通子平八字与现代病理学的跨界医学专家，"
                         "尤其擅长本命原局+大运+流年三合参分析。"},
                        {"role":"user","content": prompt}
                    ],
                    max_tokens=2000, temperature=0.7,
                )
                cached_ai = resp.choices[0].message.content
                st.session_state["bazi_ai"] = cached_ai
            except Exception as e:
                try:
                    from openai import OpenAI as OAI
                    client2 = OAI()
                    resp2 = client2.chat.completions.create(
                        model="gemini-2.5-flash",
                        messages=[
                            {"role":"system","content":"你是一位精通子平八字与现代病理学的跨界医学专家。"},
                            {"role":"user","content": prompt}
                        ],
                        max_tokens=2000, temperature=0.7,
                    )
                    cached_ai = resp2.choices[0].message.content
                except Exception as e2:
                    cached_ai = f"AI 解读暂时不可用。DeepSeek 错误：{e}"
                st.session_state["bazi_ai"] = cached_ai
        st.rerun()

    if cached_ai:
        st.markdown(
            """<div style='background:linear-gradient(135deg,#1a1d27,#21253A);
                border:1px solid #9B59B6;border-radius:14px;padding:20px;margin-top:12px;'>
                <div style='color:#9B59B6;font-size:12px;font-weight:700;
                    letter-spacing:1px;margin-bottom:14px;'>
                    DeepSeek 三合参健康深度解读（本命+大运+流年丙午）</div>""",
            unsafe_allow_html=True,
        )
        st.markdown(cached_ai)
        st.markdown("</div>", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# Tab 2.5：AI 命理对话（持久化存储）
# ─────────────────────────────────────────────────────────────────────────────
def _render_ai_chat():
    """生命洞察 AI 对话界面：持久化存储，支持跨会话查看。"""
    import uuid
    import database as db
    import auth

    st.markdown("""
    <div style='background:linear-gradient(135deg,#1a1d27,#21253A);
        border:1px solid rgba(155,89,182,0.3);border-radius:14px;
        padding:20px;margin-bottom:20px;'>
        <div style='color:#9B59B6;font-size:12px;font-weight:700;
            letter-spacing:1px;margin-bottom:8px;'>AI 命理对话室</div>
        <div style='color:#8892B0;font-size:13px;line-height:1.6;'>
            我是一位精通子平八字与现代病理学的跨界医学专家。
            请将您的健康困惑、体检指标或命理问题告诉我，
            我将结合干支五行与现代医学给出深度分析。
            <strong style='color:#9B59B6;'>对话记录将永久保存，下次登录可继续查看。</strong>
        </div>
    </div>
    """, unsafe_allow_html=True)

    user_id = auth.get_current_user_id()
    if not user_id:
        st.warning("请先登录。")
        return

    # ── 会话管理 ─────────────────────────────────────────────────────────────────────────────
    sessions = db.get_ai_sessions(user_id, session_type="bazi", limit=10)
    session_options = {"+ 新建对话": "__new__"}
    for s in sessions:
        ts = s.get("last_updated", "")[:16]
        preview = s.get("preview", "无预览")
        session_options[f"{ts} | {preview[:20]}"] = s["session_id"]

    col_sel, col_new = st.columns([4, 1])
    with col_sel:
        sel_key = st.selectbox("选择对话", list(session_options.keys()), key="e_chat_session_sel")
    with col_new:
        if st.button("新建", use_container_width=True, key="e_chat_new"):
            st.session_state["e_chat_session_id"] = str(uuid.uuid4())
            st.rerun()

    if sel_key == "+ 新建对话":
        if "e_chat_session_id" not in st.session_state:
            st.session_state["e_chat_session_id"] = str(uuid.uuid4())
        session_id = st.session_state["e_chat_session_id"]
    else:
        session_id = session_options[sel_key]
        st.session_state["e_chat_session_id"] = session_id

    # ── 加载历史消息 ──────────────────────────────────────────────────────────────────────────
    history_msgs = db.get_ai_conversation(user_id, session_id)

    # ── 显示历史消息 ──────────────────────────────────────────────────────────────────────────
    chat_container = st.container()
    with chat_container:
        if not history_msgs:
            st.markdown(
                "<div style='text-align:center;color:#4A5568;padding:40px;'>"
                "对话记录为空，请在下方输入您的问题开始对话。</div>",
                unsafe_allow_html=True
            )
        for msg in history_msgs:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            ts = msg.get("created_at", "")[:16]
            if role == "user":
                st.markdown(
                    f"""<div style='display:flex;justify-content:flex-end;margin:8px 0;'>
                        <div style='background:#1e3a5f;border:1px solid #2E5090;
                            border-radius:12px 12px 2px 12px;padding:12px 16px;
                            max-width:75%;'>
                            <div style='color:#E8EAF6;font-size:13px;line-height:1.6;'>{content}</div>
                            <div style='color:#4A5568;font-size:10px;margin-top:4px;text-align:right;'>{ts}</div>
                        </div>
                    </div>""",
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    f"""<div style='display:flex;justify-content:flex-start;margin:8px 0;'>
                        <div style='background:#1a1d27;border:1px solid rgba(155,89,182,0.3);
                            border-radius:2px 12px 12px 12px;padding:12px 16px;
                            max-width:80%;'>
                            <div style='color:#9B59B6;font-size:10px;font-weight:700;
                                margin-bottom:6px;letter-spacing:0.5px;'>AI 命理医学专家</div>
                            <div style='color:#E8EAF6;font-size:13px;line-height:1.8;'>{content}</div>
                            <div style='color:#4A5568;font-size:10px;margin-top:4px;'>{ts}</div>
                        </div>
                    </div>""",
                    unsafe_allow_html=True
                )
    # ── 输入区域 ────────────────────────────────────────────────────────────────────────────────────
    st.markdown("---")

    # 发送后清空输入框：检查标志位
    if st.session_state.get("e_chat_just_sent"):
        st.session_state["e_chat_just_sent"] = False
        default_input = ""
    else:
        default_input = st.session_state.get("e_chat_draft", "")

    user_input = st.text_area(
        "向 AI 命理医学专家提问",
        value=default_input,
        placeholder="例如：我的尿酸偏高，干支分析显示水局偏重，应该如何调节？",
        height=100,
        key="e_chat_input"
    )
    # 实时同步草稿到 session_state
    if user_input != default_input:
        st.session_state["e_chat_draft"] = user_input

    col_send, col_clear = st.columns([4, 1])
    with col_send:
        send_btn = st.button("发送问题", type="primary", use_container_width=True, key="e_chat_send")
    with col_clear:
        if st.button("清空对话", use_container_width=True, key="e_chat_clear"):
            db.delete_ai_session(user_id, session_id)
            st.session_state.pop("e_chat_session_id", None)
            st.session_state["e_chat_draft"] = ""
            st.rerun()

    if send_btn and user_input.strip():
        user_msg = user_input.strip()
        # 保存用户消息
        db.save_ai_message(user_id, session_id, "user", user_msg)

        # 构建上下文（最近10轮对话）
        recent = db.get_ai_conversation(user_id, session_id)
        messages = [
            {"role": "system", "content":
             "你是一位精通子平八字与现代病理学的跨界医学专家。"
             "你精通天干地支、五行生克、十二长生、旺相休囚死、神煞分析，"
             "同时具备现代医学知识。"
             "请结合用户的具体问题，给出深度、科学、实用的分析和建议。"
             "回答用中文，语言专业但不晦涩。"}
        ]
        for m in recent[:-1]:  # 排除刚才发送的用户消息
            messages.append({"role": m["role"], "content": m["content"]})
        messages.append({"role": "user", "content": user_msg})

        with st.spinner("命理医学专家正在思考中..."):
            try:
                from openai import OpenAI
                if not config.LLM_API_KEY:
                    st.error("❌ 未配置 LLM_API_KEY，请在环境变量或 .streamlit/secrets.toml 中设置。")
                    return
                client = OpenAI(
                    api_key=config.LLM_API_KEY,
                    base_url=config.LLM_BASE_URL
                )
                resp = client.chat.completions.create(
                    model=config.LLM_MODEL,
                    messages=messages,
                    max_tokens=2000,
                    temperature=config.LLM_TEMPERATURE,
                )
                ai_reply = resp.choices[0].message.content
            except Exception as e1:
                # 备用：Gemini 2.5 Flash
                try:
                    from openai import OpenAI as OAI
                    client2 = OAI()
                    resp2 = client2.chat.completions.create(
                        model="gemini-2.5-flash",
                        messages=messages,
                        max_tokens=2000,
                        temperature=0.75,
                    )
                    ai_reply = resp2.choices[0].message.content
                except Exception as e2:
                    ai_reply = f"暂时无法连接 AI。主要错误：{e1}"

        # 保存 AI 回复
        db.save_ai_message(user_id, session_id, "assistant", ai_reply)
        # 清空输入框：直接删除 widget key，下次渲染时 Streamlit 会用 value="" 重新初始化
        st.session_state.pop("e_chat_input", None)
        st.session_state["e_chat_draft"] = ""
        st.session_state["e_chat_just_sent"] = True
        st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
# Tab 3：CSV 工作台
# ─────────────────────────────────────────────────────────────────────────────
def _render_csv_workbench():
    st.markdown("### 📊 CSV 数据工作台")
    st.markdown(
        "<p style='color:#8892B0;font-size:13px;'>上传体检 CSV 文件，系统自动解析并生成可视化报告。</p>",
        unsafe_allow_html=True,
    )

    uploaded = st.file_uploader("上传 CSV 文件", type=["csv"], key="e_csv_upload")
    if not uploaded:
        st.info("请上传 CSV 格式的体检数据文件。支持标准血常规/生化检验格式。")
        return

    try:
        import pandas as pd
        df = pd.read_csv(uploaded)
        st.markdown(f"**已加载数据：{df.shape[0]} 行 × {df.shape[1]} 列**")
        st.dataframe(df.head(20), use_container_width=True)

        if PLOTLY_OK:
            numeric_cols = df.select_dtypes(include="number").columns.tolist()
            if numeric_cols:
                sel_col = st.selectbox("选择可视化列", numeric_cols, key="e_csv_col")
                fig = px.histogram(df, x=sel_col, nbins=20,
                                   color_discrete_sequence=["#4F8EF7"])
                fig.update_layout(
                    paper_bgcolor="#1A1D27", plot_bgcolor="#1A1D27",
                    xaxis=dict(tickfont=dict(color="#8892B0"), gridcolor="#2E3250"),
                    yaxis=dict(tickfont=dict(color="#8892B0"), gridcolor="#2E3250"),
                    height=300, margin=dict(l=20,r=20,t=20,b=20),
                )
                st.plotly_chart(fig, use_container_width=True)

        if st.button("🤖 AI 分析此数据集", type="primary", key="e_csv_ai"):
            with st.spinner("🧠 AI 正在分析 CSV 数据..."):
                try:
                    from openai import OpenAI
                    client = OpenAI()
                    summary = df.describe().to_string()
                    resp = client.chat.completions.create(
                        model="gpt-4.1-mini",
                        messages=[
                            {"role":"system","content":
                             "你是一位医疗数据分析专家，擅长解读体检数据统计摘要。"},
                            {"role":"user","content":
                             f"请分析以下体检数据的统计摘要，识别异常模式，给出健康建议：\n\n{summary[:2000]}"}
                        ],
                        max_tokens=800, temperature=0.7,
                    )
                    ai_result = resp.choices[0].message.content
                    st.markdown(
                        f"""<div style='background:#1A2744;border:1px solid #4F8EF744;
                            border-radius:12px;padding:20px;margin-top:12px;'>
                            <div style='color:#4F8EF7;font-size:12px;font-weight:700;
                                margin-bottom:12px;'>🤖 AI 数据分析报告</div>""",
                        unsafe_allow_html=True,
                    )
                    st.markdown(ai_result)
                    st.markdown("</div>", unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"AI 分析出错：{e}")
    except Exception as e:
        st.error(f"CSV 解析失败：{e}")


# ─────────────────────────────────────────────────────────────────────────────
# Tab 4：使用指南
# ─────────────────────────────────────────────────────────────────────────────
def _render_guide():
    st.markdown("### 📖 健康洞察引擎使用指南")
    st.markdown("""
**一键实验室** 提供 5 个预设实验模板，选择后点击「运行实验」即可获得深度分析报告，无需编写任何代码。

| 实验 | 说明 | 所需数据 |
|------|------|---------|
| 🔬 血常规智能解读 | 分析 WBC/RBC/HGB/PLT 等指标 | 血常规体检记录 |
| 📈 12个月趋势分析 | 识别指标长期变化趋势 | ≥2次体检记录 |
| 🌿 过敏相关性 | 分析 IgE/EOS% 与症状关联 | 过敏相关指标记录 |
| 🔮 干支五行对撞 | 五行能量与健康指标关联 | 任意体检记录 |
| 💊 干预效果评估 | 对比干预前后指标变化 | ≥2次不同日期记录 |

**干支五行对撞引擎 V4.0** 算法说明详见下方文档。
    """)


# ─────────────────────────────────────────────────────────────────────────────
# 实验执行逻辑
# ─────────────────────────────────────────────────────────────────────────────
def _execute_experiment(exp_id: str, profile: dict):
    try:
        records = db.get_records(profile["id"]) or []
        if exp_id == "cbc_analysis":
            return _exp_cbc(profile, records)
        elif exp_id == "trend_12m":
            return _exp_trend(profile, records)
        elif exp_id == "allergy_correlation":
            return _exp_allergy(profile, records)
        elif exp_id == "bazi_health":
            return _exp_bazi_quick(profile, records)
        elif exp_id == "intervention_eval":
            return _exp_intervention(profile, records)
        else:
            return "未知实验类型。", []
    except Exception as e:
        import traceback
        return f"**实验执行出错：**\n```\n{traceback.format_exc()}\n```", []


def _exp_cbc(profile: dict, records: list):
    blood_codes = {"WBC","NEU%","LYM%","EOS%","EOS","RBC","HGB","MCV","MCH","MCHC","PLT"}
    blood_recs = [r for r in records if r.get("indicator_code","").upper() in blood_codes]
    if not blood_recs:
        return "暂无血常规数据，请先录入血常规体检数据。", []

    latest_date = max(r.get("record_date","") for r in blood_recs)
    latest = [r for r in blood_recs if r.get("record_date") == latest_date]
    abnormal = [r for r in latest if r.get("status") in ("偏高","偏低")]

    lines = [f"**最新血常规（{latest_date}）** — 共 {len(latest)} 项，异常 {len(abnormal)} 项\n"]
    lines.append("| 指标 | 数值 | 单位 | 参考区间 | 状态 |")
    lines.append("|------|------|------|---------|------|")
    for r in latest:
        status = r.get("status","正常")
        emoji = "🔴" if status=="偏高" else ("🔵" if status=="偏低" else "✅")
        ref_low  = r.get("ref_low")
        ref_high = r.get("ref_high")
        ref = f"{ref_low if ref_low is not None else '-'} ~ {ref_high if ref_high is not None else '-'}"
        lines.append(f"| {r.get('indicator_name',r.get('indicator_code',''))} | "
                     f"**{r.get('value','-')}** | {r.get('unit','')} | {ref} | {emoji} {status} |")

    figs = []
    if PLOTLY_OK and len(latest) >= 3:
        names = [r.get("indicator_name", r.get("indicator_code","")) for r in latest]
        statuses = [r.get("status","正常") for r in latest]
        colors = ["#E74C3C" if s=="偏高" else "#3498DB" if s=="偏低" else "#2ECC71" for s in statuses]
        vals   = []
        for r in latest:
            v = r.get("value")
            ref_low  = r.get("ref_low")
            ref_high = r.get("ref_high")
            if v is not None and ref_low is not None and ref_high is not None:
                mid = (float(ref_low) + float(ref_high)) / 2
                rng = float(ref_high) - float(ref_low)
                vals.append(round((float(v) - mid) / rng * 100, 1) if rng > 0 else 0)
            else:
                vals.append(0)
        fig = go.Figure(go.Bar(
            x=names, y=vals, marker_color=colors,
            text=[f"{v:+.1f}%" for v in vals], textposition="outside",
            textfont=dict(color="#E8EAF6", size=10),
        ))
        fig.add_hline(y=0, line_dash="dash", line_color="#8892B0", line_width=1)
        fig.update_layout(
            paper_bgcolor="#1A1D27", plot_bgcolor="#1A1D27",
            xaxis=dict(tickfont=dict(color="#8892B0",size=9), gridcolor="#2E3250"),
            yaxis=dict(tickfont=dict(color="#8892B0",size=9), gridcolor="#2E3250",
                       title="偏离中值 %"),
            height=300, margin=dict(l=20,r=20,t=20,b=60),
            title=dict(text="血常规指标偏离参考中值分布", font=dict(color="#E8EAF6",size=13)),
        )
        figs.append(fig)

    return "\n".join(lines), figs


def _exp_trend(profile: dict, records: list):
    if not records:
        return "暂无体检数据。", []

    import pandas as pd
    df = pd.DataFrame(records)
    if "record_date" not in df.columns or "value" not in df.columns:
        return "数据格式不完整。", []

    df["record_date"] = pd.to_datetime(df["record_date"], errors="coerce")
    df = df.dropna(subset=["record_date","value"])
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    df = df.dropna(subset=["value"])

    codes = df["indicator_code"].value_counts().head(6).index.tolist()
    if not codes:
        return "数据不足，无法生成趋势图。", []

    lines = [f"**12个月健康趋势分析** — 共分析 {len(codes)} 个关键指标\n"]
    for code in codes:
        sub = df[df["indicator_code"]==code].sort_values("record_date")
        if len(sub) >= 2:
            first_val = sub["value"].iloc[0]
            last_val  = sub["value"].iloc[-1]
            change = last_val - first_val
            trend = "↑ 上升" if change > 0 else "↓ 下降" if change < 0 else "→ 持平"
            lines.append(f"- **{code}**：{first_val:.1f} → {last_val:.1f}（{trend} {abs(change):.1f}）")

    figs = []
    if PLOTLY_OK:
        fig = go.Figure()
        palette = ["#4F8EF7","#2ECC71","#E74C3C","#F39C12","#9B59B6","#1ABC9C"]
        for i, code in enumerate(codes):
            sub = df[df["indicator_code"]==code].sort_values("record_date")
            if len(sub) >= 2:
                name = sub["indicator_name"].iloc[0] if "indicator_name" in sub.columns else code
                fig.add_trace(go.Scatter(
                    x=sub["record_date"], y=sub["value"],
                    mode="lines+markers", name=name,
                    line=dict(color=palette[i%len(palette)], width=2),
                    marker=dict(size=6),
                ))
        fig.update_layout(
            paper_bgcolor="#1A1D27", plot_bgcolor="#1A1D27",
            xaxis=dict(tickfont=dict(color="#8892B0"), gridcolor="#2E3250"),
            yaxis=dict(tickfont=dict(color="#8892B0"), gridcolor="#2E3250"),
            legend=dict(font=dict(color="#E8EAF6",size=10), bgcolor="#21253A"),
            height=350, margin=dict(l=20,r=20,t=30,b=20),
            title=dict(text="关键指标12个月趋势", font=dict(color="#E8EAF6",size=13)),
        )
        figs.append(fig)

    return "\n".join(lines), figs


def _exp_allergy(profile: dict, records: list):
    allergy_codes = {"IgE","EOS","EOS%","WBC","NEU","NEU%","BASO","BASO%"}
    allergy_recs = [r for r in records if r.get("indicator_code","").upper() in allergy_codes]
    if not allergy_recs:
        return "暂无过敏相关指标数据（IgE/EOS%/WBC等）。", []

    lines = ["**过敏原与免疫指标相关性分析**\n"]
    abnormal = [r for r in allergy_recs if r.get("status") in ("偏高","偏低")]
    lines.append(f"过敏相关指标共 {len(allergy_recs)} 条记录，异常 {len(abnormal)} 条。\n")

    for r in abnormal:
        val = r.get("value")
        ref_high = r.get("ref_high")
        pct = ""
        if val is not None and ref_high is not None:
            try:
                pct = f"（超出参考上限 {(float(val)/float(ref_high)-1)*100:.0f}%）"
            except Exception:
                pass
        lines.append(f"- **{r.get('indicator_name',r.get('indicator_code',''))}** "
                     f"{r.get('value')} {r.get('unit','')} {pct} — {r.get('status','')}")

    return "\n".join(lines), []


def _exp_bazi_quick(profile: dict, records: list):
    birth_year = int(profile.get("birth_year") or 1985)
    curr_year  = datetime.now().year
    result = deep_bazi_analysis(birth_year, curr_year)
    risks  = compute_collision_risks(result, records)

    lines = [
        f"**干支五行快速分析**",
        f"本命：{result['birth_gz']}（{result['b_wx']}）",
        f"流年：{result['curr_gz']}（{result['c_wx']}）",
        f"天干关系：{result['tg_relation']}",
        f"承压系统：{result['ke_wx']}（{result['ke_body']['organ']}）",
        f"十二长生：{result['b_changsheng']}",
        f"旺相休囚：{result['b_wangxiang']}",
        "",
        f"**高风险指标：** {', '.join(r['name'] for r in risks if '高风险' in r['risk']) or '无'}",
    ]
    return "\n".join(lines), []


def _exp_intervention(profile: dict, records: list):
    if not records:
        return "暂无体检数据。", []

    import pandas as pd
    df = pd.DataFrame(records)
    if len(df) < 2:
        return "数据不足（需要至少2次体检记录）。", []

    df["record_date"] = pd.to_datetime(df.get("record_date",""), errors="coerce")
    df["value"] = pd.to_numeric(df.get("value"), errors="coerce")
    df = df.dropna(subset=["record_date","value"])

    dates = sorted(df["record_date"].unique())
    if len(dates) < 2:
        return "需要至少2个不同日期的体检记录。", []

    first_date = dates[0]
    last_date  = dates[-1]
    first = df[df["record_date"]==first_date]
    last  = df[df["record_date"]==last_date]

    merged = first.merge(last, on="indicator_code", suffixes=("_first","_last"))
    if merged.empty:
        return "两次体检无相同指标，无法对比。", []

    lines = [
        f"**干预效果追踪评估**",
        f"对比时间：{first_date.date()} → {last_date.date()}\n",
        "| 指标 | 初始值 | 最新值 | 变化 | 趋势 |",
        "|------|--------|--------|------|------|",
    ]
    for _, row in merged.iterrows():
        v1 = row.get("value_first")
        v2 = row.get("value_last")
        if v1 is None or v2 is None:
            continue
        change = float(v2) - float(v1)
        trend = "↑ 上升" if change > 0.01 else "↓ 下降" if change < -0.01 else "→ 持平"
        name = row.get("indicator_name_first", row.get("indicator_code",""))
        lines.append(f"| {name} | {v1:.1f} | {v2:.1f} | {change:+.1f} | {trend} |")

    return "\n".join(lines), []
