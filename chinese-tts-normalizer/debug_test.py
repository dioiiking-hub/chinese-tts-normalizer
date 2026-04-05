from normalizer import *

p = Protector()

# Test 1: definition dict on iPhoneX
text = "苹果iPhoneX依然保值"
text = normalize_spaces(text)
print(f"After normalize_spaces: {text}")
text = apply_definition_dict(text, p)
print(f"After definition_dict: {text}")
print(f"Protector store: {p.store}")

# Test 2: suffix rules on 5090Ti
p2 = Protector()
text2 = "RTX5090Ti显卡"
text2 = normalize_spaces(text2)
print(f"\nAfter normalize_spaces: {text2}")
text2 = apply_suffix_rules(text2, p2)
print(f"After suffix_rules: {text2}")
print(f"Protector store: {p2.store}")

# Test 3: 1080P definition dict
p3 = Protector()
text3 = "支持1080P和4K输出"
text3 = normalize_spaces(text3)
print(f"\nAfter normalize_spaces: {text3}")
text3 = apply_definition_dict(text3, p3)
print(f"After definition_dict: {text3}")
print(f"Protector store: {p3.store}")
text3 = apply_suffix_rules(text3, p3)
print(f"After suffix_rules: {text3}")
text3 = apply_number_rules(text3)
print(f"After number_rules: {text3}")
text3 = p3.restore(text3)
print(f"After restore: {text3}")

# Test 4: 5000mAh
p4 = Protector()
text4 = "搭载5000mAh电池"
text4 = normalize_spaces(text4)
print(f"\nAfter normalize_spaces: {text4}")
text4 = apply_definition_dict(text4, p4)
print(f"After definition_dict: {text4}")
text4 = apply_suffix_rules(text4, p4)
print(f"After suffix_rules: {text4}")
print(f"Protector store: {p4.store}")
text4 = apply_number_rules(text4)
print(f"After number_rules: {text4}")
text4 = p4.restore(text4)
print(f"After restore: {text4}")

# Test 5: brand generation mate80
p5 = Protector()
text5 = "mate80刚刚发布"
text5 = normalize_spaces(text5)
print(f"\nAfter normalize_spaces: {text5}")
text5 = apply_definition_dict(text5, p5)
text5 = apply_suffix_rules(text5, p5)
text5 = apply_brand_generation(text5, p5)
print(f"After brand_generation: {text5}")
print(f"Protector store: {p5.store}")
text5 = apply_number_rules(text5)
print(f"After number_rules: {text5}")
text5 = p5.restore(text5)
print(f"After restore: {text5}")
