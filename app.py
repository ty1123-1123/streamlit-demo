import streamlit as st
import PyPDF2
import time

# 全局配置（用原生布局，避免样式冲突）
st.set_page_config(page_title="简历分析系统", layout="wide")

# 初始化会话状态
if "resume_text" not in st.session_state:
    st.session_state.resume_text = ""
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# 三栏布局（原生组件，稳定显示）
col1, col2, col3 = st.columns([2, 1, 2])

# ---------------------- 左栏：简历分析 ----------------------
with col1:
    st.subheader("📄 简历分析")
    uploaded_file = st.file_uploader("上传简历（PDF/TXT）", type=["pdf", "txt"])

    # 提取简历
    if uploaded_file:
        try:
            if uploaded_file.type == "application/pdf":
                pdf_reader = PyPDF2.PdfReader(uploaded_file)
                st.session_state.resume_text = "\n".join(
                    [page.extract_text() for page in pdf_reader.pages if page.extract_text()])
            else:
                st.session_state.resume_text = uploaded_file.read().decode("utf-8")
            st.success("简历解析成功！")
        except:
            st.error("解析失败，请检查文件格式")

    # 分析按钮
    if st.button("开始分析"):
        if st.session_state.resume_text:
            st.info("### 简历分析结果\n1. 核心信息已识别\n2. 建议补充量化成果")
        else:
            st.warning("请先上传简历")

# ---------------------- 中栏：QQ企鹅 ----------------------
with col2:
    st.subheader("🤖 面试助手")
    # 本地图片（更稳定，需将企鹅图片存到代码同目录，命名为qq_penguin.png）
    # 若没有本地图片，用稳定在线链接：
    st.image("https://qlogo4.store.qq.com/qzone/10000/10000/100?1690000000", width=150)

# ---------------------- 右栏：交互对话 ----------------------
with col3:
    st.subheader("💬 交互对话")
    # 对话记录
    for role, msg in st.session_state.chat_history:
        st.chat_message(role).write(msg)

    # 初始消息
    if not st.session_state.chat_history:
        init_msg = "你好！可以咨询简历相关问题~"
        st.session_state.chat_history.append(("assistant", init_msg))
        st.chat_message("assistant").write(init_msg)

    # 输入框
    user_msg = st.chat_input("输入你的问题")
    if user_msg:
        st.session_state.chat_history.append(("user", user_msg))
        st.chat_message("user").write(user_msg)
        # 替换原“模拟回复”的代码
        if user_msg:
            st.session_state.chat_history.append(("user", user_msg))
            st.chat_message("user").write(user_msg)
            # 模板回复（无需API）
            time.sleep(1)
            # 根据问题匹配回复模板
            reply_templates = {
                "如何写好一份简历": """写好简历的核心要点：
        1. **结构清晰**：个人信息→求职意向→技能→经历→教育；
        2. **内容量化**：用数字描述成果（如“提升20%效率”）；
        3. **匹配岗位**：突出与目标岗位相关的技能/经历；
        4. **简洁精炼**：控制在1页内，避免冗余信息。""",
                "简历怎么突出优势": "突出优势的方法：\n1. 优势与岗位需求绑定；\n2. 用案例证明优势（如“擅长数据分析，曾完成XX报告”）；\n3. 放在简历前半部分，重点突出。",
                "默认回复": f"已收到你的问题：{user_msg}，后续会为你提供详细解答~"
            }
            # 匹配回复
            reply = reply_templates.get(user_msg, reply_templates["默认回复"])
            st.session_state.chat_history.append(("assistant", reply))
            st.chat_message("assistant").write(reply)