"""
模块：隐私设置
管理用户隐私偏好、数据导出与账户安全设置。
"""

import streamlit as st
import json
import os
from datetime import datetime
import database as db


PRIVACY_DEFAULTS = {
    "data_local_only": True,
    "ai_analysis_enabled": True,
    "store_ai_results": True,
    "auto_weekly_report": False,
    "share_anonymous_data": False,
    "data_retention_days": 365,
    "lock_with_pin": False,
    "pin_hash": "",
    "display_real_name": True,
    "blur_sensitive_values": False,
}

PRIVACY_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".privacy_settings.json")


def load_privacy_settings() -> dict:
    if os.path.exists(PRIVACY_FILE):
        try:
            with open(PRIVACY_FILE, "r", encoding="utf-8") as f:
                saved = json.load(f)
                merged = {**PRIVACY_DEFAULTS, **saved}
                return merged
        except Exception:
            pass
    return dict(PRIVACY_DEFAULTS)


def save_privacy_settings(settings: dict):
    with open(PRIVACY_FILE, "w", encoding="utf-8") as f:
        json.dump(settings, f, ensure_ascii=False, indent=2)


def render():
    st.markdown("## 🔒 隐私设置")
    st.markdown(
        "<p style='color:#8892B0;margin-top:-10px;'>管理您的数据隐私、AI 使用偏好与账户安全</p>",
        unsafe_allow_html=True
    )

    settings = load_privacy_settings()

    # ── 数据安全概览卡片 ──────────────────────────────────────────────────────
    st.markdown("""
    <div style='background:linear-gradient(135deg,#1a2744,#21253A);border:1px solid #2E3250;
        border-radius:12px;padding:20px;margin-bottom:24px;'>
        <div style='display:flex;align-items:center;gap:12px;margin-bottom:12px;'>
            <div style='font-size:32px;'>🛡️</div>
            <div>
                <div style='color:#E8EAF6;font-weight:700;font-size:16px;'>数据安全状态：本地保护</div>
                <div style='color:#2ECC71;font-size:13px;'>✓ 所有数据存储在您的设备本地 SQLite 数据库中</div>
            </div>
        </div>
        <div style='display:grid;grid-template-columns:repeat(3,1fr);gap:12px;'>
            <div style='background:rgba(46,204,113,0.1);border:1px solid rgba(46,204,113,0.3);
                border-radius:8px;padding:10px;text-align:center;'>
                <div style='color:#2ECC71;font-size:20px;'>🔐</div>
                <div style='color:#8892B0;font-size:11px;margin-top:4px;'>本地存储</div>
                <div style='color:#2ECC71;font-size:12px;font-weight:600;'>已启用</div>
            </div>
            <div style='background:rgba(79,142,247,0.1);border:1px solid rgba(79,142,247,0.3);
                border-radius:8px;padding:10px;text-align:center;'>
                <div style='color:#4F8EF7;font-size:20px;'>🤖</div>
                <div style='color:#8892B0;font-size:11px;margin-top:4px;'>AI 分析</div>
                <div style='color:#4F8EF7;font-size:12px;font-weight:600;'>{"已启用" if settings["ai_analysis_enabled"] else "已禁用"}</div>
            </div>
            <div style='background:rgba(167,139,250,0.1);border:1px solid rgba(167,139,250,0.3);
                border-radius:8px;padding:10px;text-align:center;'>
                <div style='color:#A78BFA;font-size:20px;'>📊</div>
                <div style='color:#8892B0;font-size:11px;margin-top:4px;'>匿名统计</div>
                <div style='color:{"#E74C3C" if settings["share_anonymous_data"] else "#2ECC71"};font-size:12px;font-weight:600;'>{"已开启" if settings["share_anonymous_data"] else "已关闭"}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3, tab4 = st.tabs(["🔒 数据隐私", "🤖 AI 使用", "🗄️ 数据管理", "👤 显示偏好"])

    with tab1:
        st.markdown("### 数据存储与传输")
        col1, col2 = st.columns(2)
        with col1:
            settings["data_local_only"] = st.toggle(
                "仅本地存储（不上传云端）",
                value=settings["data_local_only"],
                help="开启后，所有健康数据仅保存在本设备的 SQLite 文件中，不会上传任何服务器。",
                key="priv_local_only"
            )
            settings["lock_with_pin"] = st.toggle(
                "启用 PIN 码锁定",
                value=settings["lock_with_pin"],
                help="每次打开应用时需要输入 4 位 PIN 码验证身份。",
                key="priv_pin_lock"
            )
        with col2:
            settings["share_anonymous_data"] = st.toggle(
                "分享匿名统计数据",
                value=settings["share_anonymous_data"],
                help="帮助改善 AnatomySelf 系统，所有数据完全匿名化处理，不包含任何个人信息。",
                key="priv_anon_share"
            )

        if settings["lock_with_pin"]:
            st.markdown("---")
            st.markdown("**设置 PIN 码**")
            pin_col1, pin_col2 = st.columns(2)
            with pin_col1:
                new_pin = st.text_input("新 PIN 码（4位数字）", type="password",
                                         max_chars=4, key="priv_new_pin")
            with pin_col2:
                confirm_pin = st.text_input("确认 PIN 码", type="password",
                                             max_chars=4, key="priv_confirm_pin")
            if st.button("保存 PIN 码", key="priv_save_pin"):
                if new_pin == confirm_pin and len(new_pin) == 4 and new_pin.isdigit():
                    import hashlib
                    settings["pin_hash"] = hashlib.sha256(new_pin.encode()).hexdigest()
                    save_privacy_settings(settings)
                    st.success("✅ PIN 码已设置！")
                else:
                    st.error("❌ PIN 码必须是 4 位数字，且两次输入一致。")

        st.markdown("---")
        st.markdown("### 数据保留期限")
        settings["data_retention_days"] = st.select_slider(
            "自动删除超过以下天数的旧数据",
            options=[30, 90, 180, 365, 730, 0],
            value=settings.get("data_retention_days", 365),
            format_func=lambda x: "永久保留" if x == 0 else f"{x} 天",
            key="priv_retention"
        )

    with tab2:
        st.markdown("### AI 代理使用偏好")
        st.info("💡 AI 分析功能会将您的健康数据（脱敏处理后）发送至 AI 接口进行分析。关闭后将无法使用智能解读功能。")

        settings["ai_analysis_enabled"] = st.toggle(
            "启用 AI 智能分析",
            value=settings["ai_analysis_enabled"],
            key="priv_ai_enabled"
        )
        settings["store_ai_results"] = st.toggle(
            "缓存 AI 分析结果（避免重复请求）",
            value=settings["store_ai_results"],
            help="将 AI 生成的分析结果保存到本地知识库，相同指标不重复请求，节省时间。",
            key="priv_store_ai"
        )
        settings["auto_weekly_report"] = st.toggle(
            "每周自动生成健康周报",
            value=settings["auto_weekly_report"],
            help="每周一凌晨自动为所有成员生成健康周报并保存到历史记录。",
            key="priv_auto_report"
        )

        st.markdown("---")
        st.markdown("### AI 数据脱敏规则")
        st.markdown("""
        <div style='background:#21253A;border:1px solid #2E3250;border-radius:8px;padding:16px;'>
            <div style='color:#8892B0;font-size:13px;line-height:1.8;'>
                发送给 AI 的数据经过以下脱敏处理：<br>
                ✅ <strong style='color:#E8EAF6;'>姓名</strong> → 替换为「用户A」<br>
                ✅ <strong style='color:#E8EAF6;'>出生年份</strong> → 仅保留年龄段（如「40-45岁」）<br>
                ✅ <strong style='color:#E8EAF6;'>具体日期</strong> → 替换为相对时间（如「本周」）<br>
                ✅ <strong style='color:#E8EAF6;'>指标数值</strong> → 保留，用于医学分析<br>
                ❌ <strong style='color:#E8EAF6;'>不发送</strong>：地理位置、设备信息、联系方式
            </div>
        </div>
        """, unsafe_allow_html=True)

    with tab3:
        st.markdown("### 数据导出")
        _uid = st.session_state.get("auth_user_id")
        profiles = db.get_all_profiles(user_id=_uid)
        if profiles:
            export_profile = st.selectbox(
                "选择导出成员",
                options=[p["name"] for p in profiles],
                key="priv_export_profile"
            )
            selected_p = next(p for p in profiles if p["name"] == export_profile)

            col_e1, col_e2, col_e3 = st.columns(3)
            with col_e1:
                records = db.get_records(selected_p["id"], user_id=_uid)
                if records:
                    import pandas as pd
                    df_records = pd.DataFrame(records)
                    csv_records = df_records.to_csv(index=False, encoding="utf-8-sig")
                    st.download_button(
                        "📥 导出体检记录 CSV",
                        data=csv_records,
                        file_name=f"{export_profile}_体检记录_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv",
                        key="priv_dl_records",
                        use_container_width=True
                    )
            with col_e2:
                symptoms = db.get_symptom_logs(selected_p["id"], user_id=_uid)
                if symptoms:
                    import pandas as pd
                    df_sym = pd.DataFrame(symptoms)
                    csv_sym = df_sym.to_csv(index=False, encoding="utf-8-sig")
                    st.download_button(
                        "📥 导出症状日志 CSV",
                        data=csv_sym,
                        file_name=f"{export_profile}_症状日志_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv",
                        key="priv_dl_symptoms",
                        use_container_width=True
                    )
            with col_e3:
                if st.button("📥 导出完整档案 JSON", use_container_width=True, key="priv_dl_json"):
                    full_data = {
                        "profile": selected_p,
                        "medical_records": db.get_records(selected_p["id"], user_id=_uid),
                        "symptom_logs": db.get_symptom_logs(selected_p["id"], user_id=_uid),
                        "export_time": datetime.now().isoformat()
                    }
                    st.download_button(
                        "点击下载 JSON",
                        data=json.dumps(full_data, ensure_ascii=False, indent=2),
                        file_name=f"{export_profile}_完整档案_{datetime.now().strftime('%Y%m%d')}.json",
                        mime="application/json",
                        key="priv_dl_json2"
                    )

        st.markdown("---")
        st.markdown("### 危险操作")
        with st.expander("⚠️ 清除成员数据（不可恢复）", expanded=False):
            st.warning("以下操作将永久删除该成员的所有数据，无法恢复！")
            del_profile = st.selectbox(
                "选择要清除数据的成员",
                options=[p["name"] for p in profiles] if profiles else [],
                key="priv_del_profile"
            )
            confirm_del = st.text_input(
                f"输入『确认删除{del_profile}』以确认",
                key="priv_del_confirm"
            )
            if st.button("删除成员档案", type="primary", key="priv_del_btn"):
                if confirm_del == f"确认删除{del_profile}":
                    target = next((p for p in profiles if p["name"] == del_profile), None)
                    if target:
                        db.delete_profile(target["id"], user_id=_uid)
                        st.toast(f"✅ 删除成功！{del_profile} 的所有数据已永久清除。", icon="🗑️")
                        import time; time.sleep(1)
                        st.rerun()
                else:
                    st.error("确认文字不匹配，操作已取消。")

        st.markdown("---")
        with st.expander("🚨 注销账号并永久抖除所有数据", expanded=False):
            st.error("警告：此操作将删除您的账号及所有关联的成员档案、体检记录、症状日志和周报，且无法恢复！")
            import auth as auth_module
            current_username = st.session_state.get(auth_module.SESSION_USERNAME, "未知用户")
            confirm_account_del = st.text_input(
                f"输入您的用户名『{current_username}』以确认注销",
                key="priv_del_account_confirm",
                type="password"
            )
            col_del1, col_del2 = st.columns([3, 1])
            with col_del1:
                if st.button(
                    "🗑️ 永久注销账号并抖除所有医疗数据",
                    type="primary",
                    use_container_width=True,
                    key="priv_del_account_btn"
                ):
                    if confirm_account_del == current_username:
                        if _uid:
                            success = db.delete_user_and_all_data(_uid)
                            if success:
                                st.success("✅ 账号已注销，所有数据已永久抖除。")
                                import time
                                time.sleep(2)
                                auth_module.logout()
                                st.rerun()
                            else:
                                st.error("注销失败，请联系管理员。")
                        else:
                            st.error("未登录，无法注销。")
                    else:
                        st.error("用户名不匹配，操作已取消。")
            with col_del2:
                st.markdown(
                    "<div style='color:#8892B0;font-size:11px;padding-top:8px;'>"
                    "此操作不可恢复，<br>请谨慎确认。</div>",
                    unsafe_allow_html=True
                )

    with tab4:
        st.markdown("### 界面显示偏好")
        settings["display_real_name"] = st.toggle(
            "在侧边栏显示真实姓名",
            value=settings["display_real_name"],
            key="priv_display_name"
        )
        settings["blur_sensitive_values"] = st.toggle(
            "模糊化敏感数值（悬停显示）",
            value=settings["blur_sensitive_values"],
            help="开启后，体检数值默认模糊显示，鼠标悬停时才显示真实数值。",
            key="priv_blur"
        )

    st.markdown("---")
    if st.button("💾 保存所有隐私设置", type="primary", use_container_width=True, key="priv_save_all"):
        save_privacy_settings(settings)
        st.success("✅ 隐私设置已保存！")
        st.rerun()
