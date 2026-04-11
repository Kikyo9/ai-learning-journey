# -*- coding: utf-8 -*-
"""
RAG 知识库问答机器人 - PDF 版
功能：读取 PDF 文档，基于文档内容回答问题
"""

import os
import shutil
import requests
from dotenv import load_dotenv

# LangChain 相关
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

load_dotenv()

# --- 配置 ---
API_URL = "https://api.deepseek.com/v1/chat/completions"
API_KEY = os.getenv("DEEPSEEK_API_KEY")
DOCUMENT_PATH = "/Users/zhaopan/Desktop/ai-learning-journey/2604.08523v1.pdf"  # 加上 .pdf
PERSIST_DIR = "chroma_db"

# --- 1. 加载 PDF 并切分 ---
def load_and_split_pdf(file_path):
    """加载 PDF，切成小块"""
    loader = PyPDFLoader(file_path)
    documents = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,      # PDF 内容较密集，稍微大一点
        chunk_overlap=100,
    )
    chunks = text_splitter.split_documents(documents)
    print(f"✅ PDF 已加载，共 {len(documents)} 页，切分成 {len(chunks)} 个文本块")
    return chunks

# --- 2. 创建/更新向量数据库 ---
def create_vector_store(chunks, force_recreate=False):
    """将文本块向量化并存入 Chroma"""
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    # 如果强制重建，先删除旧数据库
    if force_recreate and os.path.exists(PERSIST_DIR):
        shutil.rmtree(PERSIST_DIR)
        print("🧹 旧向量数据库已删除，将重新构建")

    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=PERSIST_DIR
    )
    print("✅ 向量数据库创建/更新成功")
    return vector_store

# --- 3. 检索相关文本块 ---
def retrieve_relevant_chunks(vector_store, query, k=4):
    """根据问题检索最相关的 k 个文本块"""
    docs = vector_store.similarity_search(query, k=k)
    return docs

# --- 4. 调用大模型生成答案 ---
def generate_answer(query, context_docs):
    """将检索到的上下文和问题一起发给 DeepSeek"""
    context = "\n\n".join([doc.page_content for doc in context_docs])

    system_prompt = """你是一个知识渊博的助手，请严格根据以下提供的上下文来回答问题。
如果上下文中没有相关信息，请如实回答“根据提供的资料无法回答”。
不要编造任何信息。"""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"上下文：\n{context}\n\n问题：{query}"}
    ]

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "deepseek-chat",
        "messages": messages,
        "temperature": 0.3,
        "max_tokens": 800
    }

    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        result = response.json()
        return result["choices"][0]["message"]["content"]
    except Exception as e:
        return f"❌ 生成答案时出错：{e}"

# --- 主程序 ---
def main():
    print("=" * 50)
    print("📚 RAG 知识库问答机器人 (PDF)")
    print("=" * 50)

    if not os.path.exists(DOCUMENT_PATH):
        print(f"❌ 找不到 PDF 文件：{DOCUMENT_PATH}")
        return

    # 强制重建向量库（因为之前存的是乱码）
    print("⏳ 正在解析 PDF 并构建向量库...")
    chunks = load_and_split_pdf(DOCUMENT_PATH)
    vector_store = create_vector_store(chunks, force_recreate=True)

    print("\n✅ 初始化完成！现在可以提问了（输入 '退出' 结束）\n")

    while True:
        query = input("🧑 你的问题：").strip()
        if query.lower() in ["退出", "quit", "exit"]:
            print("👋 再见！")
            break
        if not query:
            continue

        print("🔍 正在检索相关段落...")
        relevant_docs = retrieve_relevant_chunks(vector_store, query)

        print("🤖 AI 思考中...")
        answer = generate_answer(query, relevant_docs)

        print(f"🤖 AI：{answer}\n")

if __name__ == "__main__":
    main()