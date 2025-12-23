import streamlit as st

# 网站标题
st.title("我的第一个 Streamlit 网站")
st.subheader("欢迎使用 Streamlit Community Cloud 部署")

# 交互组件：文本输入框
name = st.text_input("请输入你的名字")
if name:
    st.success(f"你好，{name}！恭喜你成功部署 Streamlit 网站！")

# 交互组件：按钮
if st.button("点击查看提示"):
    st.info("这个网站已经部署到 Streamlit Community Cloud 啦！")