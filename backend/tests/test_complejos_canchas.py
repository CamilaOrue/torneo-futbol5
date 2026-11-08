import uuid


def test_abm_complejo_y_cancha(client):
    # Genera un nombre único por ejecución (ej: Complejo Test a1b2c3)
    nombre_complejo_unico = f"Complejo Test {uuid.uuid4().hex[:6]}"

    # 1. CREATE Complejo
    res_comp = client.post(
        "/complejos",
        json={
            "nombre": nombre_complejo_unico,
            "direccion": "Av. Italia 1234",
            "departamento": "Montevideo",
        },
    )
    assert res_comp.status_code == 201
    comp_data = res_comp.json()
    id_complejo = comp_data["id_complejo"]
    assert comp_data["nombre"] == nombre_complejo_unico

    # 2. READ Complejo
    res_get_comp = client.get(f"/complejos/{id_complejo}")
    assert res_get_comp.status_code == 200

# 3. CREATE Cancha (POST /canchas/{id_complejo})
    res_cancha = client.post(
        f"/canchas/{id_complejo}",
        json={
            "nombre_cancha": "Cancha 1",
            "superficie": "sintetico",
            "techada": True,
        },
    )
    assert res_cancha.status_code == 201

    # 4. READ Canchas del complejo
    res_list_canchas = client.get(f"/canchas?id_complejo={id_complejo}")
    assert res_list_canchas.status_code == 200
    assert len(res_list_canchas.json()) >= 1

    # 5. READ Cancha específica
    res_get_cancha = client.get(f"/canchas/{id_complejo}/Cancha 1")
    assert res_get_cancha.status_code == 200

    # 6. UPDATE Cancha
    res_up_cancha = client.put(
        f"/canchas/{id_complejo}/Cancha 1",
        json={
            "nombre_cancha": "Cancha 1",  # <-- Incluido para la validación de CanchaUpdate
            "superficie": "parquet",
            "techada": False,
        },
    )
    assert res_up_cancha.status_code == 200

    # 7. DELETE Cancha y Complejo
    res_del_cancha = client.delete(f"/canchas/{id_complejo}/Cancha 1")
    assert res_del_cancha.status_code == 204

    res_del_comp = client.delete(f"/complejos/{id_complejo}")
    assert res_del_comp.status_code == 204