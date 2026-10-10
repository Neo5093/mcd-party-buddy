"""派对/体验营扫描器 + 派对黄历。

核心逻辑：
1. 在售过滤：status==2 且 upTime ≤ 今天 ≤ downTime（过期的明确剔除）
2. 可约日期：提前 3 天预订（date ≥ today + 3）
3. 场次评估：差 N 人成团提示、人数超上限预警、余位展示
4. 派对黄历：官方营销活动日历 × 可约日期 → 宜/可/忌
"""
import json
import os
from datetime import date, timedelta

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "sample_data")


def load(name):
    with open(os.path.join(DATA_DIR, name), encoding="utf-8") as f:
        return json.load(f)


def on_sale(products, today):
    """过滤在售活动：上架中且在兑换时间窗内。"""
    return [p for p in products
            if p.get("status") == 2 and p.get("upTime", "0000") <= today.isoformat() <= p.get("downTime", "9999")]


def bookable_dates(dates, today, min_lead_days=3):
    """可约日期：需提前 3 天预订。"""
    earliest = today + timedelta(days=min_lead_days)
    return [d for d in dates if date.fromisoformat(d) >= earliest]


def scout_sessions(sessions, headcount):
    """场次评估：返回带成团提示的列表。"""
    out = []
    for s in sessions:
        gap = max(0, s["partyMin"] - headcount)
        over = headcount > s["partyMax"]
        out.append({
            **s,
            "gapText": f"还差 {gap} 人成团" if gap else "已达成团线",
            "overText": f"⚠️ 超出上限（最多 {s['partyMax']} 人）" if over else "",
            "duration": f"{s['timeStart']}-{s['timeEnd']}",
        })
    return out


def almanac(dates, campaigns, today, min_lead_days=3):
    """派对黄历：宜=当天有官方活动且可约；可=可约但无活动；忌=不足提前量不可约。"""
    earliest = today + timedelta(days=min_lead_days)
    events = campaigns.get("events", {})
    rows = []
    for d in dates:
        dt = date.fromisoformat(d)
        if dt < earliest:
            mark, reason = "忌", f"不足 {min_lead_days} 天提前量"
        elif d in events:
            mark, reason = "宜", "当天有官方活动：" + "、".join(events[d][:2])
        else:
            mark, reason = "可", "正常可约"
        rows.append({"date": d, "mark": mark, "reason": reason})
    return rows


def scout(spu_id, headcount, today=None, data_dir=None):
    """一条链跑通：在售过滤 → 城市/门店 → 可约日期 → 场次 → 黄历。返回结构化结果。"""
    global DATA_DIR
    if data_dir:
        DATA_DIR = data_dir
    today = today or date.today()
    data = load("party.json")
    campaigns = load("campaigns.json")

    sale = on_sale(data["products"], today)
    product = next((p for p in sale if p["spuId"] == spu_id), None)
    if product is None:
        raise ValueError(f"spuId={spu_id} 不在在售列表（已下架或售罄）")

    dates = bookable_dates(data["dates"], today)
    stores = sorted(data["stores"], key=lambda s: s["distanceKm"])
    sessions = scout_sessions(data["sessions"], headcount)
    cal = almanac(data["dates"], campaigns, today)

    return {
        "product": product,
        "onSaleCount": len(sale),
        "droppedCount": len(data["products"]) - len(sale),
        "stores": stores,
        "bookableDates": dates,
        "sessions": sessions,
        "almanac": cal,
        "totalPrice": round(product["price"] * headcount, 2),
    }


def render(result, headcount):
    p = result["product"]
    out = [f"🎂 {p['spuName']} · ¥{p['price']:g}/人 × {headcount} 人 = ¥{result['totalPrice']:g}"]
    if p.get("partyPeople"):
        out.append(f"   成团 {p['partyPeople']} 人 · 时长约 {p.get('partyRange', 0) * 30} 分钟 · 需提前 3 天预订")
    out.append(f"   在售活动 {result['onSaleCount']} 个（已剔除过期 {result['droppedCount']} 个）")
    out.append("")
    out.append("📍 最近门店 Top 5：")
    for i, s in enumerate(result["stores"][:5], 1):
        out.append(f"  {i}. {s['name']}（{s['distanceKm']}km）")
    out.append("")
    out.append("📅 场次（可约日期 " + "、".join(d[5:] for d in result["bookableDates"]) + "）：")
    for s in result["sessions"]:
        line = f"  · {s['duration']} 余位 {s['leftNum']} · {s['gapText']}"
        if s["overText"]:
            line += " " + s["overText"]
        out.append(line)
    out.append("")
    out.append("🗓 派对黄历：")
    for r in result["almanac"]:
        out.append(f"  {r['mark']} {r['date']} {r['reason']}")
    return "\n".join(out)


if __name__ == "__main__":
    import sys
    sid = int(sys.argv[1]) if len(sys.argv) > 1 else 5224
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    print(render(scout(sid, n, today=date(2026, 10, 10)), n))
