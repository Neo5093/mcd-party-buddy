# WorkBuddy 开发对话上下文

> 本文件记录「麦门派对搭子 PartyBuddy」使用 WorkBuddy 开发的完整对话与执行上下文，用于大赛 WorkBuddy 联动奖励核验。
> 项目全程在 WorkBuddy 客户端中完成：需求分析、MCP 接入、技能开发、真实接口实测、代码编写、视频剪辑、物料制作。

## 使用到的 WorkBuddy 能力

- **自定义连接器（MCP）**：在 `~/.workbuddy/mcp.json` 配置麦当劳 MCP（streamableHttp + Bearer Token），期间排查并修复了「Authorization 缺少 Bearer 前缀」「客户端启动时才读配置不热加载」两个实际问题
- **技能（Skill）**：开发并装载 `party-buddy` 技能（SKILL.md + scripts + sample_data）
- **专家团（Expert Team）**：调用 skill-design-team 完成需求评审，产出 10 项开放问题清单并逐项拍板
- **GitHub 连接器**：验证仓库文件树、读取竞品 README、查询参赛 Issue 评论状态
- **本地执行**：Python 脚本编写与自测、ffmpeg 视频剪辑（字幕卡渲染/分段加速/拼接/GIF 导出）

## 会话一 · 2026-10-09（定题 + 接入 + 实测 + 建仓报名）

1. 用户给出麦当劳 GitHub 组织地址，要求了解活动与参赛方式 → 输出活动规则、时间线、奖励结构分析
2. 用户申请到 MCP Token，要求配置连接器 → 写入 `mcd-mcp` 配置并修正 Bearer 前缀，initialize 握手 HTTP 200 验证通过
3. 重启后连接器面板未显示新条目 → 定位为「客户端仅在启动时读取 mcp.json」，指导 UI 添加/重启解决
4. 输出 33 个 MCP 工具分类清单 + 6 个 Skill 融合方向候选 → 用户拍板「团建派对管家」差异化方向
5. 实测派对/团餐工具链路（mall-points-products 26 个在售活动、覆盖 300+ 城市、团餐 beType=6 工具齐备）
6. 专家团需求评审 → 10 项开放问题 → 用户拍板：双主线融合、全虚构数据、录屏止于确认页、命名「麦门派对搭子 PartyBuddy」
7. 创建项目骨架：README / CONTEST_DECLARATION（官方原文）/ MCP_INTEGRATION / skill/SKILL.md
8. **A 线真实链路实测**：25 人团建人均 45 → 三方案（分享狂欢实付 955.75，人均 38.23），满折阶梯真实生效；发现预约窗口仅 6 天、助餐服务与折扣联动等 6 条实战规则并回写 SKILL.md
9. **B 线真实链路实测**：疯狂动物城生日派对 → 北京 410 家门店 → 场次/成团逻辑全通；回写 5 条 B 线规则
10. 建仓 github.com/Neo5093/mcd-party-buddy（Public）并推送，在活动主仓库发 Issue #151 完成报名（官方机器人确认参赛成功）

## 会话二 · 2026-10-10（竞品侦察 + 代码补齐 + 视频物料 + 传播备稿）

1. 确认报名成功、RANKING.md 上榜（第 62 名），输出获奖路径拆解（前 100 保底 / 前 3 冲刺）
2. 竞品侦察：拉取头部项目 README（榜1 mcd-saver-strategist、榜2 同赛道 mcd-party-officer、mcd-group-order-captain），输出差距清单——最大缺口：缺可运行源代码（比赛硬性要求）
3. 用户拍板全做 → 完成 P0 代码骨架：
   - `scripts/mcd_client.py` 纯标准库 MCP 客户端（Token 走环境变量）
   - `scripts/team_feast.py` 团餐满折优化器（三套方案模板 + 阶梯计算 + 下一档差额提示）
   - `scripts/party_scout.py` 派对扫描 + 派对黄历（官方活动日历 × 可约日期）
   - `scripts/demo.py` 离线演示 + `scripts/selftest.py` 7 项断言全过（复现真实算价 955.75）
   - `sample_data/` 六个真实接口返回的脱敏样例
4. 合规文件：mcp-config.example.json（占位符）、LICENSE、README 架构图与目录结构
5. 录屏支持：产出 90 秒分镜手册（docs/record-guide.md）；为避免真实地址泄露，用 MCP 创建虚构演示地址「王府井大街255号 金拱门派对大厦7层」并实测可配送
6. 用户录制两条原片（团建 242s / 派对 258s）→ 抽帧定位关键画面 → ffmpeg 合成 92 秒成片（三张字幕卡 + 分段加速）→ docs/demo.mp4（2.9MB）+ demo.gif（2MB，458 帧），嵌入 README 首屏
7. 传播备稿：小红书/脉脉/掘金三平台成稿 + 投放节奏表（docs/promo/posts.md）；四组海报提示词（docs/promo/poster-prompts.md）
8. 用户据此制作两张海报（团建主视觉 + 生日派对），已收入 docs/promo/

## 产出清单

| 文件 | 说明 |
|---|---|
| skill/SKILL.md | 技能主文件（11 条实测规则沉淀） |
| scripts/ | MCP 客户端、满折优化器、派对扫描、demo、自测、卡片生成器 |
| sample_data/ | 真实接口脱敏样例（菜单/促销/助餐/费项/派对/活动日历） |
| docs/demo.mp4 + demo.gif | 90 秒双线演示视频与首屏 GIF |
| docs/demo.html | 效果演示页 |
| examples/ | 团建结算单卡、派对邀请函（可发群） |
| docs/promo/ | 三平台传播稿、海报提示词、两张海报 |
| docs/record-guide.md | 录屏作战手册 |

—— 全程使用 WorkBuddy 开发完成 · 2026-10-09 ~ 2026-10-10
