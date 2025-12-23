import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

st.title("我的交互型 Streamlit 网站")

# 1. 文本输入 + 按钮（基础交互）
user_name = st.text_input("请输入你的名字")
if st.button("提交名字"):
    if user_name:
        st.success(f"你好，{user_name}！")
    else:
        st.warning("请输入名字～")

# 2. 下拉选择框 + 滑块（多组件联动）
st.subheader("互动数据展示")
# 下拉选择：选择图表类型
chart_type = st.selectbox("选择图表类型", ["柱状图", "折线图"])
# 滑块：选择数据点数量
data_count = st.slider("选择数据点数量", min_value=5, max_value=20, value=10)

# 3. 生成随机数据并绘图（交互结果展示）
if st.button("生成图表"):
    x = np.arange(data_count)
    y = np.random.randint(1, 100, size=data_count)  # 随机数据

    fig, ax = plt.subplots()
    if chart_type == "柱状图":
        ax.bar(x, y, color="skyblue")
    else:
        ax.plot(x, y, color="salmon", marker="o")

    ax.set_title(f"{chart_type}展示（{data_count}个数据点）")
    st.pyplot(fig)