import streamlit as st
import subprocess
import sys

st.set_page_config(page_title="环境诊断", layout="wide")
st.title("🔍 云端环境诊断")

# 1. Python 版本和路径
st.header("1. Python 环境")
st.code(f"版本: {sys.version}\n可执行文件: {sys.executable}\n路径: {sys.path}")

# 2. 已安装的包列表
st.header("2. 已安装的包（pip list）")
result = subprocess.run([sys.executable, "-m", "pip", "list"], capture_output=True, text=True)
st.code(result.stdout)

# 3. 尝试导入 sentence_transformers
st.header("3. 导入 sentence_transformers")
try:
    import sentence_transformers
    st.success(f"✅ 导入成功！版本: {sentence_transformers.__version__}")
except ImportError as e:
    st.error(f"❌ 导入失败: {e}")
    # 显示更详细的导入错误堆栈
    import traceback
    st.code(traceback.format_exc())

# 4. 尝试导入 transformers
st.header("4. 导入 transformers")
try:
    import transformers
    st.success(f"✅ 导入成功！版本: {transformers.__version__}")
except ImportError as e:
    st.error(f"❌ 导入失败: {e}")

# 5. 手动安装 sentence-transformers（强制重装）
st.header("5. 强制重装 sentence-transformers")
if st.button("执行重装（可能需要1分钟）"):
    with st.spinner("正在运行 pip install --force-reinstall sentence-transformers==2.2.2 ..."):
        proc = subprocess.run(
            [sys.executable, "-m", "pip", "install", "--force-reinstall", "sentence-transformers==2.2.2"],
            capture_output=True, text=True
        )
        st.code(proc.stdout)
        st.code(proc.stderr)
        if proc.returncode == 0:
            st.success("重装完成，请刷新页面或重启应用。")
        else:
            st.error("重装失败。")