"""
================================================================================
SUITE DE PRUEBAS INTEGRALES: ABM COMPLEJOS Y CANCHAS (FLUJO Y CASOS BORDE)
================================================================================
Descripción:
    Este archivo contiene pruebas de integración automatizadas para verificar
    el funcionamiento correcto de los servicios y endpoints de Complejos y Canchas.

Casos evaluados:
    1. Flujo ABM Completo:
       - Creación, lectura, actualización y eliminación exitosa de Complejo y Cancha.
    2. Validaciones de Conflicto (409 Conflict):
       - Intento de crear un complejo con un nombre duplicado.
    3. Validaciones de Elemento No Encontrado (404 Not Found):
       - Consulta y eliminación de complejos/canchas inexistentes.
       - Intento de crear una cancha en un complejo que no existe.
    4. Validaciones de Entrada / Tipos (422 Unprocessable Entity):
       - Intento de crear un complejo omitiendo campos obligatorios (dirección/departamento).
================================================================================
"""

import uuid


def test_abm_complejo_y_cancha_casos_borde(client_integracion):
    # Generamos identificadores únicos para la ejecución
    nombre_complejo_valido = f"Complejo Norte {uuid.uuid4().hex[:6]}"
    nombre_cancha_valida = "Cancha Sintética A"

    # =========================================================================
    # 1. CASOS DE ERROR AL CREAR COMPLEJO (422 y 409)
    # =========================================================================

    # 1.1 Validar 422 si faltan datos requeridos (ej: sin dirección ni departamento)
    res_invalido = client_integracion.post("/complejos", json={"nombre": nombre_complejo_valido})
    assert res_invalido.status_code == 422

    # 1.2 Crear un Complejo válido exitosamente (201)
    res_comp = client_integracion.post(
        "/complejos",
        json={
            "nombre": nombre_complejo_valido,
            "direccion": "Av. Bolivia 5678",
            "departamento": "Montevideo",
        },
    )
    assert res_comp.status_code == 201
    id_complejo = res_comp.json()["id_complejo"]

    # 1.3 Validar 409 Conflict intentando duplicar el nombre del complejo
    res_duplicado = client_integracion.post(
        "/complejos",
        json={
            "nombre": nombre_complejo_valido,
            "direccion": "Otra dirección 999",
            "departamento": "Canelones",
        },
    )
    assert res_duplicado.status_code == 409

    # =========================================================================
    # 2. CASOS DE ERROR AL CREAR CANCHA (404)
    # =========================================================================

    # 2.1 Intento de crear una cancha en un id_complejo que NO existe (debe ser 404)
    res_cancha_huerfana = client_integracion.post(
        "/canchas/999999",
        json={
            "nombre_cancha": "Cancha Fantasma",
            "superficie": "sintetico",
            "techada": True,
        },
    )
    assert res_cancha_huerfana.status_code == 404

    # 2.2 Crear Cancha válida en el complejo real (201)
    res_cancha = client_integracion.post(
        f"/canchas/{id_complejo}",
        json={
            "nombre_cancha": nombre_cancha_valida,
            "superficie": "sintetico",
            "techada": True,
        },
    )
    assert res_cancha.status_code == 201

    # =========================================================================
    # 3. VERIFICACIÓN Y LECTURA (GET)
    # =========================================================================

    # 3.1 Consultar cancha existente (200)
    res_get_cancha = client_integracion.get(f"/canchas/{id_complejo}/{nombre_cancha_valida}")
    assert res_get_cancha.status_code == 200
    assert res_get_cancha.json()["nombre_cancha"] == nombre_cancha_valida

    # 3.2 Consultar cancha inexistente en complejo real (404)
    res_get_inexistente = client_integracion.get(f"/canchas/{id_complejo}/CanchaInexistente")
    assert res_get_inexistente.status_code == 404

    # =========================================================================
    # 4. ACTUALIZACIÓN (PUT)
    # =========================================================================

    # 4.1 Actualizar la cancha existente (200)
    res_up = client_integracion.put(
        f"/canchas/{id_complejo}/{nombre_cancha_valida}",
        json={
            "nombre_cancha": nombre_cancha_valida,
            "superficie": "parquet",
            "techada": False,
        },
    )
    assert res_up.status_code == 200
    assert res_up.json()["superficie"] == "parquet"
    assert res_up.json()["techada"] is False

    # =========================================================================
    # 5. LIMPIEZA Y ELIMINACIÓN (DELETE)
    # =========================================================================

    # 5.1 Eliminar la cancha creada (204)
    res_del_cancha = client_integracion.delete(
        f"/canchas/{id_complejo}/{nombre_cancha_valida}"
    )
    assert res_del_cancha.status_code == 204

    # 5.2 Verificar que intentar eliminarla nuevamente da 404
    res_del_rePETIDO = client_integracion.delete(
        f"/canchas/{id_complejo}/{nombre_cancha_valida}"
    )
    assert res_del_rePETIDO.status_code == 404

    # 5.3 Eliminar el complejo (204)
    res_del_comp = client_integracion.delete(f"/complejos/{id_complejo}")
    assert res_del_comp.status_code == 204

    # 5.4 Verificar que el complejo ya no existe (404)
    res_get_comp_del = client_integracion.get(f"/complejos/{id_complejo}")
    assert res_get_comp_del.status_code == 404