# Paper10 课题立项/开题报告替代稿

日期：2026-06-18

状态：课题立项临时材料。本文档用于在正式论文定稿前说明 Paper10 的研究问题、技术路线、已有工作基础、阶段性结论和后续计划，不是正式投稿论文，也不替代最终 manuscript、数据可用性声明或代码/数据归档材料。

依据文件：

- `e0_ceus_stage3_manuscript_draft_2026-06-18.md`
- `e0_ceus_stage3_manuscript_reframe_2026-06-18.md`
- `e0_original_vision_stage3_confirmatory_rollouts_2026-06-18.md`
- `e0_original_vision_stage3_confirmatory_rollouts_2026-06-18.json`
- `e0_submission_blocker_decision_packet_2026-06-11.md`
- `e0_integrated_citation_and_statistical_reporting_policy_2026-06-12.md`

## 一、课题名称

基于 monitor-gated value labels 的 GeoJEPA-MPC 农田布局规划方法研究

## 二、课题背景与研究意义

农田布局优化不是单纯的地块分类问题，而是一个带有空间约束和长期后果的序贯规划问题。一次局部地块交换会影响后续坡度降低、连片性改善、百亩方聚合和投资分布，因此规划算法需要在有限预算下评估多步候选行动，而不能只依赖单步即时收益。

传统 GIS 多目标优化和土地整治规划方法能够表达约束和评价指标，但在复杂空间状态下进行滚动候选搜索时，往往需要大量人工规则或高计算成本。强化学习和模型预测控制为序贯决策提供了技术路线，但直接把学习到的 value labels 用于农田布局规划会带来新的风险：如果候选标签质量没有经过监控，训练出的 value head 可能放大错误排序，并在 rollout 中产生不稳定或不可解释的规划建议。

本课题的意义在于把研究重点从“更大规模标签是否一定更好”转向“什么样的 value labels 可以被信任并进入规划流程”。这一路线更适合作为农田布局智能规划的可复现技术基础，因为它既关注性能提升，也明确报告失败边界和部署约束。

## 三、拟解决的核心问题

Paper10 当前要解决的问题可以概括为：

在受约束的农田布局规划中，如何利用 monitor-gated value labels 训练和筛选 GeoJEPA-MPC 的候选行动，使 value filtering 在可复现的条件下改善规划 rollout，同时识别不应被升级为论文主张或工程部署主张的边界情形。

这个问题包括四个子问题：

1. 如何把农田布局规划表述为带硬约束的有限步序贯 block-level swap 任务。
2. 如何生成有限 horizon 的候选行动 return labels，并用 candidate regret、candidate overlap 和 one-step regret 等指标判断标签质量。
3. 如何在 value-head 训练和 rollout 推理之间建立“soft training and hard inference”机制，即训练阶段用奖励和惩罚塑造候选排序，推理阶段用 executable mask 和 paired swap 规则保证可执行性。
4. 如何在 Bishan、Dongxing/Neijiang 等真实环境证据中区分可支持结论、诊断性失败和未来工作边界。

## 四、研究目标

本课题的总体目标是形成一个可复现、可审计、边界清晰的 GeoJEPA-MPC 农田布局规划 workflow，用 monitor-gated value labels 控制 value filtering 的使用条件。

具体目标如下：

1. 构建面向农田布局规划的 GeoJEPA-MPC 方法框架，包含空间表征、候选行动生成、有限 horizon rollout、value labels 生成、monitor gate 和 value filtering。
2. 在 Bishan 环境中验证 monitor-gated value labels 是否能够在已通过 gate 的标签规模上改善 rollout reward 和稳定性。
3. 对 Stage 3 的 50-state 候选行进行 confirmatory rollout，检验更大标签规模是否能在同一匹配基线下继续提升。
4. 在 Dongxing/Neijiang 外部区域中评估 workflow 的适配性和校准需求，避免把第二地区实验过度解释为稳健迁移优越性。
5. 形成面向正式论文和项目验收的 claim-evidence map，明确哪些结论已被当前证据支持，哪些仍属于 submission blocker 或后续研究任务。

## 五、研究内容与技术路线

### 5.1 任务建模

课题将农田布局规划建模为有限 horizon 的 block-level planning-unit abstraction。每一步 planner 选择一个 block，环境在该 block 内执行最多五个 paired farmland-forest swaps。交换规则优先把较高坡度的未交换农田转为林地，并把较低坡度的未交换林地转为农田，从而在保持执行规则可复现的同时推进坡度与连片性目标。

