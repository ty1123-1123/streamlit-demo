import streamlit as st

# 页面标题
st.title("我的第一个 Streamlit 网站")
st.write("欢迎使用 Streamlit Community Cloud 部署")

# 1. 文本输入框（获取用户输入）
user_name = st.text_input("请输入你的名字")

# 2. 按钮（触发交互）
if st.button("点击查看提示"):
    # 3. 逻辑处理：判断输入是否为空，返回不同反馈
    if user_name:
        st.success(f"你好，{user_name}！欢迎使用这个网站～")
    else:
        st.warning("请先输入你的名字哦！")
