# M13 · 最终混音：中文重演人声与原节目声场

调研日期：2026-09-25。范围是**个人使用、可本地批处理的最终混音**，不是音源分离（M02）、重叠说话人分离（M03）或长音频拼接（M12）。本稿核对官方文档、仓库、发布记录和公开 issue；**没有安装候选、混制样片或做两小时播客实测**。下文的分类是复用判断，不代表音质已验收。

## 结论与四档口径

**以 FFmpeg filtergraph 为主混音引擎（DIRECT REUSE），以 `ffmpeg-normalize` 承担可选的成品响度处理（DIRECT REUSE）。** FFmpeg 已有多输入时间定位、浮点混音、`sidechaincompress`、声道/声像处理、淡变、EBU R128 测量与 `loudnorm`；这些是**现成信号处理能力**，并没有替本项目决定哪些英文词要压低、哪些笑声或吸气要保留、分离残留怎样避开中文配音。[FFmpeg 滤镜文档](https://ffmpeg.org/ffmpeg-filters.html)、[FFmpeg 命令行文档](https://ffmpeg.org/ffmpeg.html)。

`WRAP·ADAPT` 指适合包进程序但需写本项目数据转换和控制层；`REFERENCE` 指借鉴设计或局部使用、不选为主链；`REJECT` 指不满足本阶段开源、本地、可回溯的主链要求，**不代表工具无用**。四档是按本项目任务划分的，不是项目整体质量排名。[M12 模块稿](12-long-audio-assembly.md)已提出以 OpenTimelineIO 表示多轨时间线、FFmpeg 渲染，并将片段缓存与续跑状态作为本项目编排语义；两稿的接口仍待后续实验冻结。

## 目标轨与时间轴边界

目标轨为：中文克隆人声主轨、被动态压低的原英文人声、保留的笑声/吸气/咳嗽/叹气/短促反应、原背景音乐、原环境声与 room tone。**推论：**同一原节目音频分出的“原英文人声 stem”和“背景 stem”可能含互相泄漏，直接相加可能把英文残声、音乐染色或瞬态重复放大；本稿不把分离输出称为可无损 round-trip。M02 [子票](https://github.com/CometDash77/project-babel/issues/3)负责 stem 质量，M03 [子票](https://github.com/CometDash77/project-babel/issues/4)负责多人重叠区间；M13 只消费其带来源和时间坐标的结果。

建议的**交接契约（对 M12 方案的细化，不是既有实现）**：沿用 M12 的片段清单/多轨时间线，交付中文人声片段的源文件、绝对起止时间、speaker、原句/事件 ID、片段级增益和拼接/交叉淡变记录；M13 在同一绝对时间轴上引用各原声 stem 与保留事件。拼接接缝和对齐修正要作为显式事件保留，不能只拿一条无法定位原片段的中文长音频。若 M12 只交整段文件，M13 仍可混音，但难以针对单句复核、重新渲染和追踪接缝。WhisperX 的词/句时间戳与独立 speaker 区间来源见 [M04 模块稿](04-asr-timeline.md#时间轴输出交给-m07-的已知事实)；重叠事件不能从单一 speaker 标签推断。

## 候选逐项比较

GitHub 维护快照核于 2026-09-25；`pushed_at` 只说明仓库有推送，`open_issues_count` 含 PR，均不证明质量或响应速度。最近 release 是 GitHub API 的 `releases/latest`；没有结果不等于从未发布。表中的本地运行表示官方提供入口，**不是本机跑通**。

| 候选 / 分类 | 时间轴、ducking、声像、导出与具体复用点 | 响度、批处理、本地与维护证据 | 边界 |
| --- | --- | --- | --- |
| [FFmpeg](https://github.com/FFmpeg/FFmpeg) · **DIRECT REUSE**（主混音引擎） | CLI `-filter_complex` 和多输入；`atrim`/`asetpts`/`adelay` 定位，`amix` 混轨，`sidechaincompress` 用**第二路信号**驱动第一路压缩，`pan`/`stereotools` 控声像，`afade`/`acrossfade` 处理边界，WAV/FLAC/有损格式由编码器导出。[滤镜说明](https://ffmpeg.org/ffmpeg-filters.html) | `ebur128`/`loudnorm` 可测量及归一化；CLI 可脚本批跑，无模型 GPU 要求。官方 [9.0.2 稳定版](https://ffmpeg.org/download.html)发布于 2026-09-18；[许可说明](https://github.com/FFmpeg/FFmpeg/blob/master/LICENSE.md)为 LGPL 2.1+ 基础，启用 GPL/外部库可改变发行二进制的条件。 | 图的构造、轨道选择和响度目标须自定；复杂长图的性能与边界行为需实测。GitHub 是镜像，镜像的开放 issue 数不能代表官方工单。 |
| [ffmpeg-normalize](https://github.com/slhck/ffmpeg-normalize) · **DIRECT REUSE**（成品响度工具） | Python API/CLI 封装 FFmpeg；复用成品级 EBU R128 双遍归一化、真峰值目标、统计/批处理、选定音轨处理。它**不编排**人声与原声的逐句关系。[README](https://github.com/slhck/ffmpeg-normalize) | 本地 Python + FFmpeg、Docker，CPU 工具；`--preset podcast`、批处理和可记录编码设置均有官方说明。[v1.42.0](https://github.com/slhck/ffmpeg-normalize/releases/tag/v1.42.0)于 2026-09-02 发布；[许可证](https://github.com/slhck/ffmpeg-normalize/blob/master/LICENSE.md)为 MIT 文本；仓库未归档，最近推送 2026-09-02。 | 只在最终混合后定一次总体目标；若每段各自归一化，可能抹掉表演动态。静音开头影响增益的[历史 issue](https://github.com/slhck/ffmpeg-normalize/issues/146)提示真实素材需复核。 |
| [ffmpeg-python](https://github.com/kkroening/ffmpeg-python) · **WRAP·ADAPT**（可选 Python 图封装） | `.filter()`、多输入、`get_args()`/`compile()` 支持生成与记录复杂滤镜图；可封装 `sidechaincompress`、`amix` 等，但它本身**不实现**混音算法或时间轴规则。[README 与 API](https://github.com/kkroening/ffmpeg-python) | Apache-2.0；纯 Python，需另装 FFmpeg；仓库未归档，最近推送 2024-08-04，GitHub latest release 无结果。Windows/Linux 安装依赖 FFmpeg 本体。 | 对调试和命令回溯有价值；维护节奏较慢。直接生成 FFmpeg 命令是否更简单，留待实际图规模判定。 |
| [Pydub](https://github.com/jiaaro/pydub) · **REFERENCE**（短片段操作） | `AudioSegment.overlay(position=...)`、`pan()`、`export()`、append/crossfade 便于局部操作；`gain_during_overlay` 是**固定 dB**，不是信号驱动的 sidechain。[API 文档](https://github.com/jiaaro/pydub/blob/master/API.markdown) | MIT；本地 Python，非 WAV 编解码通常借 FFmpeg；[v0.25.1](https://github.com/jiaaro/pydub/releases/tag/v0.25.1)于 2021-03-10 发布，未归档且最近推送 2026-03-19。 | 全长大量 overlay 的性能有[公开报告](https://github.com/jiaaro/pydub/issues/550)，大文件仍在[开放提案](https://github.com/jiaaro/pydub/issues/135)中；因此不作为两小时、多短片段主混音引擎。 |
| [Editly](https://github.com/mifi/editly) · **REFERENCE**（声明式编排例子） | JSON/JS `audioTracks[{path,start,cutFrom,cutTo,mixVolume}]` 可表示轨道位置，CLI/API 可批跑；文档的“audio ducking”通过输出音频 normalization 描述，**未证实是两路独立信号的 sidechain**。[README](https://github.com/mifi/editly#edit-spec) | MIT；Node + FFmpeg；官方列 Windows/macOS/Linux；[v0.15.0-rc.1](https://github.com/mifi/editly/releases/tag/v0.15.0-rc.1)于 2025-01-19 发布，最近推送 2025-05-12。 | 以视频为主，音频规范不覆盖原节目保留事件、stem 溯源和精细压低策略；不选为音频主链。 |
| [auto-editor](https://github.com/WyattBlue/auto-editor) · **REFERENCE**（时间轴交换） | [v3 时间轴](https://auto-editor.com/docs/v3)能表达多层重叠音视频，CLI 可渲染/导出编辑器项目；可借鉴可持久化的 timeline 与人工复核出口。[README](https://github.com/WyattBlue/auto-editor) | 仓库 Unlicense；[31.6.0](https://github.com/WyattBlue/auto-editor/releases/tag/31.6.0)于 2026-09-06 发布，最近推送 2026-09-19；本地 CLI。 | 核心是自动剪切静音/视频编辑，没有证据证明能代替 M13 的多 stem sidechain 混音决策。v3 格式官方称仅部分稳定，需锁版本。 |
| [mixing](https://github.com/thorwhalen/mixing) · **REFERENCE**（轻量 Python 例子） | `duck_audio` 有电平检测、`overlay_audio`/`loop_audio`/`concatenate_audio` 可做音床和接缝；[作者文档](https://github.com/thorwhalen/mixing/blob/main/.claude/skills/mixing-audio/SKILL.md)明确是**固定深度 ducker**，不是压缩器/VAD，无 lookahead，非语音响声也会触发。 | MIT；依赖 FFmpeg/Pydub/soundfile；未归档，最近推送 2026-09-22，GitHub latest release 无结果；项目规模/长节目案例证据不足。 | 不凭“sidechain ducking”字样认定满足本项目的保留原英文/保留反应规则；只借鉴接口与局部音床处理。 |
| [Auphonic Multitrack](https://eu1.auphonic.com/help/api/multitrack.html) · **REJECT**（本阶段本地主链；商业服务对照） | 官方 API 有逐轨 `backforeground=ducking`、`ducking_fadetime`、pan、offset、导出处理后分轨与总体 loudness。 | 有批处理 API，但服务端处理与非开源算法不符合本轮“GitHub 成熟开源、本地可回溯”主链；个人用途不自动改变此点。 | 可作为功能对照和后续听感基准；上传原节目、成本、时长和数据治理另议，不在本阶段选作依赖。 |

## 现成能力与必须自建的编排规则

| 决策面 | 可直接使用的能力 | 本项目仍要明确的规则 |
| --- | --- | --- |
| 时间轴 | FFmpeg 滤镜图接受多路音频及位置处理；Editly/auto-editor 给出声明式轨道表示。 | 把 M12 片段与 M02/M03/M04 的绝对时间、speaker/事件 ID 对齐；选择修正、重叠与缺片段的处理；保留时间坐标版本。 |
| 动态压低 | FFmpeg `sidechaincompress` 是真实信号驱动，能调 threshold、ratio、attack、release、knee。[官方示例](https://ffmpeg.org/ffmpeg-filters.html#sidechaincompress) | 中文人声作何种检测信号；原英文是否只在对应译句压低；笑声/短反应是否豁免；音乐与 room tone 是否跟随、压低多少；要不要语句级增益包络而不只靠压缩器。 |
| 响度与声像 | `ebur128`、`loudnorm`、`pan`、`amix`、`alimiter` 等现成；`ffmpeg-normalize` 包装最终双遍处理。[滤镜文档](https://ffmpeg.org/ffmpeg-filters.html) | 目标 LUFS、真峰值、声像与原节目匹配策略；片段响度离群阈值；保证笑声与低声语气不被逐段归一化抹平。 |
| 导出/批量/回溯 | FFmpeg CLI 可无头运行并保存命令；`ffmpeg-python` 可输出实际参数；无 GPU 模型。 | 保存输入 stem 哈希、模型/分离版本、时间轴版本、完整滤镜图/参数、每段事件映射、统计值及成品文件；失败后能定位并仅重渲染受影响区间。 |

**推论：**应先把中文主轨作为完整、可定位的控制信号，将原英文压低与背景音乐压低设计成**不同处理支路**；笑声等保留事件单独放轨，避免“把原英文人声轨整体压低”同时压没真实反应。若保留事件与英文残声无法分开，此目标只能局部近似，须标记人工复核，不应宣称自动混音已解决分离问题。

## 特别风险与验收观察点

1. **人声分离残留**：在中文台词覆盖处和纯背景处分别听检英文残字、音乐抽吸、相位/瞬态重复；保留原节目与 stem 的对照。`sidechaincompress` 只改电平，不能去除分离残留。
2. **重叠讲话**：原英文两人同时说话、中文配音跨原句、笑声插入时，单一旁链与单一 `speaker` 无法表达谁该退、谁要留。逐事件标注优先级与人工复核点；M03/M12 的结论可能改变轨道设计。
3. **片段接缝**：逐句中文 TTS 边界、背景 stem 分块边界、room tone 补洞处查爆音、静音洞、呼吸截断和相位跳变。`afade`/`acrossfade` 是工具，淡变长度及是否允许覆盖讲话仍须按事件决定。
4. **响度一致性**：测成品 integrated LUFS、LRA、true peak，并抽查相邻句、说话人转换、笑声前后与安静段的短时响度；全片达标不保证局部听感一致。最终指标和容差需根据使用平台/听评确定，不能预设通用数值。
5. **可回溯性**：同一输入、相同参数与版本应能定位到相同片段和滤镜图；导出无损中间成品及最终发布格式的差异要记录。压缩编码延迟、重采样和最终 trim 可能影响边界，需核查成品时间坐标。

## 需要实验确定

1. 选含音乐、静音、双人重叠、笑声、吸气与分离残留的同一批真实播客片段，对比 FFmpeg `sidechaincompress` 与事件级增益包络的听感：英文可懂度、中文清晰度、背景抽吸、反应保留，以及 attack/release/阈值/目标衰减的可接受区间。**当前没有样片或参数结论。**
2. 在 M02 实际 stem 上测“重组原 stem”与原节目差异（响度、相位、音乐纹理、原英文泄漏）；确定哪些区间要绕过分离、哪些需人工修补。M02 尚未定案。
3. M03 定案及 M12 方案实测后核对重叠事件与拼接结果的结构：是否有每句绝对时间、speaker、保留反应 ID、接缝记录；若无，评估重建成本和误差，确定接口。
4. 用两小时、多短片段、多轨项目测 FFmpeg 生成图规模、内存、耗时、失败恢复与 Windows/Linux 同版一致性；和 Pydub/ffmpeg-python 的实际开发复杂度比较。GPU 非混音引擎要求，分离/TTS 的 GPU 成本由各自模块评估。
5. 对无损与最终有损导出各做 EBU R128/真峰值和起止时间复测，量化编解码延迟、逐段与全片响度差、背景音床接缝；据听评再定 LUFS/真峰值目标、声像及容差。
6. 验证可回溯记录是否足以从成品异常追到原节目时间、源 stem、中文片段和滤镜参数；检查个人使用情境下保存/再处理的许可及输入节目权利边界。项目只供个人使用，**不据此推断所有输入节目都可任意再传播**。

本稿给出可复用引擎和自建规则的边界；最终混音参数、分离质量与两小时稳定性均待实验，不写入“已通过”。
