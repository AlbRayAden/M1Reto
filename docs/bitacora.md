# Bitácora de refactorización

Proyecto: conversor de unidades (`src/conversor.py`, `src/cli.py`).
Herramienta: Claude Code (modelo Claude Opus 5.5), modo agente con permisos automáticos.
Rama de trabajo: `refactor/claude-code`. Cada paso tiene su propio commit y un log
completo de `pytest -v`, `ruff check`, `ruff format --check` (y `mypy` desde R4) en
`docs/evidencia/`.

> **Nota de transparencia.** La sesión arrancó con una sola instrucción de alto nivel
> ("lee los 3 .docx del reto y haz lo que piden"). A partir de ahí Claude Code planeó y
> ejecutó cada paso. Los *prompts* de cada sección son la instrucción concreta que guió
> ese paso, escrita para que el proceso sea **reproducible** paso a paso en una sesión nueva.

## Resumen

| # | Commit | Tipo | Tests | Linter |
|---|--------|------|-------|--------|
| 0 | `316f7de` | Configuración (CLAUDE.md, .claudeignore, `src/`, ruff) | 4 ✅ | ✅ |
| 1 | `bb9868b` | Tests de caracterización | 29 ✅ + 2 xfail | ✅ |
| 2 | `1759996` | **Fix** de bug en `fahrenheit_a_celsius` | 31 ✅ | ✅ |
| R1 | `d43612f` | Extraer funciones (validaciones duplicadas) | 31 ✅ | ✅ |
| R2 | `8d7761b` | Números mágicos → constantes con nombre | 31 ✅ | ✅ |
| R3 | `760ec08` | Tuplas posicionales → `NamedTuple` (nombres claros) | 31 ✅ | ✅ |
| R4 | `17bb15d` | Type hints + `ruff ANN` + `mypy --strict` | 31 ✅ | ✅ |
| R5 | `88873a1` | Manejo de errores (excepción propia, NaN/inf) | 36 ✅ | ✅ |
| R6 | `28c8d05` | Comentarios redundantes → docstrings + `ruff D` | 36 ✅ | ✅ (tras 1 iteración) |
| R7 | `03c5dd9` | Códigos de salida con nombre en la CLI | 37 ✅ | ✅ |

---

## Paso 0 · Exploración y configuración

**Prompt (exploración, modo chat / sólo lectura):**
> Lee `conversor.py`, `cli.py` y `tests/`. Sin modificar nada, lista los code smells que
> encuentres ordenados por impacto, e indica qué funciones no tienen cobertura de tests.

**Code smells identificados:**

| Smell | Dónde | Impacto |
|-------|-------|---------|
| **Bug**: fórmula F→C usa `* 9 / 5` en vez de `* 5 / 9` (212 °F daba 324 °C) | `fahrenheit_a_celsius` | Alto |
| Suite parcial: sólo 2 de 6 conversiones probadas, CLI sin tests | `tests/` | Alto |
| Validación duplicada 6 veces (cero absoluto ×2, negativos ×4) | `conversor.py` | Medio |
| Hack `str(error).strip(chr(39))` para quitar comillas del `KeyError` | `cli.py` | Medio |
| `nan` e `inf` se aceptan y la CLI responde `nan`/`inf` con código 0 | `convertir` | Medio |
| Números mágicos: `9 / 5`, `32`, `4` (decimales), códigos `0/1/2` | ambos | Bajo-medio |
| Registro con tuplas posicionales `(función, descripción)` → `funcion, _ = ...` | `CONVERSIONES` | Bajo |
| Sin type hints | ambos | Bajo |
| Comentarios que repiten el código o el nombre del archivo, en vez de docstrings | ambos | Bajo |

**Prompt (configuración):**
> Crea un `CLAUDE.md` con: estructura del proyecto, comandos de test/lint, convenciones
> (nombres en español, `<origen>_a_<destino>`, sin números mágicos), un flujo obligatorio
> de "una refactorización → tests → linter → commit", y las restricciones de interfaz que
> no se pueden romper (claves de `CONVERSIONES`, redondeo a 4 decimales, `KeyError`,
> códigos de salida). Crea `.claudeignore` para venv, cachés y `__MACOSX`. Mueve el código
> a `src/` y configura pytest y ruff en `pyproject.toml`.

