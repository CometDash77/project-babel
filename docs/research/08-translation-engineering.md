# M08 · 翻译工程（AiNiee 深度分析）

调研日期：2026-09-25。目标是英文播客逐句转成两份中文文本：**忠实语义译文**与**最终中文表演稿**。证据来自官方仓库、源码、文档、发布和公开 issue；本次**没有安装翻译器、调用模型或翻译真实播客**。下文“可复用”指已有实现或接口可供个人用途的下一阶段试验，不代表播客效果已验证。四档分类为 DIRECT REUSE（可直接用某一现成功能）、WRAP·ADAPT（有成熟核心但须封装或改造）、REFERENCE（借设计）、REJECT（不选作该用途主链）。

## 先定播客翻译的验收对象

逐句结果必须保留：①当前句前后话轮与代词指代，不能只看孤立句；②原 speaker、角色/嘉宾资料及交叉插话，不能把不同人的台词串成一人；③原句语气、笑声/犹豫/打断等表演线索，同时区分可听见事实与模型推断；④人名、组织、品牌、专用词、禁译词、数字和单位在全期一致；⑤原句 `start/end`、真实 `duration`、停顿、重叠与关键时间锚点，表演稿需在 TTS 前接受预计朗读时长检查；⑥每句有稳定 ID，保存英文原文、两层中文、术语版本、上下文引用、模型/提示词版本、检查与人工修订记录。前五项是需求，末项使问题可追溯。M04 已给[词/句时间轴及 speaker 合并的局限](04-asr-timeline.md)，M05 与 M06 给[带不确定性的情绪观测](05-emotion.md)和[声学观测](06-prosody.md)；21 句结构化上下文由 [M07](https://github.com/CometDash77/project-babel/issues/8) 决定，时长与语义关口由 [M09](https://github.com/CometDash77/project-babel/issues/10) 决定，本稿不替它们冻结 schema 或阈值。

## 结论

**AiNiee 是 WRAP·ADAPT 主研究对象**：字幕读写、行级缓存、术语/禁翻、项目角色与背景、批处理、译后润色和规则检查都有具体实现，远超过“调用 LLM 翻译”的示例；但它的主链按文件行/字幕块处理，前文主要是原文列表，缺播客的后文、speaker、声学事件及时间预算。[README](https://github.com/NEKOparapa/AiNiee)所说的长文质量是项目方描述，不能外推为播客效果。其 [7.2.4 发布](https://github.com/NEKOparapa/AiNiee/releases/tag/AiNiee7.2.4)于 2026-09-01，仓库未归档，2026-09-09 有推送；GitHub API 的 `open_issues_count=29` 含 PR，不能当纯 issue 数。近期公开的[“下文参考”需求 #1086](https://github.com/NEKOparapa/AiNiee/issues/1086)正提示后文能力不能先当现成；[并行任务需求 #1098](https://github.com/NEKOparapa/AiNiee/issues/1098)及[停止任务缺陷 #1099](https://github.com/NEKOparapa/AiNiee/issues/1099)提示调度需验证。

**两段式先例存在，但要区分实现。** AiNiee 的 `TranslatorTask` → `PolisherTask` 与 `TRANSLATED`/`POLISHED` 状态是翻译后润色流程；[原版 `CacheItem`](https://github.com/NEKOparapa/AiNiee/blob/295d2ff19cd5ea8ce280a405fe4389a0eec411d7/ModuleFolders/Service/Cache/CacheItem.py)只有一个 `translated_text`，[润色任务](https://github.com/NEKOparapa/AiNiee/blob/295d2ff19cd5ea8ce280a405fe4389a0eec411d7/ModuleFolders/Service/TaskExecutor/PolisherTask.py)会覆写它，故不是“两份文本均持久化”的现成方案。独立分支项目 [AiNiee-Next 的 `CacheItem`](https://github.com/ShadowLoveElysia/AiNiee-Next/blob/7f001a02e2a1655c205534f4eb4537c2027ad123/ModuleFolders/Infrastructure/Cache/CacheItem.py)明确分开 `translated_text`/`polished_text`，`final_text` 优先取后者；这是更近的双层数据结构先例，但仍须把第二层从普通“润色”改成有时间预算且能回查语义的表演稿。

## AiNiee：模块/文件级复用边界

以下文件链接固定在本次核对的 AiNiee 提交 `295d2ff`，避免 `main` 后续变化使结论失效。原版为 [AGPL-3.0](https://github.com/NEKOparapa/AiNiee/blob/295d2ff19cd5ea8ce280a405fe4389a0eec411d7/LICENSE)，README 另有[个人合法用途声明](https://github.com/NEKOparapa/AiNiee#%E7%89%B9%E5%88%AB%E5%A3%B0%E6%98%8E)。当前仅作个人用途调研；若日后分发、提供网络服务或改变用途，要重新核对代码及所用模型/API 的条件。

| 能力与证据 | 可复用什么 | 播客适配与不能推断之处 |
| --- | --- | --- |
| [SrtReader](https://github.com/NEKOparapa/AiNiee/blob/295d2ff19cd5ea8ce280a405fe4389a0eec411d7/ModuleFolders/Domain/FileReader/SrtReader.py)、[VttReader](https://github.com/NEKOparapa/AiNiee/blob/295d2ff19cd5ea8ce280a405fe4389a0eec411d7/ModuleFolders/Domain/FileReader/VttReader.py) 与对应 writer | 字幕块输入/输出、`subtitle_time` 附加属性；可直接用于**字幕文件的格式往返试验** | 时间码是字符串，未原生表示 speaker、词级时间、pause/overlap 或稳定节目 ID。SRT/VTT 行切分也未必等于说话句界；时间与文本 round-trip 需验证。 |
| [CacheItem](https://github.com/NEKOparapa/AiNiee/blob/295d2ff19cd5ea8ce280a405fe4389a0eec411d7/ModuleFolders/Service/Cache/CacheItem.py)、[CacheProject](https://github.com/NEKOparapa/AiNiee/blob/295d2ff19cd5ea8ce280a405fe4389a0eec411d7/ModuleFolders/Service/Cache/CacheProject.py)、[CacheManager](https://github.com/NEKOparapa/AiNiee/blob/295d2ff19cd5ea8ce280a405fe4389a0eec411d7/ModuleFolders/Service/Cache/CacheManager.py) | 行级状态、文件分组、`extra` 元数据、定时/原子保存与续跑、按行或 token 组批；缓存设计可抽取或封装 | `extra` 可容纳元数据，但当前字段未定义双层稿、speaker/时间轴/模型版本；`generate_previous_chunks` 从当前待处理列表取**前文**，没有后文结构，也可能随过滤/重跑改变所见上下文。需稳定 ID、不可变原文、两层修订史与绝对时间。 |
| [PromptBuilder](https://github.com/NEKOparapa/AiNiee/blob/295d2ff19cd5ea8ce280a405fe4389a0eec411d7/ModuleFolders/Domain/PromptBuilder/PromptBuilder.py)、[GlossaryHelper](https://github.com/NEKOparapa/AiNiee/blob/295d2ff19cd5ea8ce280a405fe4389a0eec411d7/ModuleFolders/Domain/PromptBuilder/GlossaryHelper.py)、[CharacterHelper](https://github.com/NEKOparapa/AiNiee/blob/295d2ff19cd5ea8ce280a405fe4389a0eec411d7/ModuleFolders/Domain/PromptBuilder/CharacterHelper.py) | 按当前文本匹配术语/禁翻行，注入项目角色、人名推荐译法、角色说话方式、背景和文风，另有前文文本与翻译示例 | 角色表面向小说/游戏角色，需映射为节目嘉宾/主持人档案；背景从世界观改为节目/单期背景。`previous_text_list` 只有原文，不含 speaker/duration/事件/后文；不能仅调 prompt 就宣称达到 Smart Context。 |
| [AnalysisTask](https://github.com/NEKOparapa/AiNiee/blob/295d2ff19cd5ea8ce280a405fe4389a0eec411d7/ModuleFolders/Service/TaskExecutor/AnalysisTask.py) | 两阶段分块提取、归并角色/术语/禁翻候选并保存 `analysis_data` | 可作专名候选发现，自动提取结果仍需人工确认与版本化；游戏角色类别不等于播客人物身份，也不能把候选直接当强制词表。 |
| [TaskExecutor](https://github.com/NEKOparapa/AiNiee/blob/295d2ff19cd5ea8ce280a405fe4389a0eec411d7/ModuleFolders/Service/TaskExecutor/TaskExecutor.py)、[TranslatorTask](https://github.com/NEKOparapa/AiNiee/blob/295d2ff19cd5ea8ce280a405fe4389a0eec411d7/ModuleFolders/Service/TaskExecutor/TranslatorTask.py)、[PolisherTask](https://github.com/NEKOparapa/AiNiee/blob/295d2ff19cd5ea8ce280a405fe4389a0eec411d7/ModuleFolders/Service/TaskExecutor/PolisherTask.py) | 分块调度、限流、失败后重轮处理、译后润色、任务统计日志 | 可参考/封装调度骨架；需要逐句稳定事务、两层内容分别保存、幂等重试和修订 provenance。并发是否保持术语与跨话轮一致性**需要实验确定**。 |
| [ResponseChecker](https://github.com/NEKOparapa/AiNiee/blob/295d2ff19cd5ea8ce280a405fe4389a0eec411d7/ModuleFolders/Domain/ResponseChecker/ResponseChecker.py)、[TerminologyChecker](https://github.com/NEKOparapa/AiNiee/blob/295d2ff19cd5ea8ce280a405fe4389a0eec411d7/ModuleFolders/Service/TranslationChecker/TerminologyChecker.py)、[RuleChecker](https://github.com/NEKOparapa/AiNiee/blob/295d2ff19cd5ea8ce280a405fe4389a0eec411d7/ModuleFolders/Service/TranslationChecker/RuleChecker.py) | 行数/键序/空响应/占位符等可自动判错重试；译后术语缺失、禁翻、格式与漏译异常可报告 | 术语检查主要在原文命中后看指定译名**是否出现**，不是语义正确、词形/别名或全节目一致性的证明；默认响应检查不验证 speaker、语气、时长或完整语义。两层稿都应检查，强制失败/人工豁免规则需设计。 |

原版 README 提供 GUI 与在线/本地模型入口、字幕格式和批量文件说明，未提供本项目可直接调用的稳定“播客翻译 API”。本地可运行仅指官方有安装/启动路径，**本机未跑通**；LLM 供应商、模型、显存和成本由所选后端决定，不能为 AiNiee 写一个固定 GPU 数值。[README 功能与安装](https://github.com/NEKOparapa/AiNiee)。[真实用户 issue](https://github.com/NEKOparapa/AiNiee/issues)证明有人在使用与反馈，尚无可核查的本项目播客双层稿案例。

## 横向候选与四档分类

维护快照为 2026-09-25；GitHub `pushed_at` 是仓库级推送，`open_issues_count` 含 PR，均非效果指标。“可运行”仅指官方给出本地入口。真实播客效果、两小时吞吐、Windows/Linux 的本机兼容性均**需要实验确定**。

| 候选 / 分类 | 精确复用点与成熟性证据 | 许可、接口、局限 |
| --- | --- | --- |
| [AiNiee-Next](https://github.com/ShadowLoveElysia/AiNiee-Next) · **WRAP·ADAPT**（自动化对照） | 独立 CLI 分支；[README](https://github.com/ShadowLoveElysia/AiNiee-Next#%E5%91%BD%E4%BB%A4%E8%A1%8C%E5%8F%82%E6%95%B0)给 `translate ... --resume` 和队列，声明 Windows/Linux 本地运行、重试、失败切换、RAG；[`CacheItem.py`](https://github.com/ShadowLoveElysia/AiNiee-Next/blob/7f001a02e2a1655c205534f4eb4537c2027ad123/ModuleFolders/Infrastructure/Cache/CacheItem.py)分别存两层文本；[`RAGPlugin.py`](https://github.com/ShadowLoveElysia/AiNiee-Next/blob/7f001a02e2a1655c205534f4eb4537c2027ad123/PluginScripts/RAGPlugin/RAGPlugin.py)是关键词检索已译对照，非结构化声学上下文。 | AGPL-3.0；未归档，2026-09-24 推送，[V2.7.5](https://github.com/ShadowLoveElysia/AiNiee-Next/releases/tag/V2.7.5)于 2026-06-10 发布，API open count=1。README 的 20k 行/50 并发图是项目方展示，不是独立播客测评；后文、speaker 与时间预算仍缺。 |
| [Weblate](https://github.com/WeblateOrg/weblate) · **REFERENCE**（若选部署 CAT/TM 服务则 WRAP·ADAPT） | [翻译记忆](https://docs.weblate.org/en/latest/admin/memory.html)、[glossary](https://docs.weblate.org/en/latest/user/glossary.html)支持首选/禁用词、解释与上下文；[`autotranslate.py`](https://github.com/WeblateOrg/weblate/blob/b892031408bce327d0eb2821fe6143a87702f7ec/weblate/trans/autotranslate.py)按 `(source, context)` 优先、纯 source 回退。适合借鉴“同一句在不同节目语境不误复用”与批量 TM 查找。 | GPL-3.0；未归档，2026-09-25 推送，[2026.9.1](https://github.com/WeblateOrg/weblate/releases/tag/weblate-2026.9.1)于 09-08 发布，API open count=477。服务/API/CLI 有文档，部署成本较高；定位是软件本地化，不处理音频、话轮或表演稿。 |
| [Translate Toolkit](https://github.com/translate/translate) · **DIRECT REUSE**（格式/静态 QA 子层） | Python/CLI 的转换、unit ID/location/notes 与 [checker](https://github.com/translate/translate/blob/312811e91cbe473bcb883c26b1527468f876b120/translate/filters/checks/checker.py)可承接带稳定 ID 的文本交换与数字/占位符类检查；[官方首页](https://toolkit.translatehouse.org/)列可用格式和 3.20.0。 | 官方首页标 GPL-2.0-or-later，而 GitHub API 将仓库识别为 GPL-3.0，具体文件/版本许可解释有差异，实际复制代码前核对许可证文件。未归档，2026-09-24 推送，[3.20.0](https://github.com/translate/translate/releases/tag/3.20.0)于 09-11 发布，API open count=237。无生成式翻译、播客上下文或时间预算；必须外置音频 manifest。 |
| [Argos Translate](https://github.com/argosopentech/argos-translate) · **DIRECT REUSE**（离线句级 MT 实验基线） | [Python `translate` API](https://github.com/argosopentech/argos-translate/blob/17ed1a9b055c5ba1b51d76b683bbb0c64e2a4a88/argostranslate/translate.py)、[模型包安装](https://github.com/argosopentech/argos-translate/blob/17ed1a9b055c5ba1b51d76b683bbb0c64e2a4a88/argostranslate/package.py)及 CLI；可比较无上下文的离线机器译文与上下文方案，不能担当表演稿。 | MIT；未归档，2026-08-08 推送；GitHub latest release 仍指向 [v1.4.0（2021）](https://github.com/argosopentech/argos-translate/releases/tag/v1.4.0)，API open count=162。API 没有 speaker、glossary、时间码参数；最新代码与旧 release 的可安装对应关系、英中模型、CPU/GPU 与 Windows/Linux 运行**需要实验确定**。 |
| [OmegaT](https://github.com/omegat-org/omegat) · **REFERENCE** | [官方手册](https://omegat.sourceforge.io/manual-standard/en/chapter.project.folder.html)给项目 TM/glossary 目录，[官网/仓库说明](https://github.com/omegat-org/omegat)列 fuzzy match、TMX 与术语；借鉴长期人工修订记忆的组织方式。 | 官方说明 GPL-3.0-or-later，桌面 CAT 以人编辑段落为中心。此次 GitHub API 对该仓库返回 404，**未取得实时 release/issue/HEAD**，故不把维护状态或程序化集成判为已核实；无播客时间轴/双层稿证据。 |

这里的 DIRECT REUSE 都限定于**子层或实验基线**，不是整条播客翻译链可直接复用。Weblate/OmegaT 有成熟翻译记忆，但节目中同一句的 speaker、指代和情绪可能改变译法；即使 exact match 也应带上下文键并允许人工否决。Argos 的无上下文输出若在目标语料明显输给上下文方案，就作为基线保留而不进主链。作为“整套播客双层翻译器”，上述候选目前都不合格（**REJECT 此整体用途**），并非否定其局部能力。

## 建议的可追溯两层流水线（设计推论，非实现）

每个句 ID 先关联 M04 时间轴与 M07 结构化前后文；按该句文本和节目档案匹配经人工确认的术语、禁翻及 speaker 风格；生成**忠实语义译文**，保留命名实体、数量、否定、指代与未确定项；再以该译文及原句音频/时长线索生成**中文表演稿**，只允许可回查的口语化、停顿和长度调整。两层分别持久化，任何后续重试/人工改动都带来源、版本和理由。规则检查可先筛结构、术语、禁译、数字；语义完整性与表演自然度仍需人工盲评，M09 再加预计朗读时长与时间锚点关口。候选检查器只提供部分规则，不能说已做到“glossary enforcement”或语义等价。

## 需要实验确定：可执行清单

1. **对照样本**：取获准个人使用的英文播客多节目样本，覆盖 2 小时长节目、至少两位 speaker、专名、数字、代词回指、笑声、插话/重叠、短促反应和音乐污染；保留原音频、人工修订英文稿、时间轴与人工参考译法。按节目/说话人分层，避免同一期泄漏到测试集。
2. **上下文消融**：同一模型和参数下比较孤句、AiNiee 前文、M07 前后句结构化窗口、再加 speaker/事件资料；人工盲评指代、speaker 归属、语气和跨句连贯性。`#1086` 的下文需求与源码前文实现之间差距要以真实版本复核。
3. **两层稿对照**：AiNiee 原版翻译+润色、AiNiee-Next 双字段 CLI 与明确“忠实稿→表演稿”的独立任务说明，在相同句子比事实保真、漏译/增译、口语自然度、TTS 前预计时长、超预算句比例；保存两层与修订 diff，不把普通润色自动等同重演写作。
4. **术语和记忆**：预先锁定人物/品牌/节目词表，比较 AiNiee 提示注入+`TerminologyChecker`、Weblate 带 context 的 TM、无记忆方案；检查词形/别名/同名异人、全期一致性及误触发。记录规则可检出的比例、假阳性、人工豁免和成本。自动术语提取先由人确认。
5. **格式与时间**：对 SRT/VTT 与 M04 输出做导入→翻译→导出回环，逐 ID 对比原英文、speaker、词/句绝对时间、pause、overlap 与未对齐词；测试多行/空 cue、VTT cue ID、重叠字幕、非语言声事件。不能只比较字幕行数。
6. **工程与许可**：固定提交/发布、模型/API、提示词与词表版本，在 Windows/Linux 运行小样本及连续两小时；记录安装、内存/显存、每小时耗时、费用、限流/429、失败重试、断点续跑、重跑幂等及结果差异。原版、Next 与 Weblate/Toolkit 的 GPL/AGPL 及模型/API 条件按实际**个人用途**核对；若用途改变重新审查。
7. **真实案例证据门槛**：找到可公开核验的播客项目输入、输出与人工质量标注之前，只能说这些项目有字幕/文档/本地化使用案例。README 性能图、stars、issue 活跃度、软件演示与一小段样例均不证明英文长播客→中文表演稿质量。

最终选型留给上述同样本实验及 M07/M09 的接口决定；本票交付的是复用边界和实验方案。
