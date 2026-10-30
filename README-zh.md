# dsh-drill-script-check — 应急演练脚本核对

[English](README.md) · [简体中文](README-zh.md) · [Español](README-es.md) · [Português](README-pt.md) · [हिन्दी](README-hi.md)

<!-- topblock:v1 -->
> **这是什么**　应急演练脚本核对。输出一份「哪一行、哪一栏、差什么」的清单。
> **给谁用**　安全管理员、应急管理岗；不用懂命令行。
> **你交什么**　这项核对用到的原始材料（表格、清单或文书）；不改原件。Excel 可先转成 JSON/YAML，对话里也能代转。
> **它不做什么**　不判合规、不认定责任、不替代审核人；只列材料内部能逐条指认的差异。
> **怎么开始**　在 WorkBuddy / 扣子搜「安全合规核对包」（本检查是其中一项；上架以商城为准）；或命令行：
> `dsh plugin --profile <name> add dsh-drill-script-check`
<!-- /topblock:v1 -->

[![DSH Market](https://raw.githubusercontent.com/2BingLing/dsh-market/master/assets/readme/badge-listed-en.svg)](https://dsh.market/)
[![dshfind](https://dshfind.com/api/badge/PerryLink/dsh-drill-script-check?metric=downloads)](https://dshfind.com/en/plugins/PerryLink/dsh-drill-script-check?ref=badge)

`dsh-drill-script-check` 读取一份应急演练脚本——演练表头加每个环节一行——核对这份脚本自身的齐备与算术：每个环节是否填写演练阶段或脚本内容、是否明确指挥人、响应级别是否取自你配置的口径、有脚本动作的环节是否列明所需资源、各环节计划时长合计是否等于演练总时长、关键节点是否写明判定条件、环节序号是否重复、表头是否声明演练名称与组织单位。

## Install

```sh
dsh plugin --profile <name> add dsh-drill-script-check
dsh --profile <name> --dump-config | grep 'dsh-drill-script-check'
```

## 实际输出长什么样

![dsh-drill-script-check 工作流图：文档 → 规则包 → 核对结果。](docs/assets/dsh-drill-script-check-flow.svg)

*工作流概览：文档 → 规则包 → 核对结果。下面的示例使用实际命令面。*


本插件对自己 `DR-007` 测试夹具的**真实输出**，不是示意图。规则库不伪造引文，因此每条发现都会同时写明所引条款，以及该条款原文本次未取得。

## 它回答什么问题

### 示例

下表是示例集：第一行是详细走查，其余行是简短案例。


#### 详细输出

**工具** `drill_script_check`

**输入**

~~~json
{"rows":[{"序号":"1","演练阶段":"","脚本内容":"","指挥人":"张指挥", ...}]}
~~~
 
**输出**

~~~json
{
  "id": "dsh-drill-script-check.DR-001.de09b5a6",
  "ruleId": "DR-001",
  "severity": "warn",
  "locator": {
    "row": 1,
    "field": "phase"
  },
  "found": "第 1 行 phase、script 都为空",
  "expected": "phase、script 至少应填写一项",
  "fix": "补填演练阶段与脚本内容；本条只核对是否填写，不判断处置是否正确"
}
~~~

*来源 `dsh-drill-script-check/tests/fixtures/DR-001/DR-001-unsafe.json; dsh-drill-script-check/tests/fixtures/DR-001/cases.json; dsh-drill-script-check/rules/drill-script-check.yaml; dsh-drill-script-check/tests/index.test.ts`*

| 你会问 | 它怎么答 |
|---|---|
| 某个环节的演练阶段和脚本内容都没填，会被报出吗？ | 会。`DR-001` 同时要求 `phase` 与 `script` 两栏，两栏都空才报出该行——填了其中一栏即通过。它只核对这一栏是否填写，不判断该处置动作是否正确、是否符合预案。 |
| 我填了响应级别，`DR-003` 却报告 `skipped`，为什么？ | `DR-003` 拿 `level` 栏与 `values` 里的取值清单比对，而 `values` 出厂为空，因此在你配置本单位的分级口径之前，本条报告 `skipped`（无法执行），而不是静默通过。它只核对所填值是否在册，绝不判断某一事件应当启动哪一级响应。 |
| 纯告知性的环节没有列装备物资，会被报出吗？ | 不会。`DR-004` 只在环节的 `script` 内容已填写时才要求 `resource` 栏，因此纯告知性的环节不会被要求列资源。它只核对资源栏是否填写，不判断所列资源是否充足、是否与实际配备一致。 |
| 各环节计划时长加起来不等于演练总时长，能查出来吗？ | 能。`DR-005` 把各环节的 `durationMin` 相加，再与 `totalDurationMin` 相比，后者取自材料表头（引擎会先在行内找，再回落到表头）。本条只做加法核对，不判断时间安排是否合理、是否够用。 |
| 环节的关键节点栏要写什么？ | `DR-006` 要求该环节的 `checkpoint` 栏填写关键节点及其判定条件。它只核对这一栏是否写明，不判断该条件是否可观测、是否恰当。 |
| 同一阶段分了三个动作行，其中两行的环节序号相同。 | `DR-007` 会报出重复的 `stepNo`，因为序号重复会让时长合计与环节统计失真。同一阶段分多个动作各占一行是正常的——给每行各自的序号即可。 |

## 依据的标准

| 文件 | 文号 | 引用它的规则 |
|---|---|---|
| 《生产安全事故应急演练基本规范》 | YJ/T 9007—2019（原 AQ/T 9007—2019，2025 年第 1 号公告调整代号；本次未取得条文） | DR-001, DR-002, DR-004, DR-005, DR-006, DR-007, DR-008 |
| 本单位应急预案体系（本机构配置） | 无统一标准（本条依据为本机构预案的分级口径） | DR-003 |

**边界（中文译文，以英文原文为准）：** 本插件核对一份 **应急演练脚本** 的齐备性与算术——每个环节是否写明演练阶段与脚本内容，是否明确指挥人，响应级别是否取自你配置的取值口径，有脚本动作的环节是否列明所需资源，各环节计划时长合计是否等于演练总时长，关键节点是否写明判定条件，环节序号是否唯一，以及脚本是否写明演练名称与组织单位。它**不**判定演练是否逼真、是否有效，响应级别是否正确，处置动作是否正确，也不判定演练是否达到目标。

> ### ⚠️ 在采信报告中的引文之前，请先读这一段
>
> **每条 `excerpt` 的状态逐条不同，不是统一的。** 有的规则引用逐字条文（`kind: direct`），有的按条文原则推导（`kind: derived-from-principle`，最高 `warn`），有的阈值由本机构配置（`kind: institutional-configuration`，最高 `info`）。规则包从不概括引文：取不到原文时，`excerpt` 会如实写明，推理写在 `note` 里；并有测试断言没有任何规则声称拥有它并不拥有的引文。**对仍标为「未取得原文」的规则，取得文本后必须把 `excerpt` 换成真实条款，并把 `kind` 提升为 `direct`。**
>
> 结论性判断留给审核人：本插件只列出材料内部可以逐条指认的差异，不判断事实真伪，也不评价合规性。

## Compatibility

| 项目 | 状态 |
|---|---|
| Harness | 对等版本范围 `>=0.1.2-rc.1 <0.2.0 \|\| >=0.2.0-0 <0.3.0` —— 已实测同时接受 `0.2.0-rc.2` 与 `0.2.1-rc.2`。**已声明 `engines.dsh`**：0.2.1 起由宿主单独裁决，范围为 `>=0.2.1-0 <0.3.0` |
| Node | `^22.19.0 || >=24.0.0` |
| 平台 | 全平台（纯 ESM；无原生代码、无联网、不调用模型） |
| 工具模式 | `native` / `ptc` 均可；批量校验整个目录时建议 `ptc`，schema 成本只付一次 |

## What it does

规则表、字段说明与行为细节见 [README.md](README.md#what-it-does)（英文主版本）。本插件只列出材料与所引条款之间的字面差异，并对无法执行的检查在 `skipped` 中逐项说明。

## Configuration

全部可调参数都在 `src/config.ts` 的 Schemastery schema 中，只改 `cordis.yml` 即可生效，无需改代码；逐条阈值在 `rules/` 下的规则库文件里。

| 键 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `rulesFile` | string | `rules/drill-script-check.yaml` | 规则库文件路径，相对插件包根目录 |
| `disabledRules` | string[] | `[]` | 要停用的规则 id 列表；每条都会出现在 `skipped` 中 |
| `onlyRules` | string[] | `[]` | 只执行这些规则 id；留空表示执行全部规则 |
| `skipNotes` | string | `""` | 附加到每条 `skipped` 说明后的备注 |
| `timeoutMs` | number | `120000` | 工具协作式超时预算（毫秒） |

## Material format

支持 JSON 与 YAML。完整字段示例见 [README.md](README.md#material-format)（英文主版本）。字段在读取层是可选的，由检查引擎校验，因此部分导出的材料会产生"缺项"类差异，而不是让程序崩溃。

## Rule sources

规则数据与代码分离，每条规则都带文件名、文号、按原文自身编号体系的条款号、逐字摘录与来源地址。加载期强制：摘录必须是真实引文且不少于八个字符；依据仅为原则性条款（`kind: derived-from-principle`，严重级上限 `warn`）或本机构配置（`kind: institutional-configuration`，上限 `info`）的检查不得标为 `error`。夸大依据的规则库会在加载期失败，而不会产出一份看起来很有底气的报告。

核验中确认的边界与"刻意没有作出的结论"见 [README.md](README.md#rule-sources)（英文主版本）与随包的 `rules/evidence/` 目录。

## Troubleshooting

- **插件装上了但工具不出现**：确认 `main` 指向 `lib/index.mjs` 且 `pnpm run build` 已生成该文件；`main` 写错会让加载器静默跳过该条目。
- **`dsh plugin add` 报版本不兼容**：peer 范围覆盖 `0.1.x` 与 `0.2.x`；若运行时在其之外，可显式豁免：`dsh plugin --profile <name> allow-version <包名@版本> --dsh-version <runtime> --accept-risk`
- **某条规则没有执行**：查看 `skipped` 数组，其中写明了规则 id 与原因。
- **`check` 报 `manifest-peers` 失败**：静态检查器比对的是一份早于 0.2 世代的硬编码 peer 范围；安装期的 peer 校验以运行时为准。这是 `dsh-plugin-dev` 的已知上游问题。
- **时间看起来偏移**：全部计算都是对输入字符串做墙上时钟运算，不做时区换算。

## Development

```sh
pnpm install
pnpm run typecheck
pnpm test
pnpm run build
node ../scripts/sync-shared.mjs dsh-drill-script-check
```

第 4 项把 `../_shared` 的共享件同步进 `src/shared/`；每次改动共享件后都要重跑。

## PerryLink DSH Plugin Family

完整清单（62 个核查器 + 通用插件）见 [按材料选核查器](https://perrylink.github.io/zh/checkers/choose/)；本仓只是其中一个。

## License

[Apache License 2.0](LICENSE) © 2026 dsh-drill-script-check contributors.
