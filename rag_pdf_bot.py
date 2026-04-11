# -*- coding: utf-8 -*-
"""
RAG 知识库问答机器人
功能：读取本地文档，基于文档内容回答问题
"""

import os
import requests
from dotenv import load_dotenv

# LangChain 相关
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

load_dotenv()

# --- 配置 ---
API_URL = "https://api.deepseek.com/v1/chat/completions"
API_KEY = os.getenv("DEEPSEEK_API_KEY")
DOCUMENT_PATH = "knowledge.txt"          # 你的文档路径
PERSIST_DIR = "chroma_db"                # 向量数据库存储目录

# --- 1. 加载文档并切分 ---
def load_and_split_document(file_path):
    """加载文档，切成小块"""
    loader = TextLoader(file_path, encoding="utf-8")
    documents = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=300,      # 每块最大字符数
        chunk_overlap=50,    # 块之间重叠字符数，避免切断上下文
    )
    chunks = text_splitter.split_documents(documents)
    print(f"✅ 文档已加载，切分成 {len(chunks)} 个文本块")
    return chunks

# --- 2. 创建向量数据库（使用免费本地 Embedding 模型）---
def create_vector_store(chunks):
    """将文本块向量化并存入 Chroma"""
    # 使用 HuggingFace 的轻量模型，第一次运行会下载（约 400MB）
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    # 创建向量库（如果已存在则加载，否则新建）
    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=PERSIST_DIR
    )
    print("✅ 向量数据库创建/更新成功")
    return vector_store

# --- 3. 检索相关文本块 ---
def retrieve_relevant_chunks(vector_store, query, k=3):
    """根据问题检索最相关的 k 个文本块"""
    docs = vector_store.similarity_search(query, k=k)
    return docs

# --- 4. 调用大模型生成答案 ---
def generate_answer(query, context_docs):
    """将检索到的上下文和问题一起发给 DeepSeek"""
    # 拼接上下文
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
        "max_tokens": 500
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
    print("📚 RAG 知识库问答机器人")
    print("=" * 50)

    # 检查文档是否存在
    if not os.path.exists(DOCUMENT_PATH):
        print(f"❌ 找不到文档：{DOCUMENT_PATH}")
        print("请先在项目文件夹中放置一个 knowledge.txt 文件。")
        return

    # 加载并处理文档（如果向量库已存在，可以跳过，这里每次都重建以确保最新）
    print("⏳ 正在处理文档...")
    chunks = load_and_split_document(DOCUMENT_PATH)
    vector_store = create_vector_store(chunks)

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