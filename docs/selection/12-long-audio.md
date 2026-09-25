# M12 · 长音频生成与拼接选型调研（research）

调研日期：2026-09-25。目标是把约两小时英文多人播客重演为中文，允许逐段重试，保留原节目时间定位、重叠讲话和同一说话人的音色。本稿只提供候选与证据，**不指定主选或备选**；该决定留给 [M12 拍板票](https://github.com/CometDash77/project-babel/issues/57)。已复核 [M12 模块稿](../research/12-long-audio-assembly.md)及[一条龙项目反查](00-mature-pipeline-stack.md)；未安装、合成音频或做两小时实验。

## 判断边界

M12 涉及四种不同能力：TTS 分块生成、已生成片段的持久化与选择性重试、原节目绝对时间及多轨表达、最终音频渲染。单次长上下文 TTS、线性有声书拼接与原播客多轨重演并不等价。[M12 模块稿](../research/12-long-audio-assembly.md)已指出，[MOSS-TTSD](https://github.com/OpenMOSS/MOSS-TTSD)声称的单会话 60 分钟仍不能证明两小时任务恢复；TTS 模型选型属于 M11。本稿将各组件按**可复用能力**横比，组合可行性仅是待验证的工程推断。

## 候选横比

热度和维护数字来自各仓库 GitHub API 的 2026-09-25 快照；stars 是关注度，不是质量评分，`pushed_at` 不证明核心路径得到修复。下文的成功案例区分官方演示、公开用户使用与本项目验收，均未发现可审计的“两小时英文多人播客 → 中文同声线、保留重叠且可续跑”案例。[前置反查的案例边界](00-mature-pipeline-stack.md#样本真实使用与维护快照)亦相同。公开 issue 仅抽样检查，不把单次答复或关闭数当作整体响应时限。

| 候选与角色 | 跑通案例、真实使用和本题复用点 | 热度、维护、许可及局限 |
| --- | --- | --- |
| [tts-audiobook-tool](https://github.com/zeropointnine/tts-audiobook-tool) · 分段生成/复核工作流 | [README](https://github.com/zeropointnine/tts-audiobook-tool#description)记录按段落、句、短语切分，生成后用 STT 检查和重试，逐行分配声音样本，审听后选择性删除与重生片段；[使用说明](https://github.com/zeropointnine/tts-audiobook-tool#usage-notes)提供保存项目状态和继续处理。官方有短样例和有声书入口，但未见原播客绝对时间、多轨重叠的公开交付案例。 | [API](https://api.github.com/repos/zeropointnine/tts-audiobook-tool)：213 stars、2026-09-17 推送、未归档、open_issues_count=2；未查到 latest release。MIT；本地 Python/FFmpeg，所需显存取决于所选 TTS 后端。保存状态是否能经断电及输入变更后正确重用，**需要实验确定**。 |
| [ebook2audiobook](https://github.com/DrewThomasson/ebook2audiobook) · 会话恢复参照 | [CLI 的 `--session`](https://github.com/DrewThomasson/ebook2audiobook#for-detailed-guide-with-list-of-all-parameters-to-use)明示中断或崩溃后继续；章节式成品和多语言 TTS 有公开运行入口。真实用户曾报告[活跃 session 被清理而丢失进度](https://github.com/DrewThomasson/ebook2audiobook/issues/1056)，说明恢复边界必须验证。另一[长文件导出问题](https://github.com/DrewThomasson/ebook2audiobook/issues/2093)中，维护者称在 59 小时文件上测过修复，用户确认导出问题解决；这是导出个案，**不是**两小时多人中文生成与续跑验证。章节顺序不表达播客绝对时间和同时说话。 | [API](https://api.github.com/repos/DrewThomasson/ebook2audiobook)：20,225 stars、2026-09-25 推送、未归档、open_issues_count=4；[v26.9.25](https://github.com/DrewThomasson/ebook2audiobook/releases/tag/v26.9.25) 当日发布。Apache-2.0；[导出 issue](https://github.com/DrewThomasson/ebook2audiobook/issues/2093)有维护者跟进与用户读回；当前版本对 session 清理风险的修复效果**需要实验确定**。 |
| [pyVideoTrans](https://github.com/jianchang512/pyvideotrans) · 成品流程参照 | [九阶段架构](https://github.com/jianchang512/pyvideotrans/blob/main/docs/architecture.md)显示按字幕逐条 TTS、配音缓存、时长对齐和 FFmpeg 合成；[对齐说明](https://github.com/jianchang512/pyvideotrans/blob/main/docs/Synchronize.md)公开逐条配音与原时段差异的处理。完整视频翻译流程已跑通，但[用户报告克隆声线第二句改变](https://github.com/jianchang512/pyvideotrans/issues/1182)，且现有证据不覆盖两小时多轨恢复。 | [API](https://api.github.com/repos/jianchang512/pyvideotrans)：19,142 stars、2026-09-24 推送、未归档；[v4.13](https://github.com/jianchang512/pyvideotrans/releases/tag/v4.13) 于 2026-09-20 发布。GPL-3.0；可参考阶段缓存和对齐策略，直接沿用需检查代码许可、接口和重叠轨能力。 |
| [OpenTimelineIO](https://github.com/AcademySoftwareFoundation/OpenTimelineIO) · 时间线数据组件 | [结构文档](https://github.com/AcademySoftwareFoundation/OpenTimelineIO/blob/main/docs/tutorials/otio-timeline-structure.md)定义 Timeline、Track、Clip、Gap、Transition，并描述多轨音频相加；可表示说话人轨和时间空隙。它是编辑信息格式，文档明确渲染效果由应用决定；不生成 TTS，也不提供片段任务 checkpoint。公开应用集成不能证明本题音频质量。 | [API](https://api.github.com/repos/AcademySoftwareFoundation/OpenTimelineIO)：1,989 stars、2026-09-22 推送、未归档、open_issues_count=212；未查到 latest release。Apache-2.0；Python/C++。绝对时间到目标采样率与 FFmpeg 的映射**需要实验确定**。 |
| [FFmpeg](https://ffmpeg.org/) · 音频渲染组件 | 官方滤镜文档提供 [`adelay`、`amix`、`acrossfade`](https://ffmpeg.org/ffmpeg-filters.html)；可按已决定的起点延迟、混合独立轨并处理合适的接缝。[FAQ](https://ffmpeg.org/faq.html#How-can-I-concatenate-video-files_003f)区分 concat filter/demuxer 用法；这些是公开可复现的功能示例，不是本项目两小时成功案例。FFmpeg 不负责 TTS、缓存语义或判断何处能淡化。 | [官网许可](https://ffmpeg.org/legal.html)：默认配置主要 LGPL，启用某些组件会变为 GPL，须按实际构建核对。活跃上游，具体二进制的版本和编译选项需落地时记录。两小时多轨内存、编码边界和输出可播放性**需要实验确定**。 |
| [pydub](https://github.com/jiaaro/pydub) · 短片段接缝参照 | [API 文档](https://github.com/jiaaro/pydub/blob/master/API.markdown#audiosegmentappend)展示 `append(crossfade=...)`；[README](https://github.com/jiaaro/pydub#how-about-an-example)有多文件列表拼接示例。适合局部接缝原型；该示例没有持久任务状态、原节目绝对时间或多轨语义。默认 crossfade 可能吞字，不能机械套用。 | [API](https://api.github.com/repos/jiaaro/pydub)：9,800 stars、2026-03-19 推送、未归档、open_issues_count=423；[latest release v0.25.1](https://github.com/jiaaro/pydub/releases/tag/v0.25.1) 发布于 2021-03-10。MIT；Python + FFmpeg。全片对象拼接的内存开销**需要实验确定**。 |

前置反查还发现 [SoniTranslate](https://github.com/R3gm/SoniTranslate) 的 checkpoint 声称及[十分钟视频仅配出 60 秒的用户报告](https://github.com/R3gm/SoniTranslate/issues/184)。因此它可作失败恢复对照，不能据 README 推定长节目已验证。[前置反查](00-mature-pipeline-stack.md#项目--m01m13-技术栈矩阵)也记录 VideoLingo 的恢复日志与删除缓存重跑限制。原模块稿提到的“Bridge”缺少可唯一识别的 URL/作者；[核查记录](../research/12-long-audio-assembly.md#结论)不足以将同名项目纳入候选。

维护响应抽样：[tts-audiobook-tool 的安装与模型 issue](https://github.com/zeropointnine/tts-audiobook-tool/issues/40)有作者数次答复及用户试用反馈；[pyVideoTrans 的配音角色 issue](https://github.com/jianchang512/pyvideotrans/issues/1187)有维护者答复，但最终由机器人超时关闭，不能视为需求已解决；[OpenTimelineIO 的安装路径 issue](https://github.com/AcademySoftwareFoundation/OpenTimelineIO/issues/2007)有社区讨论且仍开放；[pydub 的公开 issue](https://github.com/jiaaro/pydub/issues/862)未见维护者答复。这些样本只反映相应问题的处理，FFmpeg 则以[官方文档](https://ffmpeg.org/ffmpeg-filters.html)与[发布页](https://ffmpeg.org/download.html)核对组件维护，不与 GitHub issue 数横向打分。

## 供拍板票比较的实现路线（推断，均非现成集成）

1. **分段工具改造**：考察 tts-audiobook-tool 的逐段生成、复核和重生，将其输出接到本项目片段清单、绝对时间轴及渲染器。优势是已有可见工作流；缺口是多轨原时间与完整恢复语义。[项目说明](https://github.com/zeropointnine/tts-audiobook-tool)、[OTIO 结构](https://github.com/AcademySoftwareFoundation/OpenTimelineIO/blob/main/docs/tutorials/otio-timeline-structure.md)。
2. **自有片段清单 + 组件**：用独立清单记录文本、speaker、原始 `start/end`、目标区间、模型/音色版本、参数、音频校验值与状态；用 OTIO 表达轨道/空隙、FFmpeg 渲染，参照有声书工具处理重试。这是按各工具能力推导的集成方案，**不是**已成功的现成一条龙。[M12 模块稿的缓存与时间策略](../research/12-long-audio-assembly.md#建议的分段与时间策略待实验的设计判断)、[FFmpeg 滤镜](https://ffmpeg.org/ffmpeg-filters.html)。

以上路线均须把重叠讲话放到不同轨，逐片段落盘和校验后再独立导出。线性 concat 或跨完整词的固定 crossfade 无法替代这些契约。[OTIO 结构](https://github.com/AcademySoftwareFoundation/OpenTimelineIO/blob/main/docs/tutorials/otio-timeline-structure.md)、[FFmpeg acrossfade 文档](https://ffmpeg.org/ffmpeg-filters.html#acrossfade)。

## 启动前门槛：需要实验确定

- **两小时续跑**：在 10%、50%、95% 进度模拟中断，检查片段可复用、损坏检测、文本/模型/音色变化后的失效范围和重复生成耗时；尤其复核 session 清理风险。[ebook2audiobook `--session`](https://github.com/DrewThomasson/ebook2audiobook#for-detailed-guide-with-list-of-all-parameters-to-use)、[用户故障](https://github.com/DrewThomasson/ebook2audiobook/issues/1056)。
- **时间与重叠**：按原节目绝对时钟对照成品词/句起止，测每 10–15 分钟及末尾偏差、重叠讲话保留率；明确中文译文超时的处理阈值，并验证 OTIO→FFmpeg 映射。[OTIO 时间线](https://github.com/AcademySoftwareFoundation/OpenTimelineIO/blob/main/docs/tutorials/otio-timeline-structure.md)、[FFmpeg `adelay`/`amix`](https://ffmpeg.org/ffmpeg-filters.html)。
- **听感与资源**：早/中/晚抽样盲听爆音、吞字、停顿、响度和同 speaker 音色漂移；记录目标 TTS 与渲染的 GPU/CPU/RAM/磁盘峰值、耗时和最终文件可播放性。[tts-audiobook-tool 的分段与复核](https://github.com/zeropointnine/tts-audiobook-tool#description)、[M12 模块稿](../research/12-long-audio-assembly.md#需要实验确定)。

待 M12 拍板票确认的非实验条件：M11 最终 TTS 及安全分块长度；允许的时间误差和重叠保留阈值；若要研究 Bridge，提供原始项目链接。当前只按个人用途比较；实际部署时仍须核对模型权重、音色素材和所用 FFmpeg 构建的许可。[M12 模块稿](../research/12-long-audio-assembly.md#需要实验确定)、[FFmpeg 许可](https://ffmpeg.org/legal.html)。
