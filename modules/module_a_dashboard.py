"""
模块 A：家庭成员驾驶舱 V2.0
六大真实医学维度雷达图 + 评分卡片 + 家庭健康对比。
"""

import streamlit as st
import json
from datetime import datetime
import database as db
import utils


def render():
    st.markdown("## 🏠 家庭成员驾驶舱")
    st.markdown(
        "<p style='color:#8892B0;margin-top:-10px;'>实时掌握每位家庭成员的健康状态</p>",
        unsafe_allow_html=True
    )

    user_id = st.session_state.get("auth_user_id")
    profiles = db.get_all_profiles(user_id) if user_id else []
    if not profiles:
        st.info("👋 欢迎使用 AnatomySelf！请先添加家庭成员档案。")
        _render_add_member_form()
        return

    # ── 成员选择卡片 ──────────────────────────────────────────────────────────
    st.markdown("#### 成员选择")
    cols = st.columns(min(len(profiles), 4))
    selected_id = st.session_state.get("selected_profile_id", profiles[0]["id"])

    for i, profile in enumerate(profiles[:4]):
        with cols[i]:
            abnormal = db.get_latest_abnormal_records(profile["id"], user_id=user_id)
            is_selected = profile["id"] == selected_id
            border_color = "#4F8EF7" if is_selected else "#2E3250"
            status_color = "#E74C3C" if abnormal else "#2ECC71"
            status_text  = f"⚠ {len(abnormal)}" if abnormal else "✓ 正常"
            age = datetime.now().year - (profile.get("birth_year") or 1990)

            st.markdown(
                f"""<div style='background:#21253A;border:2px solid {border_color};
                    border-radius:12px;padding:16px;text-align:center;
                    {"box-shadow:0 0 12px rgba(79,142,247,0.3);" if is_selected else ""}'>
                    <div style='font-size:36px;'>{profile['avatar_emoji']}</div>
                    <div style='color:#E8EAF6;font-weight:700;font-size:15px;
                        margin-top:6px;'>{profile['name']}</div>
                    <div style='color:#8892B0;font-size:11px;'>
                        {profile.get("relation","本人")} · {age} 岁 · {profile.get("gender","—")}</div>
                    <div style='color:{status_color};font-size:13px;
                        font-weight:600;margin-top:6px;'>{status_text}</div>
                </div>""",
                unsafe_allow_html=True
            )
            if st.button(f"查看 {profile['name']}", key=f"sel_{profile['id']}",
                         use_container_width=True):
                st.session_state["selected_profile_id"] = profile["id"]
                st.rerun()

    st.markdown("---")

    # ── 当前成员详细驾驶舱 ────────────────────────────────────────────────────
    profile = next((p for p in profiles if p["id"] == selected_id), profiles[0])
    records = db.get_records(profile["id"], user_id=user_id)
    abnormal = db.get_latest_abnormal_records(profile["id"], user_id=user_id)
    age = datetime.now().year - (profile.get("birth_year") or 1990)

    # 解析 JSON 字段
    try:
        allergies = json.loads(profile.get("allergies") or "[]")
    except Exception:
        allergies = []
    try:
        chronic = json.loads(profile.get("chronic_conditions") or "[]")
    except Exception:
        chronic = []

    st.markdown(f"### {profile['avatar_emoji']} {profile['name']} 的健康驾驶舱")

    # 基本信息指标
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric("年龄", f"{age} 岁")
    with c2: st.metric("性别", profile.get("gender", "—"))
    with c3: st.metric("血型", profile.get("blood_type", "—"))
    with c4: st.metric("体检记录", f"{len(records)} 条")

    # 过敏史 + 慢性病
    col_a, col_b = st.columns(2)
    with col_a:
        allergy_html = "".join(
            f"<span style='background:rgba(231,76,60,0.15);color:#E74C3C;"
            f"border:1px solid rgba(231,76,60,0.3);border-radius:20px;"
            f"padding:2px 10px;font-size:12px;margin-right:6px;'>⚠ {a}</span>"
            for a in allergies
        ) if allergies else "<span style='color:#8892B0;font-size:13px;'>无已知过敏</span>"
        st.markdown(
            f"<div style='background:#21253A;border:1px solid #2E3250;border-radius:10px;"
            f"padding:12px;'><div style='color:#8892B0;font-size:11px;margin-bottom:8px;'>"
            f"过敏史</div>{allergy_html}</div>",
            unsafe_allow_html=True
        )
    with col_b:
        chronic_html = "".join(
            f"<span style='background:rgba(243,156,18,0.15);color:#F39C12;"
            f"border:1px solid rgba(243,156,18,0.3);border-radius:20px;"
            f"padding:2px 10px;font-size:12px;margin-right:6px;'>🏥 {c}</span>"
            for c in chronic
        ) if chronic else "<span style='color:#8892B0;font-size:13px;'>无慢性病史</span>"
        st.markdown(
            f"<div style='background:#21253A;border:1px solid #2E3250;border-radius:10px;"
            f"padding:12px;'><div style='color:#8892B0;font-size:11px;margin-bottom:8px;'>"
            f"慢性病史</div>{chronic_html}</div>",
            unsafe_allow_html=True
        )

    st.markdown("---")

    # ── 健康预警 ──────────────────────────────────────────────────────────────
    if abnormal:
        st.markdown(f"#### 🚨 健康预警 — 最新检查发现 {len(abnormal)} 项异常指标")
        warn_cols = st.columns(min(len(abnormal), 3))
        for i, rec in enumerate(abnormal[:6]):
            with warn_cols[i % 3]:
                arrow = "↑" if rec.get("status") == "偏高" else "↓"
                color = "#E74C3C" if rec.get("status") == "偏高" else "#F39C12"
                st.markdown(
                    f"""<div style='background:rgba(231,76,60,0.08);border:1px solid rgba(231,76,60,0.3);
                        border-radius:10px;padding:14px;text-align:center;margin-bottom:8px;'>
                        <div style='color:#8892B0;font-size:11px;'>{rec['indicator_name']}</div>
                        <div style='color:{color};font-size:22px;font-weight:700;'>
                            {arrow} {rec['value']}</div>
                        <div style='color:#8892B0;font-size:11px;'>{rec['unit']}</div>
                        <div style='color:{color};font-size:12px;font-weight:600;'>
                            {rec.get("status","—")}</div>
                    </div>""",
                    unsafe_allow_html=True
                )
    else:
        st.success("✅ 最新检查所有指标均在正常范围内")

    st.markdown("---")

    # ── V2.0 六维健康雷达 + 评分卡片 ─────────────────────────────────────────
    st.markdown("#### 🎯 六维健康评分")

    # 计算六维评分
    scores = utils.compute_dimension_scores(records)
    avg_score = sum(scores.values()) / len(scores)
    overall_grade, overall_color = utils.get_dimension_grade(avg_score)

    # 综合评分横幅
    st.markdown(
        f"""<div style='background:linear-gradient(135deg,#1a2744,#21253A);
            border:1px solid #2E3250;border-radius:12px;padding:16px 24px;
            margin-bottom:20px;'>
            <div style='display:flex;align-items:center;gap:20px;'>
                <div style='text-align:center;min-width:80px;'>
                    <div style='font-size:42px;font-weight:800;color:{overall_color};
                        line-height:1;'>{avg_score:.0f}</div>
                    <div style='color:{overall_color};font-size:13px;font-weight:600;
                        margin-top:4px;'>{overall_grade}</div>
                    <div style='color:#8892B0;font-size:10px;'>综合健康评分</div>
                </div>
                <div style='flex:1;'>
                    <div style='color:#E8EAF6;font-size:14px;font-weight:600;margin-bottom:6px;'>
                        {profile["name"]} 的健康状况</div>
                    <div style='color:#8892B0;font-size:12px;line-height:1.6;'>
                        基于 {len(records)} 条体检记录，从代谢健康、免疫力、呼吸功能、
                        循环功能、消化功能、骨骼健康六个维度综合评估。
                        {"存在 " + str(len(abnormal)) + " 项异常指标需要关注。" if abnormal else "所有监测指标均在参考范围内。"}
                    </div>
                </div>
            </div>
        </div>""",
        unsafe_allow_html=True
    )

    # 六维评分卡片（3列布局）
    dim_cols = st.columns(3)
    for i, (dim_name, score) in enumerate(scores.items()):
        grade, grade_color = utils.get_dimension_grade(score)
        dim_cfg = utils.MEDICAL_DIMENSIONS[dim_name]
        with dim_cols[i % 3]:
            bar_width = int(score)
            bar_color = dim_cfg["color"]
            st.markdown(
                f"""<div style='background:#21253A;border:1px solid #2E3250;
                    border-radius:10px;padding:14px;margin-bottom:12px;'>
                    <div style='display:flex;justify-content:space-between;
                        align-items:center;margin-bottom:8px;'>
                        <div style='color:#E8EAF6;font-size:13px;font-weight:600;'>
                            {dim_cfg["icon"]} {dim_name}</div>
                        <div style='color:{grade_color};font-size:13px;
                            font-weight:700;'>{score:.0f}</div>
                    </div>
                    <div style='background:#2E3250;border-radius:4px;height:6px;
                        margin-bottom:6px;overflow:hidden;'>
                        <div style='background:{bar_color};height:100%;
                            width:{bar_width}%;border-radius:4px;'></div>
                    </div>
                    <div style='display:flex;justify-content:space-between;'>
                        <div style='color:#8892B0;font-size:10px;'>{dim_cfg["desc"]}</div>
                        <div style='color:{grade_color};font-size:10px;
                            font-weight:600;'>{grade}</div>
                    </div>
                </div>""",
                unsafe_allow_html=True
            )

    # 雷达图 + 维度说明
    radar_col, info_col = st.columns([3, 2])
    with radar_col:
        if records:
            fig_radar = utils.plot_health_radar(records, profile["name"])
            st.plotly_chart(fig_radar, use_container_width=True)
        else:
            st.info("暂无体检数据，请在「智能指标分析仪」中录入数据。")

    with info_col:
        st.markdown("**📊 维度说明**")
        for dim_name, dim_cfg in utils.MEDICAL_DIMENSIONS.items():
            score = scores[dim_name]
            grade, grade_color = utils.get_dimension_grade(score)
            indicators_str = "、".join(
                utils.INDICATOR_PHYSIOLOGY.get(code, {}).get("name", code)
                for code in list(dim_cfg["indicators"].keys())[:3]
            )
            st.markdown(
                f"""<div style='display:flex;align-items:center;gap:8px;
                    padding:6px 0;border-bottom:1px solid #2E3250;'>
                    <div style='font-size:16px;'>{dim_cfg["icon"]}</div>
                    <div style='flex:1;'>
                        <div style='color:#E8EAF6;font-size:12px;font-weight:600;'>
                            {dim_name}</div>
                        <div style='color:#8892B0;font-size:10px;'>{indicators_str}…</div>
                    </div>
                    <div style='color:{grade_color};font-size:12px;
                        font-weight:700;'>{score:.0f}</div>
                </div>""",
                unsafe_allow_html=True
            )

    st.markdown("---")

    # ── 添加新成员 ────────────────────────────────────────────────────────────
    with st.expander("➕ 添加新成员", expanded=False):
        _render_add_member_form()

    # ── 家庭健康对比 ──────────────────────────────────────────────────────────
    if len(profiles) > 1:
        st.markdown("#### 📊 家庭健康对比")
        family_data = {}
        for p in profiles:
            recs = db.get_records(p["id"], user_id=user_id)
            if recs:
                family_data[p["name"]] = recs
        if family_data:
            fig_compare = utils.plot_family_comparison(family_data)
            st.plotly_chart(fig_compare, use_container_width=True)


