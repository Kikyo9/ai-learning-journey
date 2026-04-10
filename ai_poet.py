# -*- coding: utf-8 -*-
"""
我的第一个 AI 模型调用程序
功能：调用 DeepSeek 大模型，让 AI 写一首诗
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_URL = "https://api.deepseek.com/v1/chat/completions"
API_KEY = os.getenv("DEEPSEEK_API_KEY")

def ask_ai(prompt):
    """向 DeepSeek 发送请求并返回回答"""
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": "你是一位才华横溢的诗人，擅长用简洁优美的语言创作。"},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.8,  # 控制创造性，0~2 之间，越大越天马行空
        "max_tokens": 200
    }

    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        response.raise_for_status()  # 如果请求失败，抛出异常
        result = response.json()
        return result["choices"][0]["message"]["content"]
    except Exception as e:
        return f"❌ 出错了：{e}"

def main():
    print("=" * 40)
    print("🤖 AI 诗人已上线！")
    print("=" * 40)

    topic = input("请给一个主题（如：春天、代码、咖啡）：")
    print("\n⏳ AI 正在创作中...\n")

    poem = ask_ai(f"请以“{topic}”为主题，写一首四句的现代诗。")

    print("📜  AI 的作品：")
    print("-" * 20)
    print(poem)
    print("-" * 20)

if __name__ == "__main__":
    main()