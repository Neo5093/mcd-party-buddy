# MCP 集成说明

本文件说明「麦门派对搭子 PartyBuddy」对麦当劳 MCP Server 的实际使用情况、调用流程与业务价值。

## 使用的 MCP Server

| 项 | 值 |
|---|---|
| Server | `mcd-mcp` |
| 接入地址 | `https://mcp.mcd.cn` |
| 协议 | Streamable HTTP |
| 认证 | `Authorization: Bearer <Token>`（环境变量占位，不入库） |

## 使用的工具（15 个）

### A 线 · 企业团餐外送（beType=6）

| 工具 | 用途 |
|---|---|
| delivery-query-addresses | 获取/选择配送地址 |
| delivery-query-stores | 按地址查可配送门店（beType=6） |
| query-meals | 查可售餐品，按官方内置预算档位规则搭配（20-30 元=汉堡+小食……） |
| query-promotions | **团餐专属**：查门店满减/满折规则，由模型解读并计算最优搭配 |
| query-meal-assistance | 查团餐助餐服务（gmServiceCode） |
| query-store-coupons | 查该门店可用优惠券 |
| calculate-price | 计算总价（含优惠券/助餐服务/餐具），价格单位“分”→ 展示转“元” |
| create-order | 人工确认后创建订单，返回支付链接（支持 reservationDate 预约送达） |
| query-order / order-list | 下单后查进度/历史 |

### B 线 · 派对/体验营预约

| 工具 | 用途 |
|---|---|
| mall-points-products | 列派对商品（shopId=5；按 status=2 上架中 + downTime 未过期过滤） |
| query-party-city | 查可办城市（实测覆盖 300+ 城市） |
| query-party-store | 查城市下可办门店 |
| query-party-store-date | 查门店可约日期 |
| query-party-store-session | 查场次（含 partyMin/partyMax/leftNum，用于“差 N 人成团”提示） |
| party-order-create | 人工确认后创建预约单（包场=1/拼团=2） |

## 调用流程

**A 线**：收集人数+人均预算+送达时间 → 地址 → 门店 → 拉菜单与促销规则 → 生成 2-3 套搭配方案（确定性脚本计算最优组合，LLM 负责解读呈现）→ 方案对比表 → 人工确认 → create-order → 返回支付链接（用户自行支付）

**B 线**：收集派对类型+城市+日期偏好 → 过滤在售活动 → 城市 → 门店 → 日期 → 场次（余位/成团数）→ 人工确认 → party-order-create

## 业务价值

- 把「组织者」场景从 30 分钟人肉比价/翻场次，压缩到一次对话
- query-promotions 的满减规则解读是官方留给模型的开放命题，本技能用确定性计算兜底（scripts/team_feast.py），保证公开展示算价零出错
- 全流程真实交易闭环但安全可控：下单前强制确认、不自动支付

## 配套脚本（确定性计算层）

| 脚本 | 职责 | 对应 MCP 工具 |
|---|---|---|
| scripts/mcd_client.py | 纯标准库 MCP 客户端（Token 走环境变量） | 全部 |
| scripts/team_feast.py | 团餐三套方案模板 + 满折阶梯计算 + 下一档差额提示 | query-meals / query-promotions / query-meal-assistance / calculate-price |
| scripts/party_scout.py | 在售过滤、提前 3 天可约日期、成团提示、派对黄历 | mall-points-products / party 五件套 / campaign-calendar |
| scripts/demo.py | 离线双线演示（sample_data 为真实接口返回的脱敏样例） | — |
| scripts/selftest.py | 7 项断言自测，核心计算可安全迭代 | — |

在线模式由 Agent 通过 MCP 取数后交给脚本计算；离线模式（无 Token）可直接用样例数据体验。
