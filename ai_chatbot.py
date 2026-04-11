# -*- coding: utf-8 -*-
"""
多轮对话机器人
功能：让 AI 记住上下文，实现连续对话
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_URL = "https://api.deepseek.com/v1/chat/completions"
API_KEY = os.getenv("DEEPSEEK_API_KEY")

def chat_with_ai(messages):
    """发送对话历史，返回 AI 的回答"""
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "deepseek-chat",
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 300
    }
    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()
        return result["choices"][0]["message"]["content"]
    except Exception as e:
        return f"❌ 出错了：{e}"

def main():
    print("=" * 50)
    print("🤖 多轮对话机器人已启动！")
    print("输入 '退出' 结束对话，输入 '清空' 重置记忆")
    print("=" * 50)

    # 初始化对话历史，system 消息设定 AI 的角色
    messages = [
        {"role": "system", "content": "你是一个友好、简洁的助手，回答尽量控制在三句话以内。"}
    ]

    while True:
        user_input = input("\n🧑 你：")
        if user_input.lower() in ["退出", "quit", "exit"]:
            print("👋 再见！")
            break
        if user_input.lower() in ["清空", "clear"]:
            messages = [messages[0]]  # 只保留 system 消息
            print("🧹 记忆已清空！")
            continue

        # 将用户输入加入历史
        messages.append({"role": "user", "content": user_input})

        # 调用 AI
        print("🤖 AI 思考中...")
        ai_response = chat_with_ai(messages)

        # 将 AI 回答加入历史
        messages.append({"role": "assistant", "content": ai_response})

        print(f"🤖 AI：{ai_response}")

if __name__ == "__main__":
    main()