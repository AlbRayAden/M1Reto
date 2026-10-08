# test_cli.py
# Pruebas de la interfaz de línea de comandos

from cli import ERROR_CONVERSION, EXITO, USO_INCORRECTO, main


def test_conversion_exitosa(capsys):
    assert main(["100", "c2f"]) == EXITO
    assert capsys.readouterr().out.strip() == "212.0"


def test_listar(capsys):
    assert main(["--listar"]) == EXITO
    salida = capsys.readouterr().out
    assert salida.startswith("Conversiones disponibles:")
    assert "  km2mi    Kilómetros a millas" in salida


def test_sin_argumentos_es_uso_incorrecto(capsys):
    assert main([]) == USO_INCORRECTO
    assert "se requieren VALOR y CLAVE" in capsys.readouterr().err


def test_falta_clave_es_uso_incorrecto():
    assert main(["5"]) == USO_INCORRECTO


def test_clave_invalida_muestra_error_sin_comillas(capsys):
    assert main(["5", "xyz"]) == ERROR_CONVERSION
    error = capsys.readouterr().err.strip()
    assert error.startswith("Error: Conversión no soportada: xyz.")
    assert "'" not in error


def test_valor_invalido_muestra_error(capsys):
    assert main(["-5", "km2mi"]) == ERROR_CONVERSION
    assert capsys.readouterr().err.strip() == "Error: La distancia no puede ser negativa"


def test_valor_no_finito_es_error(capsys):
    assert main(["nan", "c2f"]) == ERROR_CONVERSION
    assert capsys.readouterr().err.strip() == "Error: El valor debe ser un número finito"


def test_codigos_de_salida_estables():
    # Son parte de la interfaz pública (scripts que llaman a la CLI)
    assert (EXITO, ERROR_CONVERSION, USO_INCORRECTO) == (0, 1, 2)
