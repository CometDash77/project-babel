# M06 · Prosody / 声学特征选型调研（research）

调研日期：2026-09-25。目标是为英文多人播客的中文重演保留可追溯的音高、强弱、节奏、停顿线索。本稿复用 [M06 模块调研](../research/06-prosody.md)与[成熟流水线反查](00-mature-pipeline-stack.md)，并核对官方文档、仓库与公开用例。**只列候选及证据，不指定主选/备选。**本票没有安装工具、运行音频或做 GPU 实验；效果、性能及长节目稳定性均非实测结论。

## 已跑通的范围与本项目距离

- [pyVideoTrans 架构](https://github.com/jianchang512/pyvideotrans/blob/main/docs/architecture.md)、[VideoLingo 介绍](https://github.com/Huanshere/VideoLingo/blob/main/docs/pages/docs/introduction.zh-CN.md)与[SoniTranslate README](https://github.com/R3gm/SoniTranslate)有成品配音入口，但核对的公开流程中，语速/音量调节属于**输出处理**，没有证明从英文原声提取 Prosody 并迁移到中文。前置反查也未找到可核的两小时多人播客全链案例；该效果**需要实验确定**。
- 可核的成功范围较窄：[Parselmouth 官方示例](https://parselmouth.readthedocs.io/en/stable/examples.html)展示语音音高/强度分析；[openSMILE Python 官方用法](https://audeering.github.io/opensmile-python/usage.html)用 emoDB 音频实际提取 `eGeMAPSv02`；[torchcrepe 作者论文](https://interactiveaudiolab.github.io/assets/papers/morrison_thesis.pdf)记述在语音合成/编辑中使用该音高提取器。这些是工具可用的案例，不等于播客原声表演事件识别已经跑通。
- M06 应把 **测量值**、**解释性事件**与[M05 情绪标签](../research/05-emotion.md)分开。F0、RMS、loudness、语速可形成候选观测；“强调、兴奋、悲伤”不能由单一值直接断定。这是据[工具输出定义](https://librosa.org/doc/0.11.0/generated/librosa.pyin.html)与[openSMILE 特征集说明](https://audeering.github.io/opensmile-python/)推导的项目边界，事件阈值**需要实验确定**。

## 候选横比

维护数字是 2026-09-25 读取 [GitHub 仓库 API](https://docs.github.com/en/rest/repos/repos#get-a-repository) 的快照。星数只代表关注度，`pushed_at` 只代表仓库推送，`open_issues_count` 含 PR；均不证明本项目音质或响应时效。以下“案例”明确区分官方可运行示例、研究使用与真实节目验收。

| 候选 / 角色 | 已跑通案例与可复用能力 | 热度、维护、许可与响应证据 | 本项目缺口 |
| --- | --- | --- | --- |
| [librosa](https://github.com/librosa/librosa) · 基础声学测量 | [官方 F0 教程](https://librosa.org/doc/dev/auto_tutorials/01-intro/03-f0.html)跑通 `pyin`、有声标记与概率（教程音源是乐器）；[`feature.rms`](https://librosa.org/doc/0.11.0/generated/librosa.feature.rms.html)给逐帧能量。可在说话人片段上计算曲线；[音乐 beat tracker](https://librosa.org/doc/0.11.0/beat.html)不是语速测量。 | [API](https://api.github.com/repos/librosa/librosa)：8,630 stars、1,076 forks、51 open issues/PR，未归档，最近推送 2026-09-24；[1.0.0 发布](https://github.com/librosa/librosa/releases/tag/1.0.0)于 2026-08-11；[ISC](https://github.com/librosa/librosa/blob/main/LICENSE.md)。近期发布表明仍有维护，未统计 issue 响应时间。 | pYIN/RMS 不识别 speaker、停顿语义或强调；音乐、重叠、增益变化及两小时 CPU 耗时**需要实验确定**。 |
| [Parselmouth / Praat](https://github.com/YannickJadoul/Parselmouth) · 声学核查 | [Parselmouth 语音分析示例](https://parselmouth.readthedocs.io/en/stable/examples.html)和[Praat 入门](https://praat.org/manual/Intro.html)覆盖 pitch、intensity；[API](https://parselmouth.readthedocs.io/en/stable/api_reference.html)提供 harmonicity 等调用。适于 F0/强度/声质复核，不直接产出表演事件。 | [API](https://api.github.com/repos/YannickJadoul/Parselmouth)：1,291 stars、131 forks、22 open issues/PR，未归档，最近推送 2026-08-21；[v0.4.7](https://github.com/YannickJadoul/Parselmouth/releases/tag/v0.4.7)于 2025-11-27；[GPL-3.0-or-later](https://github.com/YannickJadoul/Parselmouth#license)。README 列 Windows/Linux/macOS 安装；未统计 issue 响应时间。 | 短句、噪声、重叠下 F0/HNR 稳定性及两小时处理**需要实验确定**；若未来分发软件，须重新核对 GPL 义务。 |
| [openSMILE Python](https://github.com/audeering/opensmile-python) · 小型标准特征集 | [官方教程](https://audeering.github.io/opensmile-python/usage.html)对真实语音库音频运行 `process_signal`、`process_files`、`process_index`；[`eGeMAPSv02` 文档](https://audeering.github.io/opensmile-python/)列 25 个 LLD / 88 个 functionals，涵盖 F0、loudness、voice quality。可做可复核的声学基线，不宜把 88 维统计量直接交给 M07。 | [API](https://api.github.com/repos/audeering/opensmile-python)：334 stars、42 forks、34 open issues/PR，未归档，最近推送 2026-09-15；[v2.6.0](https://github.com/audeering/opensmile-python/releases/tag/v2.6.0)于 2025-07-31。[官方双许可说明](https://github.com/audeering/opensmile-python#license)允许私人、研究、教育使用开源版本；当前个人用途符合该范围，商业/分发需另核。未统计 issue 响应时间。 | 特征不是“升调/强调”事件；片段长度、LLD 到事件的聚合、平台及长音频资源**需要实验确定**。 |
| [torchcrepe](https://github.com/maxrmorrison/torchcrepe) · F0 对照 | [官方语音范围示例](https://github.com/maxrmorrison/torchcrepe#computing-pitch-and-periodicity-from-audio)给 pitch、periodicity、CPU/GPU 与 batch 参数；[作者语音合成/编辑研究](https://interactiveaudiolab.github.io/assets/papers/morrison_thesis.pdf)给实际采用案例。其 periodicity 是估计辅助量，不是已校准的表演置信度。 | [API](https://api.github.com/repos/maxrmorrison/torchcrepe)：524 stars、81 forks、6 open issues/PR，未归档，最近推送 2025-05-16；GitHub 无 latest release，[安装/源码](https://github.com/maxrmorrison/torchcrepe)仍可见；[MIT](https://github.com/maxrmorrison/torchcrepe/blob/master/LICENSE)。近期正式发布与 issue 响应节奏未获证实。 | 静音/低周期性伪 F0、八度错误、不同 batch 行为、CPU/GPU 成本与播客泛化**需要实验确定**；不覆盖响度或节奏。 |
| [SLAM+](https://github.com/vieenrose/SLAMplus) · 音高轮廓风格化参考 | [官方示例](https://github.com/vieenrose/SLAMplus#examples-of-configuration)显示 PitchTier + TextGrid 的区间风格化及 `L/l/m/h/H` 标签，输入需先清理 F0；可参考全局/局部基线思想，不是直接处理原始混音的轮子。 | [API](https://api.github.com/repos/vieenrose/SLAMplus)：4 stars、0 forks、0 open issues/PR，最近推送 2024-03-09，无 latest release；[LGPL-3.0](https://github.com/vieenrose/SLAMplus/blob/master/LICENSE)。低关注和较早推送提示集成维护成本，0 open issues 不能推断响应快。 | 英文多人长播客、清理输入、TextGrid 对齐、音高标签到本项目业务事件的映射**需要实验确定**；缺能量和语速。 |
| [AutoRPT](https://github.com/TSG99/AutoRPT) · prominence/boundary 研究参考 | [官方 README 的运行步骤与输出说明](https://github.com/TSG99/AutoRPT#step-3-run-autorpt)展示 WAV + TextGrid → suspected prominence/boundary 的 TextGrid/CSV；证明某种结构化韵律标注工具存在，标签体系不覆盖所有重演线索。 | [API](https://api.github.com/repos/TSG99/AutoRPT)：4 stars、4 forks、0 open issues/PR，最近推送 2025-07-10，无 latest release；API 未识别许可，仓库未见可核的授权文件。无可核 issue 响应样本；0 open issues 不代表已维护。 | 许可证未确认前只参考思路；英语变体、重叠/音乐、长音频、Windows/Linux 运行与事件准确率**需要实验确定**。 |

## 给拍板票的比较维度与启动前门槛

候选不是同一层级的一对一替代：librosa、Parselmouth、openSMILE 与 torchcrepe 测量声学量；SLAM+ 整理音高轮廓；AutoRPT 预测其标注体系内的事件。就本项目已核证据，**没有一个候选被证明能单独把多说话人混音长播客变成可信的中文重演提示**。这只限本次检索候选，不声称不存在其他方案。[各项目输入输出](https://github.com/audeering/opensmile-python)、[SLAM+ 输入要求](https://github.com/vieenrose/SLAMplus)、[AutoRPT 输入要求](https://github.com/TSG99/AutoRPT)。

建议 grilling 票逐题比较：声学覆盖（F0/强度/声质）、窗口和绝对时间索引、可解释性、噪声/重叠的弃权能力、CPU/GPU 资源、Windows/Linux 安装与许可。语速和停顿应以 [M04 词/句时间轴](../research/04-asr-timeline.md)及有效发声段推导；不能用音乐节拍代替。给 M07 的候选事件建议保留 `speaker_id`、原节目绝对起止、音源（混音/人声 stem）、提取器版本参数、单位、有效帧比例、相对说话人基线、质量/弃权原因与词句引用；这是接口建议，非已定 schema。

**需要实验确定（本地图只记录启动前门槛，本票不执行）：**

1. 以同一批获准使用的英文多人播客，覆盖两小时、打断/重叠、背景音乐、轻声、笑声及压缩音质；标注音高方向、相对强度、语速、停顿和可弃权片段。比较 pYIN、Praat、torchcrepe 与 openSMILE 的有声/八度错误、事件 precision/recall、边界误差、说话人间误报及标注一致性。
2. 对原混音与 M02 分离人声分别运行，核对分离伪影、响度/增益差及重叠区 speaker 归属；弱证据保持 `unknown`，不补猜事件。
3. 固定版本，测 Windows/Linux 的安装、两小时切片/续跑、每小时耗时、峰值内存/显存；核实 openSMILE 当前个人用途许可、Parselmouth 后续分发义务，以及 AutoRPT 是否取得明确授权。

这些是效果验收门槛，不构成本票的实测结果。主选/备选留给「M06 · Prosody / 声学特征选型拍板（grilling）」与用户决定。
