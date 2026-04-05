import re
from pypinyin import pinyin, Style

# ===== 第一层：定义权词典 =====
DEFINITION_DICT = {
    "iPhoneX": "iPhone十",
    "iPhone X": "iPhone十",
    "YU7": "YU七",
    "1080P": "幺零八零P",
    "1080p": "幺零八零P",
    "720P": "七二零P",
    "720p": "七二零P",
    "4K": "四K",
    "2K": "二K",
}

# ===== 第二层：代差规则 =====
BRAND_HISTORY = {
    "mate": [7, 8, 9, 10, 20, 30, 40, 50, 60, 70, 80, 90],
    "小米": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15],
    "红米": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13],
}

# ===== 工具函数 =====

def normalize_spaces(text):
    text = re.sub(r'([a-zA-Z0-9])\s+([a-zA-Z0-9])', r'\1\2', text)
    text = re.sub(r'([\u4e00-\u9fff])\s+([a-zA-Z0-9])', r'\1\2', text)
    text = re.sub(r'([a-zA-Z0-9])\s+([\u4e00-\u9fff])', r'\1\2', text)
    return text

def count_syllables(text):
    result = pinyin(text, style=Style.NORMAL)
    return len(result)

def num_to_chinese_whole(num_str):
    """整体读法，不省略末位单位"""
    units = ["", "十", "百", "千", "万"]
    digits_map = ["零", "一", "二", "三", "四", "五", "六", "七", "八", "九"]
    num = int(num_str)
    if num == 0:
        return "零"
    result = ""
    s = str(num)
    length = len(s)
    for i, d in enumerate(s):
        digit = int(d)
        unit = units[length - i - 1] if length - i - 1 < len(units) else ""
        if digit != 0:
            result += digits_map[digit] + unit
        elif result and not result.endswith("零"):
            result += "零"
    result = result.rstrip("零")
    if result.startswith("一十"):
        result = result[1:]
    return result

def num_to_chinese_whole_oral(num_str):
    """
    整体读法+口语省略：
    只有末位全是零（整百整千）才省略最后单位
    9000→九千 ✓  5000→五千 ✓
    9400→九千四百（不省）✓  980→九百八十（不省）✓
    """
    result = num_to_chinese_whole(num_str)
    num = int(num_str)
    # 只有非整千的整百数才省略末位单位（9400→九千四，但 5000→五千 不省）
    if num % 100 == 0 and num % 1000 != 0:
        if result.endswith("百") and len(result) > 2:
            result = result[:-1]
    return result

def num_to_chinese_digit(num_str):
    """逐位读法，1读幺"""
    digits = {
        "0": "零", "1": "幺", "2": "二", "3": "三", "4": "四",
        "5": "五", "6": "六", "7": "七", "8": "八", "9": "九"
    }
    return "".join(digits[d] for d in num_str)

def best_reading(num_str):
    """最小阻力：取音节更短的读法"""
    whole = num_to_chinese_whole_oral(num_str)
    digit = num_to_chinese_digit(num_str)
    whole_syl = count_syllables(whole)
    digit_syl = count_syllables(digit)
    return whole if whole_syl <= digit_syl else digit

# ===== 保护机制（每次normalize重置）=====

class Protector:
    def __init__(self):
        self.store = []

    @staticmethod
    def _encode_idx(idx):
        """将数字索引编码为纯字母，避免被数字正则匹配"""
        if idx == 0:
            return 'a'
        chars = []
        while idx > 0:
            chars.append(chr(ord('a') + idx % 26))
            idx //= 26
        return ''.join(reversed(chars))

    @staticmethod
    def _decode_idx(s):
        """将字母编码还原为数字索引"""
        result = 0
        for c in s:
            result = result * 26 + (ord(c) - ord('a'))
        return result

    def protect(self, text):
        idx = len(self.store)
        self.store.append(text)
        tag = self._encode_idx(idx)
        return f"\x00{tag}\x00"

    def restore(self, text):
        def repl(m):
            return self.store[self._decode_idx(m.group(1))]
        return re.sub(r'\x00([a-z]+)\x00', repl, text)

# ===== 各层处理函数 =====

def apply_definition_dict(text, p):
    for word, replacement in DEFINITION_DICT.items():
        text = text.replace(word, p.protect(replacement))
    return text

