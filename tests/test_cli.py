# test_cli.py
# Pruebas de la interfaz de línea de comandos

from cli import main


def test_conversion_exitosa(capsys):
    assert main(["100", "c2f"]) == 0
    assert capsys.readouterr().out.strip() == "212.0"


def test_listar(capsys):
    assert main(["--listar"]) == 0
    salida = capsys.readouterr().out
    assert salida.startswith("Conversiones disponibles:")
    assert "  km2mi    Kilómetros a millas" in salida


def test_sin_argumentos_es_uso_incorrecto(capsys):
    assert main([]) == 2
    assert "se requieren VALOR y CLAVE" in capsys.readouterr().err


def test_falta_clave_es_uso_incorrecto():
    assert main(["5"]) == 2


def test_clave_invalida_muestra_error_sin_comillas(capsys):
    assert main(["5", "xyz"]) == 1
    error = capsys.readouterr().err.strip()
    assert error.startswith("Error: Conversión no soportada: xyz.")
    assert "'" not in error


def test_valor_invalido_muestra_error(capsys):
    assert main(["-5", "km2mi"]) == 1
    assert capsys.readouterr().err.strip() == "Error: La distancia no puede ser negativa"
