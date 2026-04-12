# -*- coding: utf-8 -*-
"""
RAG 知识库问答 Web 应用（最终稳定版）
"""

import os
import tempfile
import warnings
import streamlit as st
from dotenv import load_dotenv
import requests

warnings.filterwarnings("ignore", category=UserWarning, module="torch")

os.environ['HF_HOME'] = '/tmp/.hf_cache'
os.environ['TRANSFORMERS_CACHE'] = '/tmp/.hf_cache'

from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

load_dotenv()
API_KEY = os.getenv("DEEPSEEK_API_KEY")
API_URL = "https://api.deepseek.com/v1/chat/completions"

# 页面配置必须放在最顶部
st.set_page_config(page_title="📚 PDF 智能问答", page_icon="🤖", layout="wide")

@st.cache_resource(show_spinner=False)
def load_embedding_model():
    with st.spinner("⏳ 首次运行正在下载 Embedding 模型（约 400MB），请稍候..."):
        return HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )

def main():
    st.title("📚 PDF 知识库问答机器人")
    st.markdown("上传任意 PDF 文件，即可针对内容进行智能问答。")

    # 初始化会话状态
    if "vector_store" not in st.session_state:
        st.session_state.vector_store = None
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "file_processed" not in st.session_state:
        st.session_state.file_processed = False

    with st.sidebar:
        st.header("📁 1. 上传 PDF")
        uploaded_file = st.file_uploader("选择一个 PDF 文件（支持中文）", type=["pdf"])

        if uploaded_file is not None:
            current_file_name = uploaded_file.name
            if "last_file_name" not in st.session_state or st.session_state.last_file_name != current_file_name:
                st.session_state.last_file_name = current_file_name

                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                    tmp_file.write(uploaded_file.getvalue())
                    tmp_path = tmp_file.name

                with st.spinner("⏳ 正在解析 PDF 并构建向量知识库..."):
                    try:
                        loader = PyPDFLoader(tmp_path)
                        documents = loader.load()
                        total_pages = len(documents)

                        text_splitter = RecursiveCharacterTextSplitter(
                            chunk_size=600, chunk_overlap=150,
                            separators=["\n\n", "\n", "。", "！", "？", "；", " ", ""]
                        )
                        chunks = text_splitter.split_documents(documents)
                        total_chunks = len(chunks)

                        embeddings = load_embedding_model()
                        persist_dir = tempfile.mkdtemp()
                        vector_store = Chroma.from_documents(
                            documents=chunks, embedding=embeddings, persist_directory=persist_dir
                        )

                        st.session_state.vector_store = vector_store
                        st.session_state.messages = []
                        st.session_state.file_processed = True
                        os.unlink(tmp_path)

                        st.success(f"✅ 成功加载 {total_pages} 页，切分为 {total_chunks} 个文本块")
                    except Exception as e:
                        st.error(f"❌ 处理 PDF 时出错：{str(e)}")
                        st.session_state.file_processed = False

        if st.session_state.get("file_processed"):
            st.info(f"📄 当前文件：{st.session_state.last_file_name}")

        st.divider()
        with st.expander("⚙️ 高级检索设置"):
            k_value = st.slider("检索段落数量", 2, 10, 6)
            temperature = st.slider("模型创造性", 0.0, 1.0, 0.3, 0.1)

    st.header("💬 2. 开始问答")
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("请输入你的问题（例如：这篇论文的主要贡献是什么？）"):
        if st.session_state.vector_store is None:
            st.error("请先在侧边栏上传 PDF 文件。")
        else:
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.spinner(f"🔍 正在检索 {k_value} 个最相关段落..."):
                docs = st.session_state.vector_store.similarity_search(prompt, k=k_value)
                context = "\n\n---\n\n".join([doc.page_content for doc in docs])

            with st.spinner("🤖 AI 正在分析上下文并生成答案..."):
                system_prompt = """你是一个严谨的学术助手，请严格基于以下提供的上下文来回答问题。
                重要规则：
                1. 如果上下文中有明确相关信息，请准确提取并组织语言回答。
                2. 如果上下文只包含部分相关信息，请仅基于已有信息回答，并指出可能存在的信息缺口。
                3. 如果上下文中完全没有相关信息，请如实回答：“根据提供的资料，无法回答该问题。”
                4. 绝对不要编造任何上下文之外的信息。"""

                messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"【参考资料】\n{context}\n\n【用户问题】\n{prompt}"}
                ]
                headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
                payload = {"model": "deepseek-chat", "messages": messages, "temperature": temperature, "max_tokens": 1000}

                try:
                    response = requests.post(API_URL, headers=headers, json=payload, timeout=45)
                    response.raise_for_status()
                    result = response.json()
                    answer = result["choices"][0]["message"]["content"]
                except requests.exceptions.Timeout:
                    answer = "❌ 请求超时，请稍后重试。"
                except requests.exceptions.RequestException as e:
                    answer = f"❌ API 调用失败：{str(e)}"
                except Exception as e:
                    answer = f"❌ 未知错误：{str(e)}"

            st.session_state.messages.append({"role": "assistant", "content": answer})
            with st.chat_message("assistant"):
                st.markdown(answer)
                with st.expander("🔎 查看检索到的参考资料（共 {} 段）".format(len(docs))):
                    for i, doc in enumerate(docs, 1):
                        st.markdown(f"**📄 片段 {i}**")
                        st.text(doc.page_content[:500] + ("..." if len(doc.page_content) > 500 else ""))
                        st.divider()

    st.divider()
    st.caption("💡 提示：上传新 PDF 会自动清空历史对话。调整右侧高级设置可优化回答效果。")

if __name__ == "__main__":
    main()