# M01 · 音频获取与预处理

调研日期：2026-09-25。目标是为「英文长播客 → 中文重演」取得可追溯的原节目音频，并产生后续分离、ASR、说话人和声学分析可共同定位的工作音频。本稿只核对官方仓库、文档、源码／许可、release 与公开 issue；**没有下载节目、安装工具或运行两小时音频实验**。当前项目仅供个人使用；下述复用判断不等于未来分发时的许可结论，也不代表对任何节目内容的使用授权。

## 从最终输出倒推输入

最终重演要保留多人互动、音色、情绪、节奏与背景声，故 M01 不应把「标准化后声音」当唯一原件。应保存原始下载文件、来源 URL／RSS GUID／节目元数据、下载工具及版本、音轨／声道／采样率／时长、校验值；另产可解码的工作副本及每个切片的**原节目绝对起止时间**。这是本项目的接口推论，不是候选工具已经提供的一体化 pipeline。[M04 时间轴稿](04-asr-timeline.md)和 [M06 声学稿](06-prosody.md)都依赖原始时间与音量语境；若切片各自做响度标准化，会改变跨片段的强弱比较，因此先按整集测量与处理，原件留存，切片参数和偏移单独记录。切片边界、音轨选择、背景声保留及响度目标须随下游实验确定。

## 获取段：候选与复用判断

维护快照来自 2026-09-25 GitHub 仓库／latest release API。`pushed_at` 只说明仓库有推送，`open_issues_count` 含 PR；两者都不能证明特定路径稳定。表中「本地」指官方给出安装／执行入口，非本机验证。下载均不要求 GPU；长文件、站点限流、断点续传和 Windows/Linux 实际表现**需要实验确定**。

