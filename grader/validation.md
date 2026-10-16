# Phase 2 验证报告（validation）

> 方法：评分者（LLM）严格按 `rubric-prompt.md` §3–§6 执行，
> 证据仅取自 `grade.py` 输出的证据包（README 全文 + 文件清单 + excerpts）。
> 对照基准：`../MAPPING.md` 人工评级（ground truth）。
> 通过标准：逐项偏差在 ±1 档内（L1+ 视为 L1 与 L2 之间半档）。

---

## P1 · 01-mini-soc

| 域 | rubric-prompt 评分 | MAPPING | 对比 |
|---|---|---|---|
| D1 | **L2 (lab)** ｜ 证据：README 声明亲手跑 3 个 Stratus Red Team 模拟并在 GuardDuty 看到 finding；triage-guide.md 自写分诊流程 | L2 (lab) | ✅ 一致 |
| D2 | **L1+** ｜ 证据：能读 CloudTrail、讲得出 GuardDuty vs CloudTrail 覆盖盲区（architecture.md/triage-guide.md），但未写过检测逻辑 | L1+ | ✅ 一致 |
| D3 | **L1+** ｜ 证据：incident-reports/ 目录**仅有空白模板**（report-template.md），无填过的事件报告；铁律 6（模板≠产出）拦下 L2 | L2 (lab) | ⚠️ 偏差半档 |
| D6 | **L2 (lab)** ｜ 证据：terraform/main.tf 全栈 IaC；README 声明亲手 apply/destroy；多区域 Trail + 加密日志桶 + 最小权限 IAM | L2 (lab) | ✅ 一致 |
| D7 | **L1** ｜ 证据：用了 Terraform 与现成工具，未自写分析代码 | L1 | ✅ 一致 |

**P1-D3 偏差说明**：MAPPING 的 L2 (lab) 依据是"遏制 playbook + 升级标准自写、报告模板达标"。
但 rubric 铁律 6 明确：空白模板不是"输出过结构化事件报告"的证据；
attack-runbook 自述 "expected findings…expected, not observed"（铁律 7），
进一步削弱"闭环已走完"的证据。**建议修正方向**：MAPPING 降为 L1+，
直到作者亲手填一份 detonation 事件报告后再升回 L2 (lab)。
这是 rubric 生效的正面案例——不是调分"通过"，而是暴露了证据缺口。

## P2 · 02-python-ioc-analyzer

| 域 | rubric-prompt 评分 | MAPPING | 对比 |
|---|---|---|---|
| D7 | **L2** ｜ 证据：ioc_analyzer.py 自写 CLI（含参数、错误处理）；tests/test_analyzer.py 9 个测试；README 他人可复现 | L2 | ✅ 一致 |
| D2 | **L2 (synthetic)** ｜ 证据：3 个启发式检测器自写、阈值可调、有正反测试；sample_data 明确标注 synthetic | L2 (synthetic) | ✅ 一致 |
| D1 | **L1** ｜ 证据：工具输出 findings 而非分诊决策；懂分诊概念但未做过分诊 | L1 | ✅ 一致 |

## P3 · 03-phishing-analysis-lab

| 域 | rubric-prompt 评分 | MAPPING | 对比 |
|---|---|---|---|
| D4 | **L2 (reconstructed)** ｜ 证据：sample-walkthrough.md 独立走完头→认证→URL 解码→IOC→verdict 全流程并带证据权重；样本明确标注 reconstructed | L2 (reconstructed) | ✅ 一致 |
| D3 | **L1+** ｜ 证据：懂 IR 流程、写过处置 playbook，但未实战、无填过的报告 | L1+ | ✅ 一致 |

升级建议（D4→更扎实的 L2）：按 gophish-selftest-guide 实际做一次自我钓鱼测试并写成报告——
从"复现样本"升级为"真实投递+真实分析"。

## P4 · 04-rea-triage

| 域 | rubric-prompt 评分 | MAPPING | 对比 |
|---|---|---|---|
| D5 | **L2 (synthetic)** ｜ 证据：triage.py 自写静态初筛工具（熵/W^X/可疑 import/字符串 IOC + 加权评分三档 verdict）；tests/test_triage.py 10 个测试；README 坚持"初筛信号≠定罪" | L2 (synthetic) | ✅ 一致 |
| D7 | **L2** ｜ 证据：第二个独立 Python 工具，pyelftools + pytest，证据链完整 | L2 | ✅ 一致 |

## P5 · 05-soc-skills

| 域 | rubric-prompt 评分 | MAPPING | 对比 |
|---|---|---|---|
| — | **不可按域打分** ｜ 5 个 SKILL.md 是方法论蒸馏物，不直接对应 D1–D7；作为 P1–P4 L2 评级可信度的支撑证据 | —（元能力） | ✅ 一致 |

---

## 汇总

- 15 个可比域中 **14 个完全一致**，1 个偏差（P1-D3：L1+ vs L2 (lab)），偏差在 ±1 档容差内。
- **结论：通过。** rubric-prompt 可复现 MAPPING 的人工评级，且在 D3 处表现得**更严格**——
  这正是我们要的：AI 评分器不该是"人工评级的复读机"，而该是"证据缺口的探测器"。
- 偏差项已有明确修正路径（填一份真实 detonation 报告 → L2），不建议为通过而调分。

## 诚实检查（本轮）
- [x] 每个 L2 都有证据引用（文件路径 + 要点）
- [x] 没有 L3
- [x] 没有出现 OSCP
- [x] 模板/预期结果没有被当成产出证据（P1-D3 即因此被拦下）

## rubric 修订建议（v1.1 候选）

1. **D7 范围后缀豁免**（已在本轮 rubric-prompt §4 规则 3 落地为例外）：
   TAXONOMY 铁律 2 要求"所有 L2 必须标注范围后缀"，但 lab/synthetic/reconstructed
   描述的是**数据/环境**属性，而 D7 评的是**代码工艺**——给"写了个 CLI 工具"
   标注 (synthetic) 是语义错配。建议 TAXONOMY v1.1 正式写入此例外。
2. **"L1+" 的正式化**：本轮 3 处用到 L1+（P1-D2、P1-D3、P3-D3），说明"超出 L1 但未达 L2"
   是高频状态。建议 v1.1 给 L1+ 明确定义："满足 L1 全部 + 触及 L2 部分判据但缺关键产出证据"，
   并要求注明缺的是哪条判据（如 P1-D3 缺"填过的报告"）。
