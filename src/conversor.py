"""Funciones de conversión de unidades y registro de conversiones disponibles."""

import math
from collections.abc import Callable
from typing import NamedTuple

# Factores de conversión (valores de referencia internacionales)
FACTOR_KM_A_MILLAS = 0.621371
FACTOR_KG_A_LIBRAS = 2.20462
FACTOR_CELSIUS_A_FAHRENHEIT = 9 / 5
DESPLAZAMIENTO_FAHRENHEIT = 32

# Límite físico inferior para temperaturas en grados Celsius
CERO_ABSOLUTO_C = -273.15

# Decimales con los que convertir() redondea para una salida consistente
DECIMALES_SALIDA = 4


class ConversionNoSoportadaError(KeyError):
    """Se lanza cuando la clave de conversión no existe en CONVERSIONES.

    Hereda de KeyError para mantener compatibilidad con código que ya la capturaba así.
    """

    def __init__(self, clave: str, disponibles: list[str]) -> None:
        """Guarda la clave inválida y arma el mensaje con las claves disponibles."""
        super().__init__(clave)
        self.clave = clave
        self.mensaje = f"Conversión no soportada: {clave}. Usa una de: {', '.join(disponibles)}"

    def __str__(self) -> str:
        """Devuelve el mensaje sin las comillas que agrega KeyError.__str__."""
        return self.mensaje


def _validar_temperatura(celsius: float) -> None:
    """Lanza ValueError si la temperatura está por debajo del cero absoluto."""
    if celsius < CERO_ABSOLUTO_C:
        raise ValueError("Temperatura por debajo del cero absoluto")


def _validar_no_negativo(valor: float, magnitud: str) -> None:
    """Lanza ValueError si una magnitud física (distancia, masa) es negativa."""
    if valor < 0:
        raise ValueError(f"{magnitud} no puede ser negativa")


def celsius_a_fahrenheit(celsius: float) -> float:
    """Convierte grados Celsius a Fahrenheit."""
    _validar_temperatura(celsius)
    return celsius * FACTOR_CELSIUS_A_FAHRENHEIT + DESPLAZAMIENTO_FAHRENHEIT


def fahrenheit_a_celsius(fahrenheit: float) -> float:
    """Convierte grados Fahrenheit a Celsius."""
    resultado = (fahrenheit - DESPLAZAMIENTO_FAHRENHEIT) / FACTOR_CELSIUS_A_FAHRENHEIT
    _validar_temperatura(resultado)
    return resultado


def km_a_millas(km: float) -> float:
    """Convierte kilómetros a millas."""
    _validar_no_negativo(km, "La distancia")
    return km * FACTOR_KM_A_MILLAS


def millas_a_km(millas: float) -> float:
    """Convierte millas a kilómetros."""
    _validar_no_negativo(millas, "La distancia")
    return millas / FACTOR_KM_A_MILLAS


def kg_a_libras(kg: float) -> float:
    """Convierte kilogramos a libras."""
    _validar_no_negativo(kg, "La masa")
    return kg * FACTOR_KG_A_LIBRAS


def libras_a_kg(libras: float) -> float:
    """Convierte libras a kilogramos."""
    _validar_no_negativo(libras, "La masa")
    return libras / FACTOR_KG_A_LIBRAS


class Conversion(NamedTuple):
    """Entrada del registro: función de conversión y su descripción legible."""

    funcion: Callable[[float], float]
    descripcion: str


# Registro central: clave de conversión -> Conversion
CONVERSIONES: dict[str, Conversion] = {
    "c2f": Conversion(celsius_a_fahrenheit, "Celsius a Fahrenheit"),
    "f2c": Conversion(fahrenheit_a_celsius, "Fahrenheit a Celsius"),
    "km2mi": Conversion(km_a_millas, "Kilómetros a millas"),
    "mi2km": Conversion(millas_a_km, "Millas a kilómetros"),
    "kg2lb": Conversion(kg_a_libras, "Kilogramos a libras"),
    "lb2kg": Conversion(libras_a_kg, "Libras a kilogramos"),
}


def convertir(valor: float, clave: str) -> float:
    """Convierte `valor` según `clave` y redondea a DECIMALES_SALIDA decimales.

    Raises:
        ConversionNoSoportadaError: si `clave` no está en CONVERSIONES.
        ValueError: si `valor` no es finito o no es físicamente válido.
    """
    if clave not in CONVERSIONES:
        raise ConversionNoSoportadaError(clave, sorted(CONVERSIONES))
    if not math.isfinite(valor):
        raise ValueError("El valor debe ser un número finito")
    return round(CONVERSIONES[clave].funcion(valor), DECIMALES_SALIDA)
