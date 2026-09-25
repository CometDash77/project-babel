# M06 · Prosody / 声学特征

调研日期：2026-09-25。目标是给英文播客→中文重演提供少量、可追溯的表演线索。本稿核对官方仓库、文档、配置、发布与 issue；**未安装或运行提取器，未测试真实播客或长音频**。以下复用分类是资料判断，质量、速度与平台适配均须按文末「需要实验确定」核查。

## 结论：先定义下游真正需要什么

跨语言重演需要知道某位说话人在**何时**抬高/压低音高、扩大音域、增强或减弱声强、加快或放慢语速，以及哪里有较长停顿。音高基线、音域和响度随说话人、麦克风、混音而变，直接把原始 Hz、RMS 或整段平均值写成“激动/强调”会混淆测量与解释。M07 应接收带原节目绝对时间、说话人、来源与质量标记的**候选观测/事件**；情绪标签由 [M05](05-emotion.md) 另行提供，词/句界来自 [M04](04-asr-timeline.md)，这里不冻结 Smart Context schema。这是从用途推导的接口建议，不是已验证的声学判据。

**推荐研究路线**：用 [librosa](https://github.com/librosa/librosa) 取得 RMS 与 pYIN F0/有声标记，或用 [torchcrepe](https://github.com/maxrmorrison/torchcrepe) 作为难段音高对照；从 M04 可靠词时间戳推导局部语速和停顿。用户已明确本项目仅供个人使用，因此可直接把 [openSMILE Python](https://github.com/audeering/opensmile-python) 的 `eGeMAPSv02` 小集合纳入候选，核对音高、响度和必要的 voice quality；其官方双许可仍要求用途改变时复核。从曲线到“升调/强调/加速”仍需本项目定义、验证和保留弃权；[SLAM+](https://github.com/vieenrose/SLAMplus) 仅提供音高轮廓风格化的参考，不能现成输出整个播客的业务事件。

## 候选横向核查

维护快照取自 2026-09-25 GitHub 仓库和 latest release API。`pushed_at` 是仓库级最近推送，不证明该功能近期维护；`open_issues_count` 包含 PR，不能视为纯 issue 数。“可本地运行”指文档有本地入口，不代表本机跑通。GPU/内存与两小时录音吞吐均没有本项目实测。

| 项目 / 归类 | 真正提供的能力与具体复用点 | 维护、许可、接口和平台 | 本项目缺口 |
| --- | --- | --- | --- |
| [librosa](https://github.com/librosa/librosa) · **WRAP·ADAPT**（基础测量） | [pYIN](https://librosa.org/doc/0.11.0/generated/librosa.pyin.html) 给 F0、有声标记和有声概率；[`feature.rms`](https://librosa.org/doc/0.11.0/generated/librosa.feature.rms.html) 给逐帧 RMS。复用这些 Python 函数，不把 [`beat_track` 的音乐节拍](https://librosa.org/doc/0.11.0/beat.html)当说话语速。 | [ISC](https://github.com/librosa/librosa/blob/main/LICENSE.md)；未归档，最近推送 2026-09-24；[1.0.0](https://github.com/librosa/librosa/releases/tag/1.0.0) 于 2026-08-11 发布；API `open_issues_count=51`。本地 Python/CPU，跨平台安装文档可用；所选版本及依赖须固定。[安装说明](https://librosa.org/doc/main/install.html) | pYIN/RMS 不识别说话人、重点词或声学事件；背景音乐、重叠说话及增益变化可污染估计。两小时 CPU 成本、Windows/Linux 组合和误差**需要实验确定**。 |
| [torchcrepe](https://github.com/maxrmorrison/torchcrepe) · **WRAP·ADAPT**（F0 难段对照） | [`predict`](https://github.com/maxrmorrison/torchcrepe#computing-pitch-and-periodicity-from-audio) 给音高与可选 periodicity；提供静音/周期性阈值、平滑、文件批处理及 [CLI](https://github.com/maxrmorrison/torchcrepe#command-line-interface)。复用音高估计和质量线索，不把 periodicity 当已校准的“表演置信度”。 | [MIT](https://github.com/maxrmorrison/torchcrepe/blob/master/LICENSE)；未归档，最近推送 2025-05-16；未查到 latest release，`setup.py` 标 `0.0.24`；API `open_issues_count=6`。PyTorch，README 提供 CPU/GPU `device`、`batch_size`；Windows/Linux 安装与显存峰值**需要实验确定**。 | README 明说低周期性与静音可致伪音高，阈值需调；已有[多条音频 batch 疑问](https://github.com/maxrmorrison/torchcrepe/issues/34)，但报告中的报错也含浮点数 `hop_length`，不能当多样本不受支持的证明。无响度、语速或事件语义；实际 batch 能力**需要实验确定**。 |
| [Parselmouth / Praat](https://github.com/YannickJadoul/Parselmouth) · **WRAP·ADAPT**（声学核查与 voice quality） | [API](https://parselmouth.readthedocs.io/en/stable/api_reference.html) 有 `Sound.to_pitch[_ac]`、`to_intensity`、`to_harmonicity_cc`，并可调用 Praat；适合检查 F0、强度、HNR 及必要时声质。其 F0/强度是曲线，不是“强调/悲伤”事件。 | [GPL-3.0-or-later](https://github.com/YannickJadoul/Parselmouth/blob/master/README.md#license)；个人使用不是本次排除条件。未归档，最近推送 2026-08-21；[v0.4.7](https://github.com/YannickJadoul/Parselmouth/releases/tag/v0.4.7) 于 2025-11-27 发布；API `open_issues_count=22`。README 明列 Linux/macOS/Windows `pip` 安装。 | Praat 声质量在短句、多人、噪声下的有效性**需要实验确定**。须封装时间回填、说话人归一化和质量标记；如将来分发软件，再复核 GPL 义务。 |
| [openSMILE Python](https://github.com/audeering/opensmile-python) · **WRAP·ADAPT**（个人使用范围内的声学基线） | [`eGeMAPSv02`](https://github.com/audeering/opensmile-python/blob/main/README.rst#feature-sets) 提供 25 个低层描述符或 88 个片段统计量；[配置](https://github.com/audeering/opensmile-python/blob/main/opensmile/core/config/egemaps/v02/eGeMAPSv02_core.lld.conf.inc)含 F0 半音、loudness、jitter、shimmer、HNR 等。`ComParE_2016` 的 6373 个 functionals 对 M07 输入过量，先不采用。复用 `Smile`、`process_signal`/`process_files` 作基线及候选特征筛选。 | [官方 README 的双许可说明](https://github.com/audeering/opensmile-python/blob/main/README.rst#license)允许私人、研究、教育用途的开源版本，并排除商业产品；当前个人使用与前者一致。未归档，最近推送 2026-09-15；[v2.6.0](https://github.com/audeering/opensmile-python/releases/tag/v2.6.0) 于 2025-07-31 发布；API `open_issues_count=34`。仅 64 位 Python；[用法](https://github.com/audeering/opensmile-python/blob/main/docs/usage.rst)支持信号、文件、索引及多 worker。 | 88 个统计量也不等于事件或可直接输入 LLM 的描述；LLD→事件与说话人归一化仍需做。Windows/Linux、长段耗时、内存**需要实验确定**；用途改变时再核对授权。 |
| [SLAM+](https://github.com/vieenrose/SLAMplus) · **REFERENCE**（曲线→轮廓标签） | README 描述将**人工清理后的** F0 曲线在选定语言学区间内风格化，输出 L/l/m/h/H 等旋律层级；输入需要 [PitchTier + TextGrid](https://github.com/vieenrose/SLAMplus#whats-slam-)。可参考说话人全局/局部基线与区间内轮廓标签的设计。 | [LGPL-3.0](https://github.com/vieenrose/SLAMplus/blob/master/LICENSE)；未归档，最近推送 2024-03-09；未查到 latest release，API `open_issues_count=0`。README 给 Linux、macOS、Windows 安装步骤，但依赖和输入准备较手工。 | 主要处理音高，不覆盖能量、语速、多人重叠；法语语料示例不是英语长播客验证。清理 F0、生成对齐 TextGrid 与映射到业务事件需自做；长期维护和适配**需要实验确定**。 |
| [AutoRPT](https://github.com/TSG99/AutoRPT) · **REFERENCE**（事件检测研究） | 官方 README 描述从 WAV + TextGrid 标注 prominence / boundary，输出 CSV 和 TextGrid，并有 RNN/LSTM 流程；这证明存在从声学量到结构化 prosodic event 的项目，但其事件本体并不覆盖全部重演需求。 | 仓库未归档，最近推送 2025-07-10；未查到 latest release；API 未识别许可，`open_issues_count=0`。[README](https://github.com/TSG99/AutoRPT#step-3-run-autorpt)提供 Python CLI/文件选择运行方式，涉及 Parselmouth、PyTorch、spaCy 等依赖。 | 未确定许可证前不直接集成；输入要求 TextGrid，英文变体、模型泛化、长音频、Windows/Linux 跑通及事件质量均**需要实验确定**。 |

## 从连续曲线压缩为少量可追溯事件

目前找到的现成工具分别擅长**测量**（librosa、torchcrepe、Praat、openSMILE）、**音高风格化**（SLAM+）或特定标注体系的**prominence / boundary**（AutoRPT）；未找到能直接输入混音、多说话人长播客并输出本项目全套可靠、LLM 友好事件的成熟轮子。此为本次候选范围内的调研结论，不宣称不存在别的项目。

建议 M07 把原始时序与压缩层分开：先将 M04 句/词和 M03 待定的 speaker 区间映射到原节目绝对时间；逐帧只保留有声/有效 F0 与能量及质量标记；在每位说话人的可靠片段上建立相对基线，再对**有时间界限**的局部区间计算 F0 中位数与音域、起止方向、相对能量、词/秒或音节/秒与停顿。只有跨过经验证的阈值且不受重叠/音乐污染时，才提出 `pitch_rise`、`pitch_fall`、`energy_peak`、`pace_change`、`long_pause` 等**候选**事件；阈值、短句处理和是否用音节率都需听评确定。若证据弱，保留 `unknown`/原因而不补全标签。这里的事件词表是待检验的示例，**不是 schema 冻结**。

`pitch range` 不宜只取极值（伪 F0 易放大）；可先试有声帧的分位差。`pitch direction` 不宜跨无声间隙盲连曲线。RMS 是信号能量，既不等于感知响度，也不排除背景音乐；需优先在可归属的人声片段与可比增益条件下分析。语速应来自可靠词界和实际发声时长；`librosa.beat` 的音乐 BPM 不是讲话速度。Jitter/shimmer/HNR 可作为声质研究线索，但是否能稳定表达某段的气声、嘶哑或疲惫，须另作标注与听评。

给 M07 的**输入建议**（非最终结构）：每个统计值/事件保留 `source_audio_id`、绝对 `start/end`、候选 `speaker_id`、音频来源（原混音/分离人声）、提取器与版本、参数、单位、原始值/相对基线、有效帧比例、质量/弃权原因、与 M04 词/句 ID 的关联。LLM 只需要少量区间级描述与引用，不应接收所有帧或 88/6373 维向量。M07 再决定序列化、阈值与跨模块冲突处理。

## 需要实验确定

1. 在同一批英文播客（两小时、多人、打断、音乐、压缩音质、轻声、笑声）按 speaker/节目切片，人工复核 F0、音域方向、能量、语速与停顿；比较 librosa pYIN、Parselmouth 与 torchcrepe，记录有声错误、八度错误、漏检和伪峰。
2. 对原混音、M02 待定的人声分离结果分别测量；确认分离伪影和增益变化对 F0/RMS/voice quality 的影响。M03 未定前不把重叠区间强行归给一个人。
3. 对“强调、升调、加速、停顿”建立标注指南和听评集；以片段级 precision/recall、事件边界误差、不同说话人的误报及人工一致性选择阈值。验证 SLAM+/AutoRPT 输出能否辅助本项目，而非直接继承其标签语义。
4. 固定版本分别在 Windows/Linux 测 CPU/GPU、峰值内存/显存、每小时音频耗时、连续两小时处理和失败恢复；评估提取器与声学压缩是否值得放入生产链。
5. 当前按用户明确的个人使用范围记录 openSMILE 双许可与 Parselmouth GPL；AutoRPT 的许可仍未识别，故只参考研究思路。如将来分发或转为商业用途，再核对相应软件和模型许可。

本票只给 M07 可用的声学来源及待验证压缩方法；具体 schema、阈值、生产选型和模型运行结果尚未确定。
