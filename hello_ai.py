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


    ai_age = 3
    try:
        user_age = input("请问你今年多大啦？~")
        user_age = int(user_age)
        if user_age == ai_age:
            print(f"哇塞~你和我一样大，都是{ai_age}岁")
        elif user_age > ai_age:
            print(f"哦~那你比我大，咱们差{user_age-ai_age}岁呢~")
        else:
            print(f"哦~那你比我小诶，我比你大{ai_age-user_age}岁呢~")
    except:
        print("要好好输入你的年龄哦，那明明是一个数字呢~")
        

if __name__ == "__main__":
    main()
