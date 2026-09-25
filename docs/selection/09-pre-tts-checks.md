# M09 · TTS 前质量检查（文本阶段关口）选型调研

调研日期：2026-09-25。只研究英文播客原稿、原时间轴和中文译稿进入最终 TTS 前的文本检查；不指定主选或备选。证据基底是 [M09 模块稿](../research/09-pre-tts-checks.md)和[一条龙技术栈反查](00-mature-pipeline-stack.md)，下表另核对了官方文档、仓库、发布记录和公开使用路径。没有安装候选、测量项目样本或生成中文语音；个人用途以外须重新核对代码与模型权重许可。

## 已有成品流程给出的边界

[pyVideoTrans 的架构](https://github.com/jianchang512/pyvideotrans/blob/main/docs/architecture.md)有字幕行数/时间匹配、文本清理和逐句参考片段截取；[VideoLingo 的公开流程](https://github.com/Huanshere/VideoLingo/blob/main/docs/pages/docs/introduction.zh-CN.md)有字幕长度及翻译格式检查；[SoniTranslate 的说明](https://github.com/R3gm/SoniTranslate)提供人工字幕编辑。这些是可运行配音流程中的文本检查先例，未见其公开主流程证明自动完成英中语义核查、专名读法、克隆参考有效性和最终时长预测。[反查报告](00-mature-pipeline-stack.md)也未找到可核的“两小时英文多人播客保留重叠与背景、输出中文同声线成品”。因此现有案例只能证明局部工作流可运行，不能作为本项目通过率证据；完整效果**需要实验确定**。

## 候选横比与证据

归类沿用[模块稿的四档含义](../research/09-pre-tts-checks.md)：DIRECT REUSE 指明确子能力，WRAP·ADAPT 指需要数据与规则适配，REFERENCE 指只参考方法或待实验的扩展。归类不是主选/备选。热度与维护数字取 [GitHub 仓库 API](https://docs.github.com/en/rest/repos/repos#get-a-repository) 2026-09-25 快照；star、推送和 release 只能说明社区与维护活动，不能说明播客检查质量；`open_issues_count` 包含 PR，也不能等同响应速度。

| 候选及定位 | 已跑通的公开路径和可复用能力 | 热度、维护、许可 | 适配代价及待证实点 |
| --- | --- | --- | --- |
| [Translate Toolkit `pofilter` / `poconflicts`](https://docs.translatehouse.org/projects/translate-toolkit/en/latest/commands/pofilter.html)，WRAP·ADAPT | 官方[`pofilter` 示例](https://docs.translatehouse.org/projects/translate-toolkit/en/latest/commands/pofilter.html)展示输入本地化文件并输出失败条目；[规则清单](https://docs.translatehouse.org/projects/translate-toolkit/en/latest/commands/pofilter_tests.html)含空译、数字、变量、禁译词等。[`poconflicts` 文档](https://docs.translatehouse.org/projects/translate-toolkit/en/latest/commands/poconflicts.html)给出同源多译检查。是本地化检查成功路径，不是播客成品证明。 | [仓库](https://api.github.com/repos/translate/translate)约 980 stars，未归档，2026-09-25 有推送；[3.20.0](https://github.com/translate/translate/releases/tag/3.20.0) 于 2026-09-11 发布；代码 GPL-3.0。公开发布证明持续维护，具体 issue 响应时限未系统抽样。 | 播客片段须转成 PO/XLIFF/TMX 或调用其 API，再还原片段 ID 和证据跨度；英中数词改写、单位换算、意译及拆并句会误报。`poconflicts` 不能代替实体级术语一致性；准确率与集成成本**需要实验确定**。 |
| [WeTextProcessing](https://github.com/wenet-e2e/WeTextProcessing)，DIRECT REUSE 的文本规范化子能力 | 官方[README 示例](https://github.com/wenet-e2e/WeTextProcessing#1-how-to-use)展示中文/英文 TN、ITN；[映射契约](https://github.com/wenet-e2e/WeTextProcessing/blob/master/docs/python-rule-architecture.md)说明 `normalize_with_mapping` 返回输入/输出 Unicode 跨度与 n-best，可记录数字、日期等朗读形式。证明接口可运行，不证明对本项目混合语句正确。 | [仓库](https://api.github.com/repos/wenet-e2e/WeTextProcessing)约 826 stars，未归档，2026-07-29 推送；[v1.2.0](https://github.com/wenet-e2e/WeTextProcessing/releases/tag/v1.2.0) 于 2026-06-10 发布；代码 Apache-2.0。issue 样本少，响应速度不能仅由未结数量推断。 | 只复用读法候选和映射，不用 TN 结果证明译义正确。数字、单位、缩写、人名及中英夹杂的读法和最终 TTS 前处理一致性**需要实验确定**。 |
| [pypinyin](https://github.com/mozillazg/python-pinyin)，DIRECT REUSE 的音节计数子能力 | 官方[用法示例](https://github.com/mozillazg/python-pinyin/blob/master/docs/usage.rst)展示词组、多音字与自定义词典；[0.55.0 更新记录](https://github.com/mozillazg/python-pinyin/blob/master/CHANGELOG.rst)记载修复分词导致的读音问题。是成熟的拼音转换路径，不是时长预测器。 | [仓库](https://api.github.com/repos/mozillazg/python-pinyin)约 5.36k stars，未归档，2026-07-20 推送；[v0.55.0](https://github.com/mozillazg/python-pinyin/releases/tag/v0.55.0) 于 2025-07-20 发布；MIT。上述修复是维护响应实例，不代表普遍响应时限。 | 需先规范化数值和外语、对专名加人工词典；未知字与多音字应标不确定。音节到秒的 speaker 速率、停顿预算与超时漏报**需要实验确定**。 |
| [COMET / CometKiwi](https://github.com/Unbabel/COMET)，WRAP·ADAPT 的语义疑点排序 | 官方[无参考评分命令](https://github.com/Unbabel/COMET#reference-free-evaluation)以 `src` + `mt` 给出分数；[模型目录](https://github.com/Unbabel/COMET/blob/master/MODELS.md)列出训练和评价用途，属于机器翻译评价的公开成功路径。无参考分数可排序人工复核，不能定位每个遗漏，更不能当自动放行分。 | [仓库](https://api.github.com/repos/Unbabel/COMET)约 779 stars，未归档，2026-04-21 推送；[v2.2.7](https://github.com/Unbabel/COMET/releases/tag/v2.2.7) 于 2025-09-01 发布。代码 Apache-2.0；[模型许可表](https://github.com/Unbabel/COMET/blob/master/LICENSE.models.md)将 `wmt22-cometkiwi-da` 列为 CC-BY-NC-SA，且[README](https://github.com/Unbabel/COMET#quick-installation)提示部分模型需先接受许可并登录。 | 英中口语、省略、术语、长上下文和多对多片段映射是否可靠**需要实验确定**；模型资源及许可单独核。官方[分数解释](https://github.com/Unbabel/COMET#interpreting-scores)不支持直接设绝对播出阈值。 |
| [XCOMET-XL / DocCOMET](https://github.com/Unbabel/COMET)，REFERENCE 的错误跨度与上下文方法 | 官方[XCOMET JSON 示例](https://github.com/Unbabel/COMET#basic-scoring-command)使用 `src` + `mt` + `ref` 报错误跨度；[DocCOMET 上下文示例](https://github.com/Unbabel/COMET#scoring-with-context)展示 `--enable-context`。属于官方演示和研究用途，未找到无人工参考中文播客成功案例。 | 同一 COMET 仓库维护快照；[XCOMET-XL 模型卡](https://huggingface.co/Unbabel/XCOMET-XL)显示 3.5B 参数及受限访问，模型许可须依[官方表](https://github.com/Unbabel/COMET/blob/master/LICENSE.models.md)单独核。 | 参考译文要求、中文错误跨度偏移、长上下文窗口、显存与耗时**需要实验确定**；错误标签仍需人工复核。 |
| [MFA](https://montreal-forced-aligner.readthedocs.io/en/v3.3.7/user_guide/workflows/alignment.html) / [NeMo FastPitch](https://github.com/NVIDIA-NeMo/Speech/blob/main/nemo/collections/tts/models/fastpitch.py)，REFERENCE 的时长方法 | MFA 官方流程用已有音频和同语言文本求词/音素时间界，可提供**英文原声**发声率；FastPitch 源码暴露预测 duration/帧数。两者均有官方工作流或实现证据。 | [MFA 仓库](https://api.github.com/repos/MontrealCorpusTools/Montreal-Forced-Aligner)约 1.89k stars、MIT，[v3.4.2](https://github.com/MontrealCorpusTools/Montreal-Forced-Aligner/releases/tag/v3.4.2) 于 2026-08-20 发布；[NeMo Speech 仓库](https://api.github.com/repos/NVIDIA-NeMo/Speech)约 18.5k stars、Apache-2.0，[v3.0.0](https://github.com/NVIDIA-NeMo/Speech/releases/tag/v3.0.0) 于 2026-08-07 发布。NeMo 仓库规模不等于 FastPitch 中文克隆模型可用。 | MFA 不能对尚未生成的中文语音做对齐。FastPitch 是否有与最终中文克隆 TTS 相同的模型和廉价时长接口**需要实验确定**；若没有，就不能当预生成时长预测器。 |

## 可比较的关口方案

| 方案形态 | 预期输入与可解释输出 | 适用范围与缺口 |
| --- | --- | --- |
| 结构与规则检查 | 片段 ID、speaker、绝对时间、源/译文本、锚点、术语表；输出缺漏、倒序、占位符、数字/单位、术语和计数异常及原文跨度。[`pofilter` 的失败条目形式](https://docs.translatehouse.org/projects/translate-toolkit/en/latest/commands/pofilter.html)可参考。 | 确定的缺漏可阻断；数词与术语差异先人工复核。需自写播客时间轴和多对多片段映射，现成规则库不提供这套契约。 |
| 读法与时长区间 | 对将送入 TTS 的中文先以 [WeTextProcessing](https://github.com/wenet-e2e/WeTextProcessing)给读法候选，再用 [pypinyin](https://github.com/mozillazg/python-pinyin)计汉语音节，结合目标声音样本校准的语速和显式停顿，输出上下界、未知读法和覆盖率。 | 字符比只能廉价排序；音节数不等于秒。必须比较原区间、英文实际发声区间和扣除锚点后的可用中文窗口，速率、阈值及漏报**需要实验确定**。 |
| 模型辅助复核 | [CometKiwi](https://github.com/Unbabel/COMET#reference-free-evaluation)对低分段排序；[XCOMET/DocCOMET](https://github.com/Unbabel/COMET#explaining-translation-errors)仅作为有条件的跨度/上下文研究方向。输出模型版本、输入配对、分数或错误跨度及人工处理状态。 | 分数不能证明译文正确；播客口语和拆并句可能误判。无参考模式、英中覆盖、资源和许可**需要实验确定**。 |

文本关口的分工是本项目从上述接口推导的建议，不是任何单一工具已交付的播客产品。实际中文发音、音色、情绪、抢话和混音须在合成后听评；文本检查通过不等于可播出。[M09 模块稿](../research/09-pre-tts-checks.md)给出更细的计数与时间口径。

## 启动前需要实验确定

1. 用获准使用的英文多人播客建立含术语、专名、数字/单位、中英夹杂、重叠、意译和拆并句的人工对照集；核实片段映射与时间轴后，比较各规则的误报、漏报、复核耗时和可解释性。
2. 以目标中文声音样本按节目和 speaker 留出测试，比较汉字计数、规范化音节+停顿区间及任何同模型 duration 接口；报告绝对秒误差、超预算漏报、区间覆盖率与计算成本，才定阻断阈值。
3. 测 WeTextProcessing 与 pypinyin 在专名、数值、单位、缩写和代码切换上的读法覆盖；确认估计输入与最终 TTS 前处理一致。
4. 在同一人工标注集上测 CometKiwi 的低分召回与误报；仅在拿到适合的无参考英中接口、模型许可与资源后，再测 XCOMET/DocCOMET。听评最终样段的发音、停顿、表现和混音，不能用模型分数替代。

本稿留给 [M09 拍板票](https://github.com/CometDash77/project-babel/issues/51)选择主选与备选，不在 research 票预先定案。
