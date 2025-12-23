import streamlit as st
import PyPDF2
import os
from dotenv import load_dotenv
from dashscope import Generation
from dashscope.api_entities.dashscope_response import Role

# ===================== 全局配置与样式优化 =====================
st.set_page_config(
    page_title="AI简历智能分析系统",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义样式（优化视觉体验）
st.markdown("""
    <style>
    /* 标题样式 */
    .main-title {
        font-size: 2.5rem;
        font-weight: 700;
        color: #2E4057;
        text-align: center;
        margin-bottom: 2rem;
    }
    /* 卡片样式 */
    .card {
        background-color: #F8FAFC;
        border-radius: 10px;
        padding: 1.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        margin-bottom: 1.5rem;
    }
    /* 按钮样式 */
    .stButton>button {
        background-color: #3B82F6;
        color: white;
        border-radius: 8px;
        padding: 0.5rem 1.2rem;
        border: none;
    }
    .stButton>button:hover {
        background-color: #2563EB;
    }
    /* 提示文本 */
    .hint-text {
        color: #64748B;
        font-size: 0.9rem;
    }
    </style>
""", unsafe_allow_html=True)

# 加载环境变量
load_dotenv()

# 初始化会话状态
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "resume_text" not in st.session_state:
    st.session_state.resume_text = ""
if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = ""

# ===================== 页面标题 =====================
st.markdown('<div class="main-title">📄 AI简历智能分析系统</div>', unsafe_allow_html=True)

# ===================== 侧边栏配置 =====================
with st.sidebar:
    st.header("⚙️ 系统配置")

    # API-KEY配置
    api_key = st.text_input(
        "通义千问API-KEY",
        type="password",
        help="前往 https://dashscope.aliyun.com/ 获取，新用户有免费额度"
    ) or st.secrets.get("DASHSCOPE_API_KEY")

    # 分析维度选择
    st.subheader("📋 分析维度")
    analysis_dimensions = st.multiselect(
        "选择需要分析的维度（默认全选）",
        options=[
            "岗位匹配度评估",
            "核心技能提取",
            "简历短板分析",
            "优化建议生成",
            "项目经历点评",
            "求职竞争力评分"
        ],
        default=[
            "岗位匹配度评估",
            "核心技能提取",
            "简历短板分析",
            "优化建议生成"
        ]
    )

    # 目标岗位输入
    target_job = st.text_input(
        "目标岗位（选填）",
        placeholder="例如：数据分析师、Java开发工程师",
        help="填写后AI会针对性分析岗位匹配度"
    )

    # 重置按钮
    if st.button("🔄 重置所有数据", type="secondary"):
        st.session_state.chat_history = []
        st.session_state.resume_text = ""
        st.session_state.analysis_result = ""
        st.rerun()

    # 侧边栏提示
    st.markdown('<p class="hint-text">💡 支持PDF/TXT格式简历，暂不支持扫描版PDF</p>', unsafe_allow_html=True)

# ===================== 核心功能区 =====================
col1, col2 = st.columns([1, 1.2], gap="large")

# ---------------------- 左侧：简历上传与一键分析 ----------------------
with col1:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("📤 简历上传")

    # 简历上传组件
    uploaded_file = st.file_uploader(
        "上传你的简历",
        type=["pdf", "txt"],
        label_visibility="collapsed"
    )


    # 简历文本提取函数
    def extract_resume_text(file):
        """提取简历文本，处理PDF/TXT格式"""
        text = ""
        try:
            if file.type == "application/pdf":
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            elif file.type == "text/plain":
                text = file.read().decode("utf-8")
            return text.strip()
        except Exception as e:
            st.error(f"文本提取失败：{str(e)}")
            return ""


    # 提取并保存简历文本
    if uploaded_file:
        with st.spinner("正在解析简历内容..."):
            resume_text = extract_resume_text(uploaded_file)
            if resume_text:
                st.session_state.resume_text = resume_text
                st.success("✅ 简历解析成功！")

                # 简历文本预览
                with st.expander("📜 查看简历文本（前500字）"):
                    preview_text = resume_text[:500] + "..." if len(resume_text) > 500 else resume_text
                    st.text(preview_text)
            else:
                st.error("❌ 简历解析失败，请确认文件格式（非扫描版PDF）")

    # 一键分析按钮
    st.markdown("---")
    analyze_btn = st.button(
        "🚀 开始AI分析",
        disabled=not (st.session_state.resume_text and api_key),
        use_container_width=True
    )

    if analyze_btn:
        with st.spinner("AI正在深度分析简历..."):
            # 构建专业分析提示词
            dimensions_str = "、".join(analysis_dimensions)
            prompt = f"""
            你是资深的HR和简历优化专家，请基于以下简历内容，按照【{dimensions_str}】维度进行专业分析：

            【简历内容】
            {st.session_state.resume_text}

            【目标岗位】
            {target_job if target_job else "未指定，按通用标准分析"}

            【分析要求】
            1. 每个维度单独分节，用标题区分；
            2. 语言专业且易懂，给出具体、可落地的建议；
            3. 求职竞争力评分采用1-10分制，并说明评分理由；
            4. 避免空话套话，针对简历中的具体内容分析。
            """

            # 调用通义千问API
            try:
                os.environ["DASHSCOPE_API_KEY"] = api_key
                response = Generation.call(
                    model="qwen-turbo",
                    prompt=prompt,
                    temperature=0.6,  # 降低随机性，保证分析准确性
                    max_tokens=2000
                )

                if response.status_code == 200:
                    st.session_state.analysis_result = response.output.text
                    # 同步到聊天记录
                    st.session_state.chat_history.append(
                        ("assistant", f"已完成简历分析：\n{st.session_state.analysis_result}")
                    )
                    st.success("📊 简历分析完成！请查看右侧结果")
                else:
                    st.error(f"分析失败：{response.message}")
            except Exception as e:
                st.error(f"API调用失败：{str(e)}")
    st.markdown('</div>', unsafe_allow_html=True)

# ---------------------- 右侧：分析结果 + 智能问答 ----------------------
with col2:
    # 分析结果展示区
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("📊 AI分析结果")

    if st.session_state.analysis_result:
        st.markdown(st.session_state.analysis_result)
    else:
        st.markdown('<p class="hint-text" style="text-align:center;">上传简历并点击「开始AI分析」查看结果</p>',
                    unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # 智能问答区
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("💬 简历智能问答")
    st.markdown('<p class="hint-text">基于你的简历内容，解答任何相关问题（例如：如何优化项目经历？）</p>',
                unsafe_allow_html=True)

    # 展示聊天记录
    for role, content in st.session_state.chat_history:
        with st.chat_message(role):
            st.markdown(content)

    # 问答输入框
    user_question = st.chat_input(
        "请输入你的问题...",
        disabled=not (st.session_state.resume_text and api_key)
    )

    if user_question:
        # 添加用户问题到聊天记录
        st.session_state.chat_history.append(("user", user_question))
        with st.chat_message("user"):
            st.markdown(user_question)

        # 构建多轮对话上下文
        messages = [
            {
                "role": Role.SYSTEM,
                "content": f"""
                你是简历分析专家，所有回答必须基于以下简历内容：
                {st.session_state.resume_text}
                回答要求：专业、具体、贴合简历实际内容，避免无关建议。
                """
            },
            *[{"role": role, "content": content} for role, content in st.session_state.chat_history]
        ]

        # 调用AI回复
        with st.chat_message("assistant"):
            with st.spinner("正在思考最佳答案..."):
                try:
                    os.environ["DASHSCOPE_API_KEY"] = api_key
                    response = Generation.call(
                        model="qwen-turbo",
                        messages=messages,
                        temperature=0.7,
                        max_tokens=1500
                    )

                    if response.status_code == 200:
                        ai_answer = response.output.choices[0].message.content
                        st.markdown(ai_answer)
                        st.session_state.chat_history.append(("assistant", ai_answer))
                    else:
                        st.error(f"回答失败：{response.message}")
                except Exception as e:
                    st.error(f"问答调用失败：{str(e)}")
    st.markdown('</div>', unsafe_allow_html=True)

# ===================== 底部说明 =====================
st.markdown("---")
st.caption("© 2025 AI简历智能分析系统 | 数据仅临时存储，分析完成后自动清理")