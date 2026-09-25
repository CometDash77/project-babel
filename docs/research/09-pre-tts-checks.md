# M09 · TTS 前质量检查（文本阶段关口）

调研日期：2026-09-25。范围是英文播客原稿及真实时间轴、中文译稿进入**最终** TTS 前的检查。本稿只依据官方仓库、文档、源码与发布信息作候选判断；没有安装模型、生成语音或测量本项目样本。下述阈值、精度、误报率和硬件成本均**需要实验确定**。当前用途为个人使用，若用途改变应重新核对代码及模型权重许可。

## 结论与关口分工

文本关口应输出**带证据的待修项**，而非一个“可播出分数”。建议先以原片段 ID、speaker、英文词/句绝对时间、原始 `duration`、中文文本、术语表及锚点为输入；记录检查类型、原文/译文跨度、数值、规则或模型版本、疑点和人工处理结果。阻断最终 TTS 仅适合确定的缺漏或经人工确认的严重问题。统计异常和模型分数先进入复核队列。[Translate Toolkit 的检查输出保留出错条目](https://docs.translatehouse.org/projects/translate-toolkit/en/latest/commands/pofilter.html)；[COMET 官方说明原始分数不能直接按绝对质量解释](https://github.com/Unbabel/COMET#interpreting-scores)。这是本项目的关口设计推论，并非这些工具提供的现成播客工作流。

| 层级 | 本票建议检查 | 关口动作与误报边界 |
| --- | --- | --- |
| 可自动判定 | 片段缺失/空译、ID 与 speaker 串位、时间戳无效或倒序、锚点丢失、显式占位符/指定不得翻译词缺失；数字与单位、术语出现情况；英文字符/词数与中文字符比例；中文预计时长/原始真实时长比例 | 结构性错误可阻断；数字、单位、术语及两个比例一般只报疑点。数词改写、单位换算、意译、合并拆句、语气词都会制造合法差异。字符比例只做廉价异常排序，不代替时长估算。 |
| 模型辅助 | 语义遗漏/反义、代词指代、上下文矛盾、术语所指实体、speaker 用语风格与语域、难判断的跨语言锚点 | 提供对照跨度与理由，让人复核；低质量分或“critical”标签不直接放行/阻断。错误归因、领域术语和播客口语的泛化**需要实验确定**。 |
| 必须听评 | 中文实际发音与人名读法、声音克隆音色、情绪和重音、真实停顿/抢话、混音可懂度、听感速度与播出节奏 | 文本只能检查计划的停顿和时间预算；真实实现、可播出质量须听最终语音及声场。一次文本关口不能证明它们。 |

“原始真实 duration”须明确口径：片段首尾可能包含停顿、笑声或重叠。时间预算可同时比较总区间、原英文实际发声区间和保留锚点后的可用中文发声窗；不能用英文词数推算一个已经有的真实时长。M04 的[词时间戳与缺失限制](04-asr-timeline.md)、M06 的[停顿/语速观测边界](06-prosody.md)可提供来源，但原时间轴有误时应弃权。停顿/锚点检查应比较**计划的**断句、标注停顿和相对/绝对锚点是否保留；跨语言重排允许锚点移动，不能强求逐词同位。这里不冻结 M07 的结构。

字符比例应先固定计数定义，例如英文仅计字母/数字与中文仅计汉字、数字各记一套口径，并将同一源片段对应的全部中文片段合并后计算；否则标点、空格和拆句会主导异常。术语检查宜从人工确认的双语词表及别名出发，按实体 ID 汇总同一 speaker/全节目用法；人名音译变体、同名异人、语境改变应进入人工复核。数字/单位先将源与目标各自正规化成“数值＋单位＋范围/否定”候选，再比较；百分比与小数、英制换公制、约数和日期须保留原表述作为证据，不宜凭字符串不等就阻断。这些是检查逻辑建议，阈值及归一化正确率**需要实验确定**。

## 不生成最终 TTS 的时长估计路线

1. **第一版：可解释的区间基线。** 用将送入 TTS 的中文**朗读形式**计数：先处理数字、单位、缩写、英文夹杂和人名读法，再数汉语音节及需单独估算的外语词；按节目/说话人或目标声音的已知语速表换算发声时长，加标点与明确停顿的预算。可先以 `中文汉字数 / 每秒汉字数` 作粗估，但字数不等于实际音节数，数值、单位、英文、儿化和读法会破坏等价。输出上下界、覆盖率、未知读法及所用速率表，不给伪精确的单点秒数。`预计总时长 / 原片段真实 duration` 是待审信号，阈值**需要实验确定**。语言规范化可复用 [WeTextProcessing](https://github.com/wenet-e2e/WeTextProcessing#1-how-to-use)，汉字→拼音/音节可复用 [pypinyin](https://github.com/mozillazg/python-pinyin#%E4%BD%BF%E7%94%A8%E7%A4%BA%E4%BE%8B)。速率及停顿表由本项目数据校准，不是这两个项目提供的预测器。
2. **升级一：样本校准的语速模型。** 在合法取得的同类中文录音/目标 TTS 少量样本上，以人工确认文本和实际发声区间拟合 speaker、语域、句长、标点、数字/外语占比与局部语速。用分位数或预测区间表达不确定性，按播客和 speaker 留出测试集，重点看超时漏报。英文原声可经可靠强制对齐提取**英文**局部发声率、停顿及锚点，作为相对节奏参考；跨语言传递系数**需要实验确定**。MFA 的官方工作流要求音频、文本、词典和声学模型，输出对齐结果，不能对尚不存在的中文音频做 forced alignment。[MFA 官方命令与输出](https://montreal-forced-aligner.readthedocs.io/en/v3.3.7/user_guide/workflows/alignment.html)。
3. **升级二：目标语音系统的时长预测。** 若最终选用的中文 TTS 暴露稳定的 phoneme/token duration 或频谱帧数，可尝试只运行文本编码和 duration 部分、按目标模型配置换算秒数；[NeMo FastPitch 源码的导出输出](https://github.com/NVIDIA-NeMo/Speech/blob/main/nemo/collections/tts/models/fastpitch.py)含 `num_frames`、`durs_predicted` 和 `log_durs_predicted`，并支持 `pace`。但这不是通用中文/克隆音色预测 API：官方 [NeMo Voice Agent 的 FastPitch 配置](https://docs.nvidia.com/nemo/labs-voice-agent/about/core-concepts/speech-pipeline/text-to-speech/)标明其示例为**英语单声音**。独立 FastPitch 或其他音色模型预测值迁移到最终声音克隆系统是否有效、是否真的比最终合成便宜，均**需要实验确定**。若无同模型中文 checkpoint 与接口，先保留第一版。

不要把“强制对齐”“语音识别输出 token duration”或“英文实际时长”写成中文未来时长预测器；它们回答不同问题。实际中文 TTS 发音、说话人速度控制和停顿仍需最后听评。

## 候选核查与四档归类

四档含义：**DIRECT REUSE** 可直接复用明确的子能力；**WRAP·ADAPT** 需输入/输出与本项目规则适配；**REFERENCE** 只参考接口或方法，暂不作为首版依赖；**REJECT** 指不用于本关口的特定目标，不否定项目其他用途。维护快照来自 2026-09-25 GitHub API；`pushed_at` 只是仓库最近推送，`open_issues_count` 含 PR，release 不保证此功能的质量。各项目均未在本机跑通，Windows/Linux、两小时批量成本与真实播客误报**需要实验确定**。

| 候选 / 归类 | 官方输入→输出、可解释性及具体复用点 | 本项目误报/边界；维护、接口与资源 |
| --- | --- | --- |
| [Translate Toolkit `pofilter` / `poconflicts`](https://docs.translatehouse.org/projects/translate-toolkit/en/latest/commands/pofilter.html) · **WRAP·ADAPT** | PO/XLIFF/TMX 的原文+译文→失败条目；[`numbers`、`notranslatewords`、`blank`、`variables`、`sentencecount` 等规则](https://docs.translatehouse.org/projects/translate-toolkit/en/latest/commands/pofilter_tests.html)可给出具体触发原因。[`poconflicts`](https://docs.translatehouse.org/projects/translate-toolkit/en/latest/commands/poconflicts.html)输入 PO，输出相同英文消息的不同译文；复用检查思想/函数与冲突审阅入口。 | 播客片段须适配到其本地化格式；`poconflicts` 只能找**相同源消息**的不同译文，不能解决跨句实体术语一致性。数字改汉字、单位换算、句子重组会误报，`sentencecount` 不宜硬挡。Python/CLI，本地 CPU；[GPL-3.0](https://github.com/translate/translate)；仓库未归档，2026-09-24 最近推送，[3.20.0](https://github.com/translate/translate/releases/tag/3.20.0) 于 2026-09-11 发布，API 开放 issue/PR 合计 237。 |
| [WeTextProcessing](https://github.com/wenet-e2e/WeTextProcessing) · **DIRECT REUSE**（读法规范化子能力） | 中文/英文数字等书写形式→朗读形式；中文 `Normalizer.normalize_with_mapping` 还给输入/输出 Unicode 跨度与 `token_type`，便于解释哪段 `12` 变成“十二”。复用 `wetn`/Python TN、映射与 n-best 作为数字/单位比对和计数前处理。 | TN 有规则歧义，日期、金额、科技单位、人名及英语夹杂的正确读法**需要实验确定**；必须保留原文，不可把规范化结果当译文正确的证明。Python/CLI、本地 FST；[Apache-2.0](https://github.com/wenet-e2e/WeTextProcessing)；未归档，2026-07-29 最近推送，[v1.2.0](https://github.com/wenet-e2e/WeTextProcessing/releases/tag/v1.2.0) 于 2026-06-10 发布，开放 issue/PR 合计 4。 |
| [pypinyin](https://github.com/mozillazg/python-pinyin) · **DIRECT REUSE**（汉语音节计数） | 中文字/词→拼音列表；[API](https://github.com/mozillazg/python-pinyin/blob/master/docs/usage.rst)支持多音字、变调和自定义词典，可记下输入字与候选读法。复用音节计数和人名词典入口。 | 不是朗读时长模型；数字/外语要先规范化，多音字、人名读法错误会传到估算，未知字不得静默忽略。Python/CLI、本地 CPU；MIT；未归档，2026-07-20 最近推送，[v0.55.0](https://github.com/mozillazg/python-pinyin/releases/tag/v0.55.0) 于 2025-07-20 发布，开放 issue/PR 合计 45。 |
| [COMET · CometKiwi](https://github.com/Unbabel/COMET) · **WRAP·ADAPT**（语义疑点排序） | [无参考译文模式](https://github.com/Unbabel/COMET#scoring-without-references)：`src` 英文＋`mt` 中文→片段质量估计分；可用 CLI/Python `predict` 排序低分段。官方明确分数应结合模型版本解读，不能直接当播出等级。 | 只有总分，难指出具体遗漏；专名、口语、省略、拆并句及英中播客领域误报/漏报**需要实验确定**。PyTorch，可 CPU/GPU；代码 Apache-2.0，`wmt22-cometkiwi-da` 权重为 [CC-BY-NC-SA](https://github.com/Unbabel/COMET/blob/master/LICENSE.models.md)，需接受模型条件；仓库未归档，2026-04-21 最近推送，[v2.2.7](https://github.com/Unbabel/COMET/releases/tag/v2.2.7) 于 2025-09-01 发布，开放 issue/PR 合计 64。 |
| [COMET · XCOMET-XL / DocCOMET](https://github.com/Unbabel/COMET) · **REFERENCE**（可定位错误、上下文） | XCOMET 官方示例以 `src`＋`mt`＋`ref` 运行，输出质量及 minor/major/critical 错误跨度 JSON；[README](https://github.com/Unbabel/COMET#basic-scoring-command)又说明 DocCOMET 可加入上下文。参考错误跨度与证据呈现，后续验证适合**无人工参考译文**的运行模式及英中覆盖。 | 大模型的错误跨度不是事实裁决；官方示例所需 `ref` 与本项目无参考场景不一致，具体可用 checkpoint、输出偏移和中文长上下文表现**需要实验确定**。XL 官方标 3.5B 参数、GPU/显存及长文成本待测；权重 [CC-BY-NC-SA 且 XCOMET-XL 模型访问受限](https://huggingface.co/Unbabel/XCOMET-XL)。维护数据同 COMET 仓库行。 |
| [Montreal Forced Aligner](https://montreal-forced-aligner.readthedocs.io/en/latest/) · **REFERENCE**（英文实际节奏）/ **REJECT**（中文未来时长直接预测） | [音频＋同语言稿＋词典/声学模型→词/音素时间界](https://montreal-forced-aligner.readthedocs.io/en/v3.3.7/user_guide/workflows/alignment.html)，输出 TextGrid/JSON/CSV，边界可回查。复用英文原片段语速与停顿的测量概念；若最终中文音频已经存在，对齐就晚于本关口。 | 英文 ASR 错字、重叠讲话与音乐会损坏对齐；M04 已有对齐候选，不应为 M09 重跑全长音频。CLI、本地声学模型；MIT；未归档，2026-08-20 最近推送，[v3.4.2](https://github.com/MontrealCorpusTools/Montreal-Forced-Aligner/releases/tag/v3.4.2) 同日发布，开放 issue/PR 合计 288；资源取决于模型和语料。 |
| [NeMo FastPitch](https://docs.nvidia.com/nemo-framework/user-guide/26.02/nemotoolkit/tts/models.html) · **REFERENCE**（升级实验） | 文本 token、speaker/pace 及已训练模型→预测 token duration、频谱帧数/频谱；[源码](https://github.com/NVIDIA-NeMo/Speech/blob/main/nemo/collections/tts/models/fastpitch.py)提供可解释的 `durs_predicted`，理论上可在声码器前估时。 | 该实现并无本项目可直接使用的中文克隆声音时长承诺；模型泛化、帧率换算、停顿和最终 TTS 差异**需要实验确定**。NeMo Speech Python/PyTorch，通常需 GPU；Apache-2.0 代码，具体 checkpoint 另核；仓库未归档，2026-09-24 最近推送，[v3.0.0](https://github.com/NVIDIA-NeMo/Speech/releases/tag/v3.0.0) 于 2026-08-07 发布，开放 issue/PR 合计 300（整个大仓）。 |

这些仓库的 README、示例和发布记录证明**提供何种接口**，并不证明其中文播客长任务已稳定使用。上述“直接复用”也仅指子能力，非完整关口。没有发现一个经过本项目验证、能在无中文语音条件下同时判断语义、表演与目标时长的现成工具；这是本次候选范围内的结论。

## 需要实验确定

1. 从真实播客抽样含两小时节目、多人、抢话、术语、人名、数字/单位、英文夹杂、意译及句子拆并的片段，建立人工英中对照与错误类型。先明确源片段与译片段的多对多映射、时间坐标和断句口径，再统计各规则的误报、漏报、复核耗时。
2. 用目标中文声音或同类中文实录建立 speaker/节目隔离的速率数据；比较汉字数、规范化音节数、加标点/锚点停顿的区间模型，以及可取得的 duration predictor。报告秒级绝对误差、超预算漏报、预测区间覆盖率、低覆盖率弃权率和计算成本，才定阈值；不可用英文平均语速直接替代中文速率。
3. 对数字、单位、人名、缩写、代码切换逐条核查 WeTextProcessing 和 pypinyin 的候选读法；记录人工词典与规范化失败/歧义，并确认将要送入最终 TTS 的文本规范化路径一致。
4. 在同一标注集上测 CometKiwi 的低分召回、XCOMET 错误跨度及 DocCOMET 上下文效果，特别统计“译义正确但风格不同”的误报、“高分但漏关键事实”的漏报；检查英中与无参考设置、访问条件、GPU/Windows/Linux 资源。分数阈值只能依据该数据确定。
5. 听评最终中文样段的专名发音、停顿/锚点、说话人风格、情绪、重叠与混音；文本关口通过后仍需此步骤，且不能把听评结论回填为文本模型准确率。

本稿不选定自动放行的质量分数，也不声称“文本检查通过＝可播出”。
