# AI 学习之旅：RAG PDF 问答系统

这是一个基于 DeepSeek 大模型和 Streamlit 的 PDF 知识库问答应用。上传任意 PDF，即可针对内容进行智能提问。

## 在线体验
👉 [点击访问](https://ai-pdf-web-zy.streamlit.app)

## 本地运行
1. 克隆仓库
2. 安装依赖：`pip install -r requirements.txt`
3. 设置环境变量 `DEEPSEEK_API_KEY`
4. 运行：`streamlit run app.py`

## 技术栈
- Python + Streamlit
- LangChain + ChromaDB
- DeepSeek API
- HuggingFace Embeddings
