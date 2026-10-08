# conversor.py
# Módulo principal del conversor de unidades.
# Contiene las funciones de conversión y el registro de conversiones disponibles.

# Factores de conversión (valores de referencia internacionales)
FACTOR_KM_A_MILLAS = 0.621371
FACTOR_KG_A_LIBRAS = 2.20462

# Límite físico inferior para temperaturas en grados Celsius
CERO_ABSOLUTO_C = -273.15


def _validar_temperatura(celsius):
    # Valida que la temperatura sea físicamente posible
    if celsius < CERO_ABSOLUTO_C:
        raise ValueError("Temperatura por debajo del cero absoluto")


def _validar_no_negativo(valor, magnitud):
    # Las distancias y masas negativas no tienen sentido físico
    if valor < 0:
        raise ValueError(f"{magnitud} no puede ser negativa")


def celsius_a_fahrenheit(celsius):
    _validar_temperatura(celsius)
    return celsius * 9 / 5 + 32


def fahrenheit_a_celsius(fahrenheit):
    # Convierte grados Fahrenheit a Celsius
    resultado = (fahrenheit - 32) * 5 / 9
    _validar_temperatura(resultado)
    return resultado


def km_a_millas(km):
    _validar_no_negativo(km, "La distancia")
    return km * FACTOR_KM_A_MILLAS


def millas_a_km(millas):
    _validar_no_negativo(millas, "La distancia")
    return millas / FACTOR_KM_A_MILLAS


def kg_a_libras(kg):
    _validar_no_negativo(kg, "La masa")
    return kg * FACTOR_KG_A_LIBRAS


def libras_a_kg(libras):
    _validar_no_negativo(libras, "La masa")
    return libras / FACTOR_KG_A_LIBRAS


# Registro central: clave de conversión -> (función, descripción)
CONVERSIONES = {
    "c2f": (celsius_a_fahrenheit, "Celsius a Fahrenheit"),
    "f2c": (fahrenheit_a_celsius, "Fahrenheit a Celsius"),
    "km2mi": (km_a_millas, "Kilómetros a millas"),
    "mi2km": (millas_a_km, "Millas a kilómetros"),
    "kg2lb": (kg_a_libras, "Kilogramos a libras"),
    "lb2kg": (libras_a_kg, "Libras a kilogramos"),
}


def convertir(valor, clave):
    # Punto de entrada único para todas las conversiones
    if clave not in CONVERSIONES:
        disponibles = ", ".join(sorted(CONVERSIONES))
        raise KeyError(f"Conversión no soportada: {clave}. Usa una de: {disponibles}")
    funcion, _ = CONVERSIONES[clave]
    # Redondeamos a 4 decimales para una salida consistente
    return round(funcion(valor), 4)