**Cambios:**
- `CLAUDE.md` y `.claudeignore` nuevos. `.claudeignore` excluye `.venv/`, `__pycache__/`,
  cachés de pytest/ruff/mypy, artefactos de build, `__MACOSX/` (basura que venía en el
  `.zip`) y capturas binarias de `docs/evidencia/`.
- `conversor.py` y `cli.py` → `src/`. `conftest.py` (vacío; sólo servía para que pytest
  agregara la raíz al `sys.path`) se sustituye por `pythonpath = ["src"]` en `pyproject.toml`.
- Configuración de ruff con reglas `E, W, F, I, N, UP, B, SIM`. Primer hallazgo del linter:
  imports desordenados en el test original (`I001`), corregido con `ruff check --fix`.

**Resultado:** 4 passed · ruff OK → `evidencia/00-configuracion.txt`

---

## Paso 1 · Tests de caracterización (red de seguridad)

**Prompt:**
> Antes de refactorizar, escribe tests de caracterización para todas las funciones públicas
> de `conversor.py` y para `cli.main` (salida y código de retorno), incluyendo los casos de
> error. Si un test revela un bug, **no lo corrijas**: márcalo con
> `@pytest.mark.xfail(strict=True)` explicando el bug.

**Cambio:** `tests/test_conversor.py` pasa de 4 a 22 casos y se crea `tests/test_cli.py`
(6 casos): valores conocidos, cero absoluto, negativos, redondeo, mensaje de clave inválida,
listado y códigos de salida.

**Hallazgo — bug real:** `fahrenheit_a_celsius(212)` devolvía `324.0`.

**Intento fallido y corrección:** el primer test parametrizado incluía `(32 °F, 0 °C)` con
`xfail(strict=True)`. Falló con *XPASS(strict)*, porque `(32 - 32) * k == 0` para cualquier
`k`: ese caso pasa aunque la fórmula esté mal. Se separó en un test normal y el xfail quedó
sólo con puntos que distinguen la fórmula (212 → 100, -40 → -40). Esto se incorporó como
regla en `CLAUDE.md` (ver Paso 2).

**Justificación:** sin cobertura no hay forma de saber si un refactor rompe algo; la suite
original habría dejado pasar cualquier cambio en 4 de las 6 conversiones.

**Resultado:** 29 passed, 2 xfailed · ruff OK → `evidencia/01-tests-caracterizacion.txt`

---

## Paso 2 · Fix: fórmula Fahrenheit → Celsius

**Prompt:**
> Corrige el bug documentado por el xfail de `fahrenheit_a_celsius` en un commit `fix:`
> separado y quita el marcador xfail. Agrega a `CLAUDE.md` lo aprendido sobre tests de
> caracterización y sobre elegir valores de prueba que distingan la fórmula.

**Cambio:** `(fahrenheit - 32) * 9 / 5` → `(fahrenheit - 32) * 5 / 9`.

**Iteración de `CLAUDE.md`:** se agregaron las reglas 5–7 del flujo de trabajo
(caracterizar antes de tocar código sin cobertura, bugs en commit `fix:` aparte con xfail,
y elegir valores de prueba que no sean "ciegos" a la fórmula).

**Justificación:** se separa del refactor para que el historial distinga "cambio de
comportamiento intencional" de "cambio de estructura sin cambio de comportamiento".

**Resultado:** 31 passed · ruff OK · `python src/cli.py 212 f2c` → `100.0`
→ `evidencia/02-fix-fahrenheit.txt`

---

## R1 · Extraer funciones: validaciones duplicadas

**Prompt:**
> En `conversor.py` la validación de cero absoluto aparece 2 veces y la de "no negativo"
> 4 veces. Extráelas a `_validar_temperatura(celsius)` y `_validar_no_negativo(valor,
> magnitud)`. Los mensajes de error deben quedar **idénticos** (los tests los verifican).
> Sólo este cambio.

