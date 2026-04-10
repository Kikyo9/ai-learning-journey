# -*- coding: utf-8 -*-
"""
我的第一个 AI 工程脚本
功能：询问用户名字，并调用系统信息
"""
import sys
import platform

def main():
    print("=" * 40)
    print("欢迎来到 AI 工程世界！")
    print(f"当前操作系统：{platform.system()} {platform.release()}")
    print(f"Python 版本：{sys.version.split()[0]}")
    print("=" * 40)

    name = input("你想给 AI 助手起什么名字？")
    print(f"\n你好，我是 {name}，你的 AI 学习伙伴。")
    print("我们的目标是：从零到一，成为 AI 工程师！")

if __name__ == "__main__":
    main()