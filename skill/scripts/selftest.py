"""自测：核心计算与过滤逻辑的断言保护。改逻辑后必跑。

    python scripts/selftest.py
"""
import os
import sys
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import team_feast
import party_scout

TODAY = date(2026, 10, 10)


def test_discount_math():
    ladder = [{"threshold": 300, "discount": 22}, {"threshold": 500, "discount": 26},
              {"threshold": 1000, "discount": 30}, {"threshold": 2000, "discount": 34}]
    tier = team_feast.best_tier(ladder, 1352.5)
    assert tier["discount"] == 30, tier
    assert team_feast.apply_discount(1352.5, 30) == 946.75
    gap = team_feast.next_tier_gap(ladder, 1352.5)
    assert gap["threshold"] == 2000 and gap["gap"] == 647.5, gap
    assert team_feast.best_tier(ladder, 299) is None
    print("✅ 满折阶梯计算（含下一档差额 647.5）")


def test_plans_reproduce_real_case():
    """复现 2026-10-09 真实算价：C 方案 25 人 应付 955.75（946.75+9 打包+0 运费）。"""
    results = team_feast.plan(25, 45.0)
    assert len(results) == 3
    by_name = {r["name"]: r for r in results}
    share = by_name["分享狂欢"]
    assert share["original"] == 1352.5, share["original"]
    assert share["payProducts"] == 946.75
    assert share["payTotal"] == 955.75, share["payTotal"]
    assert share["perPerson"] == 38.23
    assert by_name["经典四件套"]["payTotal"] == 1094.0   # 1085 + 9
    assert by_name["双堡管饱"]["payTotal"] == 1076.5     # 1067.5 + 9
    assert all(r["withinBudget"] for r in results)
    assert results[0]["name"] == "分享狂欢"  # 按实付升序，最便宜在前
    print("✅ 三套方案复现真实算价（分享狂欢 955.75 / 人均 38.23）")


def test_on_sale_filter():
    products = party_scout.load("party.json")["products"]
    sale = party_scout.on_sale(products, TODAY)
    ids = [p["spuId"] for p in sale]
    assert 15146 not in ids, "已过期的品虾会必须被剔除"
    assert 5224 in ids
    print(f"✅ 在售过滤（{len(products)} → {len(sale)}，过期品已剔除）")


def test_bookable_dates():
    dates = ["2026-10-10", "2026-10-11", "2026-10-12", "2026-10-13", "2026-10-17"]
    ok = party_scout.bookable_dates(dates, TODAY, min_lead_days=3)
    assert ok == ["2026-10-13", "2026-10-17"], ok  # 今天 10-10 + 3 天 = 10-13 起
    print("✅ 提前 3 天预订过滤")


def test_session_rules():
    sessions = [{"id": 1, "timeStart": "12:00", "timeEnd": "13:30",
                 "partyMin": 5, "partyMax": 12, "price": 58.0, "leftNum": 12}]
    ok = party_scout.scout_sessions(sessions, 10)
    assert ok[0]["gapText"] == "已达成团线" and not ok[0]["overText"]
    few = party_scout.scout_sessions(sessions, 3)
    assert few[0]["gapText"] == "还差 2 人成团"
    many = party_scout.scout_sessions(sessions, 13)
    assert "超出上限" in many[0]["overText"]
    print("✅ 成团提示 / 超限预警")


def test_almanac():
    dates = ["2026-10-11", "2026-10-14", "2026-10-15"]
    campaigns = {"events": {"2026-10-15": ["联名徽章发售"]}}
    rows = party_scout.almanac(dates, campaigns, TODAY)
    marks = {r["date"]: r["mark"] for r in rows}
    assert marks["2026-10-11"] == "忌"   # 不足 3 天提前量
    assert marks["2026-10-14"] == "可"
    assert marks["2026-10-15"] == "宜"   # 有官方活动
    print("✅ 派对黄历（宜/可/忌）")


def test_scout_end_to_end():
    r = party_scout.scout(5224, 10, today=TODAY)
    assert r["product"]["spuName"].startswith("麦当劳狂欢生日派对")
    assert r["totalPrice"] == 580.0
    assert r["droppedCount"] >= 1
    try:
        party_scout.scout(15146, 10, today=TODAY)
        raise AssertionError("过期商品应抛错")
    except ValueError:
        pass
    print("✅ 派对扫描端到端（含过期商品拒绝）")


if __name__ == "__main__":
    test_discount_math()
    test_plans_reproduce_real_case()
    test_on_sale_filter()
    test_bookable_dates()
    test_session_rules()
    test_almanac()
    test_scout_end_to_end()
    print("\n全部 7 项自测通过 ✅")