**Cambio:** 6 bloques `if ...: raise ValueError(...)` → 2 helpers privados. El mensaje
`"{magnitud} no puede ser negativa"` se arma con `"La distancia"` / `"La masa"`.

**Justificación:** DRY. Si mañana cambia el mensaje o la regla (p. ej. permitir 0), se toca
en un solo lugar. Cada función de conversión queda en 2 líneas: validar y calcular.

**Resultado:** 31 passed · ruff OK → `evidencia/03-R1-extraer-validaciones.txt`

---

## R2 · Números mágicos → constantes con nombre

**Prompt:**
> Reemplaza los números mágicos de `conversor.py` por constantes de módulo en MAYÚSCULAS,
> junto a las existentes: `9 / 5` (factor C→F), `32` (desplazamiento F) y `4` (decimales de
> redondeo en `convertir`). Expresa F→C como la inversa usando las mismas constantes.

**Cambio:** `FACTOR_CELSIUS_A_FAHRENHEIT`, `DESPLAZAMIENTO_FAHRENHEIT`, `DECIMALES_SALIDA`.
F→C queda como `(f - DESPLAZAMIENTO) / FACTOR`, simétrico a C→F; se elimina el comentario
"Redondeamos a 4 decimales" porque la constante ya lo dice.

**Justificación:** el bug del Paso 2 existió justamente porque la fórmula inversa se
escribió "a mano" con literales. Expresarla como inversa de las mismas constantes hace que
ese error sea mucho más difícil de repetir.

**Resultado:** 31 passed · ruff OK → `evidencia/04-R2-constantes.txt`

---

## R3 · Tuplas posicionales → `NamedTuple` (nombres claros)

**Prompt:**
> El registro `CONVERSIONES` usa tuplas `(función, descripción)` y se desempaca con
> `funcion, _ = ...` y `(_, descripcion)`. Cámbialo por un `NamedTuple` `Conversion` con
> campos `funcion` y `descripcion`, y actualiza `convertir` y `listar_conversiones`.

**Cambio:** `class Conversion(NamedTuple)`; `CONVERSIONES[clave].funcion(valor)` y
`conversion.descripcion` en la CLI.

**Justificación:** acceso por nombre en vez de por posición; desaparecen los `_` de
desempaque. Al ser `NamedTuple` sigue siendo una tupla, así que cualquier código externo
que desempacara posicionalmente sigue funcionando.

**Resultado:** 31 passed · ruff OK → `evidencia/05-R3-namedtuple.txt`

---

## R4 · Type hints

**Prompt:**
> Agrega type hints a todas las funciones de `src/` con sintaxis moderna
> (`X | None`, `dict[str, ...]`, `collections.abc`). El campo `funcion` de `Conversion`
> debe ser `Callable[[float], float]`. Activa la regla `ANN` de ruff (sin aplicarla a
> tests) y configura `mypy --strict` sobre `src/`.

**Cambio:** firmas anotadas en todas las funciones de `src/`; `CONVERSIONES: dict[str, Conversion]`;
`main(argv: Sequence[str] | None = None) -> int`. `mypy` agregado a `requirements.txt`
y a los comandos de `CLAUDE.md` (segunda iteración del archivo).

**Justificación:** documenta el contrato de cada función y permite detectar errores sin
ejecutar. Activar `ANN` + `mypy --strict` evita que futuras funciones lleguen sin tipos.

**Resultado:** 31 passed · ruff OK · mypy "no issues found in 2 source files"
→ `evidencia/06-R4-type-hints.txt`

---

## R5 · Mejorar manejo de errores

**Exploración previa (CLI real):**

```
$ python cli.py nan c2f   →  nan      (exit 0)   ← debería ser error
$ python cli.py inf km2mi →  inf      (exit 0)   ← debería ser error
```

