# M03 · Speaker diarization 与多人重叠讲话

调研日期：2026-09-25。用途：个人使用的英文播客→中文重演。这里只核对官方模型卡、源码、文档、发布记录和仓库状态；**未安装或运行模型，也未测真实播客**。模型自报指标、演示和本机可行性须分开看。

## 结论

**同一时刻可以有不止一位说话人。** 因而要保存可相交的原始 `speaker_id + start/end` 区间，而非为每个词、句或时刻只留一个 speaker。推荐以本地 [pyannote Community-1](https://huggingface.co/pyannote/speaker-diarization-community-1) 作 **WRAP·ADAPT** 主基线；以 [NVIDIA Nemotron-3-Diarization](https://huggingface.co/nvidia/Nemotron-3-Diarization) 作 **WRAP·ADAPT** 新候选盲比。前者同时提供常规与 exclusive diarization；**仅常规结果能保留重叠**，exclusive 只供与 [M04](04-asr-timeline.md) 转写时间戳对齐。后者输出至多八路逐帧 speaker 活动概率及后处理区间，适合独立核查重叠，但刚于 2026-09-23 发布，真实节目效果**需要实验确定**。[pyannote 输出源码](https://github.com/pyannote/pyannote-audio/blob/main/src/pyannote/audio/pipelines/speaker_diarization.py)、[NVIDIA 模型卡](https://huggingface.co/nvidia/Nemotron-3-Diarization)。

三件事必须分开：**diarization** 估计谁在何时讲话；**overlap detection** 只判断哪些时间同时有至少两位说话人，未必识别双方；**overlapping speech separation** 输出多路音频波形，既不自动给全局 speaker ID，也不提供可靠文本。优先从可重叠 diarization 区间或逐帧活动的同时激活推导 overlap，留独立检测器作对照；只在确有重叠且 ASR/听评受损的**局部片段**试 [SpeechBrain SepFormer](https://huggingface.co/speechbrain/sepformer-wsj02mix) 或 [Asteroid](https://github.com/asteroid-team/asteroid) 分离。纯人声/背景音分离属 M02，不用其结果代替多人语音分离。

## 候选与复用分类

分类是本票的调研决策，不是实测通过。GitHub 维护快照取自 2026-09-25 API：`open_issues_count` 含 PR，`pushed_at` 仅说明仓库有推送。各行所列模型许可与代码许可分别核对；个人用途也须遵守模型条款。

| 分支 / 候选 / 分类 | 官方证据：真实输出与具体复用点 | 许可、维护与推理入口 | 资源、长音频与主要限制 |
| --- | --- | --- | --- |
| Diarization：[pyannote Community-1](https://huggingface.co/pyannote/speaker-diarization-community-1) · **WRAP·ADAPT** | `Pipeline.from_pretrained` 本地返回 `speaker_diarization`（可相交 `Annotation`）、`exclusive_speaker_diarization`（无 overlap）和可选 speaker embeddings；[源码还提供可序列化的 `start/end/speaker` 两套列表](https://github.com/pyannote/pyannote-audio/blob/main/src/pyannote/audio/pipelines/speaker_diarization.py)。复用常规区间作为主时间轴、exclusive 作 M04 词标注辅助。 | [pyannote.audio](https://github.com/pyannote/pyannote-audio) 代码 MIT；[该权重](https://huggingface.co/pyannote/speaker-diarization-community-1) CC BY 4.0，下载前需同意 HF 用户条件并提供联系信息；下载后官方支持离线本地推理。仓库未归档，最近推送 2026-09-24，最新 release `4.0.7`（2026-06-30），`open_issues_count=43`。 | 默认 CPU、可 CUDA；官方 2025-09 DER 表计入 overlap、无 forgiveness collar，例如 AMI IHM 17.0%、VoxConverse 11.2%，均非本项目精度。16 kHz 单声道，读取时自动重采样/混声道；Windows/Linux 安装、两小时 speaker 数、边界与显存峰值**需要实验确定**。[模型卡](https://huggingface.co/pyannote/speaker-diarization-community-1) |
| Diarization / 活动检测：[Nemotron-3-Diarization](https://huggingface.co/nvidia/Nemotron-3-Diarization) · **WRAP·ADAPT**（新候选） | NeMo `SortformerEncLabelModel.diarize` 给标记区间；底层 `[T,8]` 每 speaker 活动概率，默认 10 ms 步长，可同时激活多路。复用逐帧概率、speaker 区间与 overlap 交叉验证；最多八位**全局候选说话人**，不是八人同时发声的保证。[模型卡输出](https://huggingface.co/nvidia/Nemotron-3-Diarization) | [NeMo Speech](https://github.com/NVIDIA-NeMo/Speech) 代码 Apache-2.0；权重受 [OpenMDW 1.1](https://huggingface.co/nvidia/Nemotron-3-Diarization) 约束，模型卡明示可个人/商业用途。NeMo 仓库未归档，最近推送 2026-09-24，release v3.0.0（2026-08-07），`open_issues_count=300`（全仓）；权重 2026-09-23 新发布。Python/NeMo、Transformers 与官方 C++ CLI 均有入口。 | 官方称分块推理无固定时长上限，非两小时稳定性证明；主文档以 NVIDIA GPU/Linux 安装示例为主，列多种 NVIDIA GPU，但无适用于本机的显存峰值。Windows、CPU、长节目跨 chunk 身份稳定性及混音域泛化**需要实验确定**。自报 DER 包含 overlap；参考 RTTM、collar 及数据集与 pyannote 不同，**不可直接横比**。[模型卡协议](https://huggingface.co/nvidia/Nemotron-3-Diarization) |
| Diarization：[NeMo Streaming Sortformer 4spk v2.1](https://huggingface.co/nvidia/diar_streaming_sortformer_4spk-v2.1) · **REFERENCE**（既有对照） | `diarize` 返回 `begin/end/speaker_index`，可选逐帧概率；官方 [diarization README](https://github.com/NVIDIA-NeMo/Speech/blob/main/examples/speaker_tasks/diarization/README.md) 给 RTTM 导出和含 overlap 的 DER。复用数据格式、分块及 speaker cache 对照。 | NeMo 代码 Apache-2.0，**该权重**另受 [NVIDIA Open Model License](https://huggingface.co/nvidia/diar_streaming_sortformer_4spk-v2.1) 约束；维护状态同上。 | 至多四位说话人；适合验证长节目分块和身份一致性，不应把 4spk 模型的限制归给 Nemotron-3。Windows/GPU 峰值及播客实测**需要实验确定**。 |
| Overlap：[pyannote 旧 OSD pipeline](https://huggingface.co/pyannote/overlapped-speech-detection) · **REFERENCE** | `output.get_timeline().support()` 给“≥2 人讲话”的区间，**不标双方身份，也不输出分离波形**；可作独立 overlap 召回对照。 | 模型卡标 MIT，下载需接受条件；它明写依赖 `pyannote.audio 2.1`。[pyannote 4.0 发布记录](https://github.com/pyannote/pyannote-audio/releases)已移除未维护的 OSD task/pipeline，故不能假设可直接装在 Community-1 的 4.x 环境。 | 固定旧环境的兼容、长节目资源、过检/漏检需实验；不作新主链依赖。 |
| Overlap：常规 diarization 区间求交 / Nemotron 同帧多路激活 · **DIRECT REUSE**（输出与判定规则） | 两条独立 speaker 区间相交、或同帧至少两路过阈值，形成候选 overlap 区间；前者保留身份，后者可保留活动概率。该判定是**本项目推论**，不是 pyannote/NeMo 原生“已确认重叠”真值。[pyannote 输出](https://github.com/pyannote/pyannote-audio/blob/main/src/pyannote/audio/pipelines/speaker_diarization.py)、[Nemotron 输出](https://huggingface.co/nvidia/Nemotron-3-Diarization) | 无新增权重；遵循上游各自许可。复用上游可重叠输出，阈值、最短持续时间和合并间隙自行校准。 | 两名说话人均漏检时求交也会漏检；假阳性相交会误触发分离。精确率/召回率**需要实验确定**。 |
| Separation：[SpeechBrain SepFormer WSJ0-2Mix](https://huggingface.co/speechbrain/sepformer-wsj02mix) · **WRAP·ADAPT**（局部试验首选） | [`SepformerSeparation.from_hparams`、`separate_batch` / `separate_file`](https://github.com/speechbrain/speechbrain/blob/89ead74d163463d30c62329a09cfdb4c54f5abc1/speechbrain/inference/separation.py#L27-L85) 输出 `[batch,time,2]` 两路估计波形；复用预训练推理，不把 source index 当跨片段 speaker ID。 | [SpeechBrain](https://github.com/speechbrain/speechbrain) 代码 Apache-2.0；[该模型卡](https://huggingface.co/speechbrain/sepformer-wsj02mix) 标 Apache-2.0。仓库未归档，最近推送 2026-08-27，release v1.1.1 同日，`open_issues_count=189`。本地 Python/PyTorch。 | 训练/评价面向 WSJ0-2Mix；真实播客混响、音乐、第三人插话、分离伪影、局部 GPU/CPU 成本**需要实验确定**。分离片段必须恢复原绝对时间并重做 source↔speaker 关联。 |
| Separation：[Asteroid](https://github.com/asteroid-team/asteroid) Conv-TasNet 等 · **REFERENCE**（替换后端） | [`BaseModel.from_pretrained` 与 encoder-masker-decoder `forward`](https://github.com/asteroid-team/asteroid/blob/5366d1fd7056a6ffb8b828fe2d83adbc43659521/asteroid/models/base_models.py#L92-L224) 输出多路估计波形；复用模型接口与 Conv-TasNet/DPRNN recipes 作不同计算成本的对照。 | 代码 MIT，**具体 checkpoint/训练数据许可逐个复核**。仓库未归档，最近推送 2026-09-24；最近 GitHub release v0.7.0 为 2023-10-12，`open_issues_count=55`。本地 PyTorch。 | 框架可用不代表每个预训练权重适合播客；Windows、长片段显存及源数/音质**需要实验确定**。 |
| [WhisperX `assign_word_speakers`](https://github.com/m-bain/whisperX/blob/main/whisperx/diarize.py) 作为唯一 speaker timeline · **REJECT** | 它为每词/片段按相交时长选**一个** speaker；可供 M04 阅读单词归属，但不能持久化为完整多人互动时间轴，也不做语音分离。[M04 分析](04-asr-timeline.md) | WhisperX 自身 BSD-2-Clause；其所用 diarization 权重另核对。 | 重叠时会丢第二位说话人的同期活动；原始区间必须另存。 |

## 时间轴与模块边界：给 M04 / M07

- **持久化建议，待 M07 定案**：每条原始说话人活动记录带 `source_audio_id`、原节目绝对 `start/end`、`speaker_id`、模型/权重版本、切片 offset、来源音轨、阈值/后处理参数与质量/弃权理由。同一时刻允许多条记录。另存从区间求交或独立 OSD 得到的 overlap 区间及证据来源；不要修改或覆盖原始 speaker 区间。speaker ID 只是本节目的候选簇，**不是现实身份识别**。
- M04 的 `segments/words` 与 speaker 区间是**两层数据**。可用 exclusive/最大相交 speaker 为词给一个便于展示的标签，但同时保留与该词相交的**全部**原始 speaker 区间及不确定性。`pause`、`turn`、打断、接话和 overlap 是后续按可靠词界、speaker 活动与规则推导的事件，不是一个 `speaker` 字段自带的信息。[WhisperX 源码](https://github.com/m-bain/whisperX/blob/main/whisperx/diarize.py)、[M04](04-asr-timeline.md)。
- 局部分离的产物另存：原混音与两路波形引用、原绝对区间、source index、模型版本、关联的候选 speaker ID、匹配依据/置信与质量标记。**source index 不等于 speaker ID**；多路波形不能代替原混音，尤其不能直接用于 M06 的原始声学表现测量。分离后 ASR 是否找回被遮挡的词，要与原音听评核对。
- [pyannote `speech_separation.py` 源码](https://github.com/pyannote/pyannote-audio/blob/main/src/pyannote/audio/pipelines/speech_separation.py)展示联合返回 `diarization, sources` 的研究接口；未在官方 Community-1 模型卡中见可直接使用的相应公开预训练 pipeline，故只列 **REFERENCE**，不宣称 Community-1 本身会输出分离波形。

## 需要实验确定（后续实验票输入；本票未运行）

1. **标注样本**：从至少一集约两小时英文播客抽取单人、双人插话、抢话、笑声/短反馈、第三人加入、远场/压缩音质、音乐/环境声等片段；人工标每位 speaker 的可相交绝对区间、实际 overlap 与不可判段，保存原声作盲听基准。
2. **Diarization 横比**：固定音频与评估协议，比较 Community-1、Nemotron-3 和 NeMo 4spk v2.1：含 overlap 的 DER（明确 collar）、说话人数/身份跨 chunk 错误、短反馈漏检、边界误差及两小时连续运行。不同厂商自报 DER 不直接排名。
3. **Overlap 检测**：在同一人工标注上比较区间求交、Nemotron 多路概率阈值、隔离旧环境的 pyannote OSD；按区间 precision/recall/F1 与触发延迟，并区分真重叠和音乐、笑声、回声。测试阈值、最短长度、合并间隙，记录假阳性导致的无谓分离。
4. **局部分离**：仅对 overlap 片段试 SpeechBrain SepFormer 与至少一个 Asteroid 模型；按双方 ASR 漏词变化、盲听可懂度、音色/节奏伪影、第三人残留、source↔speaker 匹配错误和耗时/显存评估。保留未分离原声，必要时允许“无法可靠分离”。
5. **可运行性/许可**：固定版本在 Windows、Linux 分别检查 HF 用户条件/模型条款、Python/CUDA/FFmpeg 安装、CPU 与现有 GPU 的峰值显存/内存、局部与两小时批处理失败恢复；记录重采样/切片/VAD 后的绝对时间回填。若未来超出个人用途，重新审查各权重许可。

本稿仅给出可复用轮子、输出语义和实验判据；没有证明任何候选已能在目标播客上正确分离或准确标记所有重叠说话人。