当前证据边界是 block-level，而不是任意不规则 cadastral parcel exchange。未来若要进入更接近工程应用的 parcel-level 部署，需要补充 area-tolerance matching、shared-perimeter-weighted contiguity、shape compactness 和显式 parcel geometry constraints。

### 5.2 状态、动作约束与奖励

状态包括 block-level features 和 county-level global features。Block features 覆盖农田/林地坡度、可交换面积、剩余交换潜力、compactness、当前农田面积和投资状态；global features 覆盖预算比例、全局农田坡度、连片性、step fraction、坡度和连片性变化、百亩方数量和面积、乡镇投资熵以及单个乡镇最大投资比例。

动作选择使用 base mask 和 executable mask 的交集。Base mask 判断 block 是否仍有可交换农田和林地；executable mask 进一步判断候选 block 是否能按照环境中的 connectivity-adjusted scoring rule 执行有意义的 paired swap。这样可以避免 planner 选择表面可用但实际无效的动作。

奖励函数汇总 stepwise farmland slope reduction、contiguity change、connected baimu-fang area change、新增 baimu-fang bonus、baimu-fang area decrease penalty 和 zero-swap penalty。主要评价指标为 100-step rollout total reward，辅助指标包括 final slope change、final contiguity change 和 final baimu-area change。

### 5.3 GeoJEPA-MPC 与 value filtering

GeoJEPA-MPC 由 geospatial predictive representation、候选行动生成、有限 horizon rollout scoring 和 scalar value filter 组成。Planner 在 executable mask 下采样候选 block actions，评估候选 future，并将 model-predictive rollout score 与 value-head output 结合，用于最终行动选择。

Value filter 不直接从未经控制的候选 return 集合中训练，而是依赖经过 monitor gate 筛选的 value labels。每个 label set 在进入 value-head 训练前都需要经过 candidate regret、candidate overlap 和 one-step regret 检查。通过 gate 的 label set 才能进入 manuscript-facing value-head training；未通过 gate 的 label set 作为诊断证据保留，而不被包装成正向结果。

### 5.4 Monitor-gated evidence control

本课题的核心机制是 monitor-gated evidence control。它不是简单追求更大标签规模，而是建立一个“标签是否可信”的判断层：

- candidate regret 用于衡量候选 top-k 与 return-ranked top-k 之间的 return gap；
- candidate overlap 用于衡量候选集合与 return-ranked 集合的一致性；
- one-step regret 用于判断 multi-step return 是否保留了超越 immediate reward 的信息。

这一机制让失败实验也有方法学价值：如果某个更大标签规模未能带来更好 rollout，它说明当前 candidate proposal、seed、top-k 或 monitor design 还不能支持更强主张，而不是被忽略或混入正向结果。

### 5.5 实验设计

Bishan 是当前主要验证环境。课题已形成 10x12/top4 pilot、20x16/top5 validated anchor 和 Stage 3 50-state confirmatory rollouts。Bishan rollout 使用五个 seeds、100 steps、horizon 5、global top-k 50、executable masks、blend candidate scoring 和 candidate-value-weight 0.1。

Stage 3 只推进两个 Stage 1 pass rows：

- `frontier_random050_50x16_h5_seed48_f050`，top-k 6；
- `frontier_random050_50x24_h5_seed47_f075`，top-k 12。

另有 `frontier_random050_50x24_h5_seed48_f075` 被标记为 diagnostic_near_pass，只用于诊断，不与 confirmatory rows 合并。

Dongxing/Neijiang 用于外部区域校准和 stress test。该环境包含 3711 blocks 和 76,376 parcel assignments。Dongxing 实验比较 pairwise-only、20x16、50x16 return-label scaling，并检查 5、10、20 labels 的低标签预算情形。Dongxing 使用 candidate-value-weight=1.0，说明第二区域需要 planner calibration。

## 六、已有工作基础与阶段性结果

### 6.1 Bishan 20x16/top5 是当前正向锚点

当前最稳健的正向结果来自 Bishan 20x16/top5 value filter。该设置在五个 100-step rollout seeds 上达到 mean reward 69.4705，sample standard deviation 1.0004。匹配的 Paper9 baseline 为 mean reward 67.5437，sample standard deviation 7.2246。因此，在当前匹配 rollout 协议下，Bishan 20x16/top5 相对 baseline 提升 1.9269 reward units，并表现出更低 seed-level variation。

