# Awesome_Script

信创模盒 ModelHub XC（`https://modelhub.org.cn`）平台**验证通过记录**的抓取、归纳与分析。

## 这个仓库是什么

平台上有大量同事实在给国产算力卡（昇腾 / 寒武纪 / 昆仑芯 / 燧原 / 沐曦 / 海光 / 摩尔线程 / 璧仞 / 中微 / 曦望 / VastAI）提交 HuggingFace 模型做推理适配验证。
本仓库把**骨干贡献者的验证通过记录**抓下来，回答三个问题：

1. 谁在哪张卡上跑通了哪些模型？
2. 这些模型有什么共性（作者、规模、格式、任务类型）？
3. 据此可以直接复用哪些"高命中率"的模型来源？

## 数据口径

- 判定：任务 `status = success` **且** `verifyResult = 1`（验证通过），仅此才算数
- 来源：`GET /api/adapt/task/page?onlyMine=false&status=success&creatorId=<uid>`
- 覆盖：10 个贡献者账号，共 **101,818** 条验证通过记录，去重后 **50,633** 个模型
- 卡：16 张

> ⚠️ 平台数据本身是公开的（人人可在站点看到），但本仓库**不含个人账号名与明细的对应关系**，
> 汇总报表按账号聚合、原始明细做过匿名化处理。

## 结论速览

| 维度 | 结论 |
|---|---|
| 最热卡 | `Iluvatar_bi-150` 22.4%（22,837 条），其次 `ppu_zw_810e`、`hygon_k100-ai`、`Ascend_910-b3` |
| 最热模型源 | `mradermacher` **24.9%**（25,381 条），远超第二名 1.6% |
| 模型规模 | 3–8B 占 31.9%，8–14B 占 21%，70B+ 仅 0.4% |
| 权重格式 | GGUF 31.6%，AWQ 1.4%，GPTQ 0.6%，原始 fp16/bf16 极少 |
| 任务类型 | 文本生成 67.6% |

**为什么 mradermacher 占主导**：他同一仓库会同时产出 IQ1–IQ4、Q4_K_M、Q6_K、Q8_0、f16 全套量化，
不管目标卡的白名单只认哪几种（有的卡只认 `f16/bf16`，有的认 `Q8_0/Q4_0`），都能命中一个合规文件 —— 命中率高。

## 目录

```
out/
  REPORT.md                 规律报表（人×卡矩阵、作者、规模、格式、任务类型）
  user_gpu_matrix.csv       账号 × 卡 的验证通过数量矩阵
  models_unique.csv         50,633 个去重模型（作者/规模/格式/通过卡数）
  models_by_gpu.csv         卡 → 模型（不含提交人）
fetch_success_v2.py         抓取脚本（并发翻页，verifyResult=1 过滤）
summarize.py                统计与报表生成
hf_enrich.py                对模型去 HuggingFace 抓元数据（downloads/likes/license/gguf 等）
gh_auth.py                  GitHub 设备码授权（可选）
```

## 复现

```bash
python fetch_success_v2.py 8    # 抓取，产出 data/success_records.jsonl
python summarize.py             # 生成 out/ 下的报表
python hf_enrich.py 6           # 可选：补 HF 元数据
```

`fetch_success_v2.py` 里 `USERS` 是 `账号名 -> creatorId` 的映射，换人改这里即可。

## 数据说明

- 记录字段：账号、uid、taskId、卡（gpuType）、机器名、模型（HF repo id）、任务类型、时间
- `data/` 目录默认不入库（见 `.gitignore`），需要原始明细请本地跑抓取脚本
