# M02 · 人声与背景音分离

调研日期：2026-09-25。目标是从英文播客取得可供 ASR、说话人和表演分析的人声，同时保留原音乐、片头片尾、环境声与 room tone，供中文重演时重混。范围仅为候选调研；**未下载模型、未运行分离、未试听本项目样本，也未测两小时节目**。本项目仅供个人使用；代码许可与模型权重、训练数据、原节目素材的使用条件分别看待。下文“可本地运行”仅表示官方给出入口。

## 结论

1. **播客同域基线：PodcastMix，WRAP·ADAPT，仅作为实验候选。** 它明确研究 *speech/music*，提供预训练 UNet 与 ConvTasNet、CPU/GPU 命令，以及有参考轨的真实播客测试分区。[数据与评测仓库](https://github.com/MTG/Podcastmix)、[预训练推理仓库](https://github.com/MTG/Podcastmix-inference)。但后者的 [`forward_podcast.py`](https://github.com/MTG/Podcastmix-inference/blob/main/forward_podcast.py)实际从每个 WAV 的第 0 帧只读取 `segment × sample_rate` 帧，再输出两个 `s*_estimate.wav`；它**不能开箱处理整期节目**，还逐 stem 做峰值缩放，不能据输出宣称无损回拼。两个仓库均未在 GitHub API 识别出 license；取得清晰授权前只作为研究基线，权重的使用条款**需要实验确定**（含核对仓库/作者说明），不能按“GitHub 可下载”推定为开放许可。
2. **工程主实验入口：audio-separator，WRAP·ADAPT。** 复用其 `Separator.load_model()` / `separate()`、CLI 批文件、模型下载/缓存与 BS-RoFormer、MelBand-RoFormer、MDX、Demucs 等推理适配层；分别固定“人声优先”和“背景优先”模型进行盲听与重混测试。[官方 README](https://github.com/nomadkaraoke/python-audio-separator)。这是**封装**而非一种已在播客上获验证的模型；项目代码 MIT，外部权重许可逐个核对。其归一化、放大、`--single_stem`、反相生成另一 stem 和 ensemble 选择会改变 round-trip 结果，必须保存双 stem 与原始 PCM，记录处理参数。默认 RoFormer 权重是歌曲领域的人声/伴奏，不保证能把口语、串音、笑声、音效与 room tone 放到期望 stem。
3. **Demucs v4，REFERENCE（可跑对照，但不作为当前主依赖）。** MIT 代码及 `--two-stems=vocals` / Python 接口成熟，适合作歌曲领域对照；官方明确二 stem 仍先完成全分离，**不节省**时间或内存，`--segment` 可缓解显存压力，`--shifts` 按次数增加推理成本。仓库自 2025-01-01 归档，训练/评测以音乐为中心。[官方 README](https://github.com/facebookresearch/demucs)。
4. **先检测、后局部处理仍需自有编排。** inaSpeechSegmenter 的 MIT `Segmenter` 与 CSV/TextGrid 时间区间可 **DIRECT REUSE（粗略 speech/music/noise 分段）**；官方明言“speech over music/noise”标为 speech，所以它**不能检出同时有音乐的人声区间**。YAMNet 逐帧 521 类分数可 **REFERENCE** 用于构造 speech 与 music 同时活跃的候选窗，但其分数/阈值并非可靠的 stem 掩码。[inaSpeechSegmenter 官方说明](https://github.com/ina-foss/inaSpeechSegmenter)、[TensorFlow YAMNet 教程](https://www.tensorflow.org/tutorials/audio/transfer_learning_audio)。现有证据不足以认定有一款成熟项目可直接完成“overlap 检测→局部分离→无缝回贴→原时间坐标”。

**总体判断（推论）：** 两 stem 的加法闭合与“可直接拿背景重混”不同。用 `background = original - estimated_voice` 可让同一采样网格上的相加严格还原原混音，但人声漏入背景、音乐漏入人声和门限/相位伪影仍可能明显；直接相加两个模型估计 stem 也不保证闭合。原节目 PCM 永久保留，分离 stem 只是带版本与质量标记的派生资产。[audio-separator 双 stem/反相与归一化选项](https://github.com/nomadkaraoke/python-audio-separator)、[PodcastMix 推理源码的逐 stem 缩放](https://github.com/MTG/Podcastmix-inference/blob/main/forward_podcast.py)。

## 候选横向核查与逐项复用分类

维护快照由 2026-09-25 的 GitHub 仓库与 latest-release API 读取；`pushed_at` 是仓库推送，不能证明核心模型更新；`open_issues_count` **含 PR**，不能当纯 issue 数或质量评分。以下“真实案例”只指项目公开测试/使用，均非本项目实测。

| 候选 / 分类 | 复用点、能力边界与真实案例 | 维护、许可、接口与资源 |
| --- | --- | --- |
| [PodcastMix + 预训练推理](https://github.com/MTG/Podcastmix-inference) · **WRAP·ADAPT（实验）** | 复用同域 UNet/ConvTasNet 权重、`forward_podcast.py` 与 [real-with-reference 测试协议](https://github.com/MTG/Podcastmix#evaluate-over-real-podcasts-with-reference)。[论文](https://www.isca-archive.org/interspeech_2022/schmidt22_interspeech.pdf)说明把所有说话人合成一条 speech stem，基于“播客多人很少重叠”的观察；**不能处理 M03 所需的独立多人 stem**。推理源码只读每个文件首个 segment 且混为 mono；需要外部切片、跨窗拼接、通道与绝对 offset 管理。 | 两仓未归档；数据仓最近推送 2024-08-20，推理仓 2022-01-06；均无 latest release，开放 issue/PR 分别 1/0。GitHub API 未识别 license，需确认代码/权重授权。Conda + Python 脚本，44.1 kHz 预训练；README 有 CPU/GPU 两种入口，UNet 限制段长为 `2+16i` 秒。Windows、显存/速度及两小时吞吐**需要实验确定**。[推理 README](https://github.com/MTG/Podcastmix-inference)。 |
| [audio-separator](https://github.com/nomadkaraoke/python-audio-separator) 的 BS-RoFormer / MelBand-RoFormer / MDX 等 · **WRAP·ADAPT** | 复用 Python/CLI、本地批处理、模型列表与推理适配层；[README](https://github.com/nomadkaraoke/python-audio-separator)列出 vocals/instrumental、ensemble 和不同模型目标。BS/MelBand [原架构实现](https://github.com/lucidrains/BS-RoFormer)是音乐源分离，原仓 MIT 且支持 stereo、多 stem 训练；**架构代码许可不自动覆盖第三方 checkpoint**。官方公开的应用案例以卡拉 OK 为主，[维护者讨论](https://github.com/nomadkaraoke/python-audio-separator/discussions/82)还说明不同歌曲段落需要不同模型；不是播客验证。 | 未归档，最近推送 2026-08-27、release v0.47.0 同日，API issue+PR 27；代码 MIT。Python API/CLI/Docker，CPU、CUDA、MPS；Windows DirectML 对 RoFormer 有 allocator OOM、Demucs 缺算子，见 [项目限制](https://github.com/nomadkaraoke/python-audio-separator#directml-windows)。模型尺寸、显存峰值、处理两小时所需时间**需要实验确定**。 |
| [Demucs v4](https://github.com/facebookresearch/demucs) · **REFERENCE** | 复用两 stem 与四 stem 的对照、`--segment`/`--shifts` 成本控制概念；训练域为音乐，口语、环境声和重叠说话效果**需要实验确定**。 | MIT，2025-01-01 归档，最近推送 2024-04-24；无 GitHub latest release，issue+PR 275（只作快照）。CLI/Python，可 CPU/GPU；项目 README 说明 GPU OOM 时缩短 segment，二 stem 不减少开销，shifts 成本倍增。[官方说明](https://github.com/facebookresearch/demucs#separating-tracks)。 |
| [Ultimate Vocal Remover GUI](https://github.com/Anjok07/ultimatevocalremovergui) · **REFERENCE** | 参考多模型选择、试听及批文件的人机工作流；[README](https://github.com/Anjok07/ultimatevocalremovergui)定位歌曲人声移除，不把 GUI 当自动化流水线核心。可作人工对照，不提供播客多说话人或原时间轴契约。 | MIT 代码；未归档，最近推送 2025-03-13，latest release v5.6 为 2023-09-26；issue+PR 1537。Windows/macOS 包与 Linux 安装；CPU/GPU、具体模型依赖及许可分别核查。[安装/许可](https://github.com/Anjok07/ultimatevocalremovergui#installation)。 |
| [inaSpeechSegmenter](https://github.com/ina-foss/inaSpeechSegmenter) · **DIRECT REUSE（粗分段）** | `Segmenter(detect_gender=False)`、speech/music/noise 区间、CSV/TextGrid；法国电视/广播研究及监管报告是公开使用例。它把 speech+music 归 speech，不给同时存在的两个标签；不能独自作 overlap gate。[README](https://github.com/ina-foss/inaSpeechSegmenter)。 | MIT；未归档，最近推送 2026-03-12、latest release `interspeech23` 为 2023-03-30；issue+PR 9。Python/CLI/Docker，TensorFlow/FFmpeg，可本地批量文件处理；Windows 与长节目速度**需要实验确定**。 |
| [YAMNet](https://github.com/tensorflow/models/tree/master/research/audioset/yamnet) · **REFERENCE（候选窗）** | 复用逐帧 speech/music 等事件分数作为 overlap 候选提示；官方 [README](https://github.com/tensorflow/models/blob/master/research/audioset/yamnet/README.md)给本地 WAV 推理与帧可视化，基于 AudioSet 音频事件训练，不输出分离 stem，也未证明本项目所需同时语音/音乐定位精度。 | 代码所在 TensorFlow models 仓库 Apache-2.0；它是大仓，整体推送/release/issue 数不代表 YAMNet 子项目维护；子目录无独立 release。官方权重下载见 README，具体权重条款仍需核对。Python/TensorFlow，16 kHz mono，README 明示依赖 Keras 2、与 Keras 3 不兼容；Windows/Linux 与两小时成本**需要实验确定**。 |
| [Spleeter](https://github.com/deezer/spleeter) / [Open-Unmix](https://github.com/sigsep/open-unmix-pytorch) · **REJECT（当前主依赖）** | 都有 vocal/accompaniment 音乐模型、可作为补充基线；[Spleeter 模型说明](https://github.com/deezer/spleeter/wiki/3.-Models)、[Open-Unmix 推理接口](https://github.com/sigsep/open-unmix-pytorch/blob/master/docs/inference.md)。没有比上述候选更直接的播客口语、room tone 和局部分离契约，暂不加入主实验矩阵。 | 两者代码 MIT，均未归档；Spleeter 最近推送 2026-06-18、latest release v2.3.0 在 2021-09-03、issue+PR 279；Open-Unmix 最近推送 2024-06-17、v1.3.0 在 2024-04-16、issue+PR 9。分别有 Python/CLI、本地 CPU/GPU 路径；目标播客资源/音质**需要实验确定**。 |

## 关键场景、时间坐标与验收边界

- **多人重叠与串音。** vocal stem 通常汇集所有声音相似的人声；PodcastMix 论文明确将说话人合并。麦克风间串音属于同源声音的多轨混入，单通道/立体声二 stem 不保证消除。不能据“人声已分离”推断能给 M03 每位说话人独立纯净轨。[PodcastMix 论文](https://www.isca-archive.org/interspeech_2022/schmidt22_interspeech.pdf)。
- **音乐、音效、room tone。** 歌曲分离模型的人声目标与口语目标不一致；片头歌声、笑声、掌声、呼吸与混响可能被错放。背景残留的人声会与新中文人声叠影；过度去人声又可能抽走音乐泛音和原声场。两 stem 原样相加的波形误差、背景可重混程度和主观听感要**分别**评估。RoFormer [官方架构说明](https://github.com/lucidrains/BS-RoFormer)与 [audio-separator 关于不同目标模型的说明](https://github.com/nomadkaraoke/python-audio-separator)。
- **局部分离与边界。** 初步可将粗分类与逐帧 speech/music 分数并用，只对疑似重叠区间和需要更干净语音的区间跑重模型；纯音乐/纯静音原则上保留原 PCM。这是**待实测的编排推论**，不是上述工具现成能力。局部窗要加上下文、重叠与交叉淡化，检查接缝与相位；阈值与最短窗**需要实验确定**。[inaSpeechSegmenter 标签规则](https://github.com/ina-foss/inaSpeechSegmenter)、[YAMNet 帧级分类](https://www.tensorflow.org/tutorials/audio/transfer_learning_audio)。
- **原节目时间坐标。** 以原解码 PCM 的采样索引作为唯一坐标。每次处理记录源文件哈希、采样率、通道、裁切起点样本 `n0`、实际输入样本数、预留上下文、重采样映射、模型/权重版本与输出延迟。局部 stem 的样本 `k` 对应原节目 `n0+k`（若重采样则用显式有理比例和边界舍入）；写出前裁去上下文，逐窗核对样本长度和对齐，再交 M04 时间轴与 M13 混音。该接口是**本项目建议**，并非任一候选原生保证；尤其 PodcastMix 首窗读取与峰值缩放说明不能直接拿其文件名/输出时长当绝对位置。[推理源码](https://github.com/MTG/Podcastmix-inference/blob/main/forward_podcast.py)、[M04 时间轴模块稿](04-asr-timeline.md)。

## 需要实验确定

1. 用同一组**获准个人使用**的英文播客片段建立人工对照：纯语音、纯音乐、speech+music、两人打断/同说、跨麦串音、笑声/呼吸、片头尾与 room tone；比较 PodcastMix UNet/ConvTasNet 和 audio-separator 中明确锁定的 BS-RoFormer、MelBand-RoFormer、MDX 权重，以及 Demucs 对照。记录具体权重许可、版本与下载出处，先核清 PodcastMix 授权。
2. 对每个候选单独测可分析语音（ASR 漏词、VAD/说话人线索、听辨）、背景可重混（残留旧人声、音乐损伤、声场和 room tone）、伪影（抽吸、水声、瞬态、切片接缝），并分别测 `original - voice` 残差和模型背景 stem；“两 stem 相加误差小”不能替代盲听。
3. 取短段与两小时节目，在 Windows/Linux 固定环境记录模型下载、CPU/GPU/显存/内存峰值、磁盘中间文件、每小时处理时间、失败恢复、批量连续运行、分段开销。PodcastMix 的首窗读取缺口须在实验编排中显式补足；不能从它的 README 推断长节目已获支持。
4. 比较 inaSpeechSegmenter/YAMNet 候选窗与人工 speech+music/噪声标注的召回、误报；在漏检一段音乐或人声的代价下决定是否值得局部分离。独立核对每段起止样本、重采样回填、通道/相位、静音接缝与原节目绝对时间。

本稿给 M14 提供候选与证据边界，给 M03/M04/M13 提供时间与 stem 风险接口；最终模型、阈值和混音方案均未冻结。
