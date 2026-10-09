# dsh-drill-script-check — 应急演练脚本核对

[![DSH Market](https://raw.githubusercontent.com/2BingLing/dsh-market/master/assets/readme/badge-listed-en.svg)](https://dsh.market/)

`dsh-drill-script-check` 读取一份应急演练脚本——演练表头加每个环节一行——核对这份脚本自身的齐备与算术：每个环节是否填写演练阶段或脚本内容、是否明确指挥人、响应级别是否取自你配置的口径、有脚本动作的环节是否列明所需资源、各环节计划时长合计是否等于演练总时长、关键节点是否写明判定条件、环节序号是否重复、表头是否声明演练名称与组织单位。

## 实际输出长什么样

![Terminal demo of dsh-drill-script-check: real output over its DR-007 fixture](https://raw.githubusercontent.com/PerryLink/dsh-drill-script-check/main/docs/assets/dsh-drill-script-check-demo.png)

本插件对自己 `DR-007` 测试夹具的**真实输出**，不是示意图。规则库不伪造引文，因此每条发现都会同时写明所引条款，以及该条款原文本次未取得。

## 它回答什么问题

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

**Boundary:** this plugin checks an **应急演练脚本** for completeness and arithmetic — that each step names its
phase and script content, that it names a commander, that the response level comes from your vocabulary, that a
step with an action lists the resources it needs, that the step durations total the drill's planned duration, that
key checkpoints state their judgement condition, that step numbers are unique, and that the script names its drill
and organiser. It does **not** decide whether a drill was realistic or effective, whether the response level was
right, whether the actions were correct, or whether the drill met its objectives.

> ### ⚠️ Read this before trusting a citation in the report
>
> **Every `excerpt` in this plugin's rule pack says, in so many words, that the clause text was not
> obtained.** The regime lives in AQ/T 9007—2019, 《生产安全事故应急条例》(国务院令第708号) and each
> institution's emergency plans. The verification pass could not retrieve verbatim clause text, so rather than
> paraphrase a quotation the pack states the gap in the `excerpt` field itself and puts the honest reasoning in
> `note`. Every rule is therefore `warn` or `info`, and a test asserts that no rule claims a quotation it does
> not have. **When the texts are in hand, replace each `excerpt` with the real clause and raise `kind` to
> `direct`.**
>
> **No response-level scale is built in.** Levels differ between plan systems — general / larger / major /
> especially major, or a unit's own Ⅰ–Ⅳ — so `DR-003` reports itself in `skipped` until you configure your
> vocabulary, and it never judges which level an event should trigger. That is the incident commander's call.
>
> The resource rule fires only when a script action is present, so a step that is purely informational is not
> asked for equipment. And the duration total is read from the header, where a drill's planned length normally
> lives.

## Compatibility

| 项目 | 状态 |
|---|---|
| Harness | 对等版本范围 `>=0.1.2-rc.1 <0.2.0 \|\| >=0.2.0-0 <0.3.0` —— 已实测同时接受 `0.2.0-rc.2` 与 `0.2.1-alpha.1`。**刻意不声明 `engines.dsh`**：它没有任何读取者，也无法拒装任何宿主 |
| Node | `^22.19.0 || >=24.0.0` |
| 平台 | 全平台（纯 ESM；无原生代码、无联网、不调用模型） |
| 工具模式 | `native` / `ptc` / `both` 均可；批量校验整个目录时建议 `ptc`，schema 成本只付一次 |

## What it does

规则表、字段说明与行为细节见 [README.md](README.md#what-it-does)（英文主版本）。本插件只列出材料与所引条款之间的字面差异，并对无法执行的检查在 `skipped` 中逐项说明。

## Install

```sh
dsh plugin --profile <name> add dsh-drill-script-check
dsh --profile <name> --dump-config | grep 'dsh-drill-script-check'
```

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

## License

[Apache License 2.0](LICENSE) © 2026 dsh-drill-script-check contributors.
