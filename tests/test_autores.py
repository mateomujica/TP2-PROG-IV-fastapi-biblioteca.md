
# Prueba todos los casos de autores: crear, listar, consultar,
# modificar y eliminar (casos felices y casos de error 404).
def test_crear_autor(cliente):
    """Prueba crear un autor exitosamente (caso feliz, 201)"""
    respuesta = cliente.post("/autores", json={
        "nombre": "Gabriel Garcia Marquez",
        "nacionalidad": "Colombiana"
    })
    assert respuesta.status_code == 201
    datos = respuesta.json()
    assert datos["id"] is not None
    assert datos["nombre"] == "Gabriel Garcia Marquez"
    assert datos["nacionalidad"] == "Colombiana"


def test_listar_autores(cliente):
    """Prueba listar todos los autores guardados"""
    cliente.post("/autores", json={"nombre": "Jorge Luis Borges", "nacionalidad": "Argentina"})
    cliente.post("/autores", json={"nombre": "Julio Cortazar", "nacionalidad": "Argentina"})

    respuesta = cliente.get("/autores")
    assert respuesta.status_code == 200
    datos = respuesta.json()
    assert len(datos) == 2


def test_obtener_autor_por_id(cliente):
    """Prueba consultar un autor por su ID existente"""
    creado = cliente.post("/autores", json={"nombre": "Isabel Allende", "nacionalidad": "Chilena"}).json()

    respuesta = cliente.get(f"/autores/{creado['id']}")
    assert respuesta.status_code == 200
    assert respuesta.json()["nombre"] == "Isabel Allende"


def test_obtener_autor_inexistente_da_404(cliente):
    """Prueba que buscar un autor que no existe da 404 (Regla 7)"""
    respuesta = cliente.get("/autores/9999")
    assert respuesta.status_code == 404
    assert respuesta.json()["detail"] == "Autor no encontrado"


def test_actualizar_autor(cliente):
    """Prueba modificar los datos de un autor"""
    creado = cliente.post("/autores", json={"nombre": "Mario Vargas Llosa", "nacionalidad": "Peruana"}).json()

    respuesta = cliente.put(f"/autores/{creado['id']}", json={
        "nombre": "Mario Vargas Llosa (Nobel)",
        "nacionalidad": "Hispano-peruana"
    })
    assert respuesta.status_code == 200
    assert respuesta.json()["nombre"] == "Mario Vargas Llosa (Nobel)"
    assert respuesta.json()["nacionalidad"] == "Hispano-peruana"


def test_actualizar_autor_inexistente_da_404(cliente):
    """Prueba que actualizar un autor inexistente da 404 (Regla 7)"""
    respuesta = cliente.put("/autores/9999", json={"nombre": "Fantasma"})
    assert respuesta.status_code == 404


def test_eliminar_autor(cliente):
    """Prueba borrar un autor exitosamente"""
    creado = cliente.post("/autores", json={"nombre": "Autor Temporal", "nacionalidad": "Desconocida"}).json()

    respuesta = cliente.delete(f"/autores/{creado['id']}")
    assert respuesta.status_code == 200

    # Comprobamos que ya no exista
    consulta = cliente.get(f"/autores/{creado['id']}")
    assert consulta.status_code == 404


def test_eliminar_autor_inexistente_da_404(cliente):
    """Prueba que borrar un autor que no existe da 404 (Regla 7)"""
    respuesta = cliente.delete("/autores/9999")
    assert respuesta.status_code == 404
