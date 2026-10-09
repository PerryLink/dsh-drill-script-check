# dsh-drill-script-check — Verificação da completude e da aritmética de um guião de simulacro de emergência

[![DSH Market](https://raw.githubusercontent.com/2BingLing/dsh-market/master/assets/readme/badge-listed-en.svg)](https://dsh.market/)

`dsh-drill-script-check` lê um guião de simulacro de emergência —o cabeçalho do simulacro mais uma linha por etapa— e verifica a completude e a aritmética desse guião: se cada etapa regista a sua fase de simulacro ou o seu conteúdo de guião, se nomeia um responsável de comando, se o nível de resposta vem do vocabulário que configura, se uma etapa com ação de guião enumera os recursos de que necessita, se as durações das etapas somam a duração prevista do simulacro, se um ponto crítico declara a sua condição de julgamento, se não há números de etapa repetidos e se o cabeçalho nomeia o simulacro e a entidade organizadora.

## Como é a saída

![Terminal demo of dsh-drill-script-check: real output over its DR-007 fixture](https://raw.githubusercontent.com/PerryLink/dsh-drill-script-check/main/docs/assets/dsh-drill-script-check-demo.png)

Saída real deste plugin sobre o seu próprio fixture de teste `DR-007` — não é uma simulação. O pacote de regras não inventa citações, por isso cada achado nomeia a cláusula aplicada e avisa que o seu texto não foi obtido.

## O que ele responde

| Você pergunta | O que ele responde |
|---|---|
| Uma etapa não tem preenchidas nem a fase do simulacro nem o conteúdo do guião. Isso é reportado? | Sim. `DR-001` pede em conjunto as colunas `phase` e `script` e reporta a etapa em que nenhuma das duas está preenchida — basta uma delas para passar. Verifica que a coluna está preenchida, não se a ação está correta ou conforme ao seu plano de emergência. |
| Preenchi o nível de resposta, mas `DR-003` reporta-se em `skipped`. Porquê? | `DR-003` compara a coluna `level` com o vocabulário de `values`, que vem vazio, por isso, até configurar os seus próprios níveis, a regra reporta que não pôde ser executada em vez de passar em silêncio. Só verifica que o valor consta da sua lista: nunca julga que nível um evento deveria desencadear. |
| Uma etapa meramente informativa não enumera equipamento. Isso é assinalado? | Não. `DR-004` pede a coluna `resource` apenas quando o conteúdo `script` dessa etapa está preenchido, pelo que a uma etapa informativa não se pedem meios. Verifica que os recursos estão enumerados, não que sejam suficientes ou que correspondam ao que existe no local. |
| As durações das etapas não somam a duração prevista do simulacro. Isso é detetado? | Sim. `DR-005` soma os valores de `durationMin` das etapas e compara esse total com `totalDurationMin`, que toma do cabeçalho do material: procura primeiro dentro da linha e recorre ao cabeçalho. É apenas uma verificação de soma: não julga se a distribuição do tempo é razoável ou suficiente. |
| O que deve conter a coluna de ponto crítico de uma etapa? | `DR-006` exige que a coluna `checkpoint` —o ponto crítico com a sua condição de julgamento— esteja preenchida na etapa. Verifica que algo foi aí escrito, não que a condição seja observável ou adequada. |
| Uma fase reparte-se por três linhas de ação e duas delas levam o mesmo número de etapa. | `DR-007` reporta o `stepNo` repetido, porque a repetição torna pouco fiáveis o total das durações e a contagem das etapas. Repartir uma fase por várias linhas de ação é normal: dê a cada linha o seu próprio número de etapa. |

## Normas que segue

| Documento | Número | Regras que o citam |
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

| Superfície | Estado |
|---|---|
| Harness | Faixa de peers `>=0.1.2-rc.1 <0.2.0 \|\| >=0.2.0-0 <0.3.0` — verificada para aceitar tanto `0.2.0-rc.2` quanto `0.2.1-alpha.1`. **`engines.dsh` não é declarado**: não tem leitor e não pode recusar nenhum host |
| Node | `^22.19.0 || >=24.0.0` |
| Plataformas | Todas (ESM puro; sem código nativo, sem rede, sem chamada ao modelo) |
| Modo de ferramenta | Funciona em `native`, `ptc` e `both`; para um diretório inteiro use `ptc` |

## What it does

A tabela de regras, os campos e o comportamento detalhado estão em [README.md](README.md#what-it-does) (versão principal em inglês). O plugin apenas lista divergências literais frente às cláusulas citadas e indica em `skipped` cada verificação que não pôde ser executada.

## Install

```sh
dsh plugin --profile <name> add dsh-drill-script-check
dsh --profile <name> --dump-config | grep 'dsh-drill-script-check'
```

## Configuration

Todos os parâmetros ajustáveis ficam no esquema Schemastery de `src/config.ts`, portanto mudam pelo `cordis.yml` sem editar código; os limites por regra ficam no pacote de regras sob `rules/`.

| Chave | Tipo | Padrão | Descrição |
|---|---|---|---|
| `rulesFile` | string | `rules/drill-script-check.yaml` | Caminho do pacote de regras, relativo à raiz do pacote |
| `disabledRules` | string[] | `[]` | Ids de regras a desativar; cada uma aparece em `skipped` |
| `onlyRules` | string[] | `[]` | Executar apenas estas regras; vazio executa todas |
| `skipNotes` | string | `""` | Nota acrescentada a cada motivo de `skipped` |
| `timeoutMs` | number | `120000` | Orçamento de tempo limite cooperativo da ferramenta |

## Material format

Aceita JSON ou YAML. O exemplo completo de campos está em [README.md](README.md#material-format) (versão principal em inglês). Os campos são opcionais na camada de leitura e validados pelo motor, de modo que uma exportação parcial gera achados sobre o que falta em vez de falhar.

## Rule sources

Os dados das regras ficam separados do código: cada regra traz documento, número, cláusula na numeração própria da fonte, trecho literal e URL de origem. O carregador impõe que o trecho seja citação real de pelo menos oito caracteres e que uma verificação baseada apenas em princípio geral (`kind: derived-from-principle`, teto `warn`) ou em política local (`kind: institutional-configuration`, teto `info`) nunca seja declarada `error`.

Os limites verificados e as conclusões deliberadamente **não** afirmadas estão em [README.md](README.md#rule-sources) (versão principal em inglês) e em `rules/evidence/`.

## Troubleshooting

- **O plugin instala mas a ferramenta não aparece**: confirme que `main` resolve para `lib/index.mjs` e que `pnpm run build` o gerou.
- **`dsh plugin add` recusa o pacote**: a faixa de peers cobre `0.1.x` e `0.2.x`; fora dela, conceda isenção explícita com `dsh plugin --profile <name> allow-version <pkg@ver> --dsh-version <runtime> --accept-risk`.
- **Uma regra não executou**: leia o arranjo `skipped`.
- **`check` informa `manifest-peers` como falha**: problema conhecido do `dsh-plugin-dev`; o runtime aplica a compatibilidade na instalação.
- **Os horários parecem deslocados**: toda a aritmética é de hora local sobre as cadeias fornecidas.

## Development

```sh
pnpm install
pnpm run typecheck
pnpm test
pnpm run build
node ../scripts/sync-shared.mjs dsh-drill-script-check
```

O último comando copia o kit compartilhado de `../_shared` para `src/shared/`; execute-o novamente após cada alteração compartilhada.

## License

[Apache License 2.0](LICENSE) © 2026 dsh-drill-script-check contributors.
