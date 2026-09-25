# M13 · 最终混音选型调研（research）

调研日期：2026-09-25。范围为个人用途、可本地批处理的中文重演人声与原节目声场混音。本稿只列候选与证据，**不指定主选或备选**；选择留给 [M13 选型拍板票](https://github.com/CometDash77/project-babel/issues/59)。复用 [M13 模块稿](../research/13-final-mix.md)和[成熟一条龙技术栈反查](00-mature-pipeline-stack.md)；本次补核官方文档、仓库、发布记录及公开使用报告。未安装工具、未混制样片、未跑两小时节目。

## 实际案例能证明到哪里

| 案例 | 可核证据 | 对本题的边界 |
| --- | --- | --- |
| [pyVideoTrans](https://github.com/jianchang512/pyvideotrans/blob/main/docs/architecture.md) | 官方九阶段架构将配音、背景与输出合成串成一条流程；[时间轴对齐说明](https://github.com/jianchang512/pyvideotrans/blob/main/docs/Synchronize.md)展示逐条配音、填静音及合成处理。 | 证明开源成品项目使用 FFmpeg 类合成路线；未证明原英文反应可选择性保留、分离残留可消除，或两小时多人播客达标。 |
| [SoniTranslate](https://github.com/R3gm/SoniTranslate) | README 记录 mix 选项、音频分离、视频/音频输出与前后对比。 | 证明存在可用的配音混合入口；[真实用户报告](https://github.com/R3gm/SoniTranslate/issues/184)曾出现十分钟视频只生成约一分钟配音，不能由演示外推长节目可靠性。 |
| [ffmpeg-normalize](https://github.com/slhck/ffmpeg-normalize) | 官方 README 给出 `--preset podcast`、批量 EBU R128 双遍处理、Python API 和统计输出示例；[Windows GUI 问题及修复](https://github.com/slhck/ffmpeg-normalize/issues/319)提供真实用户反馈及维护响应。 | 证明响度处理有人实际使用；它不处理逐句时间轴、保留反应或动态压低策略。 |
| [Pydub](https://github.com/jiaaro/pydub/blob/master/API.markdown) | 官方文档有 `overlay(position=...)`、`gain_during_overlay`、声像和导出示例；[多次 overlay 的用户报告](https://github.com/jiaaro/pydub/issues/550)给出大批量操作变慢的实例。 | 证明短片段叠加入口可用，亦暴露全长大量片段的性能风险；不是本项目两小时性能测量。 |

这些案例覆盖“可运行/有人使用”，尚无公开可核的“英文多人播客两小时 → 中文同声线 → 保留重叠、反应和背景”的完整案例；达到该目标**需要实验确定**。[反查样本与限制](00-mature-pipeline-stack.md#样本真实使用与维护快照)。

## 候选横比

下表热度及维护为 2026-09-25 [GitHub 仓库元数据](https://docs.github.com/en/rest/repos/repos#get-a-repository)与 release 快照。Star 是关注度，推送日期不是核心路径质量，单个 issue 也不能代表平均响应时间。FFmpeg 的 GitHub 仓库是镜像，官方发布以其下载页为准。许可只记录项目代码或官方发行条件，不能替代具体二进制及素材的许可核查。

| 候选与角色 | 本题能力与成功证据 | 热度、维护、许可 | 限制 / 待验证 |
| --- | --- | --- | --- |
| [FFmpeg filtergraph](https://ffmpeg.org/ffmpeg-filters.html)（独立混音引擎候选） | `adelay`/`atrim`、`amix`、`sidechaincompress`、`pan`、`afade`、`ebur128`、`loudnorm` 覆盖定位、混轨、旁链、声像和响度；[官方旁链示例](https://ffmpeg.org/ffmpeg-filters.html#sidechaincompress)明确第二路信号驱动第一路压缩。pyVideoTrans 给出成品流水线使用案例。 | [镜像](https://github.com/FFmpeg/FFmpeg)约 64.5k stars、14.3k forks，2026-09-25 有推送；[官方 9.0.2 稳定版](https://ffmpeg.org/download.html)于 2026-09-18 发布。[官方许可](https://ffmpeg.org/legal.html)基础为 LGPL，启用 GPL/外部库会改变分发条件。 | 滤镜不决定哪段英文该退、哪段笑声该留。两小时复杂滤镜图的规模、性能、跨平台渲染与听感**需要实验确定**。 |
| [ffmpeg-normalize](https://github.com/slhck/ffmpeg-normalize)（成品响度处理候选，与混音引擎组合） | [README](https://github.com/slhck/ffmpeg-normalize)明示 EBU R128 双遍、真峰值、批处理、播客 preset；已有真实问题和修复记录。 | 约 1.54k stars、130 forks；[v1.42.0](https://github.com/slhck/ffmpeg-normalize/releases/tag/v1.42.0)于 2026-09-02 发布；仓库同日推送，未归档；[MIT 许可](https://github.com/slhck/ffmpeg-normalize/blob/master/LICENSE.md)。 | 不执行多轨编排；若逐句各自归一化，可能破坏句间动态。成品目标 LUFS、true peak 和实际听感**需要实验确定**。 |
| [ffmpeg-python](https://github.com/kkroening/ffmpeg-python)（FFmpeg 图生成封装候选） | 官方 README 展示复杂图与 `get_args()`/`compile()`，可保存实际 FFmpeg 命令；算法仍由 FFmpeg 执行。 | 约 11.0k stars、947 forks，未归档；仓库上次推送为 2024-08-04，GitHub `releases/latest` 无结果；[Apache-2.0](https://github.com/kkroening/ffmpeg-python/blob/master/LICENSE)。 | 没有提供本项目时间轴或反应保留策略。与直接生成命令相比是否降低开发及排错成本，**需要实验确定**。 |
| [Pydub](https://github.com/jiaaro/pydub)（短片段操作或替代引擎候选） | [`overlay` 文档](https://github.com/jiaaro/pydub/blob/master/API.markdown#audiosegmentoverlay)可在指定位置叠加，`gain_during_overlay` 是固定 dB，不是信号驱动的旁链。 | 约 9.8k stars、1.13k forks；[v0.25.1](https://github.com/jiaaro/pydub/releases/tag/v0.25.1)于 2021-03-10 发布，仓库 2026-03-19 有推送；[MIT](https://github.com/jiaaro/pydub/blob/master/LICENSE)。 | [大量 overlay 变慢报告](https://github.com/jiaaro/pydub/issues/550)使其全长主渲染能力存疑；本项目规模的耗时、内存**需要实验确定**。 |
| [Editly](https://github.com/mifi/editly)（声明式音轨编排对照） | [官方 `audioTracks` 说明](https://github.com/mifi/editly#arbitrary-audio-tracks)支持 `start`、裁切、相对 `mixVolume`，可借鉴轨道清单形状。 | 约 5.51k stars、377 forks；[v0.15.0-rc.1](https://github.com/mifi/editly/releases/tag/v0.15.0-rc.1)于 2025-01-19 发布，2025-05-12 推送；[MIT](https://github.com/mifi/editly/blob/master/LICENSE)。 | 以视频编辑为主；文档未证明能按语音旁链和逐事件规则保留原英文反应，不宜据 `audioNorm` 字样推断可替代本题混音逻辑。 |
| [auto-editor](https://github.com/WyattBlue/auto-editor)（时间轴交换与人工复核对照） | [v3 时间轴](https://auto-editor.com/docs/v3)表达多层片段并可导出编辑项目。 | 约 5.36k stars、666 forks；[31.6.0](https://github.com/WyattBlue/auto-editor/releases/tag/31.6.0)于 2026-09-06 发布，2026-09-19 推送；[Unlicense](https://github.com/WyattBlue/auto-editor/blob/master/LICENSE)。 | 官方称 v3 格式部分稳定；核心自动剪切能力未证明适合多 stem 旁链。格式兼容**需要实验确定**。 |
| [mixing](https://github.com/thorwhalen/mixing)（轻量 ducker 接口对照） | [作者说明](https://github.com/thorwhalen/mixing/blob/main/.claude/skills/mixing-audio/SKILL.md)称 `duck_audio` 为固定深度 ducker、无 lookahead、非语音响声也可触发。 | 仓库 0 stars、0 forks，2026-09-22 推送；[MIT](https://github.com/thorwhalen/mixing/blob/main/LICENSE)，GitHub `releases/latest` 无结果。 | 没有成熟长节目案例，不应把它与 FFmpeg 的 `sidechaincompress` 视为同等验证程度。 |
| [Auphonic Multitrack](https://auphonic.com/help/api/multitrack.html)（商业服务功能对照） | 官方 API 有逐轨 ducking、pan、offset 与总体 loudness，可作功能/听感参照。 | 托管服务；不适用 GitHub stars、开源 release 或本地代码许可比较。 | 非本地开源主链；上传权利、成本和处理时长另核。个人用途不等于输入可任意外传。 |

上述候选的“角色”只说明技术层次，不是主选/备选排序。`ffmpeg-normalize` 与 `ffmpeg-python` 都依赖 FFmpeg，不能把它们当作与 FFmpeg 完全独立的后备渲染器。若拍板要求**独立引擎备选**，现有证据没有证明 Pydub 或 Editly 满足本题全部多轨和旁链条件；这项取舍留给 [grilling 票](https://github.com/CometDash77/project-babel/issues/59)。

## 对拍板有用的边界

1. **轨道与时间轴。** [M12 模块稿](../research/12-long-audio-assembly.md)建议多轨片段清单/时间线与 FFmpeg 渲染。M13 至少需消费中文片段绝对起止时间、speaker/事件 ID、原英文 stem、背景 stem、需保留的笑声/呼吸等事件及接缝记录；这是接口建议，非现有实现。分离残留和重叠说话人由 [M02](../research/02-vocal-separation.md)、[M03](../research/03-diarization-overlap.md) 的实际输出决定。
2. **动态压低。** FFmpeg [旁链压缩](https://ffmpeg.org/ffmpeg-filters.html#sidechaincompress)可被中文人声驱动，但只能调电平，不能识别“英文词/笑声/吸气”语义。原英文和背景音乐需要各自的控制规则；若保留反应仍混在英文 stem 内，事件级豁免可能无法实现，**需要实验确定**。
3. **响度与交付。** [FFmpeg `ebur128`/`loudnorm`](https://ffmpeg.org/ffmpeg-filters.html)和 [ffmpeg-normalize](https://github.com/slhck/ffmpeg-normalize)可记录 integrated loudness、LRA、true peak，但全片达标不能证明局部听感。是否逐段修正、最终目标值和无损/有损导出的差异**需要实验确定**。
4. **可回溯性。** 建议保存源文件与 stem 哈希、时间轴版本、FFmpeg 版本、滤镜图/参数、响度测量和成品映射。该记录是本项目拟定规则，不是候选工具自动提供的完整审计契约。

## 启动前「需要实验确定」清单

- 用同一组含音乐、双人重叠、笑声、呼吸和旧人声残留的获准素材，比较旁链压缩与事件级增益包络的中文可懂度、英文残声、反应保留及背景抽吸；定参数区间。
- 对 M02 实际 stem 做原节目重组对照，听检相位、瞬态、音乐纹理和泄漏；确定无法分开反应事件时的人工复核规则。
- 用两小时、多短片段项目测滤镜图规模、内存、耗时、失败恢复、Windows/Linux 版本差异，并与 Pydub/封装路线的开发复杂度比较。
- 对无损母版与有损成品复测时间坐标、LUFS/LRA/true peak、接缝和声像；依据使用场景及听评定目标和容差。此票不运行 GPU/音频实验。
