"""
模块 B：智能指标分析仪 V4.0
- 修复：血常规模板扩充至 15 项核心指标（含 MCV/MCH/MCHC/NEU%/LYM% 等）
- 修复：session_state 与全局成员 selected_profile_id 同步
- 修复：所有 None 值防护，消除 TypeError
- 修复：录入后趋势图 + AI 自动解读
"""

import streamlit as st
import json
from datetime import datetime, date
import database as db
import utils
import agent
import auth
try:
    import ocr_agent
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

# ── 体检套餐模板 ──────────────────────────────────────────────────────────────
# 格式：(类别, 指标名称, 指标代码, 单位, 参考下限, 参考上限)
EXAM_TEMPLATES = {
    "血常规（完整版·15项）": [
        ("血液检查", "白细胞计数",            "WBC",  "×10⁹/L",  4.0,  10.0),
        ("血液检查", "中性粒细胞%",           "NEU%", "%",       50.0,  70.0),
        ("血液检查", "中性粒细胞绝对值",       "NEU",  "×10⁹/L",  1.8,   6.3),
        ("血液检查", "淋巴细胞%",             "LYM%", "%",       20.0,  40.0),
        ("血液检查", "淋巴细胞绝对值",         "LYM",  "×10⁹/L",  1.1,   3.2),
        ("血液检查", "单核细胞%",             "MON%", "%",        3.0,  10.0),
        ("血液检查", "嗜酸性粒细胞%",         "EOS%", "%",        0.4,   8.0),
        ("血液检查", "嗜酸性粒细胞绝对值",     "EOS",  "×10⁹/L",  0.02,  0.52),
        ("血液检查", "红细胞计数",            "RBC",  "×10¹²/L", 4.3,   5.8),
        ("血液检查", "血红蛋白",              "HGB",  "g/L",     130,   175),
        ("血液检查", "红细胞压积",            "HCT",  "%",       40.0,  50.0),
        ("血液检查", "平均红细胞体积",         "MCV",  "fL",      80.0,  100.0),
        ("血液检查", "平均红细胞血红蛋白量",   "MCH",  "pg",      27.0,  34.0),
        ("血液检查", "平均红细胞血红蛋白浓度", "MCHC", "g/L",     316,   354),
        ("血液检查", "血小板计数",            "PLT",  "×10⁹/L",  100,   300),
    ],
    "生化全套（12项）": [
        ("生化检查", "谷丙转氨酶",   "ALT",  "U/L",     7,    40),
        ("生化检查", "谷草转氨酶",   "AST",  "U/L",     13,   35),
        ("生化检查", "γ-谷氨酰转移酶","GGT", "U/L",     10,   60),
        ("生化检查", "碱性磷酸酶",   "ALP",  "U/L",     45,   125),
        ("生化检查", "总蛋白",       "TP",   "g/L",     65,   85),
        ("生化检查", "白蛋白",       "ALB",  "g/L",     40,   55),
        ("生化检查", "总胆固醇",     "TC",   "mmol/L",  0,    5.2),
        ("生化检查", "甘油三酯",     "TG",   "mmol/L",  0,    1.7),
        ("生化检查", "低密度脂蛋白", "LDL",  "mmol/L",  0,    3.4),
        ("生化检查", "高密度脂蛋白", "HDL",  "mmol/L",  1.0,  99.0),
        ("生化检查", "空腹血糖",     "GLU",  "mmol/L",  3.9,  6.1),
        ("生化检查", "肌酐",         "CREA", "μmol/L",  57,   97),
        ("生化检查", "尿酸",         "UA",   "μmol/L",  208,  428),
        ("生化检查", "血尿素氮",     "BUN",  "mmol/L",  2.9,  8.2),
    ],
    "免疫过敏套餐": [
        ("免疫检查", "IgE总量",       "IgE",  "IU/mL",  0,    100),
        ("免疫检查", "C反应蛋白",     "CRP",  "mg/L",   0,    3.0),
        ("免疫检查", "嗜酸性粒细胞%", "EOS%", "%",      0.4,  8.0),
        ("免疫检查", "嗜酸性粒细胞绝对值", "EOS", "×10⁹/L", 0.02, 0.52),
    ],
    "内分泌套餐": [
        ("内分泌检查", "促甲状腺激素", "TSH",  "mIU/L",  0.27, 4.2),
        ("内分泌检查", "25-羟维生素D", "VD3",  "ng/mL",  30,   100),
        ("内分泌检查", "空腹血糖",     "GLU",  "mmol/L", 3.9,  6.1),
    ],
    "心血管套餐": [
        ("心血管检查", "总胆固醇",    "TC",   "mmol/L", 0,    5.2),
        ("心血管检查", "甘油三酯",    "TG",   "mmol/L", 0,    1.7),
        ("心血管检查", "低密度脂蛋白","LDL",  "mmol/L", 0,    3.4),
        ("心血管检查", "高密度脂蛋白","HDL",  "mmol/L", 1.0,  99.0),
        ("心血管检查", "收缩压",      "BP_S", "mmHg",   90,   140),
        ("心血管检查", "舒张压",      "BP_D", "mmHg",   60,   90),
    ],
}


