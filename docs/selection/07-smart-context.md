# M07 · Smart Context 上下文构建：候选与证据

调研日期：2026-09-25。本稿回答 [M07 research 票](https://github.com/CometDash77/project-babel/issues/46)的证据问题，供后续 [grilling 票](https://github.com/CometDash77/project-babel/issues/47)决定主选与备选；**本稿不拍板**。先复用 [M07 模块稿](../research/07-smart-context.md)和[一条龙项目反查](00-mature-pipeline-stack.md)。本次补查公开文档、用户 issue、release 与仓库元数据；没有安装候选、调用翻译模型或运行两小时播客。下述 GitHub 数字是读取时快照，star、推送日期和 issue 数量都不是译质证明。

## 需求边界与一条龙先例

本项目的目标是对**当前语义句**提供前、后各最多 10 句的只读上下文，另外提供可修订的术语/人物记忆和有来源的局部事件。翻译输出只绑定当前句 ID；句界不能直接等同字幕 cue 或 ASR segment，交叠说话也不能被线性句序抹掉。这是 [M07 模块稿](../research/07-smart-context.md#结论与当前句所需信息)根据流水线需求提出的接口建议；21 句的收益、事件字段的帮助和 token 成本均**需要实验确定**。

一条龙参照中，[VideoLingo 文档](https://github.com/Huanshere/VideoLingo/blob/main/docs/pages/docs/introduction.zh-CN.md)明确展示 GPT 术语提取、上下文翻译与成品演示，是“术语 + 译文流水线”已跑通的案例；但文档也写明当前不能给多角色分别配音，不能推断它已解决播客重叠讲话或 M07 的音频事件结构。[pyVideoTrans 架构](https://github.com/jianchang512/pyvideotrans/blob/main/docs/architecture.md)有字幕重分句和 LLM 纠错，公开主流程未展示可审计的 episode 事实图。[SoniTranslate README](https://github.com/R3gm/SoniTranslate)展示分段、编辑与成品流程，未展示独立 Smart Context 构建。三者提供集成经验，不是完整 M07 实现的实证。

## 候选横比

“成功案例”列仅说明公开资料能证明的运行层级；文档示例不等于本项目的质量验收。维护数字来自各仓库 [GitHub API](https://docs.github.com/en/rest/repos/repos#get-a-repository) 与 release 页面，`open_issues_count` 含 PR；issue 响应仅按找到的具体案例描述。

| 候选与可借用部分 | 已跑案例、社区证据及限度 | 热度、维护、许可快照 | 对 M07 的适配与缺口 |
| --- | --- | --- | --- |
| [context_translate](https://github.com/darksylinc/context_translate)：前文、待译批次、后文三段滑窗 | [README 用法](https://github.com/darksylinc/context_translate#how-to-use)给出 CSV 输入、`--pre-ctx` / `--batch-size` / `--pos-ctx` 与本地 llama.cpp 端点例子，作者同时说明坏输出会重试，最终可能留下原文。未找到独立的播客成品或用户验收案例；“能运行示例”不等于质量已验证。 | [仓库](https://api.github.com/repos/darksylinc/context_translate) 0 stars / 0 forks，未归档，最近推送 2026-08-28；[v0.1.0](https://github.com/darksylinc/context_translate/releases/tag/v0.1.0) 发布于 2025-11-11；GPL-3.0。公开 issue 很少，无法据此计算响应质量。 | 滑窗角色和稳定行键值得复用；CSV 不承载原节目绝对时间、词界、重叠区间与来源状态，直接用作权威记录会丢信息。原工具用于两小时英→中播客的安装、成本和质量**需要实验确定**。 |
| [LLM-Subtrans](https://github.com/machinewrapped/llm-subtrans)：批次摘要、术语与源行映射验证 | [官方 wiki](https://github.com/machinewrapped/llm-subtrans/wiki/)描述按场景/批次翻译、前批摘要传递和错误重试；[真实集成用户 issue #404](https://github.com/machinewrapped/llm-subtrans/issues/404)报告 WhisperJAV 使用其 PySubtrans，但本地小模型出现格式退化和丢批；对应[修复 PR #407](https://github.com/machinewrapped/llm-subtrans/pull/407)已合并。它证明有外部使用和响应实例，也暴露 token 与结构输出风险。 | [仓库](https://api.github.com/repos/machinewrapped/llm-subtrans) 655 stars / 64 forks，未归档，最近推送 2026-09-25；[v1.7.0](https://github.com/machinewrapped/llm-subtrans/releases/tag/v1.7.0) 发布于 2026-09-15；[项目 LICENSE](https://github.com/machinewrapped/llm-subtrans/blob/main/LICENSE)为 MIT，依赖须另核。 | 摘要、术语和 ID/行数校验可借用；电影场景切分、摘要事实性及并行场景丢失前文的风险不能直接沿用。对播客句界、多人关系与声学事件仍需封装；摘要是否增益**需要实验确定**。 |
| [llm-subs](https://github.com/azratul/llm-subs)：episode/series 记忆、冲突与上下文失效 | [README 的完整命令流程](https://github.com/azratul/llm-subs)有 `analyze`、`translate`、`review` 和剧集记忆；[CHANGELOG](https://github.com/azratul/llm-subs/blob/main/CHANGELOG.md)记录源字幕指纹、记忆变更使产出过期等修复。未找到独立播客使用证明；文档及自测不能当外部成功案例。 | [仓库](https://api.github.com/repos/azratul/llm-subs) 3 stars / 0 forks，未归档，最近推送 2026-09-02；[v0.8.0](https://github.com/azratul/llm-subs/releases/tag/v0.8.0) 发布于 2026-07-10；GPL-3.0。[公开 issue/PR](https://github.com/azratul/llm-subs/issues?q=is%3Aissue+is%3Apr)主要是依赖更新，用户问题响应样本不足。 | 分离术语、人物、风格与冲突记录，按目标语言隔离记忆，并让源句/记忆版本影响缓存，是可复用设计。自动推断的性别、关系或 speaker 不能当播客事实；实际译质和长节目恢复**需要实验确定**。 |
| [VideoLingo](https://github.com/Huanshere/VideoLingo)：成品流程中的术语与上下文 | [官方介绍、教程与演示](https://github.com/Huanshere/VideoLingo/blob/main/docs/pages/docs/introduction.zh-CN.md)证明已有可运行的翻译/配音产品入口；不能由演示推出 M07 单独准确率或多 speaker 交互保真。 | [仓库](https://api.github.com/repos/Huanshere/VideoLingo) 约 18.5k stars / 2.0k forks，未归档，2026-09-25 推送；[v3.0.4](https://github.com/Huanshere/VideoLingo/releases/tag/v3.0.4) 发布于 2026-09-15；Apache-2.0。 | 可借“先提术语/背景、再译句”的流程；其视频字幕结构不是 M04–M06 的完整观测与不确定性契约，直接嵌入 M07 的边界**需要实验确定**。 |

**辅助组件，不作为完整 M07 候选。** [pysubs2 官方用法](https://github.com/tkarabela/pysubs2#usage)支持 SRT/ASS/WebVTT 读写，可作为字幕交换层；[仓库](https://api.github.com/repos/tkarabela/pysubs2)约 440 stars，2026-08-16 推送，MIT，但字幕格式不能原生保留模型来源、弃权和修订历史。[pyannote.core 数据结构文档](https://pyannote.github.io/pyannote-core/structure.html)的区间、时间轴与多轨标签可用于事件相交；[仓库](https://api.github.com/repos/pyannote/pyannote-core)约 126 stars，最新 [6.0.1](https://github.com/pyannote/pyannote-core/releases/tag/6.0.1) 在 2025-09-16，GitHub API 未给出可确认的 SPDX 许可，集成前须核许可证。它不检测重叠或笑声。[AiNiee](https://github.com/NEKOparapa/AiNiee)有 SRT/ASS/VTT、术语表、背景和上下文关联，2026-09-09 仍有 [Beta 发布](https://github.com/NEKOparapa/AiNiee/releases)，代码 AGPL-3.0；其翻译引擎与提示工程归 M08 深挖，公开资料未证明 21 句音频事件投影。以上许可对当前个人用途不自动排除候选，但分发或改变部署方式前需要复核各项条款。

## 供 grilling 票比较的方案形态

1. **滑窗机制 + 项目自有投影层**：参考 context_translate 的前/当前/后分工，以稳定句 ID 和绝对时间构建最多 21 句；字幕解析可交给 pysubs2，事件区间可借 pyannote.core。此组合是从组件能力推导的**待验证集成方案**，没有公开项目证明它整体已跑通。
2. **批次摘要/术语记忆 + 项目自有投影层**：参考 LLM-Subtrans 的摘要与行映射、llm-subs 的记忆冲突和失效规则；长程信息与局部 21 句分开存，人工确认与模型推断分开标注。摘要误导、跨批泄漏及成本**需要实验确定**。
3. **借鉴成品流程**：VideoLingo 的术语先行可作对照，但其现有上下文机制对播客交叠和声学事件的覆盖**需要实验确定**。是否采用其任何代码、仅借流程，留给 grilling 票结合 M08 的边界决定。

无论比较哪种形态，当前句原文、稳定 ID、源文件与绝对区间应是最低输入；邻句只读，交叠保留并行区间。speaker、情绪、韵律、笑声分别携带来源与“模型观测/规则推导/人工确认/未知”状态，冲突不静默覆盖；完整声学曲线留侧档，只投影少量与翻译有关的事件。这是 [M07 模块稿的字段与投影建议](../research/07-smart-context.md#字段来源与确定性边界)，尚非冻结 schema，M03–M06 的真实准确率也未得到证明。

## 启动前需要实验确定

- 同一批英文多人播客中盲评无上下文、前后 3/3、10/10、动态 token 窗口；分别开关术语记忆与声学事件，记录专名、代词、省略、打断/重叠、反讽与跨句修正的错误、人工偏好、token 和延迟。`10/10` 是目标上限，不是已验证最优值。
- 人工校核 M04 句界、词界、切片 offset、缺时戳词及 M03 多 speaker 区间；测试开头/结尾不足 21 句、同起点交叠、句界编辑后窗口及译文缓存失效。区分真正打断与仅有同时讲话。
- 在获准使用的原音上标注笑声、局部停顿、音高/能量/语速变化与“不确定”，检查 M05/M06 观测误报和弃权；验证摘要、术语与自动人物关系不会把猜测提升为事实。
- 固定版本验证 Windows/Linux 导入导出、两小时节目内存、恢复与失败重试、字幕往返信息损失和选定翻译后端的实际费用。本文没有运行这些检查，全部**需要实验确定**。

本稿不设主选或备选；候选取舍由 [M07 grilling 票](https://github.com/CometDash77/project-babel/issues/47)与用户逐题完成。
