# M12 · 长音频生成与拼接

调研日期：2026-09-25。目标是将英文双人/多人播客重演为约两小时中文节目，允许逐段重试而不重做已完成部分，并保留原节目相对时序、重叠讲话及同一说话人的音色。本文核对项目官方仓库、文档、许可、发布/维护状态与部分公开 issue；**没有运行模型、生成音频或做两小时稳定性实验**。文中“可运行”仅指有本地入口，绝不代表本机验证。当前用途仅供个人使用；软件许可与模型权重许可分别记录。

## 结论

**暂不把“Bridge”当成已确定的项目或主架构。** [M12 票](https://github.com/CometDash77/project-babel/issues/13)没有 URL、作者或完整名称；以 Bridge、audio bridge、TTS bridge 联合检索，命中的是 [实时 TTS/API 桥](https://github.com/amenophis1er/tts-bridge)、[macOS MLX API 桥](https://github.com/QuasarRyan/mlx-audio-bridge)等不同用途，未找到能唯一指认票中 Bridge、且同时证明分段缓存、绝对时间线、多轨重叠与故障续跑的仓库。**身份需要原始链接确定**；不能把名称相近当作功能证据。

当前最可复用的组合是：以 [tts-audiobook-tool](https://github.com/zeropointnine/tts-audiobook-tool) 的分段生成、保存状态和逐段复核为**工作流候选**；以 [OpenTimelineIO](https://github.com/AcademySoftwareFoundation/OpenTimelineIO) 表达轨道、片段、空隙及过渡，以 [FFmpeg](https://ffmpeg.org/ffmpeg-filters.html) 按已确认的绝对时间渲染与拼接。这里的组合是**架构推断，不是现成集成**。必须由本项目保存片段清单、输入/模型/音色版本、输出校验与状态，明确“已生成、已校验、已渲染”的边界；否则两个小时中途崩溃仍可能丢失可用结果。[ebook2audiobook](https://github.com/DrewThomasson/ebook2audiobook)的 `--session` 可作恢复机制对照，但其有声书章节顺序不能直接代表播客绝对时间。所有候选均未提供本项目已验证的“两小时、多人、跨语言、断点续跑且时间/音色连续”证据。

## 能力边界：模型与外部编排

| 问题 | TTS 模型本身 | 外部编排/拼接 |
| --- | --- | --- |
| 长输入及跨轮音色 | [MOSS-TTSD](https://github.com/OpenMOSS/MOSS-TTSD)官方声称单会话最长 60 分钟、1–5 人；[VibeVoice-TTS](https://github.com/microsoft/VibeVoice)曾声称单次最长 90 分钟、最多 4 人。均**不足以证明两小时单次稳定**，也不等于外部续跑。 | 按说话轮/语义句分块、固定 speaker→参考音色/模型版本，逐块生成与重试；生成时长和音色漂移仍须实测。 |
| 时间与重叠 | 模型“自然轮替/重叠”不等于服从原播客逐轮绝对时间。[MOSS 官方文档](https://github.com/OpenMOSS/MOSS-TTSD)没有给出本项目所需的逐轮绝对时间锁定与恢复协议。 | 保存原节目时间、目标开始/结束、说话人、轨道、实测输出时长。不同说话人同时间讲话应放不同轨，不可简单顺序拼接。 |
| 接缝 | 语义上下文、参考音色和随机采样会改变每块头尾发音。 | 仅在合适的停顿/波形零交叉附近裁切或微淡化。跨完整词语盲目 crossfade 会吞字；重叠讲话是多轨混合，非相邻语句的 crossfade。 |
| 失败恢复 | 一次模型长调用失败，模型一般不会自动交出已确认可复用的中间结果。 | 对每块做持久化、校验和可重试状态；最终导出是独立阶段。断电、输出截断、换模型/参考音色的失效范围需要实验确定。 |

## 逐候选核查与分类

分类指 **M12 具体复用点**，不是项目整体质量。维护快照取 GitHub API 2026-09-25：`pushed_at` 只表示仓库推送，`open_issues_count` 可能含 PR；“无 latest release”也不等于无 tag。真实案例若只见项目演示，不上升为两小时证明。

| 候选 / 归类 | 分块、缓存/续跑、拼接、时间线的证据与复用点 | 维护、许可、本地/资源与证据限度 |
| --- | --- | --- |
| [tts-audiobook-tool](https://github.com/zeropointnine/tts-audiobook-tool) · **WRAP·ADAPT** | 官方说明按段落/句/短语分段、生成后 STT 核查与重试、停顿修整和 EBU R128 归一化；[保存会话状态、可中断继续及按章节导出](https://github.com/zeropointnine/tts-audiobook-tool#usage-notes)。可复用分段审听、选择性重生与状态思路，或研究其代码中的具体模块。它输出读书同步词时间，不代表能导入原播客绝对时间、多人同时讲话或交叉淡化。 | MIT；未归档，最近推送 2026-09-17，latest release API 未返回，open_issues_count=2。Python 本地运行，README 给 Windows/Linux 虚拟环境、FFmpeg，支持多模型本地或 SGL-Omni；显存随后端变化，文档举 Fish S2 需 24GB、MOSS 9B 需 24GB+。官方[短样例](https://github.com/zeropointnine/tts-audiobook-tool#description)和有声书流程是使用实例，非两小时多人播客验证。 |
| [ebook2audiobook](https://github.com/DrewThomasson/ebook2audiobook) · **REFERENCE**（恢复/章节） | [CLI `--session`](https://github.com/DrewThomasson/ebook2audiobook#for-detailed-guide-with-list-of-all-parameters-to-use)明示中断/崩溃后继续，支持文本、章节、TTS 引擎与输出格式。参考 session 和分块持久化方式；其书籍/章节线性结构不能直接承载原节目多轨重叠。 | Apache-2.0；未归档，2026-09-25 推送及 v26.9.25 release，open_issues_count=7。README 提供 Windows/Linux/macOS、CPU/多种 GPU 入口；“最低 2GB RAM/1GB VRAM”为项目声称，不代表本题模型可在该资源上稳定跑两小时。公开有[处理期间 session 清理导致进度丢失的历史 issue](https://github.com/DrewThomasson/ebook2audiobook/issues/1056)；该 issue 已关闭，当前版本是否完全消除风险**需要实验确定**。 |
| [OpenTimelineIO](https://github.com/AcademySoftwareFoundation/OpenTimelineIO) · **WRAP·ADAPT**（时间线数据） | 官方[时间线结构文档](https://github.com/AcademySoftwareFoundation/OpenTimelineIO/blob/main/docs/tutorials/otio-timeline-structure.md)有 `Timeline/Track/Clip/Gap/Transition`、多轨音频相加及过渡范围，可承载句段位置、speaker 轨和局部过渡；它是编辑数据模型/交换格式，**不自动运行 TTS、持久化任务或按模型重试**。对效果的实际渲染由应用决定。 | Apache-2.0；未归档，2026-09-22 推送，latest release API 未返回，open_issues_count=212。Python/C++ 接口和本地安装文档；自身无需 GPU。与 FFmpeg 的映射、逐样本时钟和本项目元数据扩展需要适配。 |
| [FFmpeg](https://ffmpeg.org/ffmpeg-filters.html) · **DIRECT REUSE**（音频渲染组件） | 官方[`acrossfade`、`adelay`、`amix` 过滤器](https://ffmpeg.org/ffmpeg-filters.html)可处理局部淡化、绝对延迟后叠加；[concat demuxer](https://ffmpeg.org/ffmpeg-formats.html#concat-1)可串接同流参数文件，但官方警告错误 `duration` 可导致时间戳伪影，流参数也必须一致。复用 CLI/滤镜；它不决定句界、音色、不提供持久 TTS checkpoint。 | 活跃上游，GitHub 镜像 2026-09-25 推送；镜像 latest release API 未返回。官方[许可说明](https://ffmpeg.org/legal.html)：通常 LGPL-2.1+，启用部分可变 GPL。Windows/Linux 本地 CLI、CPU 可用；两小时渲染耗时、内存、重采样与编码器组合须在目标机器测。 |
| [pydub](https://github.com/jiaaro/pydub) · **REFERENCE**（短片段操作） | README 展示 `AudioSegment` 毫秒切片、`append(crossfade=...)` 和导出；可用于快速验证局部接缝，但默认逐段对象拼接没有现成断点续跑、绝对时间轴或多人轨状态。两小时全量内存占用**需要实验确定**，不据短例推断。 | MIT；未归档，2026-03-19 推送，latest release v0.25.1 为 2021-03-10，open_issues_count=423。Python + FFmpeg，Windows/Linux；CPU，GPU 非所需。 |
| [MOSS-TTSD](https://github.com/OpenMOSS/MOSS-TTSD) · **REFERENCE**（模型长上下文候选） | 官方声称单会话 60 分钟、1–5 人、中文及跨语言克隆，提供 JSONL 批量推理和 SGLang 服务；可作为 M11 的模型实验候选，但**不是**任务缓存/拼接器。60 分钟声称不推出两小时连续性，跨会话接缝与同声纹需听评。 | 代码 Apache-2.0；未归档，2026-09-06 推送，未查到 latest release，open_issues_count=53。Python/PyTorch，官方批量脚本使用可见 GPU，服务文档提示显存碎片；实际峰值显存、Windows 安装及模型权重条款需按具体版本核对。官方评测和演示不替代本题负载。 |
| [VibeVoice-TTS](https://github.com/microsoft/VibeVoice) · **REJECT**（当前上游主仓直接集成） | 官方曾声称 90 分钟单次、4 人，示例有 45 分钟对话；但[2025-09-05 公告](https://github.com/microsoft/VibeVoice)写明已从仓库移除 TTS 代码，当前表中 TTS quick try 为 Disabled。即使其他分支/权重可见，也不能据该主仓认定有受维护、可续跑的两小时 TTS 组件。 | MIT 仓库；未归档，2026-09-03 推送，open_issues_count=196（混合 ASR/TTS）。主仓 TTS 本地运行、资源与许可组合不作肯定判断；重新纳入需具体可执行来源和版本。 |
| [open-unified-tts](https://github.com/loserbcc/open-unified-tts) · **REJECT**（完整方案），**REFERENCE**（短段 crossfade） | README 展示按句/段切分、短块 TTS 后 30–50 ms crossfade；但“无限长度/无缝/音色一致”为仓库宣称，[文档](https://github.com/loserbcc/open-unified-tts#why-crossfade)未给出两小时、绝对时间线、多轨重叠或持久 checkpoint 证据。固定 30–50 ms 也可能吞掉辅音，须听评。 | Apache-2.0；仓库已归档，最后推送 2026-08-03，无 latest release，open_issues_count=1。本地 API/后端说明存在，但维护状态和恢复缺口使其不宜作主系统。 |

## 建议的分段与时间策略（待实验的设计判断）

1. **切块单位**：以有 speaker 和原节目绝对 `start/end` 的说话轮为基础，句界内再切到所选 TTS 的安全输入长度；保留词/句 ID、原区间、目标文本、音色参考与模型参数。重叠轮次分别属于不同轨。切块边界优先停顿，不在词中截断。实际长度阈值由 M11 模型和显存实验确定。
2. **缓存与续跑**：每片段的输入文本、speaker/音色参考、模型与版本、采样参数、目标区间和生成音频校验值组成可追溯记录。只复用校验通过且条件未改变的产物；失败/超时/截断块独立重试，换音色或模型后仅失效受影响块。最终节目按已冻结片段清单重新渲染，避免把半成品当成功。这是本项目需实现或适配的编排语义，以上候选尚未证明原生覆盖。
3. **时钟与接缝**：原节目绝对时间是意图，合成音频实测样本数/采样率是事实。先统一采样率、声道与响度，再决定停顿、可接受微调、局部重生或时长压缩；不可累计估算时长直接推后所有后续段。Crossfade 仅在无词边界作候选处理，重叠讲话用多轨时间定位+混合；原节目背景声与最后混音归 M13。

## 需要实验确定

1. **两小时恢复演练**：固定真实中文双人/多人译稿与参考音色，分别在 10%、50%、95% 中断/断电模拟，重启后核对已完成片段是否免重生、损坏块是否被发现、换文本/模型/音色时失效范围；统计重复耗时与磁盘峰值。现有 README 的 resume 声称不能代替演练。
2. **接缝与音色**：按说话人和节目早/中/晚随机抽取至少几十个相邻块，盲听爆音、吞字、停顿、响度跳变、韵律断裂和同一 speaker 音色漂移；比较直切、停顿拼接、短淡化与局部重生。短音频 demo 不能推出两小时结果。
3. **时间对齐与漂移**：对照 M04 原节目词/句时间与合成音频重新测得的词界，记录每 10–15 分钟及全片的绝对偏差、重叠保留率、末尾累计漂移；核查 FFmpeg concat 的时长/编码边界和 OTIO→渲染映射。中文重演自然时长可能大于或小于英文原声，需预先确定允许的拉伸/静音/重写边界。
4. **资源与平台**：在实际 Windows/Linux、目标 TTS/声卡/显卡上记录每音频分钟生成耗时、失败率、GPU 显存峰值、CPU/RAM/磁盘峰值、临时 PCM 与最终文件大小；检查连续两小时运行的显存碎片、泄漏和导出可播放性。FFmpeg 本身可用不表示所选模型可用。
5. **许可证/真实案例**：本次按个人使用，不用商业集成限制预先排除候选；真正运行前核对选定模型权重/依赖及音色素材条款。找到可公开审计的两小时多说话人项目案例时，再把它和实验数据纳入结论；当前仅见各项目自述、样例或较短演示。

**待决**：Bridge 的精确 URL/作者；M11 最终 TTS 模型及其安全分块长度；本项目可接受的时间误差、重叠保留与音色连续性阈值。上述条件未定前，不冻结完整集成选型。