# 非英文数字字符（用于边界判断）
_NOT_ALNUM = r'(?=[^A-Za-z0-9]|$)'
_NOT_ALNUM_BEFORE = r'(?<![A-Za-z0-9])'

def apply_suffix_rules(text, p):
    # 数字+Ti → 逐位+钛
    text = re.sub(
        r'(\d+)Ti' + _NOT_ALNUM,
        lambda m: p.protect(num_to_chinese_digit(m.group(1)) + "钛"),
        text
    )
    # 数字+mAh → 整体+毫安时
    text = re.sub(
        r'(\d+)[mM][aA][hH]' + _NOT_ALNUM,
        lambda m: p.protect(best_reading(m.group(1)) + "毫安时"),
        text
    )
    # 连字符后的数字+单字母（如11800H、5800H）→ 逐位+字母
    text = re.sub(
        r'(?<=-)(\d{4,})([A-Z])' + _NOT_ALNUM,
        lambda m: p.protect(num_to_chinese_digit(m.group(1)) + m.group(2)),
        text
    )
    # 连字符后的纯数字（如i7-7700、R7-5800）→ 逐位读
    text = re.sub(
        r'(?<=-)(\d{3,})' + _NOT_ALNUM,
        lambda m: p.protect(num_to_chinese_digit(m.group(1))),
        text
    )
    # 单字母+数字+单字母型号（如R9000P、GP76）→ 最小阻力读数字
    text = re.sub(
        _NOT_ALNUM_BEFORE + r'([A-Z]{1,2})(\d+)([A-Z])' + _NOT_ALNUM,
        lambda m: p.protect(
            m.group(1) + best_reading(m.group(2)) + m.group(3)
        ),
        text
    )
    return text


def apply_brand_generation(text, p):
    for brand in BRAND_HISTORY:
        history = BRAND_HISTORY[brand]
        pattern = re.compile(rf'(?<![A-Za-z])({re.escape(brand)})(\d+)')
        def replace(m, h=history):
            brand_name = m.group(1)
            num = int(m.group(2))
            if num > 99 or num not in h:
                return m.group(0)
            idx = h.index(num)
            if idx == 0:
                # 系列首款，整读
                reading = num_to_chinese_whole(str(num))
            else:
                diff = num - h[idx - 1]
                if diff <= 1:
                    # 代差≤1，整读（mate10前代mate9，差1→十）
                    reading = num_to_chinese_whole(str(num))
                else:
                    # 代差>1，逐位（mate20前代mate10，差10→二零）
                    reading = num_to_chinese_digit(str(num))
            return brand_name + p.protect(reading)
        text = pattern.sub(replace, text)
    return text

def apply_number_rules(text):
    """第三层：最小阻力，只处理未被保护的数字串
    - 后跟“元/块/钱”的数字 → 整体读法（价格）
    - 其他 → 最小阻力
    """
    # 价格：数字+元/块/钱
    text = re.sub(
        r'(\d{2,})([元块钱])',
        lambda m: num_to_chinese_whole_oral(m.group(1)) + m.group(2),
        text
    )
    # 其余数字：最小阻力
    text = re.sub(r'\d{2,}', lambda m: best_reading(m.group()), text)
    return text

def normalize(text):
    """
    中文TTS专有名词标准化主函数
    三层优先级：定义权 > 代差规则 > 最小阻力
    """
    p = Protector()
    text = normalize_spaces(text)
    text = apply_definition_dict(text, p)
    text = apply_suffix_rules(text, p)
    text = apply_brand_generation(text, p)
    text = apply_number_rules(text)
    text = p.restore(text)
    return text

if __name__ == "__main__":
    tests = [
        "华为mate9是经典，mate10是一代经典，mate80刚刚发布",
        "小米14和小米15的对比，小米10系列依然值得买",
        "荣耀500系列发布",
        "RTX5090Ti显卡支持1080P和4K输出",
        "i7-11800H处理器搭配5000mAh电池",
        "联想R9000P售价8999元",
        "天玑9400和麒麟9000的对比",
        "苹果iPhoneX依然保值",
        "微星GP76搭载RTX5090Ti",
        "搭载5000mAh电池续航20小时",
        "麒麟980处理器玩720P游戏",
        "R7-5800H和i7-7700对比",
        "i7-7700闲鱼价格7700元",
    ]
    print("=== chinese-tts-normalizer 测试 ===\n")
    for t in tests:
        result = normalize(t)
        print(f"原始：{t}")
        print(f"处理：{result}\n")
