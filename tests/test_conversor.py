# test_conversor.py
# Suite de pruebas del conversor

import pytest

from conversor import (
    CONVERSIONES,
    celsius_a_fahrenheit,
    convertir,
    fahrenheit_a_celsius,
    kg_a_libras,
    km_a_millas,
    libras_a_kg,
    millas_a_km,
)


def test_celsius_a_fahrenheit_punto_ebullicion():
    # 100 °C es el punto de ebullición del agua: 212 °F
    assert celsius_a_fahrenheit(100) == 212


def test_celsius_a_fahrenheit_punto_congelacion():
    # 0 °C corresponde a 32 °F
    assert celsius_a_fahrenheit(0) == 32


def test_km_a_millas_valor_conocido():
    # 10 km son aproximadamente 6.21 millas
    assert km_a_millas(10) == pytest.approx(6.21371)


def test_convertir_clave_invalida():
    # Una clave inexistente debe producir un KeyError
    with pytest.raises(KeyError):
        convertir(5, "leguas2parsecs")


# --- Pruebas de caracterización agregadas antes de refactorizar ---


def test_celsius_a_fahrenheit_cero_absoluto_es_valido():
    assert celsius_a_fahrenheit(-273.15) == pytest.approx(-459.67)


def test_celsius_a_fahrenheit_bajo_cero_absoluto():
    with pytest.raises(ValueError, match="cero absoluto"):
        celsius_a_fahrenheit(-300)


@pytest.mark.parametrize(("fahrenheit", "celsius"), [(212, 100), (-40, -40)])
def test_fahrenheit_a_celsius_valores_conocidos(fahrenheit, celsius):
    assert fahrenheit_a_celsius(fahrenheit) == pytest.approx(celsius)


def test_fahrenheit_a_celsius_punto_congelacion():
    # Pasa incluso con el bug: (32 - 32) * k == 0 para cualquier k
    assert fahrenheit_a_celsius(32) == 0


def test_fahrenheit_a_celsius_bajo_cero_absoluto():
    with pytest.raises(ValueError, match="cero absoluto"):
        fahrenheit_a_celsius(-500)


def test_millas_a_km_valor_conocido():
    assert millas_a_km(6.21371) == pytest.approx(10)


def test_kg_a_libras_valor_conocido():
    assert kg_a_libras(10) == pytest.approx(22.0462)


def test_libras_a_kg_valor_conocido():
    assert libras_a_kg(22.0462) == pytest.approx(10)


@pytest.mark.parametrize("funcion", [km_a_millas, millas_a_km])
def test_distancia_negativa(funcion):
    with pytest.raises(ValueError, match="distancia no puede ser negativa"):
        funcion(-1)


@pytest.mark.parametrize("funcion", [kg_a_libras, libras_a_kg])
def test_masa_negativa(funcion):
    with pytest.raises(ValueError, match="masa no puede ser negativa"):
        funcion(-1)


@pytest.mark.parametrize("funcion", [km_a_millas, millas_a_km, kg_a_libras, libras_a_kg])
def test_cero_es_valido(funcion):
    assert funcion(0) == 0


def test_claves_registradas():
    assert set(CONVERSIONES) == {"c2f", "f2c", "km2mi", "mi2km", "kg2lb", "lb2kg"}


def test_convertir_redondea_a_cuatro_decimales():
    assert convertir(10, "km2mi") == 6.2137


def test_convertir_clave_invalida_lista_disponibles():
    with pytest.raises(KeyError, match="c2f, f2c, kg2lb, km2mi, lb2kg, mi2km"):
        convertir(5, "xyz")


def test_convertir_propaga_value_error():
    with pytest.raises(ValueError):
        convertir(-1, "kg2lb")
