# Reflexión final

## Qué técnicas de prompting funcionaron mejor

**1. Pedir exploración antes que cambios.** El primer prompt fue explícitamente de sólo
lectura ("lista los code smells ordenados por impacto e indica qué no tiene cobertura").
Eso produjo un inventario que después se convirtió en el plan de refactorización, y fue lo
que reveló que la suite sólo cubría 2 de 6 conversiones. Si hubiera pedido directamente
"refactoriza este código", el bug de `fahrenheit_a_celsius` probablemente habría
sobrevivido dentro de un refactor que "no rompe tests".

**2. Un cambio por prompt, con alcance cerrado.** Los prompts que mejor funcionaron
terminaban con restricciones del tipo "sólo este cambio" o "los mensajes deben quedar
idénticos". Mantener cada paso pequeño hizo que cada diff fuera fácil de revisar y que,
si un test fallaba, la causa fuera obvia.

**3. Poner las restricciones en `CLAUDE.md` en vez de repetirlas.** Las reglas de interfaz
pública (claves, redondeo, `KeyError`, códigos de salida) y el flujo "cambio → tests →
linter → commit" quedaron escritas una sola vez. Los prompts individuales pudieron ser
cortos porque el contexto ya estaba ahí.

**4. Test primero cuando el cambio altera comportamiento.** En R5 pedí "escribe primero
los tests que fallen y luego implementa". Ver el rojo antes del verde confirma que el test
realmente prueba algo.

**5. Convertir las reglas en herramientas.** Activar `ruff ANN`, `ruff D` y `mypy --strict`
justo en el paso que introducía tipos o docstrings convierte una convención en algo que se
verifica solo. En R6 el linter encontró dos docstrings faltantes en una clase creada un
paso antes — algo que una revisión a ojo había pasado por alto.

## Qué no funcionó o ajustaría

- **Mi primer test del bug era "ciego".** Usé `32 °F → 0 °C` como caso de prueba y el
  `xfail(strict=True)` falló porque ese punto da 0 con cualquier fórmula. Aprendizaje:
  la IA (y yo) tiende a elegir los valores "famosos"; hay que pedir explícitamente valores
  que distingan la fórmula. Lo agregué como regla a `CLAUDE.md`.
- **`CLAUDE.md` no nació completo.** Lo iteré dos veces: tras el bug (reglas de
  caracterización) y tras agregar `mypy`. Para el siguiente proyecto empezaría con una
  sección "cómo escribir tests" desde el inicio.
- **Rango de un "refactor".** Rechazar `NaN`/`inf` (R5) técnicamente cambia
  comportamiento. Lo mantuve porque el comportamiento anterior era incorrecto (resultado
  basura con código de éxito), pero en un proyecto real lo separaría como `fix:`.
- **El problema de `-inf` en argparse** quedó documentado pero sin resolver: arreglarlo
  implicaba cambiar el parseo de la CLI, que estaba fuera del objetivo.

## Qué aprendí

- La IA es muy buena aplicando refactorizaciones mecánicas (extraer, renombrar, anotar
  tipos) cuando el alcance está bien delimitado; el valor humano está en **decidir qué
  cambiar y en qué orden**, y en revisar cada diff.
- "Los tests pasan" sólo significa algo si los tests cubren el código. El paso más
  valioso del reto no fue ninguna de las 7 refactorizaciones, sino los tests de
  caracterización que las hicieron seguras.
- Separar `fix:` de `refactor:` en el historial hace que el PR se lea solo: quien revisa
  sabe exactamente qué commits deberían ser neutrales en comportamiento.
- Un commit por paso con su log de evidencia hace el proceso auditable y fácil de
  revertir si algo sale mal.