def _render_add_member_form():
    """渲染添加新成员表单。"""
    with st.form("add_member_form", clear_on_submit=True):
        st.markdown("**新成员基本信息**")
        col1, col2, col3 = st.columns(3)
        with col1:
            name = st.text_input("姓名 *", placeholder="如：若谷")
            relation = st.selectbox("关系", ["本人", "配偶", "儿子", "女儿",
                                              "父亲", "母亲", "兄弟", "姐妹", "其他"])
        with col2:
            birth_year = st.number_input("出生年份 *", min_value=1920,
                                          max_value=datetime.now().year, value=1990)
            gender = st.selectbox("性别", ["男", "女", "其他"])
        with col3:
            blood_type = st.selectbox("血型", ["A型", "B型", "O型", "AB型", "未知"])
            avatar = st.selectbox("头像", ["👤", "👨", "👩", "👦", "👧",
                                            "🧑", "👴", "👵", "🧒"])

        allergies_input = st.text_input("过敏史（逗号分隔）",
                                         placeholder="如：花粉, 青霉素, 海鲜")
        chronic_input = st.text_input("慢性病史（逗号分隔）",
                                       placeholder="如：高血压, 糖尿病")

        if st.form_submit_button("✅ 添加成员", type="primary", use_container_width=True):
            if not name:
                st.error("姓名不能为空！")
            else:
                allergies = [a.strip() for a in allergies_input.split(",") if a.strip()]
                chronic = [c.strip() for c in chronic_input.split(",") if c.strip()]
                new_id = db.create_profile(
                    name=name, relation=relation, birth_year=birth_year,
                    gender=gender, blood_type=blood_type,
                    allergies=allergies, chronic_conditions=chronic,
                    avatar_emoji=avatar,
                    user_id=st.session_state.get("auth_user_id")
                )
                st.session_state["selected_profile_id"] = new_id
                st.toast(f"✅ 成功添加成员！{name} 的档案已创建。", icon="👤")
                import time; time.sleep(1)
                st.rerun()
