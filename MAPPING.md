# 项目 → 技能映射（MAPPING）

> 骨架 v1.0 · 2026-10-15
> 对象：`~/workspace/soc-home-lab/` 下 5 个项目（作者亲手完成）。
> 评分铁律：证据先行、范围后缀、L3 恒空、模糊取低。
> 证书对标说明：GSEC（作者备考中，SEC401/GSEC ~2026-12-28）、Security+、OSCP。
> "对标"指技能内容与证书 domain 有交集，可辅助备考；**不等于"达到证书水平"**。

---

## P1 · 01-mini-soc（AWS Mini SOC）

**做了什么**：Terraform 从零搭 CloudTrail→加密 S3→GuardDuty→Security Hub；
亲手跑 3 个 Stratus Red Team 攻击模拟（S3 数据渗出、IAM 提权、EC2 挖矿）；
写 triage-guide（GuardDuty finding 分诊）和 incident report 模板；
含 attack-runbook（ATT&CK 映射）与架构决策文档。

| 技能域 | 等级 | 一句话证据 |
|---|---|---|
| D1 安全监控与告警分诊 | **L2 (lab)** | 亲手跑攻击→在 GuardDuty 看到真实 finding→按自写分诊指南定级处置，全链路独立完成 |
| D2 日志分析与检测工程 | L1+ | 能读 CloudTrail 回答 who/what/where；讲得出 GuardDuty vs CloudTrail 覆盖盲区，但没写过生产检测规则 |
| D3 事件响应与报告 | **L2 (lab)** | 遏制 playbook（隔离 EC2、吊销凭证、回滚 S3 策略）+ 升级标准均为自写；报告模板达到"没在场能看懂"标准 |
| D6 云安全（AWS） | **L2 (lab)** | IaC 全栈自建、多区域 Trail、加密日志桶、最小权限 IAM 角色，全部亲手 terraform apply/destroy |
| D7 安全自动化与脚本 | L1 | 用了 Terraform 和现成工具，未自写分析代码（代码部分见 P2/P4） |

**证书对标**：GSEC —— 覆盖 incident handling / 日志分析实操面，强辅助备考；
Security+ —— 覆盖 architecture & operations 部分 domain；
OSCP —— 仅攻击者视角启蒙（知道攻击长什么样），**无实质对标**。

---

## P2 · 02-python-ioc-analyzer（Python IOC 分析器）

**做了什么**：亲手写的 Python CLI 工具：解析 CloudTrail JSON，
3 个启发式检测器（异地登录、暴力破解滑动窗口、高危 IAM/EC2 API），
AbuseIPDB 富化（无 key 优雅降级），输出 Markdown 事件报告；
9 个 pytest 测试；CLI 参数可调阈值。

| 技能域 | 等级 | 一句话证据 |
|---|---|---|
| D7 安全自动化与脚本 | **L2** | 独立写出带 CLI、错误处理、9 个测试的可用工具，README 他人可复现——这是硬证据 |
| D2 日志分析与检测工程 | **L2 (synthetic)** | 检测逻辑自写、阈值可调、有正反测试用例；但训练数据全合成，geo 启发式明确标注为 demo 级 |
| D1 安全监控与告警分诊 | L1 | 懂分诊概念，工具输出的是 findings 而非分诊决策 |

**证书对标**：GSEC —— Python/日志分析是 GSEC 实操加分项；
Security+ —— automation/scripting domain 有交集。
**不虚标**：启发式简单、单数据源（仅 CloudTrail），README 已如实写清局限。

---

## P3 · 03-phishing-analysis-lab（钓鱼邮件分析）

**做了什么**：header 分析 cheatsheet（SPF/DKIM/DMARC 速查）；
一份**复现样本**（明确标注 reconstructed）的端到端 walkthrough：
Received 链→发件人伪造→认证结果逐行解读→多层 URL 解码→附件 IOC→定级→Tier-1 处置；
GoPhish 自测指南（仅限自己邮箱，含合规边界）；空白报告模板（拒绝预填虚构案例）。

