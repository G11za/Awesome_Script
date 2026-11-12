# ModelHub XC 验证通过记录分析

- 记录总数：**101,818** 条（status=success 且 verifyResult=1）
- 去重模型：**50,633** 个
- 涉及账号：10 个；卡：16 张

## 一、账号 × 卡 矩阵（验证通过条数）

| 账号 | Ascend_910-b3 | Ascend_910-b4 | Biren_166m | Cambricon_mlu-370-x4 | Cambricon_mlu-370-x8 | Iluvatar_bi-100 | Iluvatar_bi-150 | Iluvatar_mrv-100 | Kunlunxin_p-800 | Kunlunxin_r-200-8f | MetaX_c-500 | Mthreads_s4000 | Sunrise_pt-200-x1 | Vastai_va16 | hygon_k100-ai | ppu_zw_810e | 合计 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| cpuz | 75 | 79 | 120 | 17 | 97 | 41 | 29 | 18 | 46 |  | 92 | 51 | 5 | 6 | 62 |  | 738 |
| i-dengming | 598 | 665 | 604 | 1188 | 1733 | 466 | 1245 | 222 | 268 |  | 194 | 221 | 69 | 169 | 269 | 243 | 8154 |
| i-kanxinlei | 1058 | 359 | 6 |  | 12 | 2023 | 10443 | 25 | 1032 |  | 1435 | 918 | 597 | 95 | 1800 | 4612 | 24415 |
| i-liyongjie | 2640 | 1441 | 2565 | 73 | 208 | 780 | 2884 | 9 | 213 |  | 1750 | 1193 |  |  | 1104 |  | 14860 |
| i-xiejiahao | 2566 | 1524 | 359 | 110 | 147 | 1615 | 2842 | 100 | 316 |  | 618 | 1668 | 375 | 366 | 434 | 1751 | 14791 |
| lucky | 384 | 142 | 230 | 23 | 117 | 1116 | 161 | 20 | 355 |  | 87 | 218 | 13 | 185 | 111 |  | 3162 |
| lucy | 293 | 147 | 219 | 30 | 95 | 1023 | 271 | 24 | 75 |  | 111 | 317 | 112 | 269 | 123 |  | 3109 |
| sunruoxi | 650 | 760 | 831 | 507 | 1098 | 669 | 2540 | 1 | 1538 |  | 1554 | 595 | 835 | 63 | 1124 | 3743 | 16508 |
| yancuili | 60 | 110 | 79 | 72 | 133 | 8 | 85 | 1 | 108 |  | 88 | 2 |  | 59 | 42 |  | 847 |
| zhoushasha | 158 | 1164 | 1374 | 152 | 1018 | 326 | 2337 |  | 1184 | 2 | 830 | 739 |  | 4 | 3946 | 2000 | 15234 |
| **合计** | 8482 | 6391 | 6387 | 2172 | 4658 | 8067 | 22837 | 420 | 5135 | 2 | 6759 | 5922 | 2006 | 1216 | 9015 | 12349 | **101818** |

## 二、模型作者 Top 20

| 作者 | 条数 | 占比 |
|---|---|---|
| mradermacher | 25381 | 24.9% |
| TheBloke | 1664 | 1.6% |
| kairawal | 1097 | 1.1% |
| longtermrisk | 975 | 1.0% |
| bartowski | 924 | 0.9% |
| prithivMLmods | 851 | 0.8% |
| 18-Death | 785 | 0.8% |
| QuantFactory | 676 | 0.7% |
| RichardErkhov | 668 | 0.7% |
| unsloth | 535 | 0.5% |
| xw1234gan | 522 | 0.5% |
| MaziyarPanahi | 515 | 0.5% |
| DevQuasar | 494 | 0.5% |
| shisa-ai | 484 | 0.5% |
| mlx-community | 433 | 0.4% |
| laion | 412 | 0.4% |
| fpadovani | 405 | 0.4% |
| choiqs | 392 | 0.4% |
| mlabonne | 356 | 0.3% |
| AI-ModelScope | 354 | 0.3% |

## 三、模型规模分布

| 规模 | 条数 | 占比 |
|---|---|---|
| <1B | 3969 | 3.9% |
| 1-3B | 12681 | 12.5% |
| 3-8B | 32444 | 31.9% |
| 8-14B | 21344 | 21.0% |
| 14-32B | 2836 | 2.8% |
| 32-70B | 839 | 0.8% |
| 70B+ | 397 | 0.4% |
| 无标注 | 27308 | 26.8% |

## 四、模型格式标识（名字里带的）

| 标识 | 条数 |
|---|---|
| GGUF | 32187 |
| AWQ | 1376 |
| GPTQ | 600 |
| BF16 | 515 |
| FP16 | 391 |
| Q8_0 | 85 |
| FP8 | 66 |
| F16 | 57 |
| INT4 | 33 |
| Q4_0 | 33 |
| Q4_K_M | 15 |
| Q3_3 | 4 |

## 五、任务类型

| 类型 | 条数 |
|---|---|
| 文本生成 | 68867 |
| 未标注 | 30250 |
| 句子相似度 | 847 |
| 视觉多模态理解 | 573 |
| 强化学习 | 270 |
| 语音识别 | 191 |
| 问答 | 164 |
| 翻译 | 140 |
| 语义相关性 | 87 |
| 特征抽取 | 56 |
| 文本分类 | 55 |
| 光学字符识别 | 48 |

## 六、跨卡通用模型 Top 20（同一模型在多张卡上验证通过）

| 模型 | 通过卡数 | 人数 |
|---|---|---|
| ArnaudDev/symfony_ai_maker-V0.7-Qwen3-0.6B-16bit | 12 | 2 |
| ArnaudDev/symfony_ai_maker-V0.7.1-Qwen3-0.6B-16bit | 12 | 2 |
| ArnaudDev/symfony_ai_maker-V0.7.2-Qwen3-0.6B-16bit | 12 | 2 |
| kairawal/Llama-3.1-8B-Instruct-GA-SynthDolly-1A-E1 | 11 | 3 |
| Cartik/BastiAI-2-Instruct | 11 | 3 |
| MaziyarPanahi/calme-2.8-qwen2-7b | 10 | 3 |
| mlabonne/DareBeagle-7B-v2 | 10 | 3 |
| rishabhrj11/distillspec-qwen600m | 10 | 2 |
| JamesGern/lorel.ai_long_train | 10 | 4 |
| ali-elganzory/Qwen3-1.7B-Base-SFT-Tulu3-decontaminated | 10 | 3 |
| ArnaudDev/symfony_ai_maker-V0.8.1-Qwen3-0.6B-16bit | 10 | 2 |
| choiqs/Qwen3-1.7B-tldr-bsz128-ts500-regular-skywork8b-seed42-lr1e-5-warmup10-checkpoint350 | 10 | 2 |
| ligeng-dev/tw-data-train_final_replaced_from_classified-fix-format-8node-resume | 10 | 2 |
| LorenaYannnnn/Qwen3-0.6B-g_general_reward_e_sycophancy-seed_0-sky_r_weak_syco | 10 | 2 |
| onocloud/ono-ai-v1-full | 10 | 2 |
| GRAI-UNSTPB/llama-2-7b-ft-cwi-2018-es | 10 | 1 |
| abcorrea/sok-v5 | 10 | 1 |
| oisee/qwen2.5-coder-abap | 10 | 1 |
| hishab/titulm-llama-3.2-3b-v2.0-Instruct-v1.0 | 10 | 1 |
| zarakiquemparte/zarablend-1.1-l2-7b | 9 | 3 |