def render():
    st.markdown("""
    <div style="display:flex;align-items:center;justify-content:space-between;
         margin-bottom:24px;padding-bottom:16px;border-bottom:1px solid rgba(79,142,247,0.15);">
      <div>
        <div style="font-size:11px;text-transform:uppercase;letter-spacing:0.1em;color:#8892B0;margin-bottom:4px;">DATA CENTER</div>
        <div style="font-size:22px;font-weight:700;color:#E8EAF6;">数据中心</div>
      </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown(
        "<p style='color:#8892B0;margin-top:-10px;'>"
        "录入体检数据，AI 立即执行生理学深度解读并展示历史趋势</p>",
        unsafe_allow_html=True
    )

    # V4.0：按当前登录用户加载成员
    user_id = auth.get_current_user_id()
    profiles = db.get_all_profiles(user_id=user_id)
    if not profiles:
        st.warning("请先在「家庭成员驾驶舱」中添加成员档案。")
        return

    # ── 成员选择（与全局 selected_profile_id 同步）────────────────────────────
    profile_map = {p["id"]: p for p in profiles}
    global_pid = st.session_state.get("selected_profile_id")

    # 确定默认选中索引
    if global_pid and global_pid in profile_map:
        default_idx = next(
            (i for i, p in enumerate(profiles) if p["id"] == global_pid), 0
        )
    else:
        default_idx = 0

    profile_labels = [f"{p['avatar_emoji']} {p['name']}" for p in profiles]
    selected_label = st.selectbox(
        "选择成员",
        profile_labels,
        index=default_idx,
        key="b_profile_sel"
    )
    profile = next(p for p in profiles
                   if f"{p['avatar_emoji']} {p['name']}" == selected_label)

    # 同步回全局 session_state
    st.session_state["selected_profile_id"] = profile["id"]

    tab_input, tab_ocr, tab_analysis, tab_history = st.tabs(
        ["📝 数据录入", "📷 智能导入", "🧠 AI 深度分析", "📈 历史趋势"]
    )

    with tab_input:
        _render_input_tab(profile)

    with tab_ocr:
        _render_ocr_import_tab(profile)

    with tab_analysis:
        _render_analysis_tab(profile)

    with tab_history:
        _render_history_tab(profile)


# ─────────────────────────────────────────────────────────────────────────────
# Tab 1：数据录入
# ─────────────────────────────────────────────────────────────────────────────
def _render_input_tab(profile: dict):
    st.markdown("### 📝 体检数据录入")

    input_mode = st.radio(
        "录入方式",
        ["📋 使用模板批量录入", "✏️ 自定义单项录入"],
        horizontal=True,
        key="b_input_mode"
    )

    record_date = st.date_input("检查日期", value=date.today(), key="b_record_date")

    if input_mode == "📋 使用模板批量录入":
        _render_template_input(profile, record_date)
    else:
        _render_custom_input(profile, record_date)

    # ── 录入后立即显示趋势图 + AI 解读 ───────────────────────────────────────
    just_saved = st.session_state.get("b_just_saved_codes", [])
    just_saved_pid = st.session_state.get("b_just_saved_pid")

    if just_saved and just_saved_pid == profile["id"]:
        st.markdown("---")
        st.markdown("#### 📈 刚录入指标的历史趋势")
        for code in just_saved[:4]:
            history = db.get_indicator_history(profile["id"], code, user_id=st.session_state.get("auth_user_id"))
            if history and len(history) >= 1:
                info = utils.get_indicator_info(code) or {"name": code, "unit": ""}
                try:
                    fig = utils.plot_indicator_trend(
                        history, info.get("name", code), info.get("unit", "")
                    )
                    st.plotly_chart(fig, use_container_width=True)
                except Exception as e:
                    st.caption(f"趋势图暂不可用：{e}")

        # 自动触发 AI 分析（针对异常指标，最多2项）
        records = db.get_records(profile["id"], user_id=st.session_state.get("auth_user_id"))
        abnormal = [
            r for r in records
            if r.get("status") in ("偏高", "偏低")
            and r.get("indicator_code") in just_saved
        ]
        if abnormal:
            st.markdown("---")
            st.markdown("#### 🤖 AI 自动解读（异常指标）")
            for rec in abnormal[:2]:
                _render_ai_analysis_card(rec, profile)


def _render_template_input(profile: dict, record_date: date):
    """模板批量录入。"""
    template_name = st.selectbox(
        "选择体检套餐模板",
        list(EXAM_TEMPLATES.keys()),
        key="b_template_sel"
    )
    template = EXAM_TEMPLATES[template_name]

    st.markdown(
        f"""<div style='background:#21253A;border:1px solid #2E3250;
            border-radius:10px;padding:16px;margin-bottom:12px;'>
            <div style='color:#4F8EF7;font-size:13px;font-weight:600;
                margin-bottom:12px;'>
                {template_name} — 共 {len(template)} 项指标
                <span style='color:#8892B0;font-size:11px;margin-left:8px;'>
                    （数值为 0 的项目将被跳过）</span>
            </div>""",
        unsafe_allow_html=True
    )

    # 表头
    hcol1, hcol2, hcol3 = st.columns([3, 2, 3])
    with hcol1:
        st.markdown("<div style='color:#8892B0;font-size:11px;font-weight:600;'>指标名称</div>",
                    unsafe_allow_html=True)
    with hcol2:
        st.markdown("<div style='color:#8892B0;font-size:11px;font-weight:600;'>检测值</div>",
                    unsafe_allow_html=True)
    with hcol3:
        st.markdown("<div style='color:#8892B0;font-size:11px;font-weight:600;'>参考区间</div>",
                    unsafe_allow_html=True)

    values_input = {}
    for cat, name, code, unit, ref_low, ref_high in template:
        col1, col2, col3 = st.columns([3, 2, 3])
        with col1:
            st.markdown(
                f"<div style='padding:6px 0;color:#E8EAF6;font-size:13px;'>"
                f"<b>{name}</b> <span style='color:#8892B0;font-size:11px;'>({code})</span>"
                f"</div>",
                unsafe_allow_html=True
            )
        with col2:
            val = st.number_input(
                f"{code}_val",
                min_value=0.0, max_value=99999.0,
                value=0.0, step=0.01,
                key=f"b_val_{code}_{template_name[:4]}",
                label_visibility="collapsed"
            )
            values_input[code] = (cat, name, code, unit, ref_low, ref_high, val)
        with col3:
            st.markdown(
                f"<div style='padding:6px 0;color:#8892B0;font-size:11px;'>"
                f"{ref_low} ~ {ref_high} {unit}</div>",
                unsafe_allow_html=True
            )

    st.markdown("</div>", unsafe_allow_html=True)

    if st.button("💾 保存并立即分析", type="primary",
                 use_container_width=True, key="b_save_template"):
        saved_codes = []
        for code, (cat, name, c, unit, ref_low, ref_high, val) in values_input.items():
            if val > 0:
                db.add_medical_record(
                    profile_id=profile["id"],
                    record_date=str(record_date),
                    category=cat,
                    indicator_name=name,
                    indicator_code=code,
                    value=val,
                    unit=unit,
                    ref_low=ref_low,
                    ref_high=ref_high,
                    user_id=st.session_state.get("auth_user_id")
                )
                saved_codes.append(code)
        if saved_codes:
            st.success(f"✅ 已保存 {len(saved_codes)} 项指标数据！")
            st.session_state["b_just_saved_codes"] = saved_codes
            st.session_state["b_just_saved_pid"] = profile["id"]
            st.rerun()
        else:
            st.warning("请至少输入一项数值（大于0）。")


def _render_custom_input(profile: dict, record_date: date):
    """自定义单项录入。"""
    with st.form("custom_record_form", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        with c1:
            cat = st.selectbox("类别", ["血液检查", "生化检查", "免疫检查",
                                         "内分泌检查", "心血管检查", "影像检查", "其他"])
            ind_name = st.text_input("指标名称 *", placeholder="如：总胆固醇")
        with c2:
            ind_code = st.text_input("指标代码", placeholder="如：TC")
            unit = st.text_input("单位", placeholder="如：mmol/L")
        with c3:
            value = st.number_input("检测值 *", min_value=0.0,
                                     max_value=99999.0, value=0.0, step=0.01)
            ref_low = st.number_input("参考下限", min_value=0.0,
                                       max_value=99999.0, value=0.0, step=0.01)
            ref_high = st.number_input("参考上限", min_value=0.0,
                                        max_value=99999.0, value=0.0, step=0.01)

        if st.form_submit_button("💾 保存并分析", type="primary",
                                  use_container_width=True):
            if not ind_name:
                st.error("指标名称不能为空！")
            else:
                code = ind_code.strip() or ind_name[:4].upper()
                db.add_medical_record(
                    profile_id=profile["id"],
                    record_date=str(record_date),
                    category=cat,
                    indicator_name=ind_name,
                    indicator_code=code,
                    value=value,
                    unit=unit,
                    ref_low=ref_low if ref_low > 0 else None,
                    ref_high=ref_high if ref_high > 0 else None,
                    user_id=st.session_state.get("auth_user_id")
                )
                st.success(f"✅ 已保存 {ind_name} = {value} {unit}")
                st.session_state["b_just_saved_codes"] = [code]
                st.session_state["b_just_saved_pid"] = profile["id"]
                st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
# Tab 2：AI 深度分析
# ─────────────────────────────────────────────────────────────────────────────
def _render_analysis_tab(profile: dict):
    st.markdown("### 🧠 AI 生理学深度分析")

    user_id = st.session_state.get("auth_user_id")
    records = db.get_records(profile["id"], user_id=user_id)
    if not records:
        st.info("暂无体检数据，请先在「数据录入」Tab 中录入数据。")
        return

    # 安全获取最新日期
    dates = [r.get("record_date") for r in records if r.get("record_date")]
    if not dates:
        st.info("暂无有效的体检日期数据。")
        return

    latest_date = max(dates)
    latest_records = [r for r in records if r.get("record_date") == latest_date]
    abnormal = [r for r in latest_records if r.get("status") in ("偏高", "偏低")]
    normal = [r for r in latest_records if r.get("status") == "正常"]

    # 统计卡片
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("最新检查日期", latest_date)
    with col2:
        st.metric("异常指标", f"{len(abnormal)} 项",
                  delta=f"-{len(abnormal)}" if abnormal else None,
                  delta_color="inverse")
    with col3:
        st.metric("正常指标", f"{len(normal)} 项")

    # 指标状态卡片（最多显示12项）
    if latest_records:
        st.markdown("#### 最新检查结果")
        display_records = latest_records[:12]
        cols_per_row = 4
        for row_start in range(0, len(display_records), cols_per_row):
            row_recs = display_records[row_start:row_start + cols_per_row]
            cols = st.columns(cols_per_row)
            for i, rec in enumerate(row_recs):
                with cols[i]:
                    status = rec.get("status", "正常")
                    if status == "偏高":
                        color, bg, arrow = "#E74C3C", "rgba(231,76,60,0.1)", "↑"
                    elif status == "偏低":
                        color, bg, arrow = "#F39C12", "rgba(243,156,18,0.1)", "↓"
                    else:
                        color, bg, arrow = "#2ECC71", "rgba(46,204,113,0.1)", "→"
                    val_str = str(rec.get("value", "—"))
                    unit_str = rec.get("unit", "") or ""
                    st.markdown(
                        f"""<div style='background:{bg};border:1px solid {color}44;
                            border-radius:10px;padding:10px;text-align:center;
                            margin-bottom:8px;min-height:90px;'>
                            <div style='color:#8892B0;font-size:10px;
                                margin-bottom:4px;'>{rec.get("indicator_name","—")}</div>
                            <div style='color:{color};font-size:16px;font-weight:700;'>
                                {arrow} {val_str}</div>
                            <div style='color:#8892B0;font-size:10px;'>{unit_str}</div>
                            <div style='color:{color};font-size:11px;
                                font-weight:600;margin-top:2px;'>{status}</div>
                        </div>""",
                        unsafe_allow_html=True
                    )

    st.markdown("---")
    st.markdown("#### 选择指标进行 AI 深度分析")

    # 安全构建指标列表
    code_to_rec = {}
    for r in latest_records:
        code = r.get("indicator_code")
        if code and code not in code_to_rec:
            code_to_rec[code] = r

    all_codes = list(code_to_rec.keys())
    if not all_codes:
        st.info("暂无可分析的指标。")
        return

    abnormal_codes = [r.get("indicator_code") for r in abnormal
                      if r.get("indicator_code")]
    default_code = (abnormal_codes[0] if abnormal_codes else all_codes[0])

    # 安全获取默认索引
    default_idx = all_codes.index(default_code) if default_code in all_codes else 0

    selected_code = st.selectbox(
        "选择指标",
        options=all_codes,
        index=default_idx,
        format_func=lambda c: (
            f"{code_to_rec[c].get('indicator_name', c)} "
            f"({code_to_rec[c].get('value', '—')} {code_to_rec[c].get('unit', '')})"
            if c in code_to_rec else c
        ),
        key="b_analysis_code"
    )

    selected_rec = code_to_rec.get(selected_code)
    if not selected_rec:
        st.warning("未找到该指标的数据，请重新选择。")
        return

    # 仪表盘（安全处理 None）
    ref_low = selected_rec.get("ref_low")
    ref_high = selected_rec.get("ref_high")
    value = selected_rec.get("value")

    if value is not None and ref_high is not None:
        try:
            fig_gauge = utils.plot_indicator_gauge(
                selected_rec.get("indicator_name", selected_code),
                float(value),
                selected_rec.get("unit", ""),
                float(ref_low) if ref_low is not None else 0.0,
                float(ref_high)
            )
            st.plotly_chart(fig_gauge, use_container_width=True)
        except Exception as e:
            st.caption(f"仪表盘暂不可用：{e}")

    # 趋势图
    history = db.get_indicator_history(profile["id"], selected_code, user_id=user_id)
    if history and len(history) > 1:
        st.markdown("**历史趋势**")
        try:
            fig_trend = utils.plot_indicator_trend(
                history,
                selected_rec.get("indicator_name", selected_code),
                selected_rec.get("unit", "")
            )
            st.plotly_chart(fig_trend, use_container_width=True)
        except Exception as e:
            st.caption(f"趋势图暂不可用：{e}")

    # AI 分析
    cache_key = f"b_ai_{profile['id']}_{selected_code}"
    cached = st.session_state.get(cache_key)

    col_btn1, col_btn2 = st.columns([3, 1])
    with col_btn1:
        run_ai = st.button("🧠 AI 生理学深度解读", type="primary",
                            use_container_width=True, key="b_run_ai")
    with col_btn2:
        if st.button("🔄 清除缓存", use_container_width=True, key="b_clear_cache"):
            st.session_state.pop(cache_key, None)
            st.rerun()

    if run_ai or cached:
        if run_ai or not cached:
            with st.spinner("🔬 AI 正在检索生理学文献并生成解读，请稍候..."):
                try:
                    analysis = agent.analyze_indicator(
                        indicator_name=selected_rec.get("indicator_name", selected_code),
                        indicator_code=selected_code,
                        value=float(value) if value is not None else 0.0,
                        unit=selected_rec.get("unit", ""),
                        ref_low=float(ref_low) if ref_low is not None else 0.0,
                        ref_high=float(ref_high) if ref_high is not None else 0.0,
                        profile_info=profile
                    )
                    st.session_state[cache_key] = analysis
                except Exception as e:
                    st.error(f"AI 分析出错：{e}")
                    return
        else:
            analysis = cached

        _render_ai_analysis_card(selected_rec, profile, analysis_text=analysis)


# ─────────────────────────────────────────────────────────────────────────────
# Tab 3：历史趋势
# ─────────────────────────────────────────────────────────────────────────────
def _render_history_tab(profile: dict):
    st.markdown("### 📈 历史趋势分析")

    # 处理 OCR 入库后自动跳转逐指标
    jump_code = st.session_state.get("b_jump_to_trend")
    if jump_code:
        st.success(
            f"✅ 入库完成！已自动定位到指标 **{jump_code}** 的最新趋势曲线。"
        )
        st.session_state["b_jump_to_trend"] = None  # 清除跳转标记

    user_id = st.session_state.get("auth_user_id")
    records = db.get_records(profile["id"], user_id=user_id)
    if not records:
        st.info("暂无历史数据。")
        return

    # 按指标代码分组
    code_map: dict = {}
    for r in records:
        code = r.get("indicator_code")
        name = r.get("indicator_name", code)
        if code and code not in code_map:
            code_map[code] = name

    if not code_map:
        st.info("暂无可展示的历史趋势。")
        return

    # 如果有跳转目标，自动预选该指标
    auto_select = [jump_code] if jump_code and jump_code in code_map else []
    default_sel = auto_select if auto_select else list(code_map.keys())[:min(3, len(code_map))]

    selected_codes = st.multiselect(
        "选择要对比的指标（最多 4 项）",
        options=list(code_map.keys()),
        default=default_sel,
        format_func=lambda c: f"{code_map.get(c, c)} ({c})",
        max_selections=4,
        key="b_history_codes"
    )

    if not selected_codes:
        st.info("请至少选择一项指标。")
        return

    for code in selected_codes:
        history = db.get_indicator_history(profile["id"], code, user_id=user_id)
        if history and len(history) >= 1:
            try:
                fig = utils.plot_indicator_trend(
                    history, code_map.get(code, code),
                    records[0].get("unit", "") if records else ""
                )
                st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.caption(f"{code} 趋势图暂不可用：{e}")
        else:
            st.caption(f"{code_map.get(code, code)}：历史数据不足，无法绘制趋势图。")


# ─────────────────────────────────────────────────────────────────────────────
# 通用 AI 分析卡片
# ─────────────────────────────────────────────────────────────────────────────
def _render_ai_analysis_card(rec: dict, profile: dict, analysis_text: str = None):
    """渲染 AI 分析结果卡片（可复用）。"""
    if analysis_text is None:
        # 如果没有传入分析文本，则实时调用
        with st.spinner(f"AI 正在分析 {rec.get('indicator_name', '')}..."):
            try:
                ref_low = rec.get("ref_low")
                ref_high = rec.get("ref_high")
                analysis_text = agent.analyze_indicator(
                    indicator_name=rec.get("indicator_name", ""),
                    indicator_code=rec.get("indicator_code", ""),
                    value=float(rec.get("value", 0)),
                    unit=rec.get("unit", ""),
                    ref_low=float(ref_low) if ref_low is not None else 0.0,
                    ref_high=float(ref_high) if ref_high is not None else 0.0,
                    profile_info=profile
                )
            except Exception as e:
                st.error(f"AI 分析出错：{e}")
                return

    # 关联器官标签
    info = utils.get_indicator_info(rec.get("indicator_code", "")) or {}
    if info.get("organs"):
        organs_html = "".join(
            f"<span style='background:rgba(79,142,247,0.15);color:#4F8EF7;"
            f"border:1px solid rgba(79,142,247,0.3);border-radius:20px;"
            f"padding:3px 12px;font-size:12px;margin-right:6px;'>🫀 {o}</span>"
            for o in info["organs"]
        )
        st.markdown(
            f"""<div style='background:#21253A;border:1px solid #2E3250;
                border-radius:10px;padding:12px;margin-bottom:12px;'>
                <div style='color:#8892B0;font-size:11px;margin-bottom:8px;'>
                    关联器官 / 系统</div>
                {organs_html}
            </div>""",
            unsafe_allow_html=True
        )

    # 分析报告卡片
    ind_name = rec.get("indicator_name", rec.get("indicator_code", "—"))
    st.markdown(
        f"""<div style='background:linear-gradient(135deg,#1a2744,#21253A);
            border:1px solid #2E3250;border-radius:12px;padding:20px;
            margin-bottom:16px;'>
            <div style='color:#4F8EF7;font-size:12px;font-weight:700;
                letter-spacing:1px;margin-bottom:12px;'>
                🤖 AI 生理学解读 — {ind_name}</div>""",
        unsafe_allow_html=True
    )
    st.markdown(analysis_text)
    st.markdown("</div>", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# Tab OCR：智能报告导入（V4.0 新增）
# ─────────────────────────────────────────────────────────────────────────────
def _render_ocr_import_tab(profile: dict):
    """OCR 智能报告导入 Tab。"""
    st.markdown("### 📷 智能报告导入")
    st.markdown(
        "<p style='color:#8892B0;'>上传体检报告图片或 PDF，AI 自动识别所有指标并导入数据库。</p>",
        unsafe_allow_html=True
    )

    if not OCR_AVAILABLE:
        st.error("OCR 模块未安装，请运行 `pip install pdfplumber pytesseract` 后重试。")
        return

    # 上传区域
    st.markdown(
        """<div style='background:#21253A;border:2px dashed #2E3250;border-radius:12px;
            padding:24px;text-align:center;margin-bottom:16px;'>
            <div style='font-size:32px;margin-bottom:8px;'>📄</div>
            <div style='color:#8892B0;font-size:13px;'>支持 JPG、PNG、PDF 格式</div>
            <div style='color:#4F8EF7;font-size:11px;margin-top:4px;'>
                AI 将自动识别指标名称、数值、单位和参考区间</div>
        </div>""",
        unsafe_allow_html=True
    )

    uploaded_file = st.file_uploader(
        "上传体检报告",
        type=["jpg", "jpeg", "png", "pdf"],
        key="b_ocr_upload",
        label_visibility="collapsed"
    )

    if uploaded_file is None:
        # 示例说明
        with st.expander("📖 使用说明"):
            st.markdown("""
**支持的报告类型：**
- 医院体检报告（图片或扫描 PDF）
- 血液检查报告单
- 生化全套报告
- 任何包含「指标名称 | 数值 | 单位 | 参考区间」格式的表格

**AI 识别流程：**
1. 上传文件 → 2. AI 多模态识别 → 3. 预览并确认 → 4. 一键导入数据库

**注意事项：**
- 图片清晰度越高，识别准确率越高
- 识别后请务必核对数值，再点击「确认导入」
- 如有识别错误，可在预览表格中直接修改
            """)
        return

    # 读取文件
    file_bytes = uploaded_file.read()
    file_name = uploaded_file.name
    file_ext = file_name.lower().split(".")[-1]
    file_type = "pdf" if file_ext == "pdf" else "image"

    # 显示预览
    if file_type == "image":
        st.image(file_bytes, caption=f"已上传：{file_name}", use_container_width=True)

    # 检查是否已有识别结果缓存
    cache_key = f"ocr_result_{hash(file_bytes)}"
    cached_result = st.session_state.get(cache_key)

    col_run, col_date = st.columns([2, 1])
    with col_run:
        run_ocr = st.button(
            "🤖 AI 智能识别",
            type="primary",
            use_container_width=True,
            key="b_run_ocr",
            disabled=(cached_result is not None)
        )
    with col_date:
        import_date = st.date_input(
            "导入日期",
            value=date.today(),
            key="b_ocr_date"
        )

    if cached_result is not None:
        st.success(f"✅ 已识别 {len(cached_result)} 项指标，请在下方确认后导入。")
        if st.button("🔄 重新识别", key="b_ocr_rerun"):
            st.session_state.pop(cache_key, None)
            st.rerun()

    if run_ocr and cached_result is None:
        with st.spinner("🔬 AI 正在分析报告，识别医学指标...（约 10-20 秒）"):
            indicators, report_date = ocr_agent.extract_indicators_via_ai(
                file_bytes, file_type, file_name
            )
        if not indicators:
            st.error(f"识别失败或未找到有效指标。\n详情：{report_date}")
            return
        st.session_state[cache_key] = indicators
        cached_result = indicators
        st.success(f"✅ 识别完成！共找到 {len(indicators)} 项指标，请核对后导入。")
        st.rerun()

    # 显示识别结果预览表格
    if cached_result:
        st.markdown("#### 📋 识别结果预览（可修改后导入）")

        # 用 data_editor 让用户可以修改
        import pandas as pd
        df = pd.DataFrame(cached_result)
        display_cols = ["indicator_name", "indicator_code", "value", "unit",
                        "ref_low", "ref_high", "category", "status"]
        col_rename = {
            "indicator_name": "指标名称",
            "indicator_code": "代码",
            "value": "数值",
            "unit": "单位",
            "ref_low": "参考下限",
            "ref_high": "参考上限",
            "category": "类别",
            "status": "状态"
        }
        display_df = df[[c for c in display_cols if c in df.columns]].rename(columns=col_rename)

        # 状态着色
        def highlight_status(row):
            if row.get("状态") == "偏高":
                return ["background-color: rgba(231,76,60,0.15)"] * len(row)
            elif row.get("状态") == "偏低":
                return ["background-color: rgba(243,156,18,0.15)"] * len(row)
            return [""] * len(row)

        edited_df = st.data_editor(
            display_df,
            use_container_width=True,
            num_rows="dynamic",
            key="b_ocr_editor"
        )

        # 统计
        total = len(edited_df)
        abnormal_count = len(edited_df[edited_df.get("状态", pd.Series()).isin(["偏高", "偏低"])]) if "状态" in edited_df.columns else 0
        c1, c2, c3 = st.columns(3)
        c1.metric("识别指标数", total)
        c2.metric("异常项", abnormal_count, delta=f"-{abnormal_count}" if abnormal_count else None, delta_color="inverse")
        c3.metric("正常项", total - abnormal_count)

        st.markdown("---")
        col_import, col_cancel = st.columns([3, 1])
        with col_import:
            if st.button(
                f"✅ 确认导入 {total} 项指标到数据库",
                type="primary",
                use_container_width=True,
                key="b_ocr_confirm"
            ):
                # 构建导入数据
                import_records = []
                for _, row in edited_df.iterrows():
                    try:
                        import_records.append({
                            "profile_id": profile["id"],
                            "record_date": str(import_date),
                            "category": row.get("类别", "体检导入"),
                            "indicator_name": str(row.get("指标名称", "")),
                            "indicator_code": str(row.get("代码", "")).upper(),
                            "value": float(row.get("数值", 0)),
                            "unit": str(row.get("单位", "")),
                            "ref_low": float(row["参考下限"]) if pd.notna(row.get("参考下限")) else None,
                            "ref_high": float(row["参考上限"]) if pd.notna(row.get("参考上限")) else None,
                            "source": "OCR智能导入",
                        })
                    except (ValueError, TypeError):
                        continue

                if import_records:
                    # 入库并验证
                    _uid = st.session_state.get("auth_user_id")
                    count = db.batch_add_medical_records(import_records, user_id=_uid)
                    # 验证入库是否成功（从数据库查询确认）
                    verify_codes = [r["indicator_code"] for r in import_records[:3]]
                    verified = 0
                    for code in verify_codes:
                        hist = db.get_indicator_history(profile["id"], code, user_id=_uid)
                        if hist:
                            verified += 1
                    if count > 0:
                        st.success(
                            f"🎉 入库成功！共导入 **{count}** 项指标到 {profile['name']} 的健康档案。"
                            f"（数据库已验证 {verified}/{min(3,len(verify_codes))} 项）"
                        )
                        st.session_state.pop(cache_key, None)
                        saved_codes = [r["indicator_code"] for r in import_records]
                        st.session_state["b_just_saved_codes"] = saved_codes
                        st.session_state["b_just_saved_pid"] = profile["id"]
                        st.session_state["b_ocr_confirmed"] = True
                        # 设置档案库高亮参数，跳转到健康数据档案库并高亮显示新入库记录
                        st.session_state["archive_highlight_codes"] = saved_codes
                        st.session_state["archive_highlight_pid"] = profile["id"]
                        # 同时保留趋势图跳转标记（备用）
                        abnormal_imported = [
                            r["indicator_code"] for r in import_records
                            if r.get("status") in ("偏高", "偏低")
                        ]
                        jump_code = abnormal_imported[0] if abnormal_imported else saved_codes[0]
                        st.session_state["b_jump_to_trend"] = jump_code
                        st.balloons()
                        st.info("→ 入库成功！正在跳转到「🗂️ 健康数据档案库」，展示最新录入记录...")
                        import time; time.sleep(1)
                        st.session_state["current_page"] = "module_archive"
                        st.rerun()
                    else:
                        st.error("⚠️ 入库失败，请检查数据库连接。")
                else:
                    st.error("没有有效数据可导入，请检查表格内容。")

        with col_cancel:
            if st.button("❌ 取消", use_container_width=True, key="b_ocr_cancel"):
                st.session_state.pop(cache_key, None)
                st.rerun()