与早期 10x12/top4 pilot 相比，20x16/top5 的 mean reward 从 65.2566 提高到 69.4705，sample standard deviation 从 5.0037 降低到 1.0004。由于 slope、contiguity 和 baimu-area 等辅助指标并非全部同向改善，当前应表述为 reward 和 weak-seed behavior 改善，而不是所有规划指标全面改善。

### 6.2 Stage 3 不支持直接 50-state 正向扩展主张

Stage 3 confirmatory rollouts 完成了两个 50-state value-filter rows 的训练和 rollout，但它们没有超过匹配 baseline：

- `frontier_random050_50x16_h5_seed48_f050` top-k 6 的 mean reward 为 64.2960，比 matched Paper9 baseline 低 3.2477；
- `frontier_random050_50x24_h5_seed47_f075` top-k 12 的 mean reward 为 66.2544，比 matched Paper9 baseline 低 1.2893。

诊断性 near-pass row `frontier_random050_50x24_h5_seed48_f075` top-k 12 的 mean reward 为 67.4913，比 baseline 低 0.0524。该结果说明存在接近 baseline 的失败模式，但 must not be pooled with confirmatory rows，不能用于加强 50-state 正向主张。

因此，当前结论不是“50-state scale-up 成功”，而是：monitor-gated workflow 可以识别 20x16/top5 这样的有效锚点，同时也能识别当前 50-state candidate rows 在匹配 baseline 下不应升级为正向结论。

### 6.3 Dongxing/Neijiang 支持校准和 stress test，不支持稳健迁移优越性

Dongxing/Neijiang 结果证明 workflow 可以运行到第二个真实县域环境，并能完成 return-label training 和 rollout summaries。相较 pairwise-only，50x16 return labels 提高了 transfer 和 scratch 两个 family 的 mean reward：transfer 从 37.8894 提高到 51.6183，scratch 从 40.2111 提高到 55.7324。

但是，50x16 family mean 中 scratch 高于 transfer，低标签预算下 5 labels 和 10 labels 也是 scratch 高于 transfer，20 labels 时 transfer 才高于 scratch。因此 Dongxing/Neijiang 目前支持“local calibration and return-label scaling”，不支持“robust Bishan-to-Dongxing transfer superiority”。

## 七、初步结论

截至 2026-06-18，Paper10 的初步结论是：

1. 本课题已形成一个可复现的 monitor-gated value-label workflow，可用于控制 GeoJEPA-MPC 中 value filtering 的使用条件。
2. Bishan 20x16/top5 是当前最明确的正向结果：在五个 100-step rollout seeds 上，mean reward 69.4705，高于 matched Paper9 baseline 的 67.5437，且 sample standard deviation 更低。
3. Stage 3 confirmatory 50-state rows 没有超过 matched Paper9 baseline，因此不能声称 direct 50-state Bishan scale-up success。
4. Dongxing/Neijiang 证明方法可迁移到第二真实环境进行校准和 stress test，但当前证据不支持 robust Bishan-to-Dongxing transfer superiority。
5. 课题的可立项价值在于提出并验证了“证据控制型 value filtering”路线：它能报告何时 value labels 有用，也能明确指出何时标签规模、candidate proposal 或 baseline policy 不足以支持更强主张。

## 八、创新点

1. 从标签规模扩张转向标签可信度控制。课题不把更大 value-label set 视为天然改进，而是用 monitor gates 判断 label set 是否可进入 value-head training。
2. 将 GeoJEPA-MPC 引入受约束农田布局规划，并把 finite-horizon value labels、executable masks 和 paired inference 结合为可复现 workflow。
3. 将失败实验纳入证据体系。Stage 3 50-state rows 没有被包装为正向扩展，而是作为 scale boundary 和 candidate-proposal/monitor-design 诊断。
4. 明确 soft training and hard inference 的实现边界。课题使用 reward/count penalties 训练候选排序，用 executable masks 和 paired swaps 保证 rollout 可执行性，但不把当前实现描述为 Constrained MDP、CPO 或 RCPO solver。
5. 在 Bishan 与 Dongxing/Neijiang 两类真实环境中建立了从主验证到外部区域校准的证据链，同时保留对迁移优越性和工程部署的限制。

## 九、可行性基础

代码和数据组织方面，仓库已经包含 Paper10 模型、planning utilities、training helpers、tests、checkpoints、smoke dataset、value labels、monitor outputs、rollout summaries、figure-ready CSV source data 和 manuscript-facing documents。当前分支为 `paper10-original-vision-validation`，已推送至 GitHub。

