# M10 · Jev 异常修复路由评估

调研日期：2026-09-25。范围是个人用途的英文播客→中文重演流水线；只核查公开资料与项目接口，**未调用 Jev、未训练分类器、未跑样片**。以下效果与成本判断若无本项目实测，均标为「需要实验确定」。

## 结论

**现在不值得把 Jev 设为必经路由；是否在少数语义歧义上引入 Jev，需要实验确定。**先让普通代码完成字符/预计时长比例、数字与术语、时间锚点等可判定检查，直接处理可唯一确定的修复；剩余案例先进入人工复核或已有翻译模型的受限结构化选择。只有在真实样本上证明 Jev 比这两个基线明显减少错误修复和人工工作，且其额外调用、中文效果与外部传输可接受时，再考虑接入。这是本票基于下列能力与风险的**推论**，不是 Jev 质量的实测结论。

“Jev”已定位为 [TypeSafe AI 官方发布的 Jev / System One 模型](https://typesafe.ai/blog/introducing-system-one-models-and-jev)，并非资料缺失。官方 [Introduction](https://docs.typesafe.ai/introduction) 与 [API reference](https://docs.typesafe.ai/api) 确认：输入 `state` 和类型化 `questions`，`Choice` 在预先列出的选项中选择并返回概率；它不生成修复文本。网上另有 [Jev AI](https://github.com/jev-ai) 等自称相关的独立站或社区项目，不能把它们的接口、价格与授权当作 TypeSafe 官方事实。

## 从失败信号倒推路由能力

路由器应接收一次检查的结构化**失败事实**：原文/译文短片段与说话人、绝对时间及词锚；字符和时长估计、TTS 语速上限；数字/单位/专名/术语的逐项对齐结果；失败规则 ID、严重度、已尝试动作及每次复检差异。长段完整节目不应直接投入分类器。数值计算、硬性约束、重试上限和最终放行仍归普通代码；这是由 [Jev 官方已知弱项：计数、数学、时间比较、长无关状态](https://docs.typesafe.ai/model-jaggedness/jev-1.13) 与本票的可复检需求共同推导出的边界。

| 可观察信号 | 首选处理 / 可考虑动作 | 不得由模型越过的边界 |
| --- | --- | --- |
| 全部硬检查 PASS；仅软性流畅度疑问 | `ACCEPT`；软性疑问无法判定则 `ESCALATE` | 硬失败不能由高概率 `ACCEPT` 覆盖。 |
| 预计时长超限，数字/术语/信息点均对齐 | 先试 `REMOVE_FILLER`；信息可浓缩时 `COMPRESS`；只是表达拗口可 `REPHRASE` | 任何删改后都重验信息、时长、锚点。 |
| 小幅时长超限，实际允许的语速仍可接受 | `ALLOW_FAST_DELIVERY` 候选 | 是否可听、上限与声线损失**需要实验确定**；不能代替 TTS/听评。 |
| 句段边界导致长短不均或说话人/停顿错配 | `SPLIT_DIFFERENTLY` | 不能改变原节目绝对时间与 speaker 归属。 |
| 数字、否定、专名、术语漏译或原意错 | `RETRANSLATE`，必要时 `ESCALATE` | 禁止只靠加速、删 filler 或强行接受绕过语义错误。 |
| 多种动作均可能、证据缺失、反复无改善 | `ESCALATE` | 不得无限循环，也不得因分类置信度高而自动授权不可证的改变。 |

动作列表是**路由指令**而非修复器。一次路由只提出一个主要动作及其理由引用；修复器可拒绝不可执行的动作。`COMPRESS`/`REPHRASE`/`RETRANSLATE` 需要生成模型或人修改文本，Jev 的 `Choice` 只能在动作中选择；[官方“Generation”限制](https://docs.typesafe.ai/model-jaggedness/jev-1.13)也明确这一点。`ESCALATE` 应永远可选；“最可能的一类”不等于该类安全可行，[官方关于 Choice 与 Noul 的差异](https://docs.typesafe.ai/model-jaggedness/jev-1.13)说明相对选择可能在所有选项都差时仍产生赢家。低置信度、候选均不可执行或互相冲突时，应弃权。

防循环建议由确定性状态机负责：按片段保留失败规则、约束与译文的版本指纹；每次动作后用同一组检查复检；只有失败项减少或经允许的质量指标改善才可继续；同一动作对同一指纹不重复；无改善、交替回退、达到调用/修复预算时 `ESCALATE`。预算可按实际样本设定，具体上限**需要实验确定**。保留动作、证据、复检结果与模型版本便于排查。[TypeSafe 官方路由示例](https://docs.typesafe.ai/patterns/intent-routing)也把最终分支和低置信度升级交给代码，而不是让模型自行执行下游操作。

## 逐候选分类

四档含义：**DIRECT REUSE** 可直接复用清晰接口；**WRAP·ADAPT** 需本项目封装与校准；**REFERENCE** 仅借鉴设计；**REJECT** 当前用途不宜采用。这里评估的是“本项目异常修复路由”的复用程度，不是工具通用能力排名。维护快照取 2026-09-25 的官方仓库/API；仓库 `pushed_at` 和开放 issue 数不证明某项功能的稳定性。

| 候选 / 分类 | 真实接口与具体复用点 | 维护、许可、成本与局限 |
| --- | --- | --- |
| **规则优先 + 固定动作表** · **DIRECT REUSE**（设计基线） | 复用本票既定 PASS/FAIL 检查作为路由的事实层：由失败规则与保护条件映射唯一动作；输出动作、失败规则和复检记录。无第三方依赖或外部调用。 | 维护成本是本项目的规则、阈值和回归样例；个人用途无第三方许可。语义模糊、多个可行修法以及“语速听起来是否太快”无法仅靠规则判断，覆盖率**需要实验确定**。这是应先测量的反方基线。 |
| [TypeSafe Jev 1.13](https://docs.typesafe.ai/models) · **WRAP·ADAPT**（条件候选） | [HTTP `POST /v1/systemone`](https://docs.typesafe.ai/api)：`state` + `model` + `questions`；`Choice` 可映射八个动作及明确的弃权条件；返回选项概率和 `confidence`。[官方 Python SDK](https://docs.typesafe.ai/sdk/python) 提供同步/异步 `system_one`。复用类型化决策接口和概率，不能复用为修复文本生成器。 | 2026-09-15 官方发布、早期访问；[官方 SDK](https://github.com/typesafe-ai/typesafe-sdk-python) 为 MIT，2026-09-21 发布 v0.7.1，仓库未归档/开放条目 6；**SDK 许可不等于托管模型权重许可**。官方 [模型页](https://docs.typesafe.ai/models)列文本输入、64k 总预算/单题 32k、$0.042/百万输入 token、输出免费；价格和配额会变化。需账号/API key、网络和向第三方传输片段；本项目真实调用费用与延迟**需要实验确定**。官方称英语最好、CJK 表现不等同；[已知弱项](https://docs.typesafe.ai/model-jaggedness/jev-1.13)包括数字、时间、间接推理和提示注入。权重非本地开放；版本应固定而非用自动漂移的 `jev-latest`。 |
| [scikit-learn](https://github.com/scikit-learn/scikit-learn) 的轻量监督分类器 · **WRAP·ADAPT**（有标注后优先对照） | [TF-IDF](https://scikit-learn.org/stable/modules/generated/sklearn.feature_extraction.text.TfidfVectorizer.html) 加 [LogisticRegression `predict_proba`](https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LogisticRegression.html)；数值失败信号可作为额外特征。复用本地训练/预测、[概率校准](https://scikit-learn.org/stable/modules/generated/sklearn.calibration.CalibratedClassifierCV.html)及 [DummyClassifier](https://scikit-learn.org/stable/modules/generated/sklearn.dummy.DummyClassifier.html) 作最低基线。 | BSD-3-Clause；2026-09-11 发布 1.9.1、未归档，2026-09-24 仍有仓库推送（GitHub API 快照）。本地 CPU/无按次费用，需人工标注、类别平衡与版本化特征；少样本、跨节目风格与中文同义改写泛化**需要实验确定**。输出概率须在留出节目上校准，不能天然视作真实正确率。 |
| [Hugging Face Transformers 零样本 NLI](https://huggingface.co/docs/transformers/main_classes/pipelines) + [mDeBERTa-v3-base-mnli-xnli](https://huggingface.co/MoritzLaurer/mDeBERTa-v3-base-mnli-xnli) · **WRAP·ADAPT**（无标注本地对照） | `pipeline("zero-shot-classification", model=...)` + `candidate_labels`，可在不训练新分类头时比较修复动作的语义描述。模型卡提供本地 Python 入口和中英文 NLI 背景。 | 框架 Apache-2.0，模型卡标 MIT；Transformers 2026-09-09 发布 v5.17.0、未归档，2026-09-25 有推送（GitHub API 快照）。本地可用，框架许可与**实际选用模型**许可需分别核对。官方管线文档说明每个候选可能增加前向计算，通常较慢；所选模型约 0.3B 参数。该模型的 XNLI 分数不是播客修复动作准确率；中文候选描述、CPU/GPU 内存、Windows/Linux 与长段吞吐**需要实验确定**。 |
| [OpenAI Structured Outputs](https://developers.openai.com/api/docs/guides/structured-outputs) · **REFERENCE**（已有生成模型时的对照路径） | 用受限 JSON schema 的 enum 输出八个动作及证据字段；可复用现有翻译模型调用路径，若语义确实复杂也能同一模型判断。调用层参考 [官方 Python SDK](https://github.com/openai/openai-python)。 | 托管模型为商业 API，SDK Apache-2.0；SDK 2026-09-24 仍有推送、未归档（GitHub API 快照）。需网络和按模型计费；结构合法不等于语义正确。[官方文档](https://developers.openai.com/api/docs/guides/structured-outputs)说明拒绝及未完成响应需单独处理。若流水线已有生成模型，这可能省去专用路由依赖；相对 Jev 的准确率、端到端成本与延迟**需要实验确定**。 |

**REJECT（作为默认路线）**：每段无条件调用 Jev 或任何 LLM，再用“模型置信度高”覆盖数字/术语/时间硬失败。该方案重复计算已有确定性事实、增加调用与错误入口，且与 [Jev 官方“数学留在代码中”](https://docs.typesafe.ai/model-jaggedness/jev-1.13) 的建议相反。这里拒绝的是接入方式，不是拒绝 Jev 作为条件候选。

## 决策所需的小实验（本票不执行）

1. 从真实节目抽取不同说话人、快语速、长数字/单位、专名、否定、打断、时间锚、已有多轮修复的片段；每例由人标注**允许动作集合**、禁止动作、最终是否可听及修复后复检结果。一个样本可能有多个合理动作，不能强迫单一标签。
2. 对同一批固定输入比较：规则基线、scikit-learn（若标注量足够）、零样本 NLI、现有生成模型结构化选择、Jev。只在规则无法唯一确定时调用模型。记录被自动处理比例、错误 `ACCEPT` / 漏掉 `RETRANSLATE` / 不必要重译、宏平均分类表现、弃权率、复检通过率、人工复核时间、每小时节目调用次数与总费用。切分应按节目/说话人，避免相邻句泄漏。
3. 将硬失败的错误放行和死循环视为高代价；分别校准每个动作的自动执行阈值，不照搬厂商示例数字。检查概率在中文片段与不同节目上的可靠性、同义改写稳定性和服务失败时回退。Jev 的 `confidence` 是选项分布的汇总，不是已证实的本域正确概率；[官方文档](https://docs.typesafe.ai/confidence)也要求按任务风险调阈值。
4. 在 Windows/Linux 和目标机器上测本地方案 CPU/GPU/内存、模型加载与批量延迟；对外部 API 记录真实请求/响应版本、错误与价格。个人用途允许研究这些选择，但云端上传播客文本的权利与隐私边界仍须针对实际素材核对。所有效果、资源和阈值结论目前**需要实验确定**。

因此，M14 汇总时应把“规则优先 + 有限动作 + 弃权/复检/预算”作为架构边界；Jev、轻量监督分类器和本地零样本模型只列为待实测的语义路由候选，不把 Jev 写成必需依赖。
