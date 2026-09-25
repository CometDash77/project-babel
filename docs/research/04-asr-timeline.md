# M04 · ASR 与精确时间轴

调研日期：2026-09-25。范围：英文播客的原文、词/片段时间戳及其与说话人时间轴的合并。这里只依据项目仓库、源码、发布记录和 issue 作选型判断；没有在本机运行模型，也没有播客样本精度测试。**需要实验确定**的事项不等同于已验证能力。

## 结论与复用边界

1. **首选候选：WhisperX，WRAP·ADAPT。** 复用其批量 ASR → CTC 强制对齐 → `assign_word_speakers` 管线，以及 `segments` / `words` 的时间戳结构。需要我们封装持久化、失败恢复、原始时间坐标、质量标记，并独立保存 diarization 区间。其 README 明确承认重叠讲话、说话人标注和部分词对齐的限制；不能直接把它的单一 `speaker` 字段当作真实多人重叠时间轴。[README 与限制](https://github.com/m-bain/whisperX#limitations-%EF%B8%8F)、[对齐源码](https://github.com/m-bain/whisperX/blob/main/whisperx/alignment.py)、[说话人分配源码](https://github.com/m-bain/whisperX/blob/main/whisperx/diarize.py)。
2. **ASR 可替换底座：faster-whisper，DIRECT REUSE（仅转写层）。** 复用 `WhisperModel` / `BatchedInferencePipeline`、`word_timestamps=True`、Silero VAD 选项和 `Segment`/`Word` 对象；它不提供完整 diarization/overlap 时间轴。若词边界精度不够，再接独立强制对齐，而非默认其词时间戳已达“精确”要求。[官方用法](https://github.com/SYSTRAN/faster-whisper#usage)。
3. **校正后的英文稿对齐备选：NeMo Forced Aligner，WRAP·ADAPT。** 复用 `tools/nemo_forced_aligner/align.py`、manifest 输入及 token/word/segment 输出。官方说明支持 1 小时以上音频，但受硬件和模型限制；它需要文本，不能独自承担原文识别或说话人/overlap。[工具 README](https://github.com/NVIDIA-NeMo/Speech/blob/main/tools/nemo_forced_aligner/README.md)。
4. **其他候选：whisper-timestamped 为 REFERENCE；stable-ts 为 REJECT（作为当前主依赖）。** 前者的词置信度和 DTW 思路值得参考，但其仓库采用 AGPL-3.0，具体集成的许可证义务须单独审查；后者虽有实用的静音修正/JSON 重处理设计，仓库已于 2026-05-30 归档并声明无限期暂停开发。[whisper-timestamped README](https://github.com/linto-ai/whisper-timestamped)、[stable-ts 仓库状态](https://github.com/jianfch/stable-ts)。

这些分类是**当前调研判断**，不是已跑通的流水线承诺。WhisperX 作为首选还需与“仅用 faster-whisper + 后置对齐”的方案在同一批播客上盲比。

## 候选横向核查

GitHub 的 `open_issues_count` 同时包含开放 issue 和 PR，不能当作纯 issue 数。下表的维护快照来自 2026-09-25 的 GitHub API 仓库及 latest release；`pushed_at` 表示仓库最近推送，不证明核心功能近期有更新。“本地可运行”仅指项目提供本地运行入口，不表示本机已成功安装。

| 项目 / 归类 | 真实能力、具体复用点 | 维护、release、issue、许可 | 本地接口 / 平台 / 资源 | 长音频与真实案例、限制 |
| --- | --- | --- | --- | --- |
| [WhisperX](https://github.com/m-bain/whisperX) · **WRAP·ADAPT** | ASR、wav2vec2/CTC 对齐、可选 pyannote diarization；复用 `load_model`、`load_align_model`、`align`、`assign_word_speakers` 和结果结构。[Python 示例](https://github.com/m-bain/whisperX#python-usage-) | BSD-2-Clause；未归档；最近推送 2026-08-30；[v3.8.6](https://github.com/m-bain/whisperX/releases/tag/v3.8.6) 发布于 2026-05-25；API `open_issues_count=227`，不能由此判断响应速度。pyannote 模型许可须另外核对。 | Python 和 `whisperx` CLI；README 提供 CUDA、CPU/int8、调小 batch 或模型降显存方案。Linux 有主流程示例；Windows 组合依赖安装是否稳定**需要实验确定**。GPU/显存随 ASR、对齐与 diarization 模型变化，不能把单一数字当整条管线要求。[CLI/Python 文档](https://github.com/m-bain/whisperX#usage--)。 | [论文](https://www.robots.ox.ac.uk/~vgg/publications/2023/Bain23/bain23.pdf)研究长音频时间对齐；仓库源码还针对“3+ hour podcasts”优化 speaker 区间查询，但不等于两小时播客完整流程已在本机验证。README 承认 overlap 和 diarization 限制。数字、符号等未对齐问题：README 仍称会缺时间戳，而当前[源码已加入 wildcard 分支](https://github.com/m-bain/whisperX/blob/main/whisperx/alignment.py)，修复在具体版本/模型下的效果**需要实验确定**。 |
| [faster-whisper](https://github.com/SYSTRAN/faster-whisper) · **DIRECT REUSE**（ASR 层） | CTranslate2 Whisper 推理，词时间戳与 VAD；复用 `WhisperModel` / `BatchedInferencePipeline`。无内建 speaker 或 overlap 语义。[README 用法](https://github.com/SYSTRAN/faster-whisper#usage) | MIT；未归档；最近推送 2025-11-19；[v1.2.1](https://github.com/SYSTRAN/faster-whisper/releases/tag/v1.2.1) 发布于 2025-10-31；API `open_issues_count=323`。 | Python 本地包；CPU/int8 与 CUDA 均有示例；README 给出 Windows/Linux CUDA 库安装途径。官方 13 分钟样本基准：RTX 3070 Ti 8GB 上 large-v2 fp16 约 4.5GB，batch=8 约 6.1GB，**仅适用于该基准**。[基准与依赖](https://github.com/SYSTRAN/faster-whisper#benchmark) | 官方列出 [WhisperX、aTrain 等实际集成](https://github.com/SYSTRAN/faster-whisper#community-integrations)，但 13 分钟基准不证明两小时稳定性。已有 [VAD/批处理漏词 issue](https://github.com/SYSTRAN/faster-whisper/issues/1270) 和 [Windows 词时间戳崩溃 issue](https://github.com/SYSTRAN/faster-whisper/issues/1342)；选定版本需回归。 |
| [NeMo Forced Aligner](https://github.com/NVIDIA-NeMo/Speech/tree/main/tools/nemo_forced_aligner) · **WRAP·ADAPT**（校正稿对齐） | 输入已有 transcript 或 ASR 文本，输出 token/word/segment 时间戳；复用 `align.py` 和 manifest/CTM 等时间标注格式。不是完整 ASR+speaker 系统。[工具说明](https://github.com/NVIDIA-NeMo/Speech/blob/main/tools/nemo_forced_aligner/README.md) | NeMo Speech 仓库 Apache-2.0；未归档；最近推送 2026-09-24；[v3.0.0](https://github.com/NVIDIA-NeMo/Speech/releases/tag/v3.0.0) 发布于 2026-08-07；API `open_issues_count=300`（整个大仓，非本工具专属）。 | NeMo ASR 安装、Python 脚本/CLI、manifest 批处理；英文模型示例明确。Linux 路径有文档；Windows 原生安装和实际 GPU 峰值**需要实验确定**。[Quickstart](https://github.com/NVIDIA-NeMo/Speech/blob/main/tools/nemo_forced_aligner/README.md) | 官方称可处理 **1+ 小时**，条件是硬件/模型；这是项目方声明而非两小时实测。提供 [Hugging Face demo](https://huggingface.co/spaces/nvidia/nemo-forced-aligner)；播客多人重叠的有效性**需要实验确定**。 |
| [whisper-timestamped](https://github.com/linto-ai/whisper-timestamped) · **REFERENCE** | Whisper 注意力图 + DTW 生成词时间戳/置信度；可参考置信度字段、停顿和 disfluency 处理，不直接承诺并入主链。[README](https://github.com/linto-ai/whisper-timestamped) | AGPL-3.0；未归档；最近推送 2026-08-17；[v1.15.9](https://github.com/linto-ai/whisper-timestamped/releases/tag/v1.15.9) 发布于 2025-09-09；API `open_issues_count=48`；[公开 issue](https://github.com/linto-ai/whisper-timestamped/issues) 含置信度/VAD 问题。 | Python API 与 CLI/JSON；README 给出 CPU Docker 与 GPU 安装。Windows 本地组合与显存峰值**需要实验确定**。[运行说明](https://github.com/linto-ai/whisper-timestamped#usage) | 仓库有输出样例和 Docker，不是独立生产验证；长播客吞吐/内存**需要实验确定**。许可义务和已有较成熟的 WhisperX/faster-whisper 方案使其暂列参考。 |
| [stable-ts](https://github.com/jianfch/stable-ts) · **REJECT**（主依赖） | 静音修正、词重分组、对齐及可重处理的 JSON 值得设计参考。[输出/对齐说明](https://github.com/jianfch/stable-ts#output) | MIT；2026-05-30 归档且 README 明言开发无限期暂停；最新 GitHub release [2.0.0](https://github.com/jianfch/stable-ts/releases/tag/2.0.0) 为 2023-03-17；归档后开放 issue 为 0，不代表质量无问题。 | Python 与 `stable-ts` CLI；FFmpeg 前置，README 提供 Windows/Linux 安装指引。CPU/GPU 与显存取决于 Whisper 后端。[Setup](https://github.com/jianfch/stable-ts#setup) | README 有演示、SRT/JSON 输出，没有足够证据证明本项目的长播客精度；归档状态使后续维护风险过高。 |
| [whisper-diarization](https://github.com/MahmoudAshraf97/whisper-diarization) · **REFERENCE** | Whisper + CTC 对齐 + NeMo speaker 嵌入的拼装案例；参考组合顺序，不把它当 overlap 解决方案。[README](https://github.com/MahmoudAshraf97/whisper-diarization) | BSD-2-Clause；未归档；最近推送 2026-08-15；未查到 GitHub latest release；API `open_issues_count=41`。 | `diarize.py` CLI，本地 Python；README 列 Windows/Linux FFmpeg 安装；并行版提示至少 10GB VRAM 且属实验性。[安装及用法](https://github.com/MahmoudAshraf97/whisper-diarization#installation) | README 明言 overlapping speakers 未解决；有 notebook/示例，但两小时播客稳定性**需要实验确定**。 |

## 时间轴输出：交给 M07 的已知事实

- WhisperX [类型定义](https://github.com/m-bain/whisperX/blob/main/whisperx/schema.py) 给出 `segments: [{start, end, text, words: [{word, start, end, score}]}]` 及扁平 `word_segments`。`align()` [按片段对齐并返回两层结构](https://github.com/m-bain/whisperX/blob/main/whisperx/alignment.py)。`score` 是对齐分数，**不能直接当作 ASR 文本正确率**。个别词可能缺时间戳，调用方应允许缺失并标注原因。
- [diarization 源码](https://github.com/m-bain/whisperX/blob/main/whisperx/diarize.py)先得到独立的 `start/end/speaker` 区间，再按相交时长为每个 segment/word 选**一个** speaker。由此可推断：若后续需要 overlap 和 interruption，必须保留原始多 speaker 区间，不能只保存选出的单个 speaker。完整 overlap 检测与分离属于 [M03 · Speaker diarization 与多人重叠讲话](https://github.com/CometDash77/project-babel/issues/4) 的决策。
- faster-whisper [转写 API](https://github.com/SYSTRAN/faster-whisper#word-level-timestamps) 有 segment 与词的开始/结束；其 VAD 可跳过静音，但 VAD 设置会影响边界。NeMo NFA 则适合对已校正的逐句稿重新对齐；其 [manifest](https://github.com/NVIDIA-NeMo/Speech/blob/main/tools/nemo_forced_aligner/README.md) 可携带音频路径与文本。
- **推论，待 M07 定案**：pause 可以先从相邻可靠词/片段的时间差求出；turn 需结合 speaker 区间与断句规则；overlap 需从多 speaker 原始区间求交。三者都不是 WhisperX 对齐结果中可直接信任的原生字段。时间坐标必须回到原节目绝对时间，切片/VAD 的 offset 处理与精度**需要实验确定**。本票只给字段来源，不冻结 Smart Context schema。

## 需要实验确定

1. 在同一组英文播客样本（两小时、至少两位说话人，含打断、轻声、笑声、背景音乐）比较 WhisperX 全管线与 faster-whisper + NeMo NFA：WER、词边界误差、漏词、数字/专名、GPU 峰值、耗时和失败恢复。短基准/论文不能替代该验收。
2. 对 overlap 区间盲听核查：原始 diarization 区间与 WhisperX 单 speaker 分配差异；决定哪些片段必须交给 M03 的重叠讲话处理。
3. Windows 与 Linux 各跑一次固定版本的 CPU/GPU 安装、单段及长音频；记录 CUDA/cuDNN、HF 模型许可/下载、内存峰值。尤其核查 faster-whisper 的 [Windows 崩溃报告](https://github.com/SYSTRAN/faster-whisper/issues/1342)在所选版本上的状态。
4. 对数字、金额、外来词、重复词、低声与长静音检查“未对齐词”比例，并验证 WhisperX 当前 wildcard 实现和 README 限制之间的版本差异。
5. 对切片/VAD 后的绝对时间还原与连续性做可重复检查；衡量句间 pause 和 turn 推导的误差，再交 [M07 · Smart Context 上下文构建](https://github.com/CometDash77/project-babel/issues/8) 确定结构。

本稿是候选与复用边界调研；最终选型和实测质量留给地图中的后续实验及汇总。
