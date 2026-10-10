"""传播物料生成器：团建结算单卡片 + 派对邀请函（单文件 HTML，可直接发群/分享）。

    python scripts/cards.py   # 用样例数据生成 examples/ 下的两个示例卡片
"""
import json
import os
import sys
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import team_feast
import party_scout

BASE = os.path.join(os.path.dirname(__file__), "..", "..")
STYLE = """
<style>
body{font-family:-apple-system,'PingFang SC','Microsoft YaHei',sans-serif;background:#f5f5f5;margin:0;padding:24px}
.card{max-width:420px;margin:0 auto;background:#fff;border-radius:16px;overflow:hidden;box-shadow:0 2px 12px rgba(0,0,0,.08)}
.hd{background:#DA291C;color:#fff;padding:20px 24px}
.hd h1{margin:0;font-size:20px}
.hd p{margin:6px 0 0;opacity:.9;font-size:13px}
.bd{padding:20px 24px}
table{width:100%;border-collapse:collapse;font-size:14px}
td,th{padding:8px 0;border-bottom:1px dashed #eee;text-align:left}
tr:last-child td{border-bottom:none}
.num{text-align:right;font-variant-numeric:tabular-nums}
.total{display:flex;justify-content:space-between;align-items:baseline;margin-top:12px;padding-top:12px;border-top:2px solid #DA291C}
.total b{font-size:26px;color:#DA291C}
.save{display:inline-block;background:#FFC72C;color:#5A3000;border-radius:6px;padding:2px 8px;font-size:12px;margin-top:8px}
.ft{padding:14px 24px;background:#fafafa;color:#999;font-size:12px;line-height:1.6}
.pill{display:inline-block;background:#FFC72C;color:#5A3000;border-radius:999px;padding:2px 10px;font-size:12px;margin-right:6px}
</style>
"""


def render_settlement_card(plan, headcount, store_name, deliver_time):
    rows = "".join(
        f"<tr><td>{l['name']} ×{l['qty']}</td><td class='num'>¥{l['subtotal']:g}</td></tr>"
        for l in plan["lines"])
    return f"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>团建结算单 · {plan['name']}</title>{STYLE}</head><body>
<div class="card">
  <div class="hd"><h1>🍟 团建结算单</h1><p>{store_name} · {deliver_time} 送达 · {headcount} 人</p></div>
  <div class="bd">
    <table><tr><th>餐品</th><th class="num">小计</th></tr>{rows}
    <tr><td>打包服务费</td><td class="num">¥{plan['packing']:g}</td></tr>
    <tr><td>配送费</td><td class="num">¥{plan['delivery']:g}</td></tr></table>
    <div class="total"><span>实付（{plan['discountLabel']}）</span><b>¥{plan['payTotal']:g}</b></div>
    <span class="save">比原价省 ¥{plan['saved']:g} · 人均 ¥{plan['perPerson']:g}</span>
  </div>
  <div class="ft">由「麦门派对搭子」生成 · 金额以麦当劳官方 calculate-price 核价为准 · 下单前请人工确认</div>
</div>
</body></html>"""


def render_invite(product, store, date_str, session, headcount):
    duration = f"{session['timeStart']}-{session['timeEnd']}"
    return f"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>派对邀请函 · {product['spuName']}</title>{STYLE}</head><body>
<div class="card">
  <div class="hd"><h1>🎉 派对邀请函</h1><p>{product['spuName']}</p></div>
  <div class="bd">
    <p><span class="pill">📅 {date_str}</span><span class="pill">⏰ {duration}</span></p>
    <p><span class="pill">📍 {store['name']}</span></p>
    <table>
      <tr><td>地址</td><td class="num">{store['address']}</td></tr>
      <tr><td>人数</td><td class="num">{headcount} 人（成团 {product.get('partyPeople', '见详情')}）</td></tr>
      <tr><td>费用</td><td class="num">¥{product['price']:g}/人</td></tr>
      <tr><td>场次余位</td><td class="num">{session['leftNum']}</td></tr>
    </table>
  </div>
  <div class="ft">由「麦门派对搭子」生成 · 需提前 3 天预订 · 价格与场次以麦当劳官方实时结果为准</div>
</div>
</body></html>"""


def main():
    out_dir = os.path.join(BASE, "examples")
    os.makedirs(out_dir, exist_ok=True)

    plans = team_feast.plan(25, 45.0)
    card = render_settlement_card(plans[0], 25, "麦当劳北京和平里东街餐厅", "2026-10-15 12:00")
    with open(os.path.join(out_dir, "settlement-card.html"), "w", encoding="utf-8") as f:
        f.write(card)

    result = party_scout.scout(5224, 10, today=date(2026, 10, 10))
    invite = render_invite(result["product"], result["stores"][0],
                           "2026-10-17（周六）", result["sessions"][0], 10)
    with open(os.path.join(out_dir, "party-invite.html"), "w", encoding="utf-8") as f:
        f.write(invite)

    print("已生成 examples/settlement-card.html 与 examples/party-invite.html")


if __name__ == "__main__":
    main()