| 技能域 | 等级 | 一句话证据 |
|---|---|---|
| D4 钓鱼邮件分析 | **L2 (reconstructed)** | 独立走完"头→认证→URL 解码→IOC→verdict"全流程并写出带证据权重的分析；但样本是复现的，非真实钓鱼邮件量 |
| D3 事件响应与报告 | L1+ | 懂遏制/取证/上报流程，写过处置 playbook，但未实战 |

**证书对标**：GSEC / Security+ —— 钓鱼分析是两者共同覆盖的 Tier-1 核心技能，强辅助。
**诚实注**：Tier-1 分析师每天分诊数十封真实钓鱼；作者目前为复现样本训练，未达真实吞吐量。

---

## P4 · 04-rea-triage（ELF 二进制初筛）

**做了什么**：亲手写的 Python 静态分析工具：section 熵、高熵段、
W^X 可疑段、可疑 import（ptrace/memfd_create 等）、字符串 IOC 正则；
加权评分→三档 verdict（benign/suspicious/malicious）；
10 个 pytest 测试；自写 synthetic ELF 生成器做 demo；
方法论红线：初筛信号≠定罪、绝不执行样本。

| 技能域 | 等级 | 一句话证据 |
|---|---|---|
| D5 二进制/恶意软件初筛 | **L2 (synthetic)** | 独立写出带评分模型和 10 个测试的初筛工具；但仅 ELF、仅静态、样本全合成，无真实恶意软件分析 |
| D7 安全自动化与脚本 | **L2** | 第二个独立 Python 工具，pyelftools + pytest，证据链完整 |

**证书对标**：GSEC —— 恶意软件分析基础有交集；
OSCP —— **无对标**（纯防御向，无漏洞利用内容）；
**诚实注**：启发式粗糙、混淆字符串会漏报，README 已声明"起点而非 AV 定罪"。

---

## P5 · 05-soc-skills（5 个 MIT agent skills）

**做了什么**：把 P1–P4 的方法论蒸馏成 5 个 agent skill
（alert-triage / incident-report / cloudtrail-ioc / phishing-analysis / binary-triage），
每个 skill 声明触发条件、工作流、输出契约和拒绝边界。

| 技能域 | 等级 | 一句话证据 |
|---|---|---|
| —（元能力） | — | 不直接对应 D1–D7；作为"方法论系统化 + 文档工程"能力的证据，支撑 P1–P4 的 L2 评级可信度 |

**说明**：P5 的价值是证明作者能把实操沉淀为可复用的知识资产——这正是
SOC 团队里 Tier-1→Tier-2 晋升看重的 trait。HR 可读翻译："能写 playbook，能带新人。"

---

## 证书对标总表（诚实版）

| 证书 | 相关性 | 说明 |
|---|---|---|
| **GSEC**（备考中） | 强相关 | 5 个项目覆盖 incident handling、日志分析、钓鱼、恶意软件基础等实操面；是备考的**实践证据**，不是"已达到 GSEC 水平" |
| **Security+** | 中相关 | 覆盖 threats/attacks、architecture、operations 部分 domain；缺治理/合规/大量选择题知识面 |
| **OSCP** | 弱/无 | 作者工作纯防御向；仅 P1 的攻击模拟提供攻击者视角启蒙；**简历上不许出现 OSCP 字样** |

## 反虚标清单（面试前自查）

- [ ] 没说过"真实事件"——所有样本标注 synthetic / reconstructed
- [ ] 没说过"生产经验"——L3 恒空
- [ ] 没提 OSCP——防御向作者提 OSCP 是面试自杀
- [ ] 每个 L2 都有代码/报告/运行记录三选一的证据
- [ ] 被问"做过最难的部分"时有具体答案（02 的滑动窗口 / 04 的评分模型 / 01 的覆盖盲区分析）
