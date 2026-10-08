# dsh-drill-script-check — Verificación de la completitud y la aritmética de un guion de simulacro de emergencia

`dsh-drill-script-check` lee un guion de simulacro de emergencia —la cabecera del simulacro más una fila por etapa— y comprueba la completitud y la aritmética de ese guion: que cada etapa registre su fase de simulacro o su contenido de guion, que nombre a un responsable de mando, que el nivel de respuesta proceda del vocabulario que usted configure, que una etapa con acción de guion enumere los recursos que necesita, que las duraciones de las etapas sumen la duración prevista del simulacro, que un punto clave declare su condición de juicio, que no se repita ningún número de etapa y que la cabecera nombre el simulacro y la entidad organizadora.

## Qué responde

| Usted pregunta | Qué responde |
|---|---|
| Una etapa no tiene rellenas ni la fase del simulacro ni el contenido del guion. ¿Se informa de ello? | Sí. `DR-001` pide juntas las columnas `phase` y `script` e informa de la etapa en la que ninguna de las dos está rellena: basta con una de ellas para pasar. Comprueba que la columna esté rellena, no si la acción es correcta o concuerda con su plan de emergencia. |
| He rellenado el nivel de respuesta, pero `DR-003` se informa a sí misma en `skipped`. ¿Por qué? | `DR-003` compara la columna `level` con el vocabulario de `values`, que viene vacío, así que hasta que configure sus propios niveles la regla informa de que no pudo ejecutarse en lugar de pasar en silencio. Solo comprueba que el valor figure en su lista: nunca juzga qué nivel debería activar un suceso. |
| Una etapa meramente informativa no enumera equipo. ¿Se señala? | No. `DR-004` pide la columna `resource` solo cuando el contenido `script` de esa etapa está relleno, así que a una etapa informativa no se le piden medios. Comprueba que los recursos estén enumerados, no que sean suficientes o que coincidan con lo realmente disponible. |
| Las duraciones de las etapas no suman la duración prevista del simulacro. ¿Se detecta? | Sí. `DR-005` suma los valores de `durationMin` de las etapas y compara ese total con `totalDurationMin`, que toma de la cabecera del material: busca primero dentro de la fila y recurre a la cabecera. Es solo una comprobación de suma: no juzga si el reparto del tiempo es razonable o suficiente. |
| ¿Qué debe contener la columna de punto clave de una etapa? | `DR-006` exige que la columna `checkpoint` —el punto clave junto con su condición de juicio— esté rellena en la etapa. Comprueba que se haya escrito algo ahí, no que la condición sea observable o adecuada. |
| Una fase se reparte en tres filas de acción y dos de ellas llevan el mismo número de etapa. | `DR-007` informa del `stepNo` repetido, porque la repetición hace poco fiables el total de duraciones y el recuento de etapas. Repartir una fase en varias filas de acción es normal: dé a cada fila su propio número de etapa. |

## Normas que sigue

| Documento | Número | Reglas que lo citan |
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

| Superficie | Estado |
|---|---|
| Harness | Rango de peers `>=0.1.2-rc.1 <0.2.0 \|\| >=0.2.0-0 <0.3.0` — verificado para aceptar tanto `0.2.0-rc.2` como `0.2.1-alpha.1`. **No se declara `engines.dsh`**: no tiene lector y no puede rechazar ningún host |
| Node | `^22.19.0 || >=24.0.0` |
| Plataformas | Todas (ESM puro; sin código nativo, sin red, sin llamada al modelo) |
| Modo de herramienta | Funciona en `native`, `ptc` y `both`; para un directorio completo use `ptc` |

## What it does

La tabla de reglas, los campos y el comportamiento detallado están en [README.md](README.md#what-it-does) (versión principal en inglés). El plugin sólo enumera divergencias literales frente a las cláusulas citadas e indica en `skipped` cada comprobación que no pudo ejecutarse.

## Install

```sh
dsh plugin --profile <name> add dsh-drill-script-check
dsh --profile <name> --dump-config | grep 'dsh-drill-script-check'
```

## Configuration

Todos los parámetros ajustables viven en el esquema Schemastery de `src/config.ts`, por lo que se cambian desde `cordis.yml` sin tocar el código; los umbrales por regla están en el paquete de reglas bajo `rules/`.

| Clave | Tipo | Predeterminado | Descripción |
|---|---|---|---|
| `rulesFile` | string | `rules/drill-script-check.yaml` | Ruta del paquete de reglas, relativa a la raíz del paquete |
| `disabledRules` | string[] | `[]` | Ids de reglas que se dejan de ejecutar; cada una aparece en `skipped` |
| `onlyRules` | string[] | `[]` | Ejecutar solo estas reglas; vacío ejecuta todas |
| `skipNotes` | string | `""` | Nota añadida a cada motivo de `skipped` |
| `timeoutMs` | number | `120000` | Presupuesto de tiempo de espera cooperativo de la herramienta |

## Material format

Acepta JSON o YAML. El ejemplo completo de campos está en [README.md](README.md#material-format) (versión principal en inglés). Los campos son opcionales en la capa de lectura y los valida el motor, de modo que una exportación parcial produce hallazgos sobre lo que falta en lugar de un fallo.

## Rule sources

Los datos de las reglas están separados del código: cada regla lleva documento, número, cláusula en la numeración propia de la fuente, extracto literal y URL de origen. El cargador impone que el extracto sea una cita real de al menos ocho caracteres y que una comprobación basada sólo en un principio general (`kind: derived-from-principle`, tope `warn`) o en una política local (`kind: institutional-configuration`, tope `info`) nunca se declare `error`.

Los límites verificados y las conclusiones deliberadamente **no** afirmadas están en [README.md](README.md#rule-sources) (versión principal en inglés) y en `rules/evidence/`.

## Troubleshooting

- **El plugin se instala pero la herramienta no aparece**: compruebe que `main` resuelve a `lib/index.mjs` y que `pnpm run build` lo generó.
- **`dsh plugin add` rechaza el paquete**: la faixa de peers cubre `0.1.x` y `0.2.x`; fuera de ella, conceda una exención explícita con `dsh plugin --profile <name> allow-version <pkg@ver> --dsh-version <runtime> --accept-risk`.
- **Una regla no se ejecutó**: lea el arreglo `skipped`.
- **`check` informa `manifest-peers` como fallo**: es un problema conocido de `dsh-plugin-dev`; el runtime aplica la compatibilidad al instalar.
- **Los horarios parecen desplazados**: toda la aritmética es de hora local sobre las cadenas entregadas.

## Development

```sh
pnpm install
pnpm run typecheck
pnpm test
pnpm run build
node ../scripts/sync-shared.mjs dsh-drill-script-check
```

El último comando copia el kit compartido de `../_shared` a `src/shared/`; vuelva a ejecutarlo tras cada cambio compartido.

## License

[Apache License 2.0](LICENSE) © 2026 dsh-drill-script-check contributors.
