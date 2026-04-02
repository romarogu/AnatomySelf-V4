"""
模块 D：生命律动周报 V-Life Weekly Report V4.0
结构化四段式报告：
  1. 健康状况概览（评分式）
  2. 本周异常深度解析（连接生理学）
  3. 最新科研动态（PubMed 论文降级解读）
  4. 个性化学习建议
"""

import streamlit as st
import json
from datetime import datetime, timedelta
import database as db
import utils
import agent


def render():
    st.markdown("""
    <div style="display:flex;align-items:center;justify-content:space-between;
         margin-bottom:24px;padding-bottom:16px;border-bottom:1px solid rgba(79,142,247,0.15);">
      <div>
        <div style="font-size:11px;text-transform:uppercase;letter-spacing:0.1em;color:#8892B0;margin-bottom:4px;">V-LIFE WEEKLY REPORT</div>
        <div style="font-size:22px;font-weight:700;color:#E8EAF6;">生命律动周报</div>
      </div>
      <div style="font-size:11px;color:#C9A84C;letter-spacing:0.05em;">Personal Life Lab</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown(
        "<p style='color:#8892B0;margin-top:-10px;'>"
        "AI 生成结构化专属健康内参，含 PubMed 科研动态降级解读</p>",
        unsafe_allow_html=True
    )

    user_id = st.session_state.get("auth_user_id")
    profiles = db.get_all_profiles(user_id=user_id)
    if not profiles:
        st.warning("请先在「家庭成员驾驶舱」中添加成员。")
        return

    profile_options = {f"{p['avatar_emoji']} {p['name']}": p for p in profiles}
    selected_name = st.selectbox("选择成员", list(profile_options.keys()),
                                  key="weekly_profile")
    profile = profile_options[selected_name]

    tab1, tab2 = st.tabs(["📝 生成周报", "📚 历史周报"])
    with tab1:
        _render_generate_tab(profile)
    with tab2:
        _render_history_tab(profile)


def _render_generate_tab(profile: dict):
    """周报生成标签页。"""
    st.markdown("### 生成本周健康报告")

    col1, col2 = st.columns(2)
    with col1:
        week_start_date = st.date_input(
            "周报起始日期",
            value=(datetime.now() - timedelta(days=datetime.now().weekday())).date(),
            key="d_week_start"
        )
    with col2:
        week_end_date = st.date_input(
            "周报截止日期",
            value=(datetime.now() - timedelta(days=datetime.now().weekday())
                   + timedelta(days=6)).date(),
            key="d_week_end"
        )

    week_start = str(week_start_date)
    week_end = str(week_end_date)

    week_data = db.get_week_data_summary(profile["id"], week_start, week_end, user_id=st.session_state.get("auth_user_id"))
    records = week_data["records"]
    symptoms = week_data["symptoms"]

    # 数据预览卡片
    col_r, col_s, col_a = st.columns(3)
    with col_r:
        abnormal_count = sum(1 for r in records if r.get("status") in ("偏高", "偏低"))
        st.markdown(
            f"""<div style='background:#21253A;border:1px solid #2E3250;
                border-radius:10px;padding:16px;text-align:center;'>
                <div style='font-size:28px;color:#4F8EF7;font-weight:700;'>
                    {len(records)}</div>
                <div style='color:#8892B0;font-size:13px;'>本周体检记录</div>
                <div style='color:#E74C3C;font-size:11px;margin-top:4px;'>
                    {abnormal_count} 项异常</div>
            </div>""",
            unsafe_allow_html=True
        )
    with col_s:
        avg_sev = (sum(s.get("severity", 0) for s in symptoms) / len(symptoms)
                   if symptoms else 0)
        st.markdown(
            f"""<div style='background:#21253A;border:1px solid #2E3250;
                border-radius:10px;padding:16px;text-align:center;'>
                <div style='font-size:28px;color:#A78BFA;font-weight:700;'>
                    {len(symptoms)}</div>
                <div style='color:#8892B0;font-size:13px;'>本周症状记录</div>
                <div style='color:#8892B0;font-size:11px;margin-top:4px;'>
                    平均严重度 {avg_sev:.1f}/10</div>
            </div>""",
            unsafe_allow_html=True
        )
    with col_a:
        _uid = st.session_state.get("auth_user_id")
        all_records = db.get_records(profile["id"], user_id=_uid, limit=50)
        health_scores = utils.calculate_health_scores(all_records or [])
        overall = int(sum(health_scores.values()) / len(health_scores)) if health_scores else 0
        score_color = ("#2ECC71" if overall >= 80 else
                       "#F39C12" if overall >= 60 else "#E74C3C")
        st.markdown(
            f"""<div style='background:#21253A;border:1px solid #2E3250;
                border-radius:10px;padding:16px;text-align:center;'>
                <div style='font-size:28px;color:{score_color};font-weight:700;'>
                    {overall}</div>
                <div style='color:#8892B0;font-size:13px;'>综合健康评分</div>
                <div style='color:{score_color};font-size:11px;margin-top:4px;'>
                    /100</div>
            </div>""",
            unsafe_allow_html=True
        )

    if not records and not symptoms:
        st.info(
            f"本周（{week_start} ~ {week_end}）暂无新数据，将基于历史数据生成综合报告。"
        )

    # 报告选项
    with st.expander("⚙️ 报告生成选项", expanded=False):
        opt_col1, opt_col2 = st.columns(2)
        with opt_col1:
            include_pubmed = st.checkbox("包含 PubMed 科研动态", value=True,
                                          key="d_include_pubmed")
            include_physiology = st.checkbox("包含生理学深度解析", value=True,
                                              key="d_include_physiology")
        with opt_col2:
            include_learning = st.checkbox("包含个性化学习建议", value=True,
                                            key="d_include_learning")
            report_lang = st.selectbox("报告语言风格",
                                        ["专业医学（含术语）", "通俗易懂", "学术研究"],
                                        key="d_report_lang")

    generate_btn = st.button(
        f"🤖 生成 {profile['name']} 专属健康周报",
        type="primary",
        use_container_width=True,
        key="d_generate_btn"
    )

    if generate_btn:
        _uid = st.session_state.get("auth_user_id")
        if not records:
            records = db.get_records(profile["id"], limit=20, user_id=_uid)
        if not symptoms:
            symptoms = db.get_symptom_logs(profile["id"], limit=10, user_id=_uid)

        options = {
            "include_pubmed": st.session_state.get("d_include_pubmed", True),
            "include_physiology": st.session_state.get("d_include_physiology", True),
            "include_learning": st.session_state.get("d_include_learning", True),
            "lang_style": st.session_state.get("d_report_lang", "通俗易懂"),
        }

        with st.spinner(f"🔬 AI 正在为 {profile['name']} 生成结构化专属周报（含 PubMed 检索）..."):
            result = agent.generate_weekly_report_v2(
                profile, week_start, week_end, records, symptoms, options
            )

        report_id = db.save_weekly_report(
            profile["id"], week_start, week_end,
            result.get("title", f"{profile['name']} 健康周报"),
            result.get("full_markdown", ""),
            result.get("highlights", []),
            user_id=st.session_state.get("auth_user_id")
        )

        st.session_state["d_last_report"] = result
        st.session_state["d_last_profile"] = profile
        st.success(f"✅ 周报已生成并保存（ID: {report_id}）")
        st.rerun()

    # 展示最新生成的周报
    last_report = st.session_state.get("d_last_report")
    last_profile = st.session_state.get("d_last_profile", {})
    if last_report and last_profile.get("id") == profile["id"]:
        _render_structured_report(last_report, profile)


def _render_structured_report(report_data: dict, profile: dict):
    """渲染结构化四段式周报。"""
    st.markdown("---")

    # 报告标题
    title = report_data.get("title", f"{profile['name']} 健康周报")
    st.markdown(
        f"""<div style='background:linear-gradient(135deg,#1a2744,#21253A);
            border:1px solid #2E3250;border-radius:12px;padding:20px;
            margin-bottom:20px;text-align:center;'>
            <div style='color:#4F8EF7;font-size:22px;font-weight:700;'>
                {title}</div>
            <div style='color:#8892B0;font-size:13px;margin-top:6px;'>
                生成时间：{datetime.now().strftime("%Y-%m-%d %H:%M")}</div>
        </div>""",
        unsafe_allow_html=True
    )

    # ── 第一段：健康状况概览（评分式）────────────────────────────────────────
    st.markdown(
        """<div style='color:#4F8EF7;font-size:14px;font-weight:700;
            letter-spacing:2px;margin-bottom:12px;border-left:3px solid #4F8EF7;
            padding-left:12px;'>
            SECTION 01 · 健康状况概览</div>""",
        unsafe_allow_html=True
    )

    section1 = report_data.get("section1_overview", {})
    scores = section1.get("scores", {})
    if scores:
        score_cols = st.columns(len(scores))
        dim_colors = {
            "代谢健康": "#4F8EF7", "免疫力": "#A78BFA",
            "呼吸功能": "#2ECC71", "循环功能": "#E74C3C",
            "消化功能": "#F39C12", "骨骼健康": "#1ABC9C",
        }
        for i, (dim, score) in enumerate(scores.items()):
            with score_cols[i % len(score_cols)]:
                color = dim_colors.get(dim, "#4F8EF7")
                level = ("优秀" if score >= 85 else "良好" if score >= 70
                         else "一般" if score >= 55 else "需关注")
                st.markdown(
                    f"""<div style='background:{color}11;border:1px solid {color}33;
                        border-radius:10px;padding:12px;text-align:center;
                        margin-bottom:8px;'>
                        <div style='color:#8892B0;font-size:10px;'>{dim}</div>
                        <div style='color:{color};font-size:24px;font-weight:800;'>
                            {score}</div>
                        <div style='color:{color};font-size:10px;'>{level}</div>
                    </div>""",
                    unsafe_allow_html=True
                )

    overview_text = section1.get("summary", "")
    if overview_text:
        st.markdown(
            f"""<div style='background:#21253A;border:1px solid #2E3250;
                border-radius:10px;
padding:16px;margin-bottom:20px;'>
                <div style='color:#E8EAF6;font-size:13px;line-height:1.8;'>
                    {overview_text}</div>
            </div>""",
            unsafe_allow_html=True
        )

    # ── 第二段：本周异常深度解析 ─────────────────────────────────────────────
    st.markdown(
        """<div style='color:#E74C3C;font-size:14px;font-weight:700;
            letter-spacing:2px;margin:20px 0 12px;border-left:3px solid #E74C3C;
            padding-left:12px;'>
            SECTION 02 · 本周异常深度解析</div>""",
        unsafe_allow_html=True
    )

    section2 = report_data.get("section2_abnormal", {})
    abnormal_items = section2.get("items", [])
    if abnormal_items:
        for item in abnormal_items:
            severity_color = ("#E74C3C" if item.get("severity") == "高"
                              else "#F39C12" if item.get("severity") == "中"
                              else "#2ECC71")
            with st.expander(
                f"{'↑' if item.get('direction')=='偏高' else '↓'} "
                f"{item.get('indicator','—')} — {item.get('value','—')} "
                f"{item.get('unit','')}",
                expanded=True
            ):
                col1, col2 = st.columns([1, 2])
                with col1:
                    organs = item.get("organs", [])
                    if organs:
                        st.markdown(
                            "<div style='color:#8892B0;font-size:11px;margin-bottom:6px;'>"
                            "关联器官</div>",
                            unsafe_allow_html=True
                        )
                        for organ in organs:
                            st.markdown(
                                f"<span style='background:rgba(79,142,247,0.15);"
                                f"color:#4F8EF7;border:1px solid rgba(79,142,247,0.3);"
                                f"border-radius:20px;padding:3px 10px;font-size:11px;"
                                f"display:inline-block;margin:2px;'>🫀 {organ}</span>",
                                unsafe_allow_html=True
                            )
                with col2:
                    physiology = item.get("physiology_explanation", "")
                    if physiology:
                        st.markdown(
                            f"<div style='color:#E8EAF6;font-size:13px;line-height:1.7;'>"
                            f"{physiology}</div>",
                            unsafe_allow_html=True
                        )
                    risk = item.get("risk_assessment", "")
                    if risk:
                        st.markdown(
                            f"""<div style='background:{severity_color}11;
                                border:1px solid {severity_color}33;border-radius:8px;
                                padding:10px;margin-top:8px;'>
                                <div style='color:{severity_color};font-size:11px;
                                    font-weight:600;margin-bottom:4px;'>⚠️ 风险评估</div>
                                <div style='color:#E8EAF6;font-size:12px;'>{risk}</div>
                            </div>""",
                            unsafe_allow_html=True
                        )
    else:
        s2_text = section2.get("text", "")
        if s2_text:
            st.markdown(
                f"""<div style='background:#21253A;border:1px solid #2E3250;
                    border-radius:10px;padding:16px;margin-bottom:20px;'>
                    <div style='color:#E8EAF6;font-size:13px;line-height:1.8;'>
                        {s2_text}</div>
                </div>""",
                unsafe_allow_html=True
            )

    # ── 第三段：最新科研动态 ──────────────────────────────────────────────────
    st.markdown(
        """<div style='color:#A78BFA;font-size:14px;font-weight:700;
            letter-spacing:2px;margin:20px 0 12px;border-left:3px solid #A78BFA;
            padding-left:12px;'>
            SECTION 03 · 最新科研动态（PubMed 降级解读）</div>""",
        unsafe_allow_html=True
    )

    section3 = report_data.get("section3_research", {})
    papers = section3.get("papers", [])
    if papers:
        for paper in papers[:3]:
            relevance_color = ("#E74C3C" if paper.get("relevance") == "高"
                               else "#F39C12" if paper.get("relevance") == "中"
                               else "#2ECC71")
            st.markdown(
                f"""<div style='background:linear-gradient(135deg,#1a2744,#21253A);
                    border:1px solid #2E3250;border-radius:10px;padding:16px;
                    margin-bottom:12px;'>
                    <div style='display:flex;justify-content:space-between;
                        align-items:flex-start;margin-bottom:8px;'>
                        <div style='color:#4F8EF7;font-size:13px;font-weight:600;
                            flex:1;margin-right:12px;'>
                            📄 {paper.get("title","—")}</div>
                        <span style='background:{relevance_color}22;
                            color:{relevance_color};border:1px solid {relevance_color}44;
                            border-radius:20px;padding:2px 10px;font-size:10px;
                            white-space:nowrap;font-weight:600;'>
                            {paper.get("relevance","—")} 相关</span>
                    </div>
                    <div style='color:#8892B0;font-size:11px;margin-bottom:8px;'>
                        {paper.get("journal","—")} · {paper.get("year","—")}</div>
                    <div style='color:#E8EAF6;font-size:12px;line-height:1.7;
                        margin-bottom:8px;'>
                        <b style='color:#A78BFA;'>核心发现：</b>
                        {paper.get("key_finding","—")}</div>
                    <div style='background:rgba(167,139,250,0.08);border:1px solid
                        rgba(167,139,250,0.2);border-radius:8px;padding:10px;'>
                        <div style='color:#A78BFA;font-size:11px;font-weight:600;
                            margin-bottom:4px;'>💡 对您的意义（通俗解读）</div>
                        <div style='color:#E8EAF6;font-size:12px;line-height:1.6;'>
                            {paper.get("plain_language","—")}</div>
                    </div>
                </div>""",
                unsafe_allow_html=True
            )
    else:
        s3_text = section3.get("text", "")
        if s3_text:
            st.markdown(
                f"""<div style='background:#21253A;border:1px solid #2E3250;
                    border-radius:10px;padding:16px;margin-bottom:20px;'>
                    <div style='color:#E8EAF6;font-size:13px;line-height:1.8;'>
                        {s3_text}</div>
                </div>""",
                unsafe_allow_html=True
            )

    # ── 第四段：个性化学习建议 ────────────────────────────────────────────────
    st.markdown(
        """<div style='color:#2ECC71;font-size:14px;font-weight:700;
            letter-spacing:2px;margin:20px 0 12px;border-left:3px solid #2ECC71;
            padding-left:12px;'>
            SECTION 04 · 个性化学习建议</div>""",
        unsafe_allow_html=True
    )

    section4 = report_data.get("section4_learning", {})
    learning_items = section4.get("items", [])
    if learning_items:
        for item in learning_items:
            priority_color = ("#E74C3C" if item.get("priority") == "高"
                              else "#F39C12" if item.get("priority") == "中"
                              else "#2ECC71")
            st.markdown(
                f"""<div style='background:#21253A;border:1px solid #2E3250;
                    border-left:3px solid {priority_color};border-radius:8px;
                    padding:14px;margin-bottom:10px;'>
                    <div style='display:flex;justify-content:space-between;
                        align-items:center;margin-bottom:6px;'>
                        <div style='color:#E8EAF6;font-size:13px;font-weight:600;'>
                            📚 {item.get("topic","—")}</div>
                        <span style='background:{priority_color}22;color:{priority_color};
                            border:1px solid {priority_color}44;border-radius:20px;
                            padding:2px 10px;font-size:10px;font-weight:600;'>
                            {item.get("priority","—")} 优先</span>
                    </div>
                    <div style='color:#8892B0;font-size:12px;margin-bottom:6px;'>
                        {item.get("reason","")}</div>
                    <div style='color:#E8EAF6;font-size:12px;'>
                        <b style='color:#2ECC71;'>推荐资源：</b>
                        {item.get("resources","")}</div>
                </div>""",
                unsafe_allow_html=True
            )
    else:
        s4_text = section4.get("text", "")
        if s4_text:
            st.markdown(
                f"""<div style='background:#21253A;border:1px solid #2E3250;
                    border-radius:10px;padding:16px;'>
                    <div style='color:#E8EAF6;font-size:13px;line-height:1.8;'>
                        {s4_text}</div>
                </div>""",
                unsafe_allow_html=True
            )

    # 下载按钮
    st.markdown("---")
    full_md = report_data.get("full_markdown", "")
    if full_md:
        st.download_button(
            "📥 下载完整周报 (Markdown)",
            data=full_md.encode("utf-8"),
            file_name=(f"health_report_{profile['name']}_"
                       f"{datetime.now().strftime('%Y%m%d')}.md"),
            mime="text/markdown",
            use_container_width=True,
        )


def _render_history_tab(profile: dict):
    """历史周报标签页。"""
    st.markdown("### 📚 历史周报档案")

    reports = db.get_weekly_reports(profile["id"], user_id=st.session_state.get("auth_user_id"))
    if not reports:
        st.info("暂无历史周报，请先生成周报。")
        return

    for report in reports:
        highlights_raw = report.get("highlights", "[]")
        try:
            highlights = (json.loads(highlights_raw)
                          if isinstance(highlights_raw, str) else highlights_raw)
        except Exception:
            highlights = []
        hl_text = " · ".join(highlights) if highlights else "无特别提示"

        with st.expander(
            f"📅 {report['week_start']} ~ {report['week_end']} | {hl_text}",
            expanded=False
        ):
            st.markdown(report.get("content", ""))
            st.download_button(
                "📥 下载此份周报",
                data=report.get("content", "").encode("utf-8"),
                file_name=(f"health_report_{profile['name']}_"
                           f"{report['week_start']}.md"),
                mime="text/markdown",
                key=f"dl_{report['id']}",
            )
