"""团餐满折优化器 —— 确定性计算，不靠大模型口算。

核心逻辑：
1. 三套固定搭配模板（经典四件套 / 双堡管饱 / 分享狂欢），小食甜品按人头比例配（不必人手一份）
2. 满折阶梯：折后 = 原价 × (1 - discount/100)；discount=30 即 7 折
3. 助餐服务与折扣联动：GMS001 保鲜速达折扣最优，专人服务递减
4. 预算约束按「折后实付」判断；输出下一档门槛差额提示
金额估算以本模块为准，最终价格以下单前 calculate-price 核价为准。
"""
import json
import math
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "sample_data")

# 模板：别名 -> 每人份数（可 <1，表示按人头比例共享）
TEMPLATES = [
    {"key": "classic", "name": "经典四件套",
     "items": [("burger_mid", 1.0), ("fries", 1.0), ("pie", 1.0), ("cola", 1.0)]},
    {"key": "double", "name": "双堡管饱",
     "items": [("burger_light", 1.0), ("burger_cheese", 1.0), ("fries", 1.0), ("cola", 1.0)]},
    {"key": "share", "name": "分享狂欢",
     "items": [("burger_basic", 1.0), ("fries", 0.6), ("nuggets", 0.4),
               ("wings", 0.4), ("mcflurry", 0.4), ("cola", 1.0)]},
]

# 别名 -> 餐品 code（确定性选择，可按门店在售情况替换）
ALIASES = {
    "burger_mid": "901406",    # 板烧鸡腿堡 26.5
    "burger_light": "901450",  # 麦香鸡 18
    "burger_cheese": "901010", # 吉士汉堡包 16.5
    "burger_basic": "901000",  # 汉堡包 15
    "fries": "501205",         # 中薯条 15.5
    "pie": "904106",           # 香芋派 9
    "cola": "903050",          # 可口可乐中杯 11
    "nuggets": "901401",       # 麦乐鸡5块 15
    "wings": "901700",         # 麦辣鸡翅2块 16
    "mcflurry": "902372",      # 奥利奥麦旋风 16
}


def load(name):
    with open(os.path.join(DATA_DIR, name), encoding="utf-8") as f:
        return json.load(f)


def best_tier(ladder, original):
    """原价命中的最优档：threshold ≤ original 中 discount 最大的一档；无则 None。"""
    hit = None
    for tier in ladder:
        if original >= tier["threshold"] and (hit is None or tier["discount"] > hit["discount"]):
            hit = tier
    return hit


def next_tier_gap(ladder, original):
    """距下一档门槛还差多少原价；已是最高档则 None。"""
    higher = [t for t in ladder if t["threshold"] > original]
    if not higher:
        return None
    nxt = min(higher, key=lambda t: t["threshold"])
    return {"threshold": nxt["threshold"], "discount": nxt["discount"],
            "gap": round(nxt["threshold"] - original, 2)}


def apply_discount(original, discount_value):
    return round(original * (1 - discount_value / 100), 2)


def compose(template, headcount, menu):
    """按模板生成商品清单：[{code, name, price, qty, subtotal}]"""
    lines = []
    for alias, ratio in template["items"]:
        code = ALIASES[alias]
        item = menu["items"][code]
        qty = headcount if ratio >= 1.0 else math.ceil(headcount * ratio)
        lines.append({"code": code, "name": item["name"], "price": item["price"],
                      "qty": qty, "subtotal": round(item["price"] * qty, 2)})
    return lines


def plan(headcount, per_person_budget, data_dir=None):
    """生成三套方案，按实付升序。返回 dict 列表。"""
    global DATA_DIR
    if data_dir:
        DATA_DIR = data_dir
    menu = load("menu.json")
    promos = load("promotions.json")
    assist = load("assistance.json")
    fees = load("fees.json")
    budget_total = headcount * per_person_budget

    results = []
    for tpl in TEMPLATES:
        lines = compose(tpl, headcount, menu)
        original = round(sum(l["subtotal"] for l in lines), 2)
        # 选折扣最优的助餐服务档（实付最低）
        best = None
        for svc in assist["items"]:
            code = svc["gmServiceCode"]
            ladder = promos["ladders"].get(code)
            if not ladder:
                continue
            tier = best_tier(ladder, original)
            if not tier:
                continue
            pay_products = apply_discount(original, tier["discount"])
            pay_total = round(pay_products + fees["packingPrice"] + fees["deliveryPrice"], 2)
            if best is None or pay_total < best["payTotal"]:
                gap = next_tier_gap(ladder, original)
                best = {"service": svc["gmServiceName"], "gmServiceCode": code,
                        "tier": tier, "payProducts": pay_products, "payTotal": pay_total,
                        "ladder": ladder, "nextGap": gap}
        if best is None:
            continue
        results.append({
            "name": tpl["name"], "lines": lines, "original": original,
            "discountLabel": f"{best['tier']['threshold']}元档·{10 - best['tier']['discount'] / 10:g}折",
            "payProducts": best["payProducts"], "packing": fees["packingPrice"],
            "delivery": fees["deliveryPrice"], "payTotal": best["payTotal"],
            "perPerson": round(best["payTotal"] / headcount, 2),
            "saved": round(original - best["payProducts"] + fees["packingOriginal"] - fees["packingPrice"] + fees["deliveryOriginal"] - fees["deliveryPrice"], 2),
            "withinBudget": best["payTotal"] <= budget_total,
            "service": best["service"], "nextGap": best["nextGap"],
        })
    results.sort(key=lambda r: r["payTotal"])
    return results


def render(headcount, per_person_budget, results):
    """渲染 Markdown 对比表（可直接发群）。"""
    budget_total = headcount * per_person_budget
    out = [f"🍟 团餐方案 · {headcount} 人 × 人均 ¥{per_person_budget:g}（预算 ¥{budget_total:g}）", ""]
    out.append("| 方案 | 原价 | 满折 | 实付 | 人均 | 节省 | 预算内 |")
    out.append("|---|---|---|---|---|---|---|")
    for r in results:
        flag = "✅" if r["withinBudget"] else "❌ 超预算"
        out.append(f"| {r['name']} | ¥{r['original']:g} | {r['discountLabel']} | "
                   f"**¥{r['payTotal']:g}** | ¥{r['perPerson']:g} | ¥{r['saved']:g} | {flag} |")
    out.append("")
    cheapest = results[0] if results else None
    if cheapest and cheapest["nextGap"]:
        g = cheapest["nextGap"]
        out.append(f"💡 再点 ¥{g['gap']:g} 原价可升级 {g['threshold']} 元档"
                   f"（{10 - g['discount'] / 10:g} 折），省得更多。")
    out.append("")
    out.append("> 金额为估算，最终以下单前 calculate-price 核价为准；"
               f"助餐服务默认「{cheapest['service']}」（折扣最优），可升级专人分餐/摆台。")
    return "\n".join(out)


if __name__ == "__main__":
    import sys
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 25
    b = float(sys.argv[2]) if len(sys.argv) > 2 else 45.0
    print(render(n, b, plan(n, b)))
