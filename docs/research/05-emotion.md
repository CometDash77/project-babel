# M05 · 情绪识别（Speech Emotion Recognition）

调研日期：2026-09-25。范围是从英文播客的说话人语句区间提取供中文重演参考的情绪证据。本稿依据官方仓库、模型卡、推理源码、发布记录和公开 issue；**没有下载模型、运行推理或做两小时播客实测**。下述分类是下一阶段实验的候选选择，不是生产效果验收。

## 结论与复用边界

1. **主实验候选：FunASR + emotion2vec+ base/large，WRAP·ADAPT。** 复用 FunASR `AutoModel.generate`、模型权重及九类 `labels` / `scores` 输出；自行按说话人语句切音、保存绝对时间与模型版本、过滤混叠区间、校准/弃权。官方 [使用说明](https://github.com/ddlBoJack/emotion2vec#inference-with-checkpoints) 和 [模型卡](https://huggingface.co/emotion2vec/emotion2vec_plus_large)给出 16 kHz 输入、逐语句推理与文件列表入口。[源码](https://github.com/modelscope/FunASR/blob/main/funasr/models/emotion2vec/model.py)显示类别分数来自**语句级均值池化后的 softmax**；`granularity="frame"` 可返回帧级 *embedding*，但分类仍由均值池化产生，**不能把帧 embedding 说成逐帧情绪概率**。这些 softmax 分数尚未证明在真实播客上校准。
2. **可复用的英文四分类对照：SpeechBrain IEMOCAP 模型，DIRECT REUSE（仅实验基线）。** 复用其 Apache-2.0 预训练权重、`foreign_class` / `classify_batch` 与类别分数，不直接将 IEMOCAP 测试准确率外推到自然播客。[模型卡](https://huggingface.co/speechbrain/emotion-recognition-wav2vec2-IEMOCAP)明确训练于 IEMOCAP 并声明其他数据集效果无保证；[接口源码](https://huggingface.co/speechbrain/emotion-recognition-wav2vec2-IEMOCAP/blob/main/custom_interface.py)确认输出为 utterance 分类、可批量输入，[模型配置](https://huggingface.co/speechbrain/emotion-recognition-wav2vec2-IEMOCAP/blob/main/hyperparams.yaml)将 `hparams.softmax` 设为 Softmax。接口注释把 `out_prob` 写作“log posterior”，与配置不一致；应以锁定版本的配置和实际输出复核，不能直接当校准概率。
3. **自然播客相关的连续维度参照：audEERING MSP-Podcast 模型，REFERENCE；直接产品集成暂为 REJECT。** 官方[模型卡](https://huggingface.co/audeering/wav2vec2-large-robust-12-ft-emotion-msp-dim)说明它在英文 MSP-Podcast v1.7 上微调，输出 arousal / dominance / valence 约 0–1 的**回归值**，不是九类/四类概率；提供 Python 推理示例与 ONNX 导出。卡片标明仅供研究、权重为 CC BY-NC-SA 4.0，商业使用需另取许可。因而可借它验证“连续维度是否比离散标签更有用”，但不能把它当可自由嵌入产品的开放权重。

**第一性原理判断**：下游需要的是某个说话人在某段音频中的可追溯表演线索，而非强迫每句话有确定情绪。语义文本、音高/能量、笑声等可能与 SER 标签冲突；低置信度、多人重叠、过短反应或背景声污染时应保留原始分数并允许 `unknown` / 待人工复核。M07 可以接收“带来源的候选观测”，不能把模型标签当作事实或让一个模型的类别表冻结 Smart Context 结构。这是架构**推论**，需以后续听评验证。

## 候选横向核查

维护快照取自 2026-09-25 的 GitHub API 仓库及 latest release、Hugging Face 模型元数据。`pushed_at` 是整个仓库最近推送，不证明 SER 模型近期更新；GitHub `open_issues_count` 也含 PR。模型卡的单段示例或公开 Spaces 不是长播客生产案例。

| 项目 / 归类 | 英文与真实录音适配、输出 | 批量/粒度及具体复用点 | 维护、许可与本地集成 | 缺口 |
| --- | --- | --- | --- | --- |
| [FunASR](https://github.com/modelscope/FunASR) + [emotion2vec+](https://huggingface.co/emotion2vec/emotion2vec_plus_large) · **WRAP·ADAPT** | 官方声称跨语言和录音环境鲁棒，九类含 `neutral`/`other`/`unknown`；英文播客独立测试尚无证据。输出为语句级 softmax 分数，可选 50 Hz 帧 embedding。[模型卡](https://huggingface.co/emotion2vec/emotion2vec_plus_large)、[源码](https://github.com/modelscope/FunASR/blob/main/funasr/models/emotion2vec/model.py) | `AutoModel.generate` 本地 Python API；`wav.scp` 文件列表入口便于批处理，但 [原项目批量推理讨论](https://github.com/ddlBoJack/emotion2vec/issues/37)仍开放，不能据此宣称高效真正多样本 GPU batch。复用推理与输出，长节目按 M04/M03 的可靠语句区间切分。 | FunASR 代码 MIT，未归档，最近推送 2026-09-25；[v1.4.16](https://github.com/modelscope/FunASR/releases/tag/v1.4.16) 为 2026-09-18；API `open_issues_count=33`。权重[模型卡](https://huggingface.co/emotion2vec/emotion2vec_plus_large)标 `model-license`，**与代码许可分开**，需核对目标用途的具体条款。Python/PyTorch，本地模型自动下载；Windows/Linux 与 CPU/GPU 组合、显存峰值**需要实验确定**。 | [FunASR 长运行显存 issue](https://github.com/modelscope/FunASR/issues/2695)曾报告 8 GiB GPU OOM，现已关闭；关闭不证明选定版本、切片长度下无问题。长音频吞吐、跨说话人、混响/音乐/多人重叠效果**需要实验确定**。 |
| [SpeechBrain IEMOCAP 预训练模型](https://huggingface.co/speechbrain/emotion-recognition-wav2vec2-IEMOCAP) · **DIRECT REUSE**（基线） | 英文 IEMOCAP 四类情绪模型；其卡片给出的 78.7% 是 **IEMOCAP** 测试集成绩，不是播客表现。`out_prob`、最佳分数和标签为语句级输出。[模型卡](https://huggingface.co/speechbrain/emotion-recognition-wav2vec2-IEMOCAP) | [自定义接口](https://huggingface.co/speechbrain/emotion-recognition-wav2vec2-IEMOCAP/blob/main/custom_interface.py)有 `classify_batch`、`classify_file`；复用预训练模型作相同样本上的对照。仅语句级分类；无原生节目时间轴或逐帧情绪事件。 | [SpeechBrain](https://github.com/speechbrain/speechbrain) 与模型均 Apache-2.0；框架未归档，最近推送 2026-08-27；[v1.1.1](https://github.com/speechbrain/speechbrain/releases/tag/v1.1.1) 同日发布；API `open_issues_count=189`。本地 Python/PyTorch，模型卡给 CPU 默认与 CUDA `run_opts` 入口；Windows/Linux、GPU 峰值及模型卡示例与最新框架 API 兼容性**需要实验确定**。 | 训练域偏演绎语音；跨说话人/自然访谈、重叠讲话、两小时节目吞吐**需要实验确定**。官方模型卡明确不保证其他数据集表现。 |
| [audEERING MSP-Podcast 维度模型](https://huggingface.co/audeering/wav2vec2-large-robust-12-ft-emotion-msp-dim) · **REFERENCE**（直接集成 **REJECT**） | 英文播客语料训练，回归 arousal / dominance / valence；适合研究连续表演线索，但输出不是类别概率。[模型卡](https://huggingface.co/audeering/wav2vec2-large-robust-12-ft-emotion-msp-dim) | 官方 Python/PyTorch 单段示例及 ONNX 导出；未见现成节目时间轴或逐帧事件。可参考维度定义与评测切片，不复用为产品权重。 | 权重 CC BY-NC-SA 4.0、卡片明确 research only；HF 元数据显示权重最后更新于 2024-09-19。Python 本地推理；CPU/GPU、Windows/Linux 与批量吞吐需按目标环境实测。 | 训练集同域有利于研究，但仍不能证明目标节目上的跨说话人泛化。若要产品使用，先明确授权；非商用研究也需遵守原许可。 |

原始 [emotion2vec 仓库](https://github.com/ddlBoJack/emotion2vec)在 2024-12-23 后没有新推送、无 GitHub release，且 API 未识别到仓库许可；本稿选 FunASR 维护中的推理实现，不把原始研究仓库直接列为主依赖。FunASR 的 [模型权重协议](https://github.com/modelscope/FunASR/blob/main/MODEL_LICENSE)与 MIT 代码许可不同，当前对具体权重适用范围的判断仍需核对模型版本和用途；此处不作法律结论。

## 交给 M07 的输出契约建议（尚未冻结 schema）

对每个输入语句保留 `source_audio_id`、原节目绝对 `start/end`、候选 `speaker_id`、切片/分离方式、模型 ID 与版本、模型原始标签和完整分数向量、是否为 softmax/回归值、质量/弃权原因。时间轴与说话人依据分别来自 [M04 时间轴稿](04-asr-timeline.md)和未完成的 [M03](https://github.com/CometDash77/project-babel/issues/4)；帧级 embedding 不等于可直接对齐的情绪类别。M07 再决定是否映射到跨模型的情绪维度，及如何与 M06 prosody、文本和非语言声音相互校验。

## 需要实验确定

1. **统一英文播客评测**：选多说话人、打断/重叠、远场/压缩、背景音乐、短促反应和中性长段，人工标注语句级情绪及“不可判断”；按说话人和节目分层，比较 emotion2vec+ base/large、SpeechBrain 基线与人工一致性。不同数据集公布的准确率不可横比。
2. **概率校准与弃权**：保存完整分数，测 ECE/Brier、top-1 可靠度、`other`/`unknown` 占比与拒判覆盖率；不要把 softmax 高分直接解释为真实置信概率。audEERING 回归值单独评价，不能混进类别概率。
3. **切片与时间回填**：比较 M04 句界、固定滑窗和说话人区间切片；重叠/音乐片段盲听并记录过滤理由。检验同一句情绪变化会否被语句均值池化抹去，必要时再研究局部窗口推理，而不是误用 50 Hz embedding。
4. **工程与许可**：在 Windows/Linux 固定模型和依赖版本，实测 CPU/GPU 峰值、每小时音频耗时、批量与连续运行、模型下载/缓存和失败恢复；核对 emotion2vec+ 具体权重协议与预定用途。未跑这些实验前，三者均不得称为已验证的长播客方案。

本票只确定可复用能力与评测边界。M07 的最终字段、阈值、情绪本体和生产选型均未定案。