验证方面，最新保存点已经通过相关测试和 preflight 检查。最近一次验证包含 42 个相关测试通过，Paper10 preflight 为 PASS，工作树在提交后保持干净。

文档方面，已经形成 CEUS Stage 3 manuscript draft、Stage 3 manuscript reframe、submission blocker decision packet、citation/statistical-reporting policy、Data and Code Availability draft、figure/table numbering freeze 和 claim-evidence map。本文档在这些材料基础上转换为课题立项用途。

## 十、后续研究计划

### 第一阶段：立项材料定稿与基线政策确认

整理本立项报告，确认课题名称、研究目标和边界表述。重点解决 pairwise-only baseline policy：作者需要决定是否接受 matched Paper9 `rank_seed2028` baseline 作为当前 comparator，或补充一个单独标识的 pairwise-only baseline。

### 第二阶段：正式论文结构收敛

以 `e0_ceus_stage3_manuscript_draft_2026-06-18.md` 为基础，补齐正式论文所需的图表说明、参考文献格式、数据可用性声明、代码归档说明和统计报告政策。所有数值结论继续以 descriptive means、sample standard deviations 和 condition-specific comparisons 为主，除非预先制定统计检验方案。

### 第三阶段：工程部署边界补充

围绕 irregular cadastral parcel deployment 补充后续方法设计，包括 area-tolerance matching、shared-perimeter-weighted contiguity、parcel shape compactness 和 explicit parcel-geometry constraints。该阶段的目标是为后续工程化或更高水平论文提供扩展路线，而不是把当前 block-level evidence 过度解释为已解决 parcel-level 部署。

### 第四阶段：外部区域扩展与校准研究

在数据权限允许的条件下，扩展 Dongxing/Neijiang 之外的外部区域实验，预注册 candidate proposal、monitor thresholds、top-k、horizon 和 baseline protocol。该阶段重点检验 workflow 的校准能力和失败模式，而不是预设 transfer superiority。

## 十一、预期成果

1. 一套可复现的 GeoJEPA-MPC farmland layout planning workflow，包括 value-label generation、monitor gating、value-head training、value filtering 和 executable-mask rollout。
2. 一份 claim-bounded Paper10 正式论文草稿，围绕 monitor-gated value labels 和 calibrated planning-support workflow 组织。
3. 一套可审计的实验资产，包括 Bishan anchor results、Stage 3 confirmatory boundary results、Dongxing/Neijiang calibration results、source-data maps 和 reviewer smoke protocol。
4. 一套面向后续工程化的风险与边界清单，明确当前 block-level abstraction、queen contiguity、data-access routes、baseline policy 和 statistical-reporting policy 的未解决问题。

## 十二、风险、边界与待决事项

本课题当前不应声称 direct 50-state Bishan scale-up success。Stage 3 50-state confirmatory rows 已完成 rollout，但未超过 matched Paper9 baseline。

本课题当前不应声称 robust Bishan-to-Dongxing transfer superiority。Dongxing/Neijiang 支持 calibration and stress test，但 transfer 与 scratch 的结果在不同标签预算下是 mixed。

本课题当前不应声称 irregular cadastral parcel deployment 已经解决。当前实现使用 block-level planning-unit abstraction 和 queen contiguity，尚未实现 area-tolerance matching、shared-perimeter-weighted contiguity 和完整 parcel geometry constraints。

正式投稿前仍需解决以下事项：

- repository DOI 或 anonymous reviewer link；
- software licence、generated-output rights 和 model/checkpoint rights；
- full Bishan Tool2、GPKG-root geospatial inputs 和 Dongxing/Neijiang prepared data 的 public 或 controlled-access route；
- pairwise-only baseline policy；
- citation policy，尤其是 Paper9 未正式公开前的自洽引用路线；
- statistical reporting policy；
- final figure exports 和 source-data package。

## 十三、结语

Paper10 当前已经具备课题立项基础。它不是一个已经证明大规模扩展成功的系统，而是一个围绕“value labels 何时可信、何时不应升级为结论”的证据控制型农田布局规划研究。现有结果支持 Bishan 20x16/top5 的 value filtering 正向锚点，识别了 Stage 3 50-state 的边界，并在 Dongxing/Neijiang 中展示了外部区域校准需求。以此为基础继续推进，可以形成一篇结论边界清楚、复现路径完整、失败模式可解释的 Paper10 正式论文。
