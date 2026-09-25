# M07 · Smart Context 上下文构建

调研日期：2026-09-25。目标是英文播客当前句翻译时构建「前 10 句＋当前句＋后 10 句」的**最多 21 句**上下文。本稿只做资料调研与接口建议，未运行翻译模型、声学模型或两小时播客实验；所有效果、阈值和成本结论均**需要实验确定**。项目当前仅供个人使用。M04、M05、M06 已完成资料调研并解除本票依赖。[M03 模块稿](03-diarization-overlap.md)也已发布，但其 speaker 与 overlap 候选尚未实测，仍保留可修订边界。

## 结论与当前句所需信息

建议把 21 句视为**邻句检索范围**，不是每句都必须塞入所有声学数值。当前句保留完整原文、原节目绝对时间、稳定句 ID、词界引用，以及质量标记；邻句保留原文、顺序、粗略时间与候选 speaker，能帮助消歧的人物/术语/指代和少量局部事件按相关性加入。过去已确认的译名或用语可作为独立、可修订的长程记忆。翻译输出只对应当前句 ID；前后句是只读上下文。这个方案是基于下述项目能力与本项目需求的**架构推论**，21 句是否优于更小/动态窗口、每个字段是否提高译质，均**需要实验确定**。

“句”应先定义为语义翻译单元，不直接等同于 SRT/WebVTT cue 或 WhisperX segment：一个 cue 可跨句，完整句可跨多个 cue，WhisperX segment 也可包含多句。[WhisperX 的 `SingleSegment` 注释明确允许多个句子](https://github.com/m-bain/whisperX/blob/main/whisperx/schema.py)。句界、合并/拆分及稳定 ID 的产生规则须与 M04 时间轴共同验证；节目开头/结尾自然少于 21 句，缺位不伪造。时间有交叠时保留并行区间，列表仅用稳定排序显示，不从列表次序推断轮流讲话。

## 候选与具体复用点

四档含义：**DIRECT REUSE** 是在限定能力内可直接采用；**WRAP·ADAPT** 要加本项目时间轴/来源封装；**REFERENCE** 只借设计；**REJECT** 指不作为 Smart Context 的主记录或完整方案，并不否定其导出用途。维护快照来自 2026-09-25 GitHub API；`pushed_at` 为仓库级推送，`open_issues_count` 含 PR，均不能单独证明本功能质量。

| 候选 / 分类 | 一手证据与值得复用的结构、流程 | 本项目边界、维护与运行 |
| --- | --- | --- |
| [pysubs2](https://github.com/tkarabela/pysubs2) · **DIRECT REUSE**（仅字幕导入/导出） | 官方 README 给出 `load` / `save`、Python API 和批量转换 CLI；可读写 SRT、ASS、WebVTT 等，内部转成 ASS 风格表示。复用**格式解析、时间与文本交换**，不让其表示成为 Smart Context 的权威 schema。[官方 README](https://github.com/tkarabela/pysubs2#usage)。 | 维护方明说超出 ASS 可表达的制作格式特性不是目标；模型分数、来源和修订状态必须另存。纯 Python、无额外依赖、MIT；未归档，最近推送 2026-08-16，最新 tag `1.9.0`（GitHub latest release API 未返回），开放 issue/PR 合计 17。Windows/Linux 与往返保真、长播客加载成本**需要实验确定**。 |
| [context_translate](https://github.com/darksylinc/context_translate) · **WRAP·ADAPT**（滑窗逻辑） | README 明列 `--pre-ctx`、`--batch-size`、`--pos-ctx`，把前后文与待译批次区分；CSV 有原文和 `Collection` speaker 栏，另有可追踪行键。复用**前/当前/后角色**和稳定行键思路。[用法与例子](https://github.com/darksylinc/context_translate#how-to-use)。 | 目前 CSV 无音频绝对时间、词界、重叠/声学事件；README 自称 early alpha，批次不并发。Rust CLI、GPL-3.0；未归档，最近推送 2026-08-28，latest release `v0.1.0`（2025-11-11），API 开放 issue/PR 合计 0。README 展示本地 llama.cpp/Vulkan 案例，不证明 Windows/Linux 的本项目安装或两小时长播客表现，均**需要实验确定**。 |
| [LLM-Subtrans](https://github.com/machinewrapped/llm-subtrans) · **REFERENCE**（上下文记忆与验证） | 按场景分批、前批摘要/术语表传递、逐批映射和行数校验；可读 SRT/ASS/VTT。借用**场景摘要、术语记忆、译文与源行对齐校验**，不是直接继承电影场景切分。[官方说明](https://github.com/machinewrapped/llm-subtrans/wiki)、[选项](https://github.com/machinewrapped/llm-subtrans#advanced-usage)。 | 场景间并行会失去先前摘要；摘要可能误导，需保留来源与可修订性。Python GUI/CLI，有 `install.bat`/`install.sh`；项目自身 [MIT](https://github.com/machinewrapped/llm-subtrans/blob/main/LICENSE)，依赖另有许可。未归档，最近推送 2026-09-24，release `v1.7.0`（2026-09-15），开放 issue/PR 合计 11。真实长播客、LLM 成本和摘要准确率**需要实验确定**。 |
| [llm-subs](https://github.com/azratul/llm-subs) · **REFERENCE**（长程记忆与失效边界） | `analyze` 产出 episode context，`memory.json`、`glossary.json`、`style_guide.json` 与冲突记录分开；按当前块提及内容过滤记忆。缓存键含前后上下文，编辑邻句会使相关块重译。复用**相关术语过滤、冲突留痕、上下文版本影响缓存**的设计。[官方 README](https://github.com/azratul/llm-subs#memory-and-conflicts)、[缓存说明](https://github.com/azratul/llm-subs#resume-caching-and-progress)。 | 面向剧集角色/字幕，不能把自动推断的性别、关系或 speaker 当播客事实。Python CLI，GPL-3.0；未归档，最近推送 2026-09-02，release `v0.8.0`（2026-07-10），开放 issue/PR 合计 2。作者报告的 token 节省不能外推本项目；平台、成本与质量**需要实验确定**。 |
| [chatgpt-subtitle-translator](https://github.com/Cerlancism/chatgpt-subtitle-translator) · **REFERENCE**（token 预算与结构输出） | 支持结构化输出、按 token 预算携带历史、批次失败时缩小批量；timestamp 模式会提供时间但允许合并条目。借用**上下文预算与输出 ID/条目核验**，不继承合并后失去一对一的模式。[README 选项](https://github.com/Cerlancism/chatgpt-subtitle-translator#cli)。 | 历史上下文不是前后各 10 句；没有 M03/M05/M06 字段。Node.js ≥20、MIT、CLI/Web UI，支持兼容 API 与本地 Ollama；未归档，最近推送 2026-09-13，release `v3.3.2`（2026-04-13），开放 issue/PR 合计 3。Windows/Linux 与长音频成本**需要实验确定**。 |
| [pyannote.core](https://pyannote.github.io/pyannote-core/structure.html) 的 `Segment`/`Timeline`/`Annotation` · **WRAP·ADAPT**（事件时间轴） | `Segment` 有交集，`Timeline` 可持有重叠区间，`Annotation` 可在同一时间支持多轨道/标签；可借**区间相交、并行轨道和 speaker 区间查询**，并参考 RTTM 导出。[官方数据结构](https://pyannote.github.io/pyannote-core/structure.html)、[RTTM API](https://pyannote.github.io/pyannote-core/reference.html)。 | 它是时间数据结构，不会替本项目检测真实 overlap 或 laughter。M03 未定前 speaker 标签仅候选；`support()` 合并区间会丢失逐事件边界，不能取代原记录。Python 包；未归档，最近推送 2025-09-16，release `6.0.1`（同日）；GitHub API 未识别 SPDX 许可，直接集成前核对源码许可。平台与长音频内存**需要实验确定**。 |
| SRT / ASS / WebVTT / Praat TextGrid · **REFERENCE**（交换格式）；作为主记录 **REJECT** | [WebVTT 规范](https://www.w3.org/TR/webvtt1/)的 cue 有时间、可用 voice span，官方采访示例含同时讲话与笑声；[ASS 事件字段](https://github.com/SubtitleEdit/subtitleedit/blob/main/docs/reference/assa.md#events-section)有 Start/End/Name/Text；[Praat TextGrid](https://praat.org/manual/TextGrid_file_formats.html)可分 speaker/词的 interval tier 与事件 point tier。三者可用于导入、人工校对或导出；SRT 主要承载序号、时间、文本。[LLM-Subtrans 的格式支持](https://github.com/machinewrapped/llm-subtrans)可作互通例子。 | 这些格式没有统一承载模型版本、分数语义、质量/弃权、事件推导依据与修订历史的原生字段；ASS `Name`/WebVTT voice 也不证明 diarization 正确。用它们作唯一权威记录会让不确定性和 provenance 丢失。格式转换保真度**需要实验确定**。 |

[AiNiee](https://github.com/NEKOparapa/AiNiee) 支持 SRT/ASS/VTT、术语表、角色/背景/翻译风格与上下文关联，适合由 [M08](https://github.com/CometDash77/project-babel/issues/9) 深挖翻译工程；本票列 **REFERENCE**，只确认其官方声明，不推断它已支持本项目的 21 句音频事件结构。代码 AGPL-3.0；当前个人使用不据此排除，若以后分发或改变用途再复核许可。[官方 README](https://github.com/NEKOparapa/AiNiee)。

## 字段来源与确定性边界

以下是**拟议的 Smart Context 投影**，不是 M04/M05/M06 已冻结的统一 schema。“直接取”仅表示可取到该模型/工具的输出值，不表示它正确；凡需句界、时间变换或跨源匹配者都需另算。

| 需要的字段 | 来源与处理 | 记录时的语义 |
| --- | --- | --- |
| `text`、词/片段 `start/end`、对齐 `score` | 直接引用 [M04 的 WhisperX 候选结构](04-asr-timeline.md)；按句界重组并保留词/片段 ID。原节目绝对时间需验证切片 offset。 | ASR 文本和对齐分数是**模型观测**，不是听写真值；`score` 不可作 ASR 正确率。缺时间的词保留缺失原因。 |
| `duration`、句间/句内 `pause`、turn 候选 | `duration=end-start`；pause 从可靠相邻词/句界求非负间隙；turn 需结合 speaker 区间和断句规则。 | 是**从原始时间轴推导**的值/事件。说话交叠、漏词、VAD 切片或边界不可靠时不强填 pause。 |
| `speaker`、`overlap`、`interruption` | M04 的单 speaker 分配只作候选；保留 [M03](03-diarization-overlap.md) 建议的可相交原始 speaker 区间及版本，exclusive 结果仅辅助对齐。overlap 由多个有效区间相交推导；interruption 还需跨说话人起止、语义和听评，不等于 overlap。 | speaker 为**待修订的模型观测**；overlap 是依赖该观测的**推导事件**；interruption 是更高层**待验证解释**。即使 M03 调研已完成，模型仍未实测，字段仍可为空/unknown，禁止把单标签写成确定事实。 |
| `emotion` | 引用 [M05](05-emotion.md)语句级原始类别与完整分数向量、模型版本、切片来源及弃权原因；跨句/局部波动不能由单个均值池化标签推知。 | **模型观测**；softmax 非已校准概率，帧 embedding 不是逐帧情绪概率。 |
| `pitch`、`pitch range/direction`、`energy`、`pace` | 引用 [M06](06-prosody.md)的 F0/有声/能量原始观测；在有效、可归属的句内区间计算相对 speaker 基线、分位音域、局部方向/能量与由 M04 词界推导的语速。 | 原曲线是**测量/模型观测**，区间统计是**推导值**；“强调、升调、加速”是须验证阈值的**候选事件**。不把整条曲线、88/6373 维特征塞入上下文。 |
| `laughter`、非语音事件 | 可保留源字幕标注或以后检测器的带时间观测；与词/说话人区间相交后投影到句。 | 字幕人工标注可作为**来源限定的标注事实**；自动检测为**模型观测**。没有来源时不从情绪/音高凭空生成笑声。 |

“确定事实”只限可直接核验的记录事实（例如源文件 ID、文件中确有的文本、时间戳与人工已核实的标注）；它不保证源文件本身无误。每个值应携带 `source_audio_id`、原节目绝对区间、来源工具/文件及版本、原始值与单位、质量/弃权原因、修订版本及关联的句/词 ID。模型观测、规则推导和人工确认需用显式状态区分；冲突并存，不能静默覆盖。

## 21 句投影与长程记忆建议

1. 从可靠语义句序列按目标句 ID 截取前后最多 10 句。保留绝对时间，按时间加稳定 ID 排序；同起点或交叠句仍保留各自区间。前后句用于消歧，不要求模型重译；若句界变化，窗口版本与受影响译文应失效重算。这一失效边界借鉴 [llm-subs 缓存设计](https://github.com/azratul/llm-subs#resume-caching-and-progress)。
2. 先放当前句的原文、时长、可靠停顿/说话关系和少量可能影响中文措辞的局部事件；邻句优先原文、候选 speaker 与时序关系。仅加入与当前句指代、专名、纠正、插话相关的事件。长程记忆只提供已确认的术语、角色称谓、风格约束及其证据，保持与 21 句窗口分离。[LLM-Subtrans](https://github.com/machinewrapped/llm-subtrans/wiki) 的摘要与 [llm-subs](https://github.com/azratul/llm-subs#token-efficiency) 的相关性过滤是参考，不等于自动摘要可信。
3. 为每个局部事件附类型、绝对区间、关联句 ID、来源与状态；必要时只传“句末明显停顿候选”“另一人同时说话候选”等少量描述和引用。完整 F0/RMS 曲线、SER 分数向量与原始 diarization 轨道留在侧档供审计，不直接进每次提示。由声音推得的“愤怒/打断/强调”不可伪装为事实。
4. 控制目标句唯一输出、ID 对齐、空译/多译和前后文被误译的检查；上限同时受句数与 token 预算约束。是否需要摘要、动态缩窗或事件优先级，以及这些策略对英→中播客指代和表演还原的影响，**需要实验确定**。

## 需要实验确定

1. 在同一组多人英文播客的专名、代词、省略、回指、反讽、跨句修正和重叠场景上，盲评当前句翻译：无上下文、前后 3/3、10/10、动态 token 窗口；分别加/不加术语记忆及声学事件，测错误类型、人工偏好、token/耗时和长节目一致性。`21` 是票据目标，不是已证实最优窗口。
2. 人工检查 M04 句界、词界、切片 offset、缺时间词和说话交叠；验证 pause、duration、顺序、缓存失效及边界句的投影。按 M03 调研候选实测 speaker/overlap，比较单标签、原始多轨道与人工标注；专门区分 overlap 和真正 interruption。
3. 在同一可听片段上标注笑声、升降调、能量峰、语速改变及“不确定”；衡量 M05/M06 观测和压缩事件的误报、弃权与对译文的实际帮助。连续曲线阈值、speaker 归一化及音乐/分离伪影影响**需要实验确定**。
4. 固定候选版本做 Windows/Linux 本地导入与导出、长节目内存、时间坐标、并行/缓存和失败恢复检查；验证 SRT/ASS/VTT/TextGrid 往返是否丢失 speaker、overlap 或 provenance。运行端模型/GPU 成本随所选翻译后端而变，不能从各仓库示例外推。

本票未冻结生产 schema，也未声称上述候选已在本机跑通。M08 可继续研究翻译引擎；M03 候选经真实播客验证后再修订 speaker/overlap 边界。
