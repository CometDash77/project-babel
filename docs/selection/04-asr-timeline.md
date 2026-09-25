# M04 · ASR 与精确时间轴：候选证据稿

调研日期：2026-09-25。目标是从英文多人播客得到原文、词与片段时间戳，并能与说话人区间合并。本稿只整理候选和证据，**不指定主选或备选**；该取舍留给 [M04 拍板票](https://github.com/CometDash77/project-babel/issues/41)。复用基底为 [M04 模块稿](../research/04-asr-timeline.md)与[成熟一条龙技术栈反查](00-mature-pipeline-stack.md)。本次没有安装模型或运行音频；项目方演示、论文和用户报告均不等于本项目验收。

## 已跑通的公开路径及证据边界

- [VideoLingo 的成品配音流程](https://github.com/Huanshere/VideoLingo/blob/main/docs/pages/docs/introduction.zh-CN.md)使用 WhisperX 词时轴；维护者在 [2026-09 的讨论](https://github.com/Huanshere/VideoLingo/issues/598#issuecomment-5663227440)说明当前本地默认仍为 WhisperX，原因是该流程依赖稳定的时间戳和对齐。这是实际集成与维护者判断，不是对本项目播客的盲测。其[公开限制](https://github.com/Huanshere/VideoLingo/blob/main/docs/pages/docs/introduction.zh-CN.md#当前限制)包括不能给多角色分别配音。
- [pyVideoTrans 九阶段架构](https://github.com/jianchang512/pyvideotrans/blob/main/docs/architecture.md)的 ASR 默认用 faster-whisper 并输出 SRT，证明其在另一条成品配音流水线中已集成；SRT 句段时轴不能证明词边界符合本项目的“精确”要求。[faster-whisper 官方集成列表](https://github.com/SYSTRAN/faster-whisper#community-integrations)还列有 WhisperX、aTrain 等，属于真实复用线索，不提供两小时多人播客验收数据。
- [SoniTranslate 的可运行流程与演示](https://github.com/R3gm/SoniTranslate)使用 Whisper 系转写及配音，但[用户报告的 10 分钟视频仅配出 60 秒](https://github.com/R3gm/SoniTranslate/issues/184)说明成品路径不能外推成长节目可靠性。三款一条龙项目均未给出可核对的“两小时英文多人播客、保留打断和重叠说话”的词级真值评测；该目标**需要实验确定**。[反查稿](00-mature-pipeline-stack.md)

## 候选横比

下表 GitHub 热度、推送和 release 为 2026-09-25 读取的快照。星标是关注度，非识别精度；`open_issues_count` 混合开放 issue 与 PR，不能用作响应速度。近期推送也不保证本模块功能获得维护。各项许可证只指代码仓库，模型权重与依赖条款须单核。[GitHub 仓库 API](https://docs.github.com/en/rest/repos/repos#get-a-repository)、[release API](https://docs.github.com/en/rest/releases/releases#get-the-latest-release)

| 候选与适用层 | 能力、成功案例与关键限制 | 热度、维护、许可证据 |
| --- | --- | --- |
| [WhisperX](https://github.com/m-bain/whisperX) · 串联 ASR/对齐的整套候选 | [官方 Python 示例](https://github.com/m-bain/whisperX#python-usage-)给出批量 ASR → wav2vec2/CTC 强制对齐 → 可选 diarization 和词级 `start/end`；VideoLingo 的上述默认集成是成品案例。[README](https://github.com/m-bain/whisperX#limitations-%EF%B8%8F)明确重叠讲话、speaker 和数字等词的对齐限制；`assign_word_speakers` 不能当作双人同说的完整时间轴。[论文](https://arxiv.org/abs/2303.00747)研究长音频，但不代替两小时播客验收。 | [仓库](https://github.com/m-bain/whisperX)约 24.2k stars、2.4k forks，未归档，2026-08-30 有推送；[v3.8.6](https://github.com/m-bain/whisperX/releases/tag/v3.8.6)于 2026-05-25 发布；代码 BSD-2-Clause。近期[用户兼容讨论](https://github.com/m-bain/whisperX/issues/1326)有回复，但未见足以量化整体 issue 响应时长的证据。pyannote/HF 权重条件另核。 |
| [faster-whisper](https://github.com/SYSTRAN/faster-whisper) · 可替换 ASR 底座 | [官方用法](https://github.com/SYSTRAN/faster-whisper#usage)有 `WhisperModel`、批量推理、`word_timestamps=True`、Silero VAD；pyVideoTrans 与 WhisperX 均有实际集成。它的 API 没有形成独立的多说话人重叠区间；词时间戳若不满足精度，需另接对齐层。批量 VAD/片段边界的组合影响**需要实验确定**。[词时戳和 VAD 文档](https://github.com/SYSTRAN/faster-whisper#word-level-timestamps) | [仓库](https://github.com/SYSTRAN/faster-whisper)约 25.6k stars、2.1k forks，未归档，2025-11-19 最后推送；[v1.2.1](https://github.com/SYSTRAN/faster-whisper/releases/tag/v1.2.1)于 2025-10-31 发布；MIT。现存 [VAD/批处理漏词报告](https://github.com/SYSTRAN/faster-whisper/issues/1270)与 [Windows 词时戳崩溃报告](https://github.com/SYSTRAN/faster-whisper/issues/1342)，不能据 issue 断定所有版本均复现。 |
| [NeMo Forced Aligner](https://docs.nvidia.com/nemo-framework/user-guide/latest/nemotoolkit/tools/nemo_forced_aligner.html) · 已有文本的后置对齐候选 | 官方 [Quickstart、教程与 demo](https://docs.nvidia.com/nemo-framework/user-guide/latest/nemotoolkit/tools/nemo_forced_aligner.html)给出 manifest、`align.py`、token/word/segment CTM；可用人工校正稿或 ASR 文本。官方称在硬件/模型允许时能对齐 1 小时以上音频、文本越准确效果越好。它本身不是完整 ASR 或重叠说话处理器；与 faster-whisper 串接及两小时资源占用**需要实验确定**。 | 所在 [NeMo Speech 大仓](https://github.com/NVIDIA-NeMo/Speech)约 18.5k stars、3.6k forks，2026-09-24 有推送；[v3.0.0](https://github.com/NVIDIA-NeMo/Speech/releases/tag/v3.0.0)于 2026-08-07 发布；Apache-2.0。大仓更新不能证明 NFA 独立维护节奏；未找到该工具专属 issue 响应统计。 |
| [whisper-timestamped](https://github.com/linto-ai/whisper-timestamped) · 词时戳/置信度对照候选 | [官方说明和输出示例](https://github.com/linto-ai/whisper-timestamped#example-output)用 Whisper 注意力与 DTW 给词时戳、置信度，提供 Python/CLI、长文件内存控制的项目方声明；尚未找到对应本项目的多人长播客成品案例。[2026 年的 segment 数不一致报告](https://github.com/linto-ai/whisper-timestamped/issues/255)提示应核对失败路径。 | [仓库](https://github.com/linto-ai/whisper-timestamped)约 2.8k stars、209 forks，未归档，2026-08-17 有推送；[v1.15.9](https://github.com/linto-ai/whisper-timestamped/releases/tag/v1.15.9)于 2025-09-09 发布；AGPL-3.0。个人用途下具体分发/网络服务义务仍须按最终使用方式核查，不能仅凭“个人用途”忽略许可证。 |
| [stable-ts](https://github.com/jianfch/stable-ts) · 时间戳处理设计参考 | [README](https://github.com/jianfch/stable-ts)展示静音修正、重分组与 JSON 后处理；未找到证明两小时多人播客精度的可核案例。仓库已由作者于 2026-05-30 [归档](https://github.com/jianfch/stable-ts)，因此作为长期维护依赖存在明确风险；参考其处理思路不代表应引入依赖。 | [仓库](https://github.com/jianfch/stable-ts)约 2.3k stars、245 forks，MIT；[最新 GitHub release 2.0.0](https://github.com/jianfch/stable-ts/releases/tag/2.0.0)发布于 2023-03-17。归档后的零开放 issue 不能解释为零缺陷。 |
| [whisper-diarization](https://github.com/MahmoudAshraf97/whisper-diarization) · 组合实现参考 | [README 安装、用法及 notebook](https://github.com/MahmoudAshraf97/whisper-diarization)展示 Whisper/faster-whisper + CTC 对齐 + NeMo speaker 的可运行组合；作者[明确说重叠说话未解决](https://github.com/MahmoudAshraf97/whisper-diarization#known-limitations)。长节目稳定性**需要实验确定**。 | [仓库](https://github.com/MahmoudAshraf97/whisper-diarization)约 5.7k stars、504 forks，未归档，2026-08-15 有推送；BSD-2-Clause；GitHub latest-release API 无对应 release，故无法报稳定发布节奏。[开放问题示例](https://github.com/MahmoudAshraf97/whisper-diarization/issues/374)不能代表总体响应率。 |

## 时间轴接口需保留的事实

- [WhisperX 输出 schema](https://github.com/m-bain/whisperX/blob/main/whisperx/schema.py)包含 `segments`、各段 `words` 与扁平词项；`score` 是对齐分数，不能当成转写内容正确率。[对齐实现](https://github.com/m-bain/whisperX/blob/main/whisperx/alignment.py)与 README 对未对齐词的表述并不保证每个词都有可靠时间戳，缺值应显式保留。
- [WhisperX 说话人分配实现](https://github.com/m-bain/whisperX/blob/main/whisperx/diarize.py)以独立 speaker 区间和词/段交叠量分配单个标签。据此推论：为了后续 M03 的打断与多人重叠，必须另存原始多 speaker 区间和对齐结果，不能仅存最终单个 `speaker`；具体 overlap 检测归 [M03](https://github.com/CometDash77/project-babel/issues/39)。
- [NeMo NFA 的 CTM 定义](https://docs.nvidia.com/nemo-framework/user-guide/latest/nemotoolkit/tools/nemo_forced_aligner.html#output-ctm-file-format)和 [faster-whisper 的词项 API](https://github.com/SYSTRAN/faster-whisper#word-level-timestamps)格式不同。切片、VAD 后恢复原节目绝对时间，以及 pause/turn 从词项和 speaker 区间推导，属于本项目接口推论；换后端时要统一时间单位、原始 offset、空值和质量标记，正确性**需要实验确定**。M07 的结构由其拍板票决定。

## 交给拍板票的比较条件与启动前门槛

1. 同一组获准使用的英文多人播客样本，含约两小时节目、轻声、数字/专名、音乐、长静音、打断与真正重叠说话。并排比较 WhisperX 整套流程与 faster-whisper + NeMo NFA；对照 whisper-timestamped 的词边界/置信度。记录 WER、漏词、词边界误差、未对齐词比例、GPU/内存峰值、耗时和失败恢复。上述效果和资源**需要实验确定**。[WhisperX 限制](https://github.com/m-bain/whisperX#limitations-%EF%B8%8F)、[NFA 长音频条件](https://docs.nvidia.com/nemo-framework/user-guide/latest/nemotoolkit/tools/nemo_forced_aligner.html)
2. 对重叠区间逐段核查原始 diarization 与最终单标签的差异；验证 VAD/切片 offset 后词、句、speaker 是否仍对齐原节目绝对时间。M04 不替 M03 解决 overlap，结果交给 M03/M07。[WhisperX 源码](https://github.com/m-bain/whisperX/blob/main/whisperx/diarize.py)
3. 固定候选版本，在预期 Windows/Linux 与 CPU/GPU 环境检查安装、权重许可、依赖、短段与长段。特别复核 [faster-whisper Windows 报告](https://github.com/SYSTRAN/faster-whisper/issues/1342)和 WhisperX 的[对齐缺词限制](https://github.com/m-bain/whisperX#limitations-%EF%B8%8F)在选定版本中的状态；兼容性与峰值**需要实验确定**。

以上是纸面研究与开工前验收条件，未执行 GPU 实验。候选排序、主选和备选由 M04 grilling 票与用户共同确定。
