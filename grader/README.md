# Grader v1 — AI 评分器

Phase 2 产物：把 TAXONOMY 的 rubric 编码成可执行的评分 prompt，
配一个证据包收集 harness，并用 5 个 home-lab 项目做了交叉验证。

## 文件

| 文件 | 作用 |
|---|---|
| `rubric-prompt.md` | 可执行的评分 prompt：7 域 rubric + 7 条评分铁律 + 输出格式 + 反例。复制全文 + 证据包 JSON 给任意 LLM 即可打分 |
| `grade.py` | harness：给定项目目录，收集 README 全文 + 文件清单（code/test/doc/data/config 分类）+ 关键文件前 N 行，输出标准化证据包 JSON |
| `validation.md` | 本轮验证报告：LLM 按 prompt 给 5 个项目打分 vs MAPPING.md 人工评级，15 域中 14 个一致，1 个偏差（P1-D3）在容差内 |

## 用法

```bash
# 1. 收集证据包
python3 grade.py ~/workspace/soc-home-lab/02-python-ioc-analyzer -o /tmp/p2.json

# 2. 把 rubric-prompt.md 全文 + /tmp/p2.json 粘贴给 LLM，按 §5 输出格式打分
# 3. 对照已有人工评级（如有），偏差超 ±1 档需解释
```

`grade.py` 参数：`--head-lines N`（excerpts 截取行数，默认 60）、`-o/--output`（输出路径，默认 stdout）。
venv / __pycache__ / .git 等自动排除。

## 输出格式（LLM 按 prompt 输出）

```
D<k> | <L1|L1+|L2>[(lab|synthetic|reconstructed)] | 证据：<文件路径>：<要点> | 升级建议：<到下一级还差什么>
## 总评
## 诚实检查
```

## 局限性（v1）

1. **不做语义验证**：harness 只收集文件，不验证"代码真能跑"（如测试是否通过）。建议人工抽查 `pytest` 结果。
2. **README 诚实度依赖作者**：若作者在 README 虚报"亲手跑过"，prompt 只能按证据字面采信。缓解：铁律 6/7（模板≠产出、预期≠观测）已拦截最常见的两种虚报。
3. **D7 范围后缀豁免**：见 validation.md——D7 评代码工艺，不适用 lab/synthetic 后缀（TAXONOMY v1.1 待正式写入）。
4. **L1+ 非正式等级**：v1 prompt 允许输出 L1+，但 TAXONOMY 尚未正式定义（v1.1 候选）。
5. **无 LLM API 集成**：v1 是"prompt + 人工粘贴"流程；API 化（自动调模型打分、批量跑）是 Phase 2 后续工作。

## 版本

- v1.0 · 2026-10-15 · 首版 prompt + harness + 5 项目交叉验证通过
