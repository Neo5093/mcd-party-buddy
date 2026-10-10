"""离线演示：无需 MCP Token，用样例数据跑通双线全流程。

    python scripts/demo.py

样例数据来自 2026-10-09~10 麦当劳 MCP 真实接口返回（已脱敏）。
"""
import os
import sys
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import team_feast
import party_scout


def main():
    print("=" * 56)
    print("麦门派对搭子 PartyBuddy · 离线演示（样例数据已脱敏）")
    print("=" * 56)

    print("\n【A 线 · 企业团餐】25 人团建，人均预算 ¥45，送到公司\n")
    print(team_feast.render(25, 45.0, team_feast.plan(25, 45.0)))

    print("\n" + "-" * 56)
    print("\n【B 线 · 派对预约】生日派对 · 北京 · 10 人\n")
    result = party_scout.scout(5224, 10, today=date(2026, 10, 10))
    print(party_scout.render(result, 10))

    print("\n" + "=" * 56)
    print("在线模式：配置 MCD_MCP_TOKEN 后由 Agent 调真实接口，")
    print("金额以 calculate-price 核价为准，下单前必须人工确认。")


if __name__ == "__main__":
    main()
