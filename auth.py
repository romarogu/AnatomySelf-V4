"""
auth.py — AnatomySelf V5.5 认证会话管理模块
提供登录状态检查、用户 ID 获取等会话管理功能。
"""
import streamlit as st
import database as db

# ── Session State 键名常量 ──────────────────────────────────────────────────
SESSION_LOGGED_IN = "logged_in"
SESSION_USER_ID   = "user_id"
SESSION_USERNAME  = "username"
SESSION_DISPLAY   = "display_name"
SESSION_AVATAR    = "avatar"


def is_logged_in() -> bool:
    """检查当前用户是否已登录。"""
    return st.session_state.get(SESSION_LOGGED_IN, False)


def get_current_user_id() -> int | None:
    """获取当前登录用户的 ID，未登录返回 None。"""
    return st.session_state.get(SESSION_USER_ID, None)


def get_current_username() -> str:
    """获取当前登录用户的用户名，未登录返回空字符串。"""
    return st.session_state.get(SESSION_USERNAME, "")


def get_current_display_name() -> str:
    """获取当前登录用户的显示名称，未登录返回空字符串。"""
    return st.session_state.get(SESSION_DISPLAY, "")


def login(username: str, password: str) -> bool:
    """
    验证用户凭据并写入 session_state。
    返回 True 表示登录成功，False 表示失败。
    """
    user = db.authenticate_user(username, password)
    if user:
        st.session_state[SESSION_LOGGED_IN] = True
        st.session_state[SESSION_USER_ID]   = user["id"]
        st.session_state[SESSION_USERNAME]  = user["username"]
        st.session_state[SESSION_DISPLAY]   = user.get("display_name", username)
        st.session_state[SESSION_AVATAR]    = user.get("avatar", "🧑‍⚕️")
        return True
    return False


def logout():
    """清除所有登录相关的 session_state，实现登出。"""
    for key in [SESSION_LOGGED_IN, SESSION_USER_ID, SESSION_USERNAME,
                SESSION_DISPLAY, SESSION_AVATAR]:
        st.session_state.pop(key, None)
    # 清除页面导航状态
    st.session_state.pop("current_page", None)
    st.session_state.pop("selected_profile_id", None)
    st.rerun()


def register(username: str, display_name: str, password: str,
             birth_year: int = None, gender: str = None) -> tuple[bool, str]:
    """
    注册新用户。
    返回 (True, "") 表示成功，(False, "错误信息") 表示失败。
    """
    try:
        user_id = db.create_user(
            username=username,
            display_name=display_name,
            password=password,
            birth_year=birth_year,
            gender=gender,
        )
        if user_id:
            return True, ""
        return False, "用户名已存在，请更换用户名。"
    except Exception as e:
        return False, str(e)
