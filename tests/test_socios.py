# Prueba los socios: CRUD, validacion de email duplicado (Regla 8, 409)
# y errores de no encontrado (Regla 7, 404).
def test_crear_socio_exitoso(cliente):
    """Prueba registrar un nuevo socio correctamente (caso feliz, 201)"""
    respuesta = cliente.post("/socios", json={
        "nombre": "Juan Perez",
        "email": "juan@email.com",
        "activo": True
    })
    assert respuesta.status_code == 201
    datos = respuesta.json()
    assert datos["id"] is not None
    assert datos["nombre"] == "Juan Perez"
    assert datos["email"] == "juan@email.com"
    assert datos["activo"] is True


def test_crear_socio_email_duplicado_da_409(cliente):
    """Prueba que registrar dos socios con el mismo correo da 409 (Regla 8)"""
    cliente.post("/socios", json={"nombre": "Ana Gomez", "email": "ana@email.com"})

    # Intento de registrar a otra persona con el mismo email
    duplicado = cliente.post("/socios", json={"nombre": "Ana Clon", "email": "ana@email.com"})
    assert duplicado.status_code == 409
    assert duplicado.json()["detail"] == "Ya existe un socio con ese email"


def test_listar_socios(cliente):
    """Prueba listar todos los socios"""
    cliente.post("/socios", json={"nombre": "Socio 1", "email": "s1@email.com"})
    cliente.post("/socios", json={"nombre": "Socio 2", "email": "s2@email.com"})

    respuesta = cliente.get("/socios")
    assert respuesta.status_code == 200
    assert len(respuesta.json()) == 2


def test_obtener_socio_por_id_y_no_existente(cliente):
    """Prueba buscar socio por ID y error 404 si no existe (Regla 7)"""
    creado = cliente.post("/socios", json={"nombre": "Carlos", "email": "carlos@email.com"}).json()

    ok = cliente.get(f"/socios/{creado['id']}")
    assert ok.status_code == 200
    assert ok.json()["nombre"] == "Carlos"

    fallo = cliente.get("/socios/9999")
    assert fallo.status_code == 404
    assert fallo.json()["detail"] == "Socio no encontrado"


def test_actualizar_socio_y_validaciones(cliente):
    """Prueba modificar socio y validar que no use el email de otro (Regla 8)"""
    s1 = cliente.post("/socios", json={"nombre": "S1", "email": "s1@test.com"}).json()
    cliente.post("/socios", json={"nombre": "S2", "email": "s2@test.com"}).json()

    # Actualizacion valida
    editado = cliente.put(f"/socios/{s1['id']}", json={"nombre": "S1 Modificado", "activo": False})
    assert editado.status_code == 200
    assert editado.json()["nombre"] == "S1 Modificado"
    assert editado.json()["activo"] is False

    # Intento de usar el email de s2 (Regla 8: 409)
    conflicto = cliente.put(f"/socios/{s1['id']}", json={"email": "s2@test.com"})
    assert conflicto.status_code == 409

    # Modificar socio inexistente (Regla 7: 404)
    assert cliente.put("/socios/9999", json={"nombre": "Fantasma"}).status_code == 404


def test_eliminar_socio(cliente):
    """Prueba borrar un socio y error al borrar uno inexistente (Regla 7: 404)"""
    creado = cliente.post("/socios", json={"nombre": "Para Borrar", "email": "borrar@test.com"}).json()

    borrar = cliente.delete(f"/socios/{creado['id']}")
    assert borrar.status_code == 200

    # Ya no existe
    assert cliente.get(f"/socios/{creado['id']}").status_code == 404

    # Borrar inexistente
    assert cliente.delete("/socios/9999").status_code == 404
