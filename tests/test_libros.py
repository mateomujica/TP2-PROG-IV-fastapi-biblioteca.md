# Prueba los libros: CRUD, filtro de disponibles, asociacion
# con autores (relacion N a N), errores 404 y regla 8 (ISBN duplicado 409).
def test_crear_libro_exitoso(cliente):
    """Prueba crear un libro correctamente (caso feliz, 201)"""
    respuesta = cliente.post("/libros", json={
        "titulo": "Cien Anos de Soledad",
        "isbn": "978-0307474728",
        "stock": 5,
        "anio": 1967
    })
    assert respuesta.status_code == 201
    datos = respuesta.json()
    assert datos["id"] is not None
    assert datos["titulo"] == "Cien Anos de Soledad"
    assert datos["stock"] == 5
    assert datos["autores"] == []


def test_crear_libro_isbn_duplicado_da_409(cliente):
    """Prueba que no se permite crear dos libros con el mismo ISBN (Regla 8, 409)"""
    cliente.post("/libros", json={
        "titulo": "Libro Original",
        "isbn": "111-222-333",
        "stock": 3,
        "anio": 2020
    })

    # Intentamos crear otro libro con el mismo ISBN
    respuesta_duplicada = cliente.post("/libros", json={
        "titulo": "Libro Copia",
        "isbn": "111-222-333",
        "stock": 2,
        "anio": 2021
    })
    assert respuesta_duplicada.status_code == 409
    assert respuesta_duplicada.json()["detail"] == "Ya existe un libro con ese ISBN"


def test_listar_libros_y_filtro_disponibles(cliente):
    """Prueba listar todos los libros y el filtro ?disponibles=true (stock > 0)"""
    # Libro con stock disponible
    cliente.post("/libros", json={"titulo": "Con Stock", "isbn": "AAA-1", "stock": 4, "anio": 2020})
    # Libro sin stock
    cliente.post("/libros", json={"titulo": "Agotado", "isbn": "AAA-2", "stock": 0, "anio": 2020})

    # 1. Consulta general: debe traer ambos libros
    todos = cliente.get("/libros").json()
    assert len(todos) == 2

    # 2. Consulta con filtro disponibles=true: solo debe traer el que tiene stock > 0
    disponibles = cliente.get("/libros?disponibles=true").json()
    assert len(disponibles) == 1
    assert disponibles[0]["titulo"] == "Con Stock"
    assert disponibles[0]["stock"] == 4


def test_obtener_libro_por_id_y_no_existente(cliente):
    """Prueba buscar libro por ID y que un ID inexistente devuelva 404 (Regla 7)"""
    creado = cliente.post("/libros", json={"titulo": "Rayuela", "isbn": "RAY-001", "stock": 2, "anio": 1963}).json()

    ok = cliente.get(f"/libros/{creado['id']}")
    assert ok.status_code == 200
    assert ok.json()["titulo"] == "Rayuela"

    fallo = cliente.get("/libros/9999")
    assert fallo.status_code == 404
    assert fallo.json()["detail"] == "Libro no encontrado"


def test_actualizar_libro_y_validaciones(cliente):
    """Prueba actualizar libro y que falle si se repite ISBN o stock negativo"""
    l1 = cliente.post("/libros", json={"titulo": "Libro 1", "isbn": "ISBN-1", "stock": 2, "anio": 2000}).json()
    cliente.post("/libros", json={"titulo": "Libro 2", "isbn": "ISBN-2", "stock": 2, "anio": 2000}).json()

    # Modificacion exitosa
    editado = cliente.put(f"/libros/{l1['id']}", json={"titulo": "Libro 1 Modificado", "stock": 10, "anio": 2025})
    assert editado.status_code == 200
    assert editado.json()["titulo"] == "Libro 1 Modificado"
    assert editado.json()["stock"] == 10
    assert editado.json()["anio"] == 2025

    # Intento de cambiar el ISBN al de Libro 2 (Regla 8: 409)
    conflicto = cliente.put(f"/libros/{l1['id']}", json={"isbn": "ISBN-2"})
    assert conflicto.status_code == 409

    # Intento de poner stock negativo (400)
    stock_invalido = cliente.put(f"/libros/{l1['id']}", json={"stock": -5})
    assert stock_invalido.status_code == 400

    # Libro inexistente (Regla 7: 404)
    inexistente = cliente.put("/libros/9999", json={"titulo": "Nada"})
    assert inexistente.status_code == 404


def test_eliminar_libro(cliente):
    """Prueba eliminar un libro con autor asociado y error al borrar inexistente"""
    autor = cliente.post("/autores", json={"nombre": "Autor Borrar", "nacionalidad": "Argentina"}).json()
    creado = cliente.post("/libros", json={"titulo": "A Borrar", "isbn": "BORR-1", "stock": 1, "anio": 2022}).json()
    # Le asociamos el autor para comprobar que limpia las relaciones
    cliente.post(f"/libros/{creado['id']}/autores/{autor['id']}")

    # Borrado exitoso
    borrar = cliente.delete(f"/libros/{creado['id']}")
    assert borrar.status_code == 200

    # Ya no existe
    assert cliente.get(f"/libros/{creado['id']}").status_code == 404

    # Borrar inexistente da 404
    assert cliente.delete("/libros/9999").status_code == 404


def test_asociar_autor_a_libro(cliente):
    """
    Prueba asociar autores a un libro (relacion N a N)
    y que la respuesta del libro incluya sus autores.
    """
    autor1 = cliente.post("/autores", json={"nombre": "Adolfo Bioy Casares", "nacionalidad": "Argentina"}).json()
    autor2 = cliente.post("/autores", json={"nombre": "Jorge Luis Borges", "nacionalidad": "Argentina"}).json()

    libro = cliente.post("/libros", json={
        "titulo": "Seis problemas para don Isidro Parodi",
        "isbn": "PARODI-123",
        "stock": 3,
        "anio": 1942
    }).json()

    # Asociamos el primer autor
    resp1 = cliente.post(f"/libros/{libro['id']}/autores/{autor1['id']}")
    assert resp1.status_code == 200
    assert len(resp1.json()["autores"]) == 1
    assert resp1.json()["autores"][0]["nombre"] == "Adolfo Bioy Casares"

    # Asociamos el segundo autor (coautores)
    resp2 = cliente.post(f"/libros/{libro['id']}/autores/{autor2['id']}")
    assert resp2.status_code == 200
    assert len(resp2.json()["autores"]) == 2

    # Intentar asociar nuevamente el mismo autor no debe duplicarlo
    resp3 = cliente.post(f"/libros/{libro['id']}/autores/{autor1['id']}")
    assert resp3.status_code == 200
    assert len(resp3.json()["autores"]) == 2

    # Asociar con IDs inexistentes debe dar 404 (Regla 7)
    assert cliente.post(f"/libros/9999/autores/{autor1['id']}").status_code == 404
    assert cliente.post(f"/libros/{libro['id']}/autores/9999").status_code == 404
