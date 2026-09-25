# M10 · Jev 异常修复路由评估：候选与证据

调研日期：2026-09-25。此稿只供[本模块拍板票](https://github.com/CometDash77/project-babel/issues/53)核对，**不指定主选或备选**。范围是个人用途的英文多人播客中文重演；复用[既有 M10 模块稿](../research/10-jev-routing.md)的失败信号、有限动作、硬约束与复检边界，并参考[一条龙项目反查](00-mature-pipeline-stack.md)的 M10 行。未调用候选模型、未训练分类器、未跑本项目音频；本项目效果、时延与总成本均**需要实验确定**。

## 一条龙项目给出的边界

[pyVideoTrans 的九阶段架构](https://github.com/jianchang512/pyvideotrans/blob/main/docs/architecture.md)展示分层异常、可重试与不可重试错误、重试和用户可读映射；[VideoLingo 的使用说明](https://github.com/Huanshere/VideoLingo/blob/main/docs/pages/docs/introduction.zh-CN.md#当前限制)展示日志与恢复，但严格 JSON 失败时仍可能要删除 output 重试；[SoniTranslate README](https://github.com/R3gm/SoniTranslate)声明 checkpoint 续跑。它们证明有可借鉴的工程处理路径，**未证明**按播客译文的语义、时间锚和 TTS 质量选择修复动作，也未见结构化弃权/复检契约。把“程序异常重试”当成“译文修复路由成功案例”会混淆问题。

本模块可复用的输入契约是：失败规则及严重度、源文/译文局部片段、speaker 与绝对时间、数字/单位/专名/术语对齐、预计时长与允许语速、已执行动作及复检差异。输出是有限动作 `ACCEPT`、`REMOVE_FILLER`、`COMPRESS`、`REPHRASE`、`ALLOW_FAST_DELIVERY`、`SPLIT_DIFFERENTLY`、`RETRANSLATE`、`ESCALATE` 中一个，附触发事实和版本记录。硬失败（如数字、否定、术语、时间锚丢失）不能由概率覆盖；每次修复后须重检，同一失败指纹不得无限循环。上述动作和边界来自[既有 M10 模块稿](../research/10-jev-routing.md)与 [Jev 已知弱项](https://docs.typesafe.ai/model-jaggedness/jev-1.13)，是本项目设计假设，实施阈值**需要实验确定**。

## 候选横比

分类描述本模块可复用程度，不是最终排名。热度数字为 2026-09-25 的公开快照，不能替代质量或本项目成功率。

| 候选与复用程度 | 已跑案例、接口及适用点 | 热度、维护、许可与本项目缺口 |
| --- | --- | --- |
| **确定性规则 + 有限动作状态机**：直接复用设计基线 | [pyVideoTrans 架构](https://github.com/jianchang512/pyvideotrans/blob/main/docs/architecture.md)有实际成品流程中的异常分流；本项目可由既有 PASS/FAIL 事实映射唯一动作，留存复检和预算。无第三方推理服务。 | 一条龙流程并未验证本项目的语义动作选择。规则及阈值由本项目维护；多解、表达是否可听等覆盖率**需要实验确定**。 |
| **TypeSafe Jev 1.13**：条件性封装候选 | 官方 [API](https://docs.typesafe.ai/api)的 `Choice` 在闭集选项间给出概率及 confidence，适合少数无法由规则唯一判定的语义动作；[官方路由示例](https://docs.typesafe.ai/patterns/intent-routing)仍由代码执行下游。独立作者有[工单路由 live demo](https://github.com/zeke/jev)；另一作者[报告 8 个工程示例曾调用 live API](https://github.com/Foadsf/jev-for-engineers)，并公开错误题目、算术交给模型及猜测阈值造成的缺陷。均非播客修复成品。 | [官方 SDK 仓库](https://github.com/typesafe-ai/typesafe-sdk-python)约 225 stars，MIT、未归档；[v0.7.1](https://github.com/typesafe-ai/typesafe-sdk-python/releases/tag/v0.7.1)于 2026-09-21 发布并修复[密钥出现在异常信息的问题](https://github.com/typesafe-ai/typesafe-sdk-python/issues/9)。服务 2026-09-15 才[公开早期访问](https://typesafe.ai/blog/introducing-system-one-models-and-jev)。[模型页](https://docs.typesafe.ai/models)列文本输入、版本、预算与当日标价，但服务价/限额可变；SDK MIT 不代表模型权重可本地部署。需账号、网络、外传片段；中文判断、真费用、延迟与阈值**需要实验确定**。 |
| **scikit-learn TF-IDF + LogisticRegression**：有标注后封装候选 | 官方 [TF-IDF](https://scikit-learn.org/stable/modules/generated/sklearn.feature_extraction.text.TfidfVectorizer.html)、[分类概率](https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LogisticRegression.html)与[概率校准](https://scikit-learn.org/stable/modules/generated/sklearn.calibration.CalibratedClassifierCV.html)接口成熟，可融合失败规则和数值特征，在本地训练/预测；[DummyClassifier](https://scikit-learn.org/stable/modules/generated/sklearn.dummy.DummyClassifier.html)可作最低对照。这里的“成功”是通用工具接口和公开用法，未找到同类播客修复成品。 | [仓库](https://github.com/scikit-learn/scikit-learn)约 67.4k stars、BSD-3-Clause、未归档；[1.9.1](https://github.com/scikit-learn/scikit-learn/releases/tag/1.9.1)于 2026-09-11 发布，近期 [issue 有维护者答复](https://github.com/scikit-learn/scikit-learn/issues/35014)。无按次云调用，但要人工标注并按节目切分验证；少样本、类别不平衡、中文改写泛化和校准**需要实验确定**。 |
| **Transformers 零样本 NLI + mDeBERTa-v3-base-mnli-xnli**：无标注时的本地对照 | [模型卡](https://huggingface.co/MoritzLaurer/mDeBERTa-v3-base-mnli-xnli)提供 `zero-shot-classification` 用法及中文 XNLI 测试结果；[管线文档](https://huggingface.co/docs/transformers/main_classes/pipelines)提供候选标签接口。模型卡约 162k 月下载、318 likes、85 Spaces 使用，说明通用试用，**不是**修复动作准确率。 | [Transformers 仓库](https://github.com/huggingface/transformers)约 166.6k stars、Apache-2.0、未归档；[v5.17.0](https://github.com/huggingface/transformers/releases/tag/v5.17.0)于 2026-09-09 发布，近期 [issue 有维护者互动](https://github.com/huggingface/transformers/issues/49090)。模型卡标 MIT，权重许可要按实际下载版本核对。约 0.3B 参数；本机内存/延迟、标签措辞敏感性、跨节目与中文判断**需要实验确定**。 |
| **现有生成模型的结构化输出**：流程对照候选 | [OpenAI Structured Outputs](https://developers.openai.com/api/docs/guides/structured-outputs)可用 JSON Schema 限定动作 enum；若翻译阶段已有生成模型，可以复用调用路径。结构合法不保证动作正确，拒绝与未完成响应需另行处理；未找到本项目播客修复成功案例。 | [官方 Python SDK](https://github.com/openai/openai-python)约 31.7k stars、Apache-2.0、未归档；[v3.19.2](https://github.com/openai/openai-python/releases/tag/v3.19.2)于 2026-09-24 发布。托管模型价格和素材外传边界按实际提供方另核；与 Jev 比较的正确率、成本及延迟**需要实验确定**。 |

公开案例强度有明显差别：Jev 有第三方真实 API 试用和可操作演示，但示例作者明确[只有少量合成样本，不能用于校准](https://github.com/Foadsf/jev-for-engineers)；其他候选有广泛通用使用和维护记录，却没有可核的“英文多人播客译文异常 → 中文修复动作 → 复检通过”成品。**所有候选在本项目目标上的成功率均需要实验确定**。Jev 的 `Choice` 不生成修复文本，[官方限制页](https://docs.typesafe.ai/model-jaggedness/jev-1.13)也明确生成任务另用生成模型；相对概率和 confidence 不能当作本域正确率。每段无条件调用语义模型、或让概率覆盖硬失败，不符合该边界。

## 留给拍板票的判据与启动前门槛

1. 先建立同一批经许可的真实片段，覆盖快语速、数字/否定/专名、时间锚、打断、重叠、反复修复；人工标注**允许动作集合**、禁止动作、复检结果与是否可听。多个动作可合理时不强制单标签。
2. 比较规则基线、已有生成模型结构化选择、Jev、本地 NLI；标注量足够再加入监督分类器。只在规则不能唯一决定时测语义路由。记录错误 `ACCEPT`、漏掉 `RETRANSLATE`、不必要重译、弃权、复检通过、人工复核时间、每小时调用/费用；按节目和说话人切分以避免相邻句泄漏。效果差异**需要实验确定**。
3. 分动作校准自动执行阈值，测试中文改写稳定性、服务不可用时的人工回退、同指纹重复动作与修复预算。模型只提出动作，生成/执行/复检由后续组件和代码承担；阈值与停止条件**需要实验确定**。[Jev confidence 指南](https://docs.typesafe.ai/confidence)要求按风险设置阈值。
4. 在目标机器上测本地模型加载、CPU/GPU 内存与批量时延；云服务核实版本、动态价格/限额、真实文本传输许可和隐私条件。最终可部署性**需要实验确定**。

以上是证据与待验证条件，不代替[对应 grilling 票](https://github.com/CometDash77/project-babel/issues/53)的主选、备选及拒绝理由决定。
