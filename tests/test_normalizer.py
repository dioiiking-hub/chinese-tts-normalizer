"""
chinese-tts-normalizer 单元测试
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from normalizer import (
    normalize, num_to_chinese_whole, num_to_chinese_whole_oral,
    num_to_chinese_digit, best_reading
)


def test_num_to_chinese_whole():
    assert num_to_chinese_whole("0") == "零"
    assert num_to_chinese_whole("8") == "八"
    assert num_to_chinese_whole("10") == "十"
    assert num_to_chinese_whole("80") == "八十"
    assert num_to_chinese_whole("500") == "五百"
    assert num_to_chinese_whole("9000") == "九千"
    assert num_to_chinese_whole("9400") == "九千四百"
    assert num_to_chinese_whole("8999") == "八千九百九十九"
    print("✅ num_to_chinese_whole")


def test_num_to_chinese_whole_oral():
    assert num_to_chinese_whole_oral("9000") == "九千"
    assert num_to_chinese_whole_oral("5000") == "五千"
    assert num_to_chinese_whole_oral("9400") == "九千四"  # 口语省略末位百
    assert num_to_chinese_whole_oral("980") == "九百八十"
    print("✅ num_to_chinese_whole_oral")


def test_num_to_chinese_digit():
    assert num_to_chinese_digit("7700") == "七七零零"
    assert num_to_chinese_digit("11800") == "幺幺八零零"
    assert num_to_chinese_digit("5090") == "五零九零"
    assert num_to_chinese_digit("80") == "八零"
    print("✅ num_to_chinese_digit")


def test_definition_dict():
    assert "iPhone十" in normalize("iPhoneX")
    assert "幺零八零P" in normalize("1080P视频")
    assert "七二零P" in normalize("720P游戏")
    assert "四K" in normalize("4K输出")
    print("✅ definition_dict")


def test_suffix_rules():
    # Ti → 钛
    assert "五零九零钛" in normalize("RTX5090Ti显卡")
    # mAh → 毫安时
    assert "五千毫安时" in normalize("5000mAh电池")
    # 连字符+数字+字母 → 逐位
    assert "幺幺八零零H" in normalize("i7-11800H处理器")
    assert "五八零零H" in normalize("R7-5800H")
    # 连字符+纯数字 → 逐位
    assert "七七零零" in normalize("i7-7700对比")
    # 字母+数字+字母 → 最小阻力
    assert "R九千P" in normalize("联想R9000P")
    assert "GP七六" in normalize("微星GP76")
    print("✅ suffix_rules")


def test_brand_generation():
    # mate: 代差≤1 → 整读
    result = normalize("mate9和mate10")
    assert "mate九" in result
    assert "mate十" in result
    # mate: 代差>1 → 逐位
    result2 = normalize("mate80和mate70")
    assert "mate八零" in result2
    assert "mate七零" in result2
    # 小米: 连续递增，代差=1 → 整读
    result3 = normalize("小米14和小米15")
    assert "小米十四" in result3
    assert "小米十五" in result3
    print("✅ brand_generation")


def test_price_rules():
    # 价格整读
    assert "八千九百九十九元" in normalize("售价8999元")
    assert "七千七块" in normalize("7700块")
    print("✅ price_rules")


def test_same_number_different_context():
    # 同一个数字 7700 在型号和价格中读法不同
    result = normalize("i7-7700闲鱼价格7700元")
    assert "七七零零" in result  # 型号：逐位
    assert "七千七元" in result  # 价格：整读
    print("✅ same_number_different_context")


def test_full_text():
    text = (
        "搭载R7-5800H、i7-7700和i7-11800H的联想R9000P和微星GP76"
        "同时搭载RTX5090Ti最强显卡"
    )
    result = normalize(text)
    assert "五八零零H" in result
    assert "七七零零" in result
    assert "幺幺八零零H" in result
    assert "R九千P" in result
    assert "GP七六" in result
    assert "五零九零钛" in result
    print("✅ full_text")


if __name__ == "__main__":
    test_num_to_chinese_whole()
    test_num_to_chinese_whole_oral()
    test_num_to_chinese_digit()
    test_definition_dict()
    test_suffix_rules()
    test_brand_generation()
    test_price_rules()
    test_same_number_different_context()
    test_full_text()
    print("\n🎉 全部测试通过！")
