/**
 * dsh-drill-script-check — table shape and material contract.
 *
 * The plugin is data-only: this file declares which columns the material may use
 * and how they map onto canonical field names; the shared kit supplies the reader
 * and the check engine, and the rule pack declares every check. Adding a check
 * that fits an existing kind is a rule-pack edit, not a code change.
 */

import { canonicaliseRow, parseTable, type TableSpec } from './shared/table.ts'
import { runTableCheck, type TableCheckOptions, type TableInput } from './shared/rows.ts'
import type { Ruleset } from './shared/rules.ts'

/** Tool id exposed to the model, and the row id in `cordis.patch.yml`. */
export const TOOL_NAME = 'drill_script_check'

/** The register's column aliases, declared once so both the spec and the guard see them. */
const COLUMNS = {
  stepNo: ['序号', '环节序号', '步骤序号', 'stepNo'],
  phase: ['演练阶段', '阶段', '环节', 'phase'],
  script: ['脚本内容', '演练内容', '处置动作', 'script'],
  commander: ['指挥人', '指挥', '负责指挥', 'commander'],
  actor: ['参演人员', '执行人', '责任人', 'actor'],
  resource: ['所需资源', '物资装备', '救援器材', 'resource'],
  startedAt: ['开始时间', '起始时间', 'startedAt'],
  durationMin: ['计划时长', '时长', '历时', 'durationMin'],
  reportTo: ['报告对象', '上报对象', '报告单位', 'reportTo'],
  level: ['响应级别', '响应等级', '级别', 'level'],
  checkpoint: ['关键节点', '判定条件', '节点', 'checkpoint'],
  note: ['备注', '说明', 'note', 'remark'],
} as const

/** How the material declares its table. */
export const SPEC: TableSpec = {
  rowKeys: ['rows', 'items', 'steps', '环节'],
  columns: COLUMNS,
  header: {
  drillName: ['drillName', '演练名称', '演练主题'],
  drillType: ['drillType', '演练类型', '演练形式'],
  organizer: ['organizer', '组织单位', '主办单位'],
  plannedAt: ['plannedAt', '计划日期', '演练日期'],
  venue: ['venue', '演练地点', '地点'],
  participants: ['participants', '参演单位', '参演人数'],
  checkedAt: ['checkedAt', '核对日期'],
  },
}

/** Fields the material must carry somewhere for the reader to accept it. */
export const REQUIRE_ANY_OF = [
  '脚本内容',
  'script',
  '演练阶段',
  'phase',
  '指挥人',
  'commander',
  '响应级别',
  'level',
]

/**
 * Parse the material and attach its canonical field names.
 * @param source - JSON or YAML text.
 * @param target - description of where the material came from.
 * @returns the normalized table, with each row's aliases resolved to field names.
 */
export function parseMaterial(source: string, target: string): TableInput {
  const table = parseTable(source, target, {
    ...SPEC,
    ...(REQUIRE_ANY_OF === undefined ? {} : { requireAnyOf: REQUIRE_ANY_OF }),
  })
  for (const row of table.rows) canonicaliseRow(row, SPEC)
  return table
}

/**
 * Run the rule pack against the material.
 * @param input - normalized table.
 * @param ruleset - validated rule pack.
 * @param options - plugin identity, clock value, rule selection and overrides.
 * @returns the report.
 */
export function runCheck(input: TableInput, ruleset: Ruleset, options: TableCheckOptions) {
  return runTableCheck(input, ruleset, options)
}

export type { TableCheckOptions, TableInput }
