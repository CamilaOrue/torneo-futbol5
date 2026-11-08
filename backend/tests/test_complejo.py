"""
================================================================================
SUITE DE PRUEBAS INTEGRALES: ABM COMPLEJOS (AISLADO)
================================================================================
Descripción:
    Verifica el flujo CRUD completo de Complejos de forma aislada, incluyendo
    búsquedas dinámicas.
================================================================================
"""

import uuid


def test_abm_complejo_solo(client):
    nombre_complejo = f"Complejo Los Pinos {uuid.uuid4().hex[:6]}"
    departamento = "Maldonado"

    # 1. CREATE Complejo (201)
    res_crear = client.post(
        "/complejos",
        json={
            "nombre": nombre_complejo,
            "direccion": "Ruta 39 Km 15",
            "departamento": departamento,
        },
    )
    assert res_crear.status_code == 201
    id_complejo = res_crear.json()["id_complejo"]

    # 2. READ Complejo por ID (200)
    res_get = client.get(f"/complejos/{id_complejo}")
    assert res_get.status_code == 200
    assert res_get.json()["nombre"] == nombre_complejo

    # 3. READ Complejos con Query `q` (200)
    res_list = client.get(f"/complejos?q={departamento}")
    assert res_list.status_code == 200
    # Verifica que el complejo creado esté en los resultados filtrados
    assert any(c["id_complejo"] == id_complejo for c in res_list.json())

    # 4. UPDATE Complejo (200)
    nombre_actualizado = f"{nombre_complejo} Modificado"
    res_update = client.put(
        f"/complejos/{id_complejo}",
        json={
            "nombre": nombre_actualizado,
            "direccion": "Ruta 39 Km 15.5",
            "departamento": departamento,
        },
    )
    assert res_update.status_code == 200
    assert res_update.json()["nombre"] == nombre_actualizado

    # 5. DELETE Complejo (204)
    res_del = client.delete(f"/complejos/{id_complejo}")
    assert res_del.status_code == 204

    # 6. VERIFICAR ELIMINACIÓN (404)
    res_get_del = client.get(f"/complejos/{id_complejo}")
    assert res_get_del.status_code == 404