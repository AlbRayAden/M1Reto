# Conversor de unidades

Conversor de unidades de línea de comandos (temperatura, distancia y masa), refactorizado
con Claude Code como parte del reto **M1 · Refactorización asistida por IA**.

| Clave   | Conversión            |
|---------|-----------------------|
| `c2f`   | Celsius a Fahrenheit  |
| `f2c`   | Fahrenheit a Celsius  |
| `km2mi` | Kilómetros a millas   |
| `mi2km` | Millas a kilómetros   |
| `kg2lb` | Kilogramos a libras   |
| `lb2kg` | Libras a kilogramos   |

## Requisitos previos

- Python **3.10 o superior** (probado con 3.14).
- Sin dependencias de runtime: sólo librería estándar.
- Dependencias de desarrollo (en `requirements.txt`): `pytest`, `ruff`, `mypy`.

## Instalación

```bash
git clone <URL-de-tu-fork>
cd <carpeta-del-repo>
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

> Si la ruta de la carpeta contiene `:` (p. ej. "Next-Gen Coding: ..."), `venv` se niega a
> crear `.venv` ahí; créalo fuera (`python -m venv ~/.venvs/conversor`) y actívalo.

## Uso

```bash
python src/cli.py 100 c2f     # 212.0
python src/cli.py 10 km2mi    # 6.2137
python src/cli.py --listar    # tabla de conversiones
```

Códigos de salida: `0` éxito · `1` error de conversión (valor inválido o clave desconocida)
· `2` uso incorrecto (faltan argumentos).

## Tests

```bash
pytest -v
```

## Linter, formato y tipos

```bash
ruff check .            # linter (reglas en pyproject.toml)
ruff format --check .   # formato
mypy                    # verificación de tipos en modo strict sobre src/
```

## Estructura

```
├── CLAUDE.md            # Instrucciones para Claude Code
├── .claudeignore        # Archivos que Claude Code no debe leer
├── README.md
├── pyproject.toml       # Configuración de pytest, ruff y mypy
├── requirements.txt
├── src/
│   ├── conversor.py     # Lógica de conversión y registro CONVERSIONES
│   └── cli.py           # Interfaz de línea de comandos
├── tests/
│   ├── test_conversor.py
│   └── test_cli.py
└── docs/
    ├── bitacora.md      # Registro de cada refactorización
    ├── reflexion.md     # Aprendizajes y conclusiones
    └── evidencia/       # Logs de pytest/ruff/mypy después de cada paso
```
