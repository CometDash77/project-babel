# M05 · 情绪识别选型调研（research）

调研日期：2026-09-25。目标是从英文多人播客原声中提取可追溯的情绪线索，供中文重演参考。本稿只整理候选与证据；**主选和备选留给 [M05 拍板票](https://github.com/CometDash77/project-babel/issues/43)**。复用 [M05 模块稿](../research/05-emotion.md)的推理接口、输出粒度和风险核查，并对照[前置一条龙反查](00-mature-pipeline-stack.md)：pyVideoTrans、VideoLingo、SoniTranslate 的公开主流程均未列独立的原声情绪识别阶段。因此，成品配音演示不能充当 M05 的端到端成功证明；两小时多人播客效果**需要实验确定**。

## 候选横比

| 候选 | 已跑通的公开证据与边界 | 任务适配、许可、维护与热度 | 留给拍板票的取舍 |
| --- | --- | --- | --- |
| [FunASR + emotion2vec+ base/large](https://huggingface.co/emotion2vec/emotion2vec_plus_large) | [模型卡](https://huggingface.co/emotion2vec/emotion2vec_plus_large#inference-based-on-funasr)给出 16 kHz 音频的 `AutoModel.generate` 示例和 `wav.scp` 文件列表入口；[用户报告](https://github.com/ddlBoJack/emotion2vec/issues/79)实际用 FunASR + large 测试，却只得到整段情绪，反证现成入口不能直接给逐句时间戳。模型卡列有使用它的 Spaces，但上线展示不证明目标播客质量。 | 九类标签（含 `other`、`unknown`）；[源码](https://github.com/modelscope/FunASR/blob/main/funasr/models/emotion2vec/model.py)显示分类来自语句均值池化后的 softmax，50 Hz 帧输出是 embedding 而非逐帧情绪概率。FunASR [MIT 代码仓库](https://api.github.com/repos/modelscope/FunASR)约 20.5k stars、2026-09-25 有推送，[v1.4.16](https://github.com/modelscope/FunASR/releases/tag/v1.4.16) 于 09-18 发布；原始 [emotion2vec 仓库](https://api.github.com/repos/ddlBoJack/emotion2vec)约 1.19k stars、最后推送 2024-12-23，2025 年的[时间戳问题](https://github.com/ddlBoJack/emotion2vec/issues/79)仍待解决。权重卡标为 `model-license`，须与 [FunASR 模型协议](https://github.com/modelscope/FunASR/blob/main/MODEL_LICENSE)分开核对。 | 标签覆盖较广、框架近期活跃；但需要自行按 M03/M04 可靠语句切片和回填绝对时间。英文自然播客、混叠、校准、长时吞吐及权重具体适用条款**需要实验确定/进一步核对**。 |
| [SpeechBrain wav2vec2-IEMOCAP](https://huggingface.co/speechbrain/emotion-recognition-wav2vec2-IEMOCAP) | 官方[模型卡和教程](https://huggingface.co/speechbrain/emotion-recognition-wav2vec2-IEMOCAP#perform-emotion-recognition)提供 `foreign_class` 单文件推理、示例音频及 GPU 用法；[自定义接口](https://huggingface.co/speechbrain/emotion-recognition-wav2vec2-IEMOCAP/blob/main/custom_interface.py)含 `classify_batch`。模型卡列出的 Spaces 是公开使用入口，不能据此认定长播客已成功。 | 英文 IEMOCAP 四类语句分类；卡片的 78.7% 只针对 IEMOCAP，且[明确不保证其他数据集表现](https://huggingface.co/speechbrain/emotion-recognition-wav2vec2-IEMOCAP#limitations)。模型 Apache-2.0；[SpeechBrain 仓库](https://api.github.com/repos/speechbrain/speechbrain)约 11.8k stars、2026-08-27 有推送，[v1.1.1](https://github.com/speechbrain/speechbrain/releases/tag/v1.1.1) 同日发布。 | 可作为同一节目、同一切片上的英文四类基线；演绎语音训练域与自然访谈差异明显。最新库与模型卡示例兼容性、真实播客效果**需要实验确定**。 |
| [audEERING MSP-Podcast 维度模型](https://huggingface.co/audeering/wav2vec2-large-robust-12-ft-emotion-msp-dim) | [官方模型卡](https://huggingface.co/audeering/wav2vec2-large-robust-12-ft-emotion-msp-dim#usage)提供本地 Python 推理、ONNX 导出链接与示例输出；卡片展示公开 Spaces，属于可运行入口而非本项目验收案例。 | 英文 MSP-Podcast v1.7 微调，输出约 0–1 的 arousal、dominance、valence **回归值**，不可与前两者的类别分数直接比较。模型卡标 CC BY-NC-SA 4.0、`research purpose only`，商业用途需另取许可；个人用途仍须遵守许可。模型页面显示约 0.2B 参数及社区使用，但模型本身的近期核心更新与维护响应未获证明。 | 同域和连续维度值得作为研究参照；能否用于预期个人工作流及发布方式，应核对许可。跨节目、跨说话人效果和长音频处理**需要实验确定**。 |

上述 stars、推送和版本是 2026-09-25 读取 GitHub API 的快照，衡量关注度与框架活跃度，**不代表 SER 权重近期训练、问题必获响应或目标音质**。[原始 emotion2vec issue 列表](https://github.com/ddlBoJack/emotion2vec/issues)显示 2025–2026 仍有分类分数、时间戳、并发与权重许可疑问；[FunASR 问题列表](https://github.com/modelscope/FunASR/issues)和[SpeechBrain 问题列表](https://github.com/speechbrain/speechbrain/issues)也需按具体问题核对解决情况。公开证据足以说明三个候选有可运行接口或演示，**没有找到可核验的“两小时英文多人播客逐句情绪 → 中文重演”成功案例**。

## 对接边界与启动前门槛

1. 以 M03/M04 的说话人和绝对时间切出语句，保存原音 ID、起止时间、speaker 候选、切片方法、模型版本、原始类别与完整分数或维度值，以及弃权原因；这是依据现有接口提出的**本项目设计建议**。[FunASR 模型卡](https://huggingface.co/emotion2vec/emotion2vec_plus_large#usage)与[SpeechBrain 接口](https://huggingface.co/speechbrain/emotion-recognition-wav2vec2-IEMOCAP/blob/main/custom_interface.py)均只提供局部输入上的推理，不提供原节目完整时间轴。
2. `unknown` 标签不等于模型可靠地知道自己不确定；softmax 高分也未证明经过目标域校准。多人重叠、短促反应、笑声、音乐污染与分离失真应能弃权或供人工复核。[emotion2vec+ 类别表](https://huggingface.co/emotion2vec/emotion2vec_plus_large#guides)和[模型源码](https://github.com/modelscope/FunASR/blob/main/funasr/models/emotion2vec/model.py)支持这个风险判断；阈值**需要实验确定**。
3. 启动前用获准使用的英文多人播客建立同一批语句样本，含中性长段、情绪转变、重叠与背景音乐；比较人工一致性、分说话人误差、概率校准/弃权覆盖率。另测 Windows/Linux 的版本兼容、CPU/GPU 峰值、每小时处理时长、失败恢复和模型权重条款。各候选公开数据集指标不能横比；这些指标及最终生产可用性均**需要实验确定**。

本稿不排序主选/备选，不把标签映射、阈值或 M07 的结构定为既成事实。