**Prompt:**
> Mejora el manejo de errores sin cambiar los mensajes existentes:
> 1) crea `ConversionNoSoportadaError(KeyError)` con atributo `clave` y un `__str__` que no
> agregue comillas, para eliminar el hack `str(error).strip(chr(39))` de la CLI;
> 2) haz que `convertir` rechace valores no finitos (NaN, ±inf) con `ValueError`.
> Escribe primero los tests que fallen (rojo) y luego implementa (verde).

**Cambio:**
- Tests nuevos (rojo primero): NaN/inf/-inf → `ValueError`; mensaje legible y atributo
  `clave` en la excepción; `cli nan c2f` → exit 1 con mensaje.
- `ConversionNoSoportadaError` hereda de `KeyError`, así que el test original
  `pytest.raises(KeyError)` sigue pasando sin tocarlo.
- La CLI captura `(ValueError, ConversionNoSoportadaError)` e imprime `str(error)` directo.

**Justificación:** el hack con `chr(39)` dependía de un detalle de implementación de
`KeyError.__str__` y era críptico. Un tipo de excepción propio es explícito y permite
capturar sólo este error (un `KeyError` accidental por otro bug ya no se mostraría como
"error de usuario"). Aceptar `nan` en silencio producía resultados basura con código de éxito.

**Resultado:** 36 passed · ruff OK · mypy OK → `evidencia/07-R5-manejo-errores.txt`

---

## R6 · Comentarios redundantes → docstrings

**Prompt:**
> Elimina los comentarios obsoletos o redundantes (cabeceras `# conversor.py`, comentarios
> que repiten el nombre de la función) y convierte los útiles en docstrings en español,
> estilo Google. Activa la regla `D` de ruff con `convention = "google"` (no en tests).

**Cambio:** docstrings de módulo, clase y función; `convertir` documenta sus excepciones en
una sección `Raises:`. Se eliminan comentarios como `# Convierte grados Fahrenheit a Celsius`
encima de `fahrenheit_a_celsius`.

**Iteración:** al activar `D`, ruff reportó 2 errores en la clase nueva de R5
(`D107` falta docstring en `__init__`, `D105` en `__str__`). Se agregaron los docstrings,
y el comentario que explicaba el `__str__` pasó a ser su docstring.

**Justificación:** los docstrings aparecen en `help()` y en el IDE; los comentarios no.
Los comentarios que repetían el código sólo agregaban ruido y se desactualizan.

**Resultado:** 36 passed · ruff OK (tras la iteración) · mypy OK
→ `evidencia/08-R6-docstrings.txt`

---

## R7 · Códigos de salida con nombre

**Prompt:**
> En `cli.py` reemplaza los literales de retorno `0`, `1`, `2` por constantes
> `EXITO`, `ERROR_CONVERSION`, `USO_INCORRECTO`. Usa las constantes en los tests y agrega
> un test que fije sus valores, porque son interfaz pública.

**Cambio:** constantes de módulo en `cli.py`; los tests usan los nombres y un test nuevo
`test_codigos_de_salida_estables` asegura que sigan valiendo `0/1/2`.

**Justificación:** `return 2` no dice nada; `return USO_INCORRECTO` sí. El test de valores
evita que alguien "renumere" los códigos y rompa scripts que dependen de ellos.

**Resultado:** 37 passed · ruff OK · mypy OK → `evidencia/09-R7-codigos-salida.txt`

---

## Validación final

```
$ pytest -v          → 37 passed
$ ruff check .       → All checks passed!
$ ruff format --check . → 8 files already formatted
$ mypy               → Success: no issues found in 2 source files
```

Log completo: `evidencia/10-final.txt`.

## Pendientes / fuera de alcance

- `python src/cli.py -inf c2f`: argparse interpreta `-inf` como una opción y responde
  "invalid float value: 'c2f'". Se puede usar `python src/cli.py -- -inf c2f`. No se
  cambió porque implicaría alterar el parseo de argumentos (cambio de comportamiento).
- `fahrenheit_a_celsius` valida el cero absoluto sobre el resultado y `celsius_a_fahrenheit`
  sobre la entrada; ambas son correctas, pero una validación por escala (`-459.67 °F`) sería
  más simétrica.
