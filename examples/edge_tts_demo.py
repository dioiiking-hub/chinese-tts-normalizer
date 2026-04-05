"""
Edge-TTS 对比验证示例
生成原始文本 vs normalizer 处理后的音频对比
"""
import asyncio
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from normalizer import normalize

import edge_tts

VOICE = "zh-CN-YunxiNeural"
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output")

TESTS = [
    (
        "完整测试",
        "搭载R7-5800H、i7-7700和i7-11800H的联想R9000P和微星GP76同时搭载RTX5090Ti最强显卡，"
        "搭载麒麟9000处理器和天玑9400芯片的掌机支持4K和1080P输出，"
        "当年的麒麟980处理器玩720P游戏帧率爆表，搭载5000mAh电池续航也能有20小时。"
        "华为致敬mate8的经典作品mate10是一代经典，而今mate80的发布，"
        "这让我想到了苹果iPhoneX，近期荣耀500系列。"
    ),
    (
        "同数字异语境",
        "i7-7700K是经典处理器，现在闲鱼收二手i7-7700大概要7700元，比新款便宜了7700块。"
    ),
    (
        "Mate代差",
        "mate8升级mate80，要加三千，mate80再升mate90，只要五百"
    ),
]

async def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    for label, text in TESTS:
        normalized = normalize(text)
        print(f"=== {label} ===")
        print(f"  原始：{text}")
        print(f"  处理：{normalized}")

        for suffix, content in [("原始", text), ("normalizer", normalized)]:
            filename = f"{label}_{suffix}.mp3"
            path = os.path.join(OUTPUT_DIR, filename)
            comm = edge_tts.Communicate(content, VOICE)
            await comm.save(path)
            print(f"  ✅ {filename}")
        print()

    print(f"全部生成完毕：{OUTPUT_DIR}")

if __name__ == "__main__":
    asyncio.run(main())