| 候选与判断 | 已证实能力、具体复用点 | 维护／许可／接口／平台 | 真实案例与限制 |
| --- | --- | --- | --- |
| [podcast-dl](https://github.com/lightpohl/podcast-dl) · **DIRECT REUSE**（RSS 节目批量获取） | 官方 [README](https://github.com/lightpohl/podcast-dl#options) 支持 RSS URL／本地 feed、`enclosure,link` 优先级、`--limit`／日期筛选、`--attempts`、`--archive` 去重、episode JSON 和 transcript 下载；直接复用 **CLI 与 archive/metadata 输出**。 | MIT；未归档，最近推送 2026-08-17，[v12.1.4](https://github.com/lightpohl/podcast-dl/releases/tag/v12.1.4) 同日发布；API `open_issues_count=1`（[NixOS issue](https://github.com/lightpohl/podcast-dl/issues/163)），不能据此推出跨平台无故障。Node `npx` 或 release 二进制；Windows/Linux 对应构建及两小时播客下载**需要实验确定**。 | README 给实际调用例与音频／元数据归档功能，但不是独立生产稳定性数据。项目不做本任务所需的采样率转换、精确切片或 EBU R128；CLI 输出仍须映射进本项目清单。 |
| [yt-dlp](https://github.com/yt-dlp/yt-dlp) · **DIRECT REUSE**（YouTube／受支持站点） | [README](https://github.com/yt-dlp/yt-dlp/blob/master/README.md) 给 `-x --audio-format`、`--download-archive`、进度／重试和 [Python `YoutubeDL` 嵌入入口](https://github.com/yt-dlp/yt-dlp#embedding-yt-dlp)；复用 **CLI 或 Python API 的提取、下载、info JSON**。`-x` 依赖 FFmpeg/ffprobe。 | 核心仓库 Unlicense，但 [不同打包文件含其他许可证](https://github.com/yt-dlp/yt-dlp/blob/master/README.md#licensing)；未归档，最近推送 2026-09-16，[2026.08.19](https://github.com/yt-dlp/yt-dlp/releases/tag/2026.08.19) 发布；API `open_issues_count=2679`。官方提供 Windows／Linux 可执行文件，软件本身无需 GPU。 | 官方 [EJS 指南](https://github.com/yt-dlp/yt-dlp/wiki/EJS) 说明完整 YouTube 支持还需 JS runtime 与 yt-dlp-ejs；[403 issue](https://github.com/yt-dlp/yt-dlp/issues/17456)说明站点变化会破坏下载。站点支持不保证某条链接可取得，长节目成功率**需要实验确定**。不要把它当 RSS `enclosure` 的唯一通道。 |
| [feedparser](https://github.com/kurtmckee/feedparser) · **WRAP·ADAPT**（需精细选择 RSS episode 时） | 官方 [enclosures 文档](https://feedparser.readthedocs.io/en/latest/reference-entry-enclosures.html)给 `entries[i].enclosures`；复用 **Python `parse` 与条目／enclosure 数据**，由本项目选择 GUID、媒体 URL，并另配 HTTP 下载及校验。它是解析器，**不下载音频文件**。 | 源码 [BSD 类两条款许可](https://github.com/kurtmckee/feedparser/blob/main/LICENSE)；未归档，最近推送 2026-09-07，[v6.0.14](https://github.com/kurtmckee/feedparser/releases/tag/v6.0.14) 发布于 2026-07-30；API `open_issues_count=112`。纯 Python 本地包，Windows/Linux 安装可行性由其跨平台设计支持，具体组合**需要实验确定**。 | 官方 [畸形 feed issue](https://github.com/kurtmckee/feedparser/issues/599) 显示解析异常仍存在。它适合构建可审计选集，而非替代 podcast-dl 的下载重试、归档与 CLI。 |
| [gPodder](https://github.com/gpodder/gpodder) · **REFERENCE** | 已实现 RSS 订阅、episode 下载与 YouTube 相关整合；参考 **订阅／下载失败处理和元数据组织**，不把桌面客户端作为流水线主执行器。[项目仓库](https://github.com/gpodder/gpodder) | GPL-3.0-or-later（[COPYING](https://github.com/gpodder/gpodder/blob/master/COPYING)）；未归档，最近推送 2026-09-20，latest release [3.11.5](https://github.com/gpodder/gpodder/releases/tag/3.11.5) 为 2024-12-20；API `open_issues_count=350`。Python 桌面程序，有 Linux／Windows 使用入口，GPU 非前置。 | 是真实播客客户端而非纯 CLI 库；[yt-dlp 路径 issue](https://github.com/gpodder/gpodder/issues/1878) 体现集成维护成本。自动化 API 与两小时任务稳定性**需要实验确定**，本任务不优先嵌入其 GUI／内部状态。 |

**获取段选择（推论）**：普通 RSS 先用 podcast-dl CLI；需要逐条挑选或多 enclosure 审核时用 feedparser 解析，再自管下载；YouTube／站点 URL 用 yt-dlp。三者的适用入口不同，不预设单个工具覆盖所有 URL。源站可用性、访问限制及版权许可按具体节目核对，不能由工具许可证推导。

## 预处理／响度段：候选与复用判断

| 候选与判断 | 已证实能力、具体复用点 | 维护／许可／接口／平台 | 真实案例与限制 |
| --- | --- | --- | --- |
| [FFmpeg + ffprobe](https://ffmpeg.org/) · **DIRECT REUSE**（转换、探测、切片底座） | 官方 [命令文档](https://ffmpeg.org/ffmpeg.html) 支持转码／`-ss` 裁切；[segment muxer](https://ffmpeg.org/ffmpeg-formats.html#segment_002c-stream-segment_002c-ssegment)与 [loudnorm](https://ffmpeg.org/ffmpeg-filters.html#loudnorm) 提供切片和 EBU R128 单／双遍、IL/LRA/true-peak。复用 **CLI、ffprobe JSON、滤镜**，保留输入原件并记录参数。 | 官方 [8.1.3](https://ffmpeg.org/download.html) 发布于 2026-09-21；GitHub 镜像最近推送 2026-09-25，但镜像 issue 数不能代表官方问题队列。官方 [许可页](https://ffmpeg.org/legal.html)说明 LGPL/GPL 取决于构建和启用组件。Windows/Linux 官方下载入口；CPU 可运行，硬件编解码是可选项，GPU 非前置。 | FFmpeg 是广泛用于音视频处理的实际基础工具；文档明确输入侧 `-ss` 在多数格式不能直接精确 seek，转码时默认 `-accurate_seek` 才会解码丢弃多余部分，`-c copy` 会保留偏差。具体时轴精度和长音频资源占用**需要实验确定**。 |
| [ffmpeg-normalize](https://github.com/slhck/ffmpeg-normalize) · **WRAP·ADAPT**（整集响度标准化） | [README](https://github.com/slhck/ffmpeg-normalize)说明 EBU R128 默认双遍、Python API／CLI、`--print-stats`、跳过已达目标文件和 `--preset podcast`（-16 LUFS）；复用 **CLI 或 Python API 的两遍控制／统计**，底层仍用 FFmpeg。 | [MIT](https://github.com/slhck/ffmpeg-normalize/blob/master/LICENSE.md)；未归档，最近推送 2026-09-02，[v1.42.0](https://github.com/slhck/ffmpeg-normalize/releases/tag/v1.42.0) 同日发布；API `open_issues_count=1`，含 PR。Python ≥3.10 + FFmpeg，Windows 有 `colorama` 依赖，Linux 可本地运行；GPU 非前置。 | README 提供播客预设示例，但其目标不是本项目的音色／动态保真验收。作者在[线性标准化 issue](https://github.com/slhck/ffmpeg-normalize/issues/245)说明某些文件达不到线性模式目标，须检查实际输出与统计；两小时双遍耗时、峰值和声学影响**需要实验确定**。 |
| [pydub](https://github.com/jiaaro/pydub) · **REJECT**（主预处理依赖） | Python `AudioSegment` 的切片／音量操作可作 API 设计参考；[normalize 源码](https://github.com/jiaaro/pydub/blob/master/pydub/effects.py)根据最大幅值调整增益，不是 EBU R128。 | [MIT](https://github.com/jiaaro/pydub/blob/master/LICENSE)；未归档，最近推送 2026-03-19，latest release [v0.25.1](https://github.com/jiaaro/pydub/releases/tag/v0.25.1) 为 2021-03-10；API `open_issues_count=423`（含 PR），[维护讨论](https://github.com/jiaaro/pydub/issues/885)仍开放。依赖 FFmpeg 读多种格式，Python 本地包；Windows/Linux、CPU 可用性有 README 使用例，具体组合**需要实验确定**。 | 本票的核心是长音频和 R128，FFmpeg 已直接覆盖；整段加载的内存成本和与 FFmpeg 的时间轴一致性**需要实验确定**，故本轮不采用它替代 FFmpeg／ffmpeg-normalize。 |

**预处理段选择（推论）**：FFmpeg/ffprobe 做统一解码、音轨探测、转换与切片；ffmpeg-normalize 仅在确需工作副本响度一致时封装整集双遍处理并保存统计。`loudnorm` 的默认数值不是本项目已决定的响度目标；-16 LUFS 是该工具播客预设，不应无条件用于 ASR、声学特征或最终成品。输出采样率／声道、切片长度、静音策略，以及是否对分离后 stem 单独标准化，都交给下游实测。

## 需要实验确定

1. 选一条可合法使用的长 RSS 节目、YouTube 节目和直接音频 URL，分别验证下载重试／续传、元数据、校验、时长及 Windows/Linux 复现；记录工具与 FFmpeg 版本。README 示例和仓库活动不证明两小时成功率。
2. 对含片头音乐、多人交谈、静音及重叠讲话的整集，比较原件与双遍标准化工作副本的 IL/LRA/true peak、听感和 M05/M06 特征；核对 `ffmpeg-normalize` 实际是否走线性模式。原件始终保留。
3. 以已知时间标记比较 FFmpeg 转码裁切、`-c copy` 裁切和 segment 输出的首尾误差；核对样本数、声道／重采样及跨片绝对时间还原。再交 M03/M04 的下游时间轴验证。
4. 记录两小时双遍转换与切片的 CPU 时间、峰值内存／磁盘占用、异常中断后可恢复性；性能和稳定性**需要实验确定**。

本稿完成候选与复用边界的资料判断；没有音频样本实验，最终参数与端到端选型留待后续实验／M14 汇总。
