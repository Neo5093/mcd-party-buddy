# 麦门派对搭子 PartyBuddy 🎉🍟

> 一句话组局：企业团餐自动算满减，麦麦派对一键约场次。
> 基于麦当劳 MCP 的团建派对组织者专用 Skill。

![麦当劳 1024 程序员创意开发大赛参赛作品](https://img.shields.io/badge/1024-%E9%BA%A6%E5%BD%93%E5%8A%B3%E5%BC%80%E5%8F%91%E8%80%85%E5%A4%A7%E8%B5%9B-red)

**别的技能帮一个人点餐，这个技能帮一群人开趴。**

麦门派对搭子是「组织者视角」的麦当劳 Skill——不卷单人套餐推荐，专治行政/HR 和组局达人的两大麻烦事：

- 🏢 **团餐外送**：「周五下午 30 人团建，人均 40」→ 自动按预算搭配 → 解读门店满减/满折规则找到最优组合 → 支持预约送达 → 确认后下单
- 🎂 **派对/体验营预约**：生日派对、主题派对、品鉴会、读书会、麦麦体验营（职业体验营/消防体验营……）→ 选城市→门店→日期→场次，自动提示「差 N 人成团」

![90 秒双线演示](docs/demo.gif)

🎬 完整视频：[docs/demo.mp4](./docs/demo.mp4)（90 秒，片尾有求 Star 彩蛋）

## 为什么是它

| | 大众技能 | 麦门派对搭子 |
|---|---|---|
| 视角 | C 端：帮我点一份 | **B 端：帮一群人安排** |
| 难点 | 转发菜单 | 预算搭配 × 满减规则解读 × 成团管理 |
| 人群 | 每个打工人 | 行政/HR/组局人（传播语：转给你们订团建的同事） |

## 安装

1. 到 [open.mcd.cn](https://open.mcd.cn/mcp) 申请麦当劳 MCP Token（手机号登录 → 控制台 → 激活）
2. WorkBuddy → 左侧栏【专家·技能·连接器】→【连接器】→【自定义连接器】→ 配置 MCP：

```json
{
  "mcpServers": {
    "mcd-mcp": {
      "type": "streamableHttp",
      "url": "https://mcp.mcd.cn",
      "headers": {
        "Authorization": "Bearer <YOUR_MCP_TOKEN>"
      }
    }
  }
}
```

3. 安装本技能（skill/SKILL.md），在对话框里开聊

## 使用示例

**团餐线**
> “下周三中午 12 点，25 人团建，人均 45，送到公司，帮我看看怎么配最划算”
> —— 自动查门店促销规则，给出 2-3 套搭配方案（含优惠后总价、人均），你点头才下单。

**派对线**
> “想给孩子订个生日派对，北京，周末下午的场次”
> —— 列出可约门店/日期/场次余位，提示成团人数，确认后创建预约单。

## 离线体验（无需 Token）

```bash
python scripts/demo.py       # 双线全流程演示（样例数据来自真实接口，已脱敏）
python scripts/selftest.py   # 7 项自测断言
python scripts/cards.py      # 生成传播物料（结算单卡 + 派对邀请函）
```

📺 **效果演示页**：[docs/demo.html](./docs/demo.html)（浏览器打开即看双线真实输出）
📨 **传播物料示例**：[团建结算单](./examples/settlement-card.html) · [派对邀请函](./examples/party-invite.html)（单文件 HTML，可直接发群）

## 架构

```
用户一句话（人数/预算/时间/城市）
   │
   ▼
WorkBuddy Agent（理解需求、讲解方案、确认下单）
   │        │
   │        └──► scripts/（确定性计算：满折优化/场次评估/黄历）── 算术交给代码
   │
   ▼
麦当劳 MCP（mcp.mcd.cn）── 取数交给 MCP：菜单/促销/门店/场次/下单
   │
   ▼
calculate-price 核价 → 人工确认 → 下单
```

**设计原则**：取数交给 MCP，算术交给代码，表达交给 Agent。金额一律由脚本估算 + `calculate-price` 核价，模型不口算。

## 目录结构

```
mcd-party-buddy/
├── README.md                  # 本文件
├── CONTEST_DECLARATION.md     # 参赛声明（官方原文，未改动）
├── MCP_INTEGRATION.md         # MCP 集成说明
├── mcp-config.example.json    # 脱敏 MCP 配置（仅环境变量占位符）
├── LICENSE                    # MIT
├── skill/
│   └── SKILL.md               # 技能主文件（Agent 运行时加载）
├── scripts/
│   ├── mcd_client.py          # MCP 客户端（纯标准库，Token 走环境变量）
│   ├── team_feast.py          # 团餐满折优化器（三套方案模板+阶梯计算）
│   ├── party_scout.py         # 派对扫描 + 派对黄历
│   ├── demo.py                # 离线演示
│   └── selftest.py            # 自测断言
└── sample_data/               # 样例数据（2026-10-09~10 真实接口返回，已脱敏）
    ├── menu.json              # 菜单 54 个单品
    ├── promotions.json        # 团餐满折阶梯（GMS001/002/003 三档）
    ├── assistance.json        # 助餐服务
    ├── fees.json              # 打包费/运费样例
    ├── party.json             # 派对商品/城市/门店/日期/场次
    └── campaigns.json         # 官方活动日历（10 月）
```

## 目标用户

- 行政 / HR / 工会：团建订餐、亲子开放日、生日会
- 组局达人 / 家长：生日派对、主题派对、体验营
- 任何需要「帮一群人安排麦当劳」的人

## 安全边界

- ✅ 下单前强制展示清单并等待人工确认，**绝不自动支付**
- ✅ 价格/库存/场次以麦当劳官方实时结果为准
- ✅ 本仓库所有演示素材均为虚构数据，不含真实个人信息

## Roadmap

- [ ] 多地址分批订餐（行政真实场景）
- [ ] 积分账户联动（团餐攒积分提醒）
- [ ] 营养搭配维度（按热量预算配团餐）
- [ ] 成团人数凑单播报

## 参赛信息

麦当劳中国「1024 程序员创意开发大赛」参赛作品。参赛声明见 [CONTEST_DECLARATION.md](./CONTEST_DECLARATION.md)，MCP 集成说明见 [MCP_INTEGRATION.md](./MCP_INTEGRATION.md)。本项目为参赛者独立开发，非麦当劳官方产品。

## License

MIT（不含麦当劳商标与素材，相关内容权利归麦当劳所有）
