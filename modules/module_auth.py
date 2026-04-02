"""
module_auth.py — AnatomySelf V5.5 认证界面模块
提供登录与注册的完整 UI 界面，采用深空暗黑风格。
"""
import streamlit as st
import auth
import database as db


def render():
    """渲染登录/注册界面。"""
    # ── 品牌标题区 ────────────────────────────────────────────────────────────
    st.markdown("""
    <div style="text-align:center; padding: 2.5rem 0 1.5rem 0;">
        <div style="
            font-family: 'JetBrains Mono', 'Courier New', monospace;
            font-size: 0.75rem;
            letter-spacing: 0.35em;
            color: #4A9EFF;
            text-transform: uppercase;
            margin-bottom: 0.5rem;
        ">PERSONAL LIFE LAB</div>
        <div style="
            font-size: 2.2rem;
            font-weight: 700;
            color: #E8EAF0;
            letter-spacing: 0.05em;
            line-height: 1.2;
        ">解剖自我</div>
        <div style="
            font-family: 'JetBrains Mono', 'Courier New', monospace;
            font-size: 0.7rem;
            letter-spacing: 0.2em;
            color: #3D9970;
            margin-top: 0.4rem;
        ">AnatomySelf · V5.5</div>
    </div>
    """, unsafe_allow_html=True)

    # ── 居中登录卡片 ──────────────────────────────────────────────────────────
    col_l, col_c, col_r = st.columns([1, 1.2, 1])
    with col_c:
        tab_login, tab_register = st.tabs(["登录", "注册"])

        # ── 登录 Tab ─────────────────────────────────────────────────────────
        with tab_login:
            st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
            username = st.text_input(
                "用户名",
                key="login_username",
                placeholder="请输入用户名",
            )
            password = st.text_input(
                "密码",
                type="password",
                key="login_password",
                placeholder="请输入密码",
            )
            st.markdown("<div style='height:0.3rem'></div>", unsafe_allow_html=True)

            if st.button("登录", use_container_width=True, type="primary", key="btn_login"):
                if not username.strip():
                    st.error("请输入用户名。")
                elif not password:
                    st.error("请输入密码。")
                else:
                    with st.spinner("验证中..."):
                        ok = auth.login(username.strip(), password)
                    if ok:
                        st.success(f"欢迎回来，{auth.get_current_display_name()}！")
                        st.session_state["current_page"] = "module_a"
                        st.rerun()
                    else:
                        st.error("用户名或密码错误，请重试。")

            st.markdown("""
            <div style="
                margin-top: 1.2rem;
                padding: 0.8rem;
                background: rgba(74, 158, 255, 0.06);
                border: 1px solid rgba(74, 158, 255, 0.15);
                border-radius: 8px;
                font-size: 0.78rem;
                color: #8B9BB4;
                text-align: center;
            ">
                演示账号：<code style="color:#4A9EFF">ruogu</code> / <code style="color:#4A9EFF">demo123</code>
            </div>
            """, unsafe_allow_html=True)

        # ── 注册 Tab ─────────────────────────────────────────────────────────
        with tab_register:
            st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
            reg_display = st.text_input(
                "真实姓名",
                key="reg_display",
                placeholder="您的真实姓名（用于档案显示）",
            )
            reg_username = st.text_input(
                "用户名",
                key="reg_username",
                placeholder="设置登录用户名（字母/数字）",
            )
            reg_birth = st.number_input(
                "出生年份（可选）",
                min_value=1900,
                max_value=2020,
                value=1990,
                step=1,
                key="reg_birth",
            )
            reg_gender = st.selectbox(
                "性别（可选）",
                options=["不填写", "男", "女"],
                key="reg_gender",
            )
            reg_password = st.text_input(
                "密码",
                type="password",
                key="reg_password",
                placeholder="至少 6 位密码",
            )
            reg_confirm = st.text_input(
                "确认密码",
                type="password",
                key="reg_confirm",
                placeholder="再次输入密码",
            )
            st.markdown("<div style='height:0.3rem'></div>", unsafe_allow_html=True)

            if st.button("注册账号", use_container_width=True, type="primary", key="btn_register"):
                # 基础校验
                if not reg_display.strip():
                    st.error("请输入真实姓名。")
                elif not reg_username.strip():
                    st.error("请输入用户名。")
                elif len(reg_username.strip()) < 3:
                    st.error("用户名至少需要 3 个字符。")
                elif len(reg_password) < 6:
                    st.error("密码至少需要 6 位。")
                elif reg_password != reg_confirm:
                    st.error("两次输入的密码不一致。")
                else:
                    gender_val = None if reg_gender == "不填写" else reg_gender
                    with st.spinner("创建账号中..."):
                        ok, err = auth.register(
                            username=reg_username.strip(),
                            display_name=reg_display.strip(),
                            password=reg_password,
                            birth_year=int(reg_birth),
                            gender=gender_val,
                        )
                    if ok:
                        st.success(f"注册成功！欢迎 {reg_display.strip()}！已自动创建您的「本人」档案。")
                        st.info("请切换到「登录」标签页进行登录。")
                    else:
                        st.error(f"注册失败：{err}")
