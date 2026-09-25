# 巴别塔计划 · GitHub 轮子调研复用地图（终稿）

调研日期：2026-09-25。本文是 [M14 汇总票](https://github.com/CometDash77/project-babel/issues/15) 的产出，合并 [M01](01-acquisition-preprocessing.md)–[M13](13-final-mix.md) 十三份模块稿。**本阶段不含任何实现代码、模型运行或音频实测**；所有效果、成本、阈值结论均标「需要实验确定」。当前项目仅供个人使用；软件许可与模型权重许可分别看待，用途改变须重新核对。

评审说明：本稿经「技术方案评审团」三角色独立评审（软件架构师 / 应用安全工程师 / 验收测试工程师，2026-09-25，3/3 返回）；采纳的发现融入 §1、§2、§3，评审分歧记录在 §2.6，专家原始报告存于会话消息、未入库。裁决前做过两次澄清（见 §2.4、§3.2-6）。

## 四档口径（全文统一）

- **DIRECT REUSE**：限定能力内可直接调用的现成子能力（CLI/API/函数/规则），无需改造其内部。默认指**子能力/子层**，不表示整个项目可以原样顶上。
- **WRAP·ADAPT**：核心成熟，但必须包一层本项目的数据转换、时间坐标、来源记录与质量标记。
- **REFERENCE**：只借设计/接口/对照思路，不进首版主链。
- **REJECT**：不作为**本项目该用途**的主链；不否定项目本身价值。理由分三类：能力不足 / 维护状态 / 本阶段约束（如必须本地可回溯）。

**档位 = 候选 × 用途**：同一工具在不同用途下档位可以不同，本文逐处写明用途（ffmpeg-normalize、Translate Toolkit、pydub、WhisperX 均按此处理）。四档只给第三方候选；**本项目自己的设计与代码不挂四档**，一律进 §1.3 自研清单。每条归类回链到具体模块稿的具体章节。

---

## 一、完整架构图：成熟轮子 / 胶水层 / 自研

### 1.0 数据流总图

**所有跨模块接口均为「建议态」——13 稿中 0 处冻结**。这是本图最重要的属性：任何一端先动工都会返工，统一 manifest 数据契约是头号自研交付物（架构师评审 F1）。

```
原节目音频
  │ [M01 获取/预处理 · 轮] podcast-dl / yt-dlp / FFmpeg / ffprobe
  ▼
原始 PCM + 来源元数据 + 绝对起止时间   ← 权威坐标建议：原节目采样索引（秒为投影，见 §3.2-7）
  ├─→ [M02 分离 · 胶] audio-separator / PodcastMix ──→ stems（派生资产，互相泄漏）
  ├─→ [M03 diarization+overlap · 胶] pyannote Community-1 / Nemotron-3 ──→ 可相交 speaker 区间
  ├─→ [M04 ASR/词时间轴 · 胶] WhisperX / faster-whisper ──→ segments + words
  ├─→ [M06 声学测量 · 胶] librosa / torchcrepe / openSMILE ──→ F0/RMS/语速曲线
  └─→ [M05 情绪观测 · 胶] FunASR + emotion2vec+ ──→ 语句级情绪向量
        ▼
  [M07 Smart Context · 自研投影] 21 句窗口 + 稳定句 ID + 字段来源三层（观测/推导/确认）
        ▼
  [M08 翻译工程 · 胶(AiNiee/AiNiee-Next) + 自研两层稿] 忠实译文 → 中文表演稿
        ▼
  ⇄ [M09 TTS 前关口 · 自研编排] ⇄ [M10 异常修复路由 · 自研状态机]
  │        （Jev / scikit-learn / 零样本 NLI = 待实验的条件候选，非必需依赖）
  ▼ 待修项收敛
  [M11 克隆 TTS · 胶] Breeze / IndexTTS / Qwen3-TTS Base / CosyVoice / GPT-SoVITS
        ▼
  [M12 分段生成与拼装 · 胶(OpenTimelineIO + FFmpeg) + 自研编排] 片段清单 / 断点续跑 / 多轨时间线
        ▼
  [M13 最终混音 · 轮(FFmpeg filtergraph) + 自研混音规则]
        ▼
      中文重演成品

反馈环（不是单向 DAG）：M09 检查 → M10 路由 → 修复（回 M08 重译 / M11 重生成 / M12 重分块）
  → 同组复检 → 缓存失效与局部重渲染。此环无现成轮子，整块自研（架构师评审 F6）。
```

**运行形态**：各模块运行环境互斥（pyannote 2.1 与 4.x 硬冲突、YAMNet 依赖 Keras 2、各 TTS Python 版本不一、Node 工具混入 Python 链），胶水层按**每模块一个子进程 runner + manifest 文件契约**组织，不做单环境 import 拼接（架构师评审 F5）。

### 1.1 成熟轮子（直接拿，不重造）

| 能力 | 轮子 | 分类 | 回链 |
| --- | --- | --- | --- |
| RSS 播客批量获取 | podcast-dl | DIRECT REUSE | [M01 · 获取段](01-acquisition-preprocessing.md#获取段候选与复用判断) |
| 站点/YouTube 下载 | yt-dlp | DIRECT REUSE | [M01 · 获取段](01-acquisition-preprocessing.md#获取段候选与复用判断) |
| 解码/探测/切片/滤镜底座 | FFmpeg + ffprobe | DIRECT REUSE | [M01 · 预处理段](01-acquisition-preprocessing.md#预处理响度段候选与复用判断)、[M12](12-long-audio-assembly.md#逐候选核查与分类)、[M13](13-final-mix.md#候选逐项比较) |
| 粗略 speech/music/noise 分段 | inaSpeechSegmenter | DIRECT REUSE（粗分段；不能作 overlap gate） | [M02 · 横向核查](02-vocal-separation.md#候选横向核查与逐项复用分类) |
| ASR 转写层 | faster-whisper | DIRECT REUSE（仅转写） | [M04 · 结论](04-asr-timeline.md#结论与复用边界) |
| 中文读法规范化 | WeTextProcessing | DIRECT REUSE | [M09 · 候选核查](09-pre-tts-checks.md#候选核查与四档归类) |
| 汉语音节计数 | pypinyin | DIRECT REUSE | [M09 · 候选核查](09-pre-tts-checks.md#候选核查与四档归类) |
| 字幕格式导入/导出 | pysubs2 | DIRECT REUSE（仅字幕 IO） | [M07 · 候选](07-smart-context.md#候选与具体复用点) |
| 文本交换与静态 QA | Translate Toolkit | DIRECT REUSE（格式/静态 QA 子层用途；关口集成用途为 WRAP·ADAPT，见 1.2） | [M08 · 横向候选](08-translation-engineering.md#横向候选与四档分类)、[M09](09-pre-tts-checks.md#候选核查与四档归类) |
| 离线句级 MT 实验基线 | Argos Translate | DIRECT REUSE（实验基线） | [M08 · 横向候选](08-translation-engineering.md#横向候选与四档分类) |
| 英文 SER 实验基线 | SpeechBrain IEMOCAP 模型 | DIRECT REUSE（仅实验基线） | [M05 · 结论](05-emotion.md#结论与复用边界) |
| 成品响度处理 | ffmpeg-normalize | DIRECT REUSE（M13 成品用途；M01 整集标准化是另一用途，见 1.2） | [M01](01-acquisition-preprocessing.md#预处理响度段候选与复用判断)、[M13](13-final-mix.md#候选逐项比较) |

> 本表只列第三方候选。原稿曾把 M10 的「规则优先 + 固定动作表」标成 DIRECT REUSE、把 M03 的「区间求交判定」标成 DIRECT REUSE——两者都是本项目自己的推论设计而非候选项目，已按口径规则移入 §1.3（架构师评审 F3）。

### 1.2 胶水层（轮子可用，包一层就能接入）

| 能力 | 主候选（并列时为多候选盲比） | 分类 | 回链 |
| --- | --- | --- | --- |
| RSS 逐条挑选 | feedparser | WRAP·ADAPT | [M01 · 获取段](01-acquisition-preprocessing.md#获取段候选与复用判断) |
| 整集响度标准化 | ffmpeg-normalize | WRAP·ADAPT（M01 整集用途） | [M01 · 预处理段](01-acquisition-preprocessing.md#预处理响度段候选与复用判断) |
| 人声/背景分离 | audio-separator（BS-RoFormer/MelBand/MDX）、PodcastMix（同域实验，**授权待核**） | WRAP·ADAPT | [M02 · 结论](02-vocal-separation.md#结论) |
| Diarization | pyannote Community-1（主基线）、Nemotron-3（新候选） | WRAP·ADAPT | [M03 · 结论](03-diarization-overlap.md#结论) |
| 局部分离（overlap 片段） | SpeechBrain SepFormer | WRAP·ADAPT | [M03 · 候选](03-diarization-overlap.md#候选与复用分类) |
| ASR + 强制对齐管线 | WhisperX 全管线；校正稿对齐用 NeMo Forced Aligner | WRAP·ADAPT（作唯一多人重叠时间轴则 REJECT，见 M03） | [M04 · 结论](04-asr-timeline.md#结论与复用边界)、[M03 · 分类](03-diarization-overlap.md#候选与复用分类) |
| 情绪识别 | FunASR + emotion2vec+ | WRAP·ADAPT | [M05 · 结论](05-emotion.md#结论与复用边界) |
| 声学测量 | librosa(pYIN/RMS)、torchcrepe、Parselmouth、openSMILE eGeMAPSv02 | WRAP·ADAPT | [M06 · 候选横向核查](06-prosody.md#候选横向核查) |
| 上下文滑窗/记忆 | context_translate（前后/当前角色，early alpha）、pyannote.core 区间结构（SPDX 待核） | WRAP·ADAPT | [M07 · 候选](07-smart-context.md#候选与具体复用点) |
| 翻译工程 | AiNiee（字幕读写/缓存/术语/调度/检查，AGPL-3.0 固定 commit 295d2ff）、AiNiee-Next（双层稿先例） | WRAP·ADAPT | [M08 · 结论](08-translation-engineering.md#结论) |
| 文本关口检查 | pofilter/poconflicts、CometKiwi（无参考质量估计，权重许可待核） | WRAP·ADAPT（关口集成用途） | [M09 · 候选核查](09-pre-tts-checks.md#候选核查与四档归类) |
| 语义歧义路由 | Jev 1.13、scikit-learn 轻量分类器、零样本 NLI | WRAP·ADAPT（均待实验的条件候选） | [M10 · 逐候选分类](10-jev-routing.md#逐候选分类) |
| 声音克隆 + 中文 TTS | Breeze TTS 2、IndexTTS-2.5、CosyVoice 3（优先听评）；Qwen3-TTS Base（克隆 API 研究基线）；GPT-SoVITS（成熟工程基线，权重许可待核） | WRAP·ADAPT / DIRECT REUSE（Base 克隆 API 用途） | [M11 · 结论](11-voice-clone-tts.md#结论与判断口径) |
| 分段生成 + 状态续跑工作流 | tts-audiobook-tool（工作流候选；**采用时须关闭/外包其内建分段 EBU R128 归一化**，见 §3.2-8） | WRAP·ADAPT | [M12 · 结论](12-long-audio-assembly.md#结论)、[M12 · 逐候选核查](12-long-audio-assembly.md#逐候选核查与分类) |
| 多轨时间线数据 | OpenTimelineIO | WRAP·ADAPT | [M12 · 逐候选核查](12-long-audio-assembly.md#逐候选核查与分类) |
| 主混音引擎 | FFmpeg filtergraph（sidechaincompress/amix/adelay） | DIRECT REUSE（引擎；混音规则全部自研，见 §1.3-8） | [M13 · 结论](13-final-mix.md#结论与四档口径) |
| Python 滤镜图封装 | ffmpeg-python（可选，2024 后维护慢） | WRAP·ADAPT | [M13 · 候选逐项比较](13-final-mix.md#候选逐项比较) |

### 1.3 我们自己真正需要开发的部分（自研清单）

十三份模块稿一致指向：**零件都有，把零件连成「可追溯、可恢复、以原节目绝对时间为唯一坐标的播客重演流水线」的那层语义，没有任何现成项目提供。**逐项：

1. **统一 manifest / 资产簿（头号交付物）**——source_audio_id、原节目绝对时间、稳定句/词/片段 ID、每条观测的来源/版本/质量标记（provenance）、源文件哈希贯穿全链。13 稿所有跨模块交接都只是「建议」，0 处冻结；字幕/OTIO/RTTM 只能作导入导出格式，不能当主记录（架构师评审 F1/F7）。[M01](01-acquisition-preprocessing.md#从最终输出倒推输入)、[M07](07-smart-context.md#字段来源与确定性边界)
2. **权威时间坐标与区间推导规则**——采样索引为权威、秒为投影、转换记录有理比例与边界舍入；切片 offset、重采样映射、同帧多路 speaker 区间求交判定（M03 的项目推论）。三套坐标并存是错位风险的根源（架构师评审 F2）。[M02](02-vocal-separation.md#关键场景时间坐标与验收边界)、[M03](03-diarization-overlap.md#时间轴与模块边界给-m04--m07)、[M12](12-long-audio-assembly.md#建议的分段与时间策略待实验的设计判断)
3. **Smart Context schema 与 21 句投影**——字段来源三层语义、稳定句 ID、前后各 10 句截取、缓存失效边界、长程记忆与窗口分离。字幕 IO 和滑窗先例可抄，schema 本身无轮子。[M07](07-smart-context.md#字段来源与确定性边界)
4. **声学/情绪观测 → 翻译约束的转换**——F0/RMS/语速曲线压缩成带阈值的候选事件（pitch_rise、long_pause…）、speaker 归一化、弃权规则；测量轮子齐全，「曲线→LLM 友好事件」没有成熟轮子，事件→翻译约束的消费端还无人认领（§3.2-9）。[M06](06-prosody.md#从连续曲线压缩为少量可追溯事件)、[M05](05-emotion.md#交给-m07-的输出契约建议尚未冻结-schema)
5. **TTS 前文本关口的编排与阈值**——检查零件可复用，但「哪条能阻断、哪条只报疑点」的分层规则、字符比例口径、中文预计时长的区间估计模型（速率表 + 标点停顿预算）必须自研。[M09](09-pre-tts-checks.md#结论与关口分工)
6. **异常修复路由的状态机与动作表**——「规则优先 + 八个固定动作」是本项目的设计基线（自研产物，非四档对象）；PASS/FAIL 事实层、复检收敛、指纹去重、调用预算、永远可选的 ESCALATE。模型只在规则无法唯一确定时介入。[M10](10-jev-routing.md#从失败信号倒推路由能力)、[M10 · 分类](10-jev-routing.md#逐候选分类)
7. **统一 pipeline 编排 + 反馈环/缓存失效引擎**——片段清单（输入文本/参考音色/模型版本/目标区间/校验值）、断点续跑与失效范围、多轨重叠表达、OTIO→FFmpeg 渲染映射；检查→路由→修复→复检→失效传播是闭环而非单向 DAG（架构师评审 F6）。tts-audiobook-tool 与 ebook2audiobook 只给了工作流和 session 先例。[M12](12-long-audio-assembly.md#结论)
8. **混音规则**——中文主轨作控制信号、原英文压低与背景压低分路、笑声/短反应豁免轨、片段响度离群处理、可回溯滤镜图记录。FFmpeg 提供全部信号处理原语，不提供任何一条策略。[M13](13-final-mix.md#现成能力与必须自建的编排规则)
9. **子进程 stage runner 的运行形态**——环境矩阵互斥（pyannote 2.1/4.x、YAMNet Keras2/3、各 TTS Python 版本、Node 工具）决定胶水层必须按模块隔离进程、以 manifest 文件契约交换（架构师评审 F5）。

> 换言之：**自研集中在「胶水 + 规则 + 状态」，不集中在算法。**没有任何一个模块建议自己写分离、diarization、ASR、SER、F0 提取、TTS 或混音算法。

### 1.4 参考与排除（速查）

- **REFERENCE**：gPodder、Demucs、UVR、YAMNet、pyannote 旧 OSD、Asteroid、whisper-diarization、whisper-timestamped、SLAM+、AutoRPT、LLM-Subtrans、llm-subs、chatgpt-subtitle-translator、Weblate、OmegaT、XCOMET/DocCOMET、MFA（英文节奏）、OpenAI Structured Outputs、F5-TTS、MOSS-TTSD、ebook2audiobook、pydub（短片段操作）、Editly、auto-editor、mixing、pyannote speech_separation.py。
- **REJECT（限本用途）**：pydub（作主预处理依赖）、Spleeter/Open-Unmix（主分离依赖）、WhisperX 单 speaker 字段（作唯一多人重叠时间轴）、stable-ts（归档）、VibeVoice 主仓（TTS 代码已移除）、open-unified-tts（作完整方案）、Qwen CustomVoice（当克隆器）、Auphonic（本地主链，商业服务对照）、「无条件每段调 LLM」的接入方式（非项目档位）、AiNiee 等「整套播客双层翻译器」整体用途。
- 各 REJECT 的确切理由见对应模块稿，均为「不作该用途主链」，不是质量否定；双档行均已按「候选 × 用途」写明。

---

## 二、验证（不是接受）用户对自研边界的判断

用户判断：自研集中在五个方面。逐条对照 13 份模块稿证据裁决（裁决 = 证实 / 证伪 / 部分成立）。

### 2.1 Smart Context 上下文构建 — **证实**

- [M07](07-smart-context.md#字段来源与确定性边界) 自陈「拟议的 Smart Context 投影，不是已冻结的统一 schema」「本票未冻结生产 schema」——schema 与投影规则就是本项目要交付的东西，无轮子。
- 候选面证实复用有限：pysubs2 仅字幕 IO（DIRECT REUSE）；context_translate 是 early alpha 滑窗、无绝对时间/词界/重叠/声学事件（WRAP·ADAPT）；LLM-Subtrans、llm-subs、chatgpt-subtitle-translator 均只 REFERENCE；SRT/ASS/WebVTT/TextGrid 作主记录被 REJECT（无 provenance 字段）。[M07 · 候选](07-smart-context.md#候选与具体复用点)
- 旁证：AiNiee 一类工具按文件行处理，「缺播客的后文、speaker、声学事件及时间预算」，不能只调 prompt 就宣称达到 Smart Context。[M08](08-translation-engineering.md#ainiee模块文件级复用边界)
- 附注：可复用面（滑窗/记忆/区间结构/格式往返）记入 §1.2；「21 句」窗口本身是票据目标而非已证实最优，要靠窗口消融实验定（[M07 · 需要实验确定](07-smart-context.md#需要实验确定)）。

### 2.2 声学信息 → 翻译约束的转换 — **部分成立**

- **成立的一半（转换层自研 = 证实）**：[M06](06-prosody.md#从连续曲线压缩为少量可追溯事件) 直接结论——现成工具分别擅长测量（librosa/torchcrepe/Praat/openSMILE）、音高风格化（SLAM+）或特定标注（AutoRPT），「**未找到能直接输入混音、多说话人长播客并输出本项目全套可靠、LLM 友好事件的成熟轮子**」（限定「本次候选范围内」）。曲线→事件的阈值、speaker 归一化、弃权规则全部自研。[M05](05-emotion.md#结论与复用边界) 同向：SER 输出是模型观测，softmax 未校准、均值池化抹掉句内波动。
- **不成立/缺口的一半（→翻译约束）**：事件如何变成翻译层实际消费的「约束」，06→07→08 之间**无责任模块**——M06 把事件交 M07，M07 只说「按相关性加入」，M08 完全不消费事件（§3.2-9 / G3）；对译文质量的影响零实验证据。
- 因此按票面判断的完整链条（声学 → **翻译约束**）只证实前半段，判**部分成立**。

### 2.3 TTS 前检查关口 — **证实**

- [M09](09-pre-tts-checks.md#结论与关口分工) 自陈「这是本项目的**关口设计推论**，并非这些工具提供的现成播客工作流」；[M09 · 候选核查](09-pre-tts-checks.md#候选核查与四档归类) 直接结论：「**没有发现一个经过本项目验证、能在无中文语音条件下同时判断语义、表演与目标时长的现成工具**」。关口编排、分层阻断规则、三版时长估计路线全要自建（[M09 · 时长路线](09-pre-tts-checks.md#不生成最终-tts-的时长估计路线)）。
- 附注（复用面，不改变裁决）：检查零件高度可复用——WeTextProcessing/pypinyin（DIRECT REUSE）、pofilter/CometKiwi（WRAP·ADAPT）；自研的是「哪些能阻断、哪些只报疑点」的策略与阈值。且关口通过 ≠ 可播出：关口输出是「带证据的待修项」，不能替代听评（[M09 · 结论](09-pre-tts-checks.md#结论与关口分工)）。

### 2.4 异常修复路由 — **证实**

- **读法已澄清**：2026-09-25 grilling 确认，用户指「译文出问题时『发现→决定→修→复查→防死循环』这套流程要自己写代码搭出来」（读法 A）。裁决按此读法给出。
- [M10](10-jev-routing.md#结论) 结论：**现在不值得把 Jev 设为必经路由**；先让普通代码完成可判定检查，剩余案例进人工复核或已有翻译模型的受限结构化选择。路由状态机、八个有限动作、复检收敛、预算与弃权全部自研（[M10 · 路由能力](10-jev-routing.md#从失败信号倒推路由能力)）；Jev、scikit-learn、零样本 NLI 只是待实测的 WRAP·ADAPT 条件候选，「每段无条件调 Jev 再用置信度覆盖硬失败」被 REJECT（[M10 · 分类](10-jev-routing.md#逐候选分类)）。M10 并明确要求：终稿把「规则优先 + 有限动作 + 弃权/复检/预算」作为架构边界，**Jev 不写成必需依赖**。
- 备档：若日后出现「Jev 应为必经路由」的读法，M10 结论即反方证据（当时即判「不值得」）。

### 2.5 把成熟项目串成统一 pipeline — **证实**（附三条限定）

- **证实依据**：[M12](12-long-audio-assembly.md#结论)「这里的组合是**架构推断，不是现成集成**」；[M12 · 分段策略](12-long-audio-assembly.md#建议的分段与时间策略待实验的设计判断)「是本项目需实现或适配的**编排语义**，以上候选尚未证明原生覆盖」；[M13](13-final-mix.md#现成能力与必须自建的编排规则) 交接契约「对 M12 方案的细化，不是既有实现」；[M01](01-acquisition-preprocessing.md#从最终输出倒推输入)「接口推论，不是候选工具已经提供的一体化 pipeline」；[M02 · 时间坐标](02-vocal-separation.md#关键场景时间坐标与验收边界)「本项目建议，并非任一候选原生保证」；[M08 · 两层流水线](08-translation-engineering.md#建议的可追溯两层流水线设计推论非实现) 亦为「设计推论，非实现」。五稿六处交叉印证：串接层无现成覆盖，是最大的自研面。
- **限定一（包含关系）**：五点不是并列，见 §2.7——①③④发生在⑤的编排层内部，②是①→M08 的领域转换。
- **限定二（可证伪条件）**：原判「若 Bridge 被确认为成熟编排项目则降级为部分成立」；2026-09-25 用户已确认想不起该项目 → Bridge **弃用、不作依据**（§3.2-6），该可证伪点关闭。
- **限定三（安全强制条件，采纳安全工程师意见）**：编排层必须是**数据出境与凭据的唯一控制点**——外部 API（Jev/OpenAI 等）只作条件候选，默认本地优先、规则优先（[M10](10-jev-routing.md#结论)、[M13 · 需要实验确定](13-final-mix.md#需要实验确定)，策略见 §3.6）。
- **另一面如实记录（采纳验收工程师意见）**：「胶水必须自研」= 证实，但「现在就串得起来」= 零证据——本阶段 0 次实验（§四），可行性本身未验证。

### 2.6 裁决汇总与分歧记录

| 用户判断 | 终稿裁决 | 一句话理由 | 评审中的不同意见及处理 |
| --- | --- | --- | --- |
| ① Smart Context 自研 | **证实** | schema/投影无轮子，复用项均为子能力或设计借鉴 | 初稿曾判「部分成立」（滑窗/记忆可抄）；验收专家判「证实（强）」——采证实，复用面写入 2.1 附注 |
| ② 声学→翻译约束转换 | **部分成立** | 曲线→事件无轮子=证实；事件→约束无责任模块、效果零证据 | 初稿曾判「证实」（引 M06）；验收专家判「部分成立」——采部分成立，因票面含全链条 |
| ③ TTS 前检查关口 | **证实** | 关口设计推论，无现成工具同时判断语义/表演/时长 | 初稿曾判「部分成立」（零件可复用）；验收专家判「证实（强）」——采证实，零件复用写入 2.3 附注 |
| ④ 异常修复路由 | **证实** | 流程自建已由用户澄清确认；M10 状态机/动作表全自研 | 验收专家标「原意歧义，暂判部分成立」——已 grilling 澄清（读法 A），歧义关闭 |
| ⑤ 串成统一 pipeline | **证实** | 五稿六处交叉印证编排语义无现成覆盖 | 验收专家「部分成立（可串性零证据）」→ 采为 2.5 的「另一面记录」；安全专家「部分成立+强制条件」→ 采为限定三；架构师「证实+两限定」→ 采为限定一/二 |

无一条证伪。分歧不抹平：上表右列保留了所有相反意见及其归宿，原始报告在会话评审消息中。

### 2.7 五点的包含关系（避免重复计算自研工作量）

架构师评审指出：**① Smart Context、③ TTS 前关口、④ 异常修复路由都发生在⑤编排层内部；② 是①→M08 之间的领域转换。**自研工作量应按「一个编排层(⑤) + 其中三个子系统(①③④) + 一个领域转换(②)」计算，不能把五点当五个并列项目相加。

---

## 三、需要实验确定（跨模块矛盾与证据缺口统一清单）

### 3.0 清单口径

13 份模块稿各有一份编号实验清单，逐稿计数合计 **64 条**（01:4、02:4、03:5、04:5、05:4、06:5、07:4、08:7、09:5、10:4、11:6、12:5、13:6），全部 0 次执行。本文按主题合并跨稿重复项，**逐条实验设计保留在各稿原处**（去重理由：同一实验在多稿出现时只列一次并回链全部来源）。另有跨模块缺口（§3.2、§3.5）与安全证据缺口（§3.5）——后者**性质是「需检索/规范补齐」，不是跑实验能解决的**。

### 3.1 素材与标注（一切实验的前置）

1. 建立一批**获准个人使用**的两小时级英文播客标注集：人工 speaker 可相交区间、真实 overlap、情绪/声学事件标注（含「不可判断」）、英中对照译文、术语词表；按节目/说话人分层，避免相邻句泄漏。[M03](03-diarization-overlap.md#需要实验确定后续实验票输入本票未运行)、[M05](05-emotion.md#需要实验确定)、[M08](08-translation-engineering.md#需要实验确定可执行清单)

### 3.2 跨模块接口矛盾与口径统一（必须先裁决才能冻结 schema）

1. **单 speaker vs 可相交区间**：WhisperX assign_word_speakers 为每词选一个 speaker，与 M03「同一时刻可有多位说话人」冲突——必须保留原始可相交区间，单标签只作展示。[M03](03-diarization-overlap.md#时间轴与模块边界给-m04--m07) / [M04](04-asr-timeline.md#时间轴输出交给-m07-的已知事实)
2. **两 stem 相加 ≠ 无损回拼**：M02 指出残差与模型 stem 各有泄漏/伪影，M13 据此警告混音放大英文残声与音乐染色；哪些区间绕过分离需实验。[M02](02-vocal-separation.md#结论) / [M13](13-final-mix.md#特别风险与验收观察点)
3. **中文自然时长 vs 原节目绝对时间（含时长与锚点口径）**：M12 说中文重演时长可能大于或小于英文原声；M09 说不能用英文词数推中文时长且 duration 口径（是否含停顿/笑声/重叠）待定；M11 明确「不预设速度参数就能精确贴合时间轴」；M13 的逐句 ducking 以什么为锚点。允许的拉伸/静音/重写边界是 M09↔M11↔M12↔M13 的共同裁决点（架构师评审 F8）。[M09](09-pre-tts-checks.md#不生成最终-tts-的时长估计路线) / [M11](11-voice-clone-tts.md#后续同批样本实验清单本票未执行) / [M12](12-long-audio-assembly.md#建议的分段与时间策略待实验的设计判断) / [M13](13-final-mix.md#现成能力与必须自建的编排规则)
4. **逐句 reference vs 音色连续性**：M11 六候选都能逐句换参考，但换参考可能造成声线/响度跳变；reference 选择策略待同批盲听。[M11](11-voice-clone-tts.md#关键问题每句使用对应原始-reference-segment)
5. **重叠讲话的轨道表达**：原英文两人同时说话、中文配音跨原句、笑声插入时，单一旁链无法表达谁退谁留；M03/M12 的结果会改变 M13 混音设计。[M13](13-final-mix.md#特别风险与验收观察点)
6. **Bridge 身份未定 → 已弃用**：M12 票只写「Bridge 或类似工具」，无 URL/作者/全名，检索未命中可唯一指认的仓库。2026-09-25 用户澄清确认想不起该项目 → **弃用、不作架构依据**；若日后有链接，回 M12 复核。[M12](12-long-audio-assembly.md#结论)
7. **权威坐标系三套并存（建议裁决）**：M02 主张原解码 PCM 采样索引为唯一坐标，M01/M03/M07/M12 用秒级绝对 start/end。**建议**：原节目采样索引为权威、秒为投影、转换必须记录有理比例与边界舍入；回填误差入实验（M04 实验 5、M12 实验 3）。16 kHz 重采样后的回填是漂移高发点（架构师评审 F2、验收 BR4）。[M02](02-vocal-separation.md#关键场景时间坐标与验收边界) / [M04](04-asr-timeline.md#时间轴输出交给-m07-的已知事实)
8. **响度处理位置**：M01 主张整集测量与处理（分段各自标准化会改变跨片段强弱比较）；M13 警告逐段归一化抹掉表演动态；但 M12 的工作流候选 tts-audiobook-tool **内建**分段 EBU R128 归一化——采用它必须关闭/外包该功能，否则 M05/M06 特征与 M13 成品动态同时被破坏（架构师评审 F9）。[M01](01-acquisition-preprocessing.md#预处理响度段候选与复用判断) / [M12](12-long-audio-assembly.md#逐候选核查与分类) / [M13](13-final-mix.md#需要实验确定)
9. **声学事件 → 翻译约束断链（G3）**：事件如何进入翻译提示与验收无责任模块（06→07→08），需指定属主或明确「本版不做」。[M06](06-prosody.md#从连续曲线压缩为少量可追溯事件) / [M07](07-smart-context.md#字段来源与确定性边界) / [M08](08-translation-engineering.md#先定播客翻译的验收对象)
10. **中文语速/停顿速率表来源（G4）**：M09 第一版时长区间基线依赖「本项目数据校准」的速率表，尚无来源与校准方案。[M09](09-pre-tts-checks.md#不生成最终-tts-的时长估计路线)
11. **FFmpeg 版本陈述矛盾（BR2）**：M01 写「8.1.3 发布于 2026-09-21」，M13 写「9.0.2 稳定版发布于 2026-09-18」，链接同一下载页；本文不引用具体版本，动手前重查官方页（两稿未复核，哪侧正确未知）。[M01](01-acquisition-preprocessing.md#预处理响度段候选与复用判断) / [M13](13-final-mix.md#候选逐项比较)
12. **M05 对 M03 状态的过时引用（BR3）**：M05 成文时称 M03「未完成」，实际 M03 已交付；终稿一律以 docs/research/03-diarization-overlap.md 为准，M05 快照不改。[M05](05-emotion.md#交给-m07-的输出契约建议尚未冻结-schema)

### 3.3 候选效果横比（同批样本、固定协议）

13. **分离**：PodcastMix UNet/ConvTasNet（**先核授权**——两仓未识别出 license）vs audio-separator 锁定权重 vs Demucs 对照，分测可分析语音/背景可重混/伪影三维 + 两小时成本。[M02](02-vocal-separation.md#需要实验确定)
14. **Diarization/overlap**：Community-1 vs Nemotron-3 vs NeMo 4spk，含 overlap 的 DER（明确 collar）、跨 chunk 身份、短反馈漏检；不同厂商自报 DER 不可横比。[M03](03-diarization-overlap.md#需要实验确定后续实验票输入本票未运行)
15. **ASR/时间轴**：WhisperX 全管线 vs faster-whisper + NeMo NFA，WER、词边界误差、未对齐词比例、Windows 崩溃 issue 复核。[M04](04-asr-timeline.md#需要实验确定)
16. **SER**：emotion2vec+ base/large vs SpeechBrain 基线，人工一致性、ECE/Brier 校准、弃权覆盖率；不同数据集准确率不可横比。[M05](05-emotion.md#需要实验确定)
17. **声学**：librosa pYIN vs Parselmouth vs torchcrepe 在真实播客上的八度错误/伪峰；原混音 vs 分离后 stem 的 F0/RMS 差异。[M06](06-prosody.md#需要实验确定)
18. **翻译上下文消融**：孤句 / AiNiee 前文 / M07 前后句窗口 / 加 speaker·事件资料，盲评指代与连贯；两层稿（忠实稿→表演稿）对照普通润色。[M08](08-translation-engineering.md#需要实验确定可执行清单)
19. **关口误报**：各规则在数字改写、单位换算、意译、拆并句上的误报/漏报；CometKiwi 低分召回 vs XCOMET 错误跨度；时长区间模型的超时漏报与覆盖率。[M09](09-pre-tts-checks.md#需要实验确定)
20. **路由**：规则基线 vs scikit-learn vs 零样本 NLI vs 生成模型结构化选择 vs Jev，只在规则无法唯一确定时调用；错误 ACCEPT 与漏 RETRANSLATE 视为高代价。[M10](10-jev-routing.md#决策所需的小实验本票不执行)
21. **TTS 同批盲听**：Breeze / IndexTTS / Qwen Base / CosyVoice / GPT-SoVITS / F5 在固定与逐句 reference 下分测可懂度、音色相似度、表演匹配、多人一致性（四项分开打分）；**不预设速度参数能精确贴合时间轴**。[M11](11-voice-clone-tts.md#后续同批样本实验清单本票未执行)
22. **长音频恢复演练**：10%/50%/95% 中断模拟，核对已完成片段免重生、损坏块发现、换模型/音色的失效范围；接缝盲听；每 10–15 分钟绝对偏差与末尾累计漂移。[M12](12-long-audio-assembly.md#需要实验确定)
23. **混音听感**：sidechaincompress vs 事件级增益包络，英文可懂度/中文清晰度/背景抽吸/反应保留；成品 LUFS/LRA/true peak 与局部听感抽查。[M13](13-final-mix.md#需要实验确定)
24. **响度目标**：-16 LUFS 只是 ffmpeg-normalize 的播客预设，不是本项目已定目标；整集标准化对 M05/M06 特征的影响需核对。[M01](01-acquisition-preprocessing.md#预处理响度段候选与复用判断)

### 3.4 工程、平台与许可

25. **Windows/Linux 双平台与环境矩阵**：固定版本的安装、CUDA/HF 下载、峰值显存/内存、两小时批处理耗时与失败恢复；环境互斥实测（pyannote 2.1 vs 4.x 同机冲突、YAMNet Keras2/3、各 TTS Python 版本、Node 工具混入）决定子进程隔离形态（架构师评审 F5）。每份模块稿都留了这一项，全部未做。
26. **许可逐项核对（个人用途）**：PodcastMix 两仓 license 未识别；IndexTTS 用 bilibili Model Use License；Breeze/F5 权重非商业限制；GPT-SoVITS 预训练组件许可不统一；pyannote HF 门控条件；emotion2vec+ 权重协议与 MIT 代码分离；COMET 权重 CC-BY-NC-SA；openSMILE 双许可、Parselmouth/Weblate/AiNiee GPL·AGPL（个人使用不分发基本不触发；分发/服务化/商业化须重审）。**规则（采纳安全/架构评审）：许可「待核」的候选不得标为无条件 DIRECT REUSE、不进主链；终稿引用行的许可列不得留空；门控下载须本人账号接受条款并记录条款版本与 HF revision。**[M11](11-voice-clone-tts.md#候选证据与具体复用点)、[M02](02-vocal-separation.md#候选横向核查与逐项复用分类)、各模块稿维护快照表
27. **版本 pinning**：npx 固定包版本、yt-dlp/FFmpeg 固定版本、HF 权重固定 revision、AiNiee 固定 commit 295d2ff、Jev 不用自动漂移的 jev-latest。[M01](01-acquisition-preprocessing.md#获取段候选与复用判断)、[M10](10-jev-routing.md#逐候选分类)
28. **真实案例证据门槛**：本次所有「真实案例」均为项目自述/演示/样例，未找到可公开审计的「两小时多人跨语言播客重演」案例——README 性能图、stars、issue 活跃度都不构成质量证据。[M08](08-translation-engineering.md#需要实验确定可执行清单)、[M12](12-long-audio-assembly.md#需要实验确定)

### 3.5 证据缺口（非实验项：需检索/规范补齐，与「跑实验」性质不同）

以下 1–7 项由安全工程师 grep 全库确认 13 稿**均未覆盖**；8–11 为本次评审自身的材料缺口：

1. 凭据存放规范（API key 放哪、如何避免入库/明文环境变量）——外部 API 接入启动前不得默认放行。
2. 模型权重加载完整性（torch.load/pickle 反序列化、trust_remote_code、校验和/固定 revision）。
3. 依赖供应链扫描（SCA/SAST/secret scanning）与 pinning 策略。
4. 提示注入防护——翻译 LLM 消费不可信播客文本（间接注入全库无讨论；Jev 官方已知弱项含提示注入）。
5. 恶意媒体防御（FFmpeg 处理下载内容的资源限制/解压炸弹；本阶段只记设计风险，未查 CVE）。
6. 数据保留与删除策略（原音频、分离 stems、转写、克隆参考、成品的生命周期）。
7. 真人音色克隆的同意与伦理维度（各稿未覆盖；个人用途不豁免）。
8. 模块票 #2–#14 的 resolution 评论未读（本次证据基线 = 13 稿 + 地图票 #1 + 本票 #15）。
9. 各稿 2026-09-25 的 GitHub API 维护快照未复核。
10. 门控条款全文（HF pyannote/COMET 条件）与 OmegaT 状态（API 404 未取得实时状态）未核。
11. 各专家建议的验收用例（架构 V1–V5、安全 U1–U5、验收 24 条）**全部未执行**。

### 3.6 数据出境与凭据策略（本票默认立场，采纳安全工程师建议）

- **默认：本地优先、规则优先。**外部 API（TypeSafe Jev、OpenAI Structured Outputs、AiNiee 在线后端、HF Space 演示）一律是**条件候选**：接入前必须写明传什么字段、凭据存哪、版本如何固定，并逐个过实验票。
- **口径统一**：M13 REJECT Auphonic（服务端处理+上传原节目）与 M10 接受 Jev 文本传输不矛盾——前者是「本阶段主链必须本地可回溯」的**阶段约束**，后者是「尚未接入的条件候选」；任何数据出境例外按同一标准逐个论证。依据：[M10](10-jev-routing.md#结论)、[M10 · 分类](10-jev-routing.md#逐候选分类)、[M13](13-final-mix.md#候选逐项比较)、[M13 · 需要实验确定](13-final-mix.md#需要实验确定)。
- 凭据管理规范（§3.5-1）缺失不得默认放行。

---

## 四、本阶段明确没做的事

- 没有写任何实现代码、没有安装任何工具、没有运行任何模型、没有下载或试听任何音频样本；**64+ 条实验 0 次执行**，三专家建议的验收用例也全部未执行。
- 没有冻结任何 schema、阈值、LUFS 目标、模型选型或 reference 策略；13 稿跨模块接口 0 处冻结，§1.0 架构图是**推论层架构图**，不是已验证集成。
- 没有对任何许可做法律结论；「个人用途」不等于「输入节目可任意再传播」。
- 分类是 2026-09-25 的调研判断；上游归档、release 与 issue 状态会变化，动手前按模块稿的仓库链接复核版本（已知 M01/M13 的 FFmpeg 版本陈述互相矛盾，见 §3.2-11）。

---

## 五、下一步（本图之外）

本图终点是调研复用地图，以下均为**新任务/新地图**的输入，不在本图范围：

1. 按 §3.1 建标注集 → 按 §3.3 跑同批横比实验（候选实验票的素材）。
2. 用 §3.2 的接口裁决（尤其 7 号权威坐标、3 号时长锚点）冻结 Smart Context schema 与片段清单格式。
3. 用 §1.3 的九项自研清单立胶水层工程任务（统一 pipeline 是其中最大一块），按可逆性排序：先冻结数据契约（不可逆、影响全链），后冻结具体轮子（可逆）。
4. 补齐 §3.5 证据缺口，再按 §3.6 立外部接入的准入检查。

---

## 六、本票（#15）真实状态

**已完成（2026-09-25）**

- 13 份模块稿合并为本终稿：四档口径统一（档位=候选×用途）、架构图（§1.0 数据流 + §1.1–1.4 归类 + §1.3 九项自研）、五点逐条裁决（§2，含分歧记录）、统一实验/缺口清单（§3：模块内 64 条 + 跨模块 12 项接口矛盾 + 28 项主题清单 + 11 项证据缺口 + 数据出境立场）。
- 技术方案评审团 3/3 返回并采纳：架构师 10 项发现（契约未冻结/坐标/口径漂移/环境异构/反馈环/许可等）、安全工程师 6 项证据缺口与 3 项 P0、验收工程师 6 项跨模块矛盾（BR1–BR6）与 G1–G11 缺口清单。
- 两次澄清（grilling）：④ 判断读法（用户选「流程自建」→ 证实）；Bridge（用户确认想不起 → 弃用、不作依据）。

**未完成 / 悬置**

- 所有实验 0 次执行；本文任何效果/成本/阈值都不是「已验证」，全文无「生产就绪」级结论。
- schema、阈值、LUFS 目标、TTS 选型、reference 策略均未冻结。
- §3.4-26 许可待核项未核；§3.5 七项安全证据缺口未补。
- 模块票 #2–#14 resolution 未读；GitHub API 快照未复核；专家建议验收用例全部未执行。

**处置建议**：本票研究问题已答（终稿产出、四档一致、逐条回链、裁决含分歧），可评审后关闭；关闭**不解除**上述悬置项——它们按 §五 进入后续实验票/工程票。
