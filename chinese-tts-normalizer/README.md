# chinese-tts-normalizer

中文 TTS 专有名词预处理中间件。

## 问题

主流中文 TTS 引擎（豆包、MiniMax、通义、讯飞、百度）在播报产品型号、技术参数时大面积翻车：

| 原文 | 常见 TTS 读法 | 正确读法 |
|---|---|---|
| i7-11800H | i七-一万一千八百H | i七-幺幺八零零H |
| RTX5090Ti | RTX五零九零 T-i | RTX五零九零钛 |
| mate80 | mate八十 | mate八零 |
| 5000mAh | 五零零零 m-A-h | 五千毫安时 |
| 1080P | 一千零八十P | 幺零八零P |
| R9000P | R九零零零P | R九千P |

> 我用同一段文本测了 5 款主流 TTS，没有一家全对。详见 [测试报告](docs/test-report.md)。

## 解决方案

在文本送入 TTS 引擎之前，用规则引擎将专有名词转换为正确的中文读音文本。

### 三层优先级架构

```
定义权词典  →  代差规则  →  最小阻力
 (最高)        (中)        (兜底)
```

1. **定义权词典**：硬编码的确定性映射（`iPhoneX → iPhone十`、`1080P → 幺零八零P`）
2. **代差规则**：根据产品迭代历史判断读法（`mate10` 前代 `mate9`，差1 → 读"十"；`mate80` 前代 `mate70`，差10 → 读"八零"）
3. **最小阻力**：取整读和逐位读中音节更短的（`9000` → "九千" 2音节 vs "九零零零" 4音节 → 选"九千"）

### 保护机制

高优先级规则处理过的文本会被"保护"起来，低优先级规则不会重复处理，避免冲突。

## 安装

```bash
pip install pypinyin
```

## 用法

```python
from normalizer import normalize

# 单行
result = normalize("联想R9000P售价8999元，搭载i7-11800H处理器")
print(result)
# → 联想R九千P售价八千九百九十九元，搭载i7-幺幺八零零H处理器

# 搭配任意 TTS 引擎
import edge_tts, asyncio

async def speak(text):
    normalized = normalize(text)
    comm = edge_tts.Communicate(normalized, "zh-CN-YunxiNeural")
    await comm.save("output.mp3")

asyncio.run(speak("华为mate80搭载麒麟9000处理器，5000mAh电池"))
```

## 自定义

### 添加定义权词典

```python
from normalizer import DEFINITION_DICT

# 添加你的专有名词
DEFINITION_DICT["Model3"] = "Model三"
DEFINITION_DICT["PS5"] = "PS五"
```

### 添加品牌代际

```python
from normalizer import BRAND_HISTORY

# 添加新品牌的产品迭代序列
BRAND_HISTORY["pixel"] = [1, 2, 3, 4, 5, 6, 7, 8, 9]
BRAND_HISTORY["galaxy"] = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 20, 21, 22, 23, 24, 25]
```

## 测试

```bash
python normalizer.py
```

输出示例：

```
原始：华为mate9是经典，mate10是一代经典，mate80刚刚发布
处理：华为mate九是经典，mate十是一代经典，mate八零刚刚发布

原始：i7-11800H处理器搭配5000mAh电池
处理：i7-幺幺八零零H处理器搭配五千毫安时电池

原始：联想R9000P售价8999元
处理：联想R九千P售价八千九百九十九元

原始：i7-7700闲鱼价格7700元
处理：i7-七七零零闲鱼价格七千七元
```

## 规则覆盖

| 类型 | 示例 | 规则层 |
|---|---|---|
| 处理器型号 | i7-11800H, R7-5800H | 后缀规则（连字符+逐位） |
| 显卡型号 | RTX5090Ti, GP76 | 后缀规则（Ti→钛, 字母+数字+字母） |
| 手机系列 | mate80, 小米15 | 代差规则 |
| 分辨率 | 1080P, 4K | 定义权词典 |
| 电池容量 | 5000mAh | 后缀规则（mAh→毫安时） |
| 特殊命名 | iPhoneX | 定义权词典 |
| 价格 | 8999元, 7700块 | 数字规则（整读+元/块/钱） |
| 通用数字 | 980, 9400 | 最小阻力（取更短音节） |

## 设计原则

这个项目解决的不是"TTS 质量"问题，而是**语义标准化**问题。TTS 引擎本身的语音质量已经很好，但它们缺乏对中文数字/型号/参数的语境理解。

核心思路：**不要让 TTS 去猜，直接告诉它怎么读。**

## License

MIT
