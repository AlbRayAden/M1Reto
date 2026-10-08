# CLAUDE.md — Conversor de unidades

Proyecto del reto M1 "Refactorización asistida por IA". Es un conversor de unidades
(temperatura, distancia, masa) con una CLI. El objetivo es **mejorar la calidad del
código sin cambiar su comportamiento observable**.

## Estructura

```
src/conversor.py   # Funciones de conversión + registro CONVERSIONES + convertir()
src/cli.py         # CLI con argparse: `python src/cli.py VALOR CLAVE` | `--listar`
tests/             # Suite pytest (src/ se agrega al path vía pyproject.toml)
docs/bitacora.md   # Registro de cada refactorización (prompt, cambio, justificación, tests)
docs/reflexion.md  # Aprendizajes
```

`cli.py` importa `conversor` como módulo plano (`from conversor import ...`); no hay
paquete instalable. No conviertas `src/` en paquete sin que se pida explícitamente.

## Comandos

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pytest -v                 # tests
ruff check .              # linter (config en pyproject.toml)
ruff format --check .     # formato
python src/cli.py 100 c2f # prueba manual
```

## Flujo de trabajo obligatorio

1. **Una refactorización a la vez.** No mezcles tipos de cambio en un mismo paso.
2. Después de cada cambio corre `pytest -v` **y** `ruff check .`. Si algo falla, corrígelo
   antes de seguir; nunca desactives ni borres un test para que pase.
3. Un commit por refactorización, con prefijo convencional (`refactor:`, `test:`, `fix:`,
   `docs:`, `chore:`).
4. Registra el paso en `docs/bitacora.md` (prompt, cambio, justificación, resultado de tests).

## Convenciones de código

- Python ≥ 3.10, PEP 8, líneas de máximo 100 caracteres (lo valida ruff).
- **Nombres en español**, en `snake_case` para funciones/variables y `MAYUSCULAS` para
  constantes (`km_a_millas`, `FACTOR_KM_A_MILLAS`). Clases en `PascalCase`.
- Funciones de conversión con el patrón `<origen>_a_<destino>`.
- Sin números mágicos: los factores y límites físicos van como constantes de módulo.
- Docstrings en español (una línea si basta) en lugar de comentarios que repiten el código.
- Type hints en todas las funciones públicas (sintaxis moderna: `X | None`, `dict[str, ...]`).

Ejemplo del estilo esperado:

```python
def km_a_millas(km: float) -> float:
    """Convierte kilómetros a millas."""
    _validar_no_negativo(km, "La distancia")
    return km * FACTOR_KM_A_MILLAS
```

## Restricciones (no romper)

- Las claves de `CONVERSIONES` (`c2f`, `f2c`, `km2mi`, `mi2km`, `kg2lb`, `lb2kg`) y su salida
  en `--listar` son la interfaz pública: no se renombran.
- `convertir()` redondea a 4 decimales y lanza `KeyError` (o subclase) ante una clave
  desconocida; los tests dependen de ello.
- Valores inválidos (bajo el cero absoluto, distancias/masas negativas) lanzan `ValueError`.
- Códigos de salida de la CLI: `0` éxito, `1` error de conversión, `2` uso incorrecto.
- No agregues dependencias de runtime; sólo librería estándar.
