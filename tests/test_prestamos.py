
#  Prueba exhaustivamente todas las reglas de negocio de prestamos
#  y devoluciones (Reglas 1, 2, 3, 4, 5, 6 y 7).
from datetime import date, timedelta


def crear_socio_aux(cliente, nombre="Socio Test", email="socio@test.com", activo=True):
    """Funcion auxiliar para crear un socio rapido en los tests"""
    resp = cliente.post("/socios", json={"nombre": nombre, "email": email, "activo": activo})
    return resp.json()


def crear_libro_aux(cliente, titulo="Libro Test", isbn="ISBN-001", stock=5):
    """Funcion auxiliar para crear un libro rapido en los tests"""
    resp = cliente.post("/libros", json={"titulo": titulo, "isbn": isbn, "stock": stock, "anio": 2020})
    return resp.json()

# REGLA 1: Un socio no puede tener mas de 3 prestamos activos (409)
def test_regla_1_maximo_3_prestamos_activos(cliente):
    """Prueba que un socio solo puede tener hasta 3 prestamos activos (4to da 409)"""
    socio = crear_socio_aux(cliente, email="lector@test.com")
    libros = [
        crear_libro_aux(cliente, f"Libro {i}", f"ISBN-{i}", stock=2)
        for i in range(1, 5)
    ]

    # Pedimos los primeros 3 prestamos (deben funcionar bien, 201)
    for i in range(3):
        resp = cliente.post("/prestamos", json={"socio_id": socio["id"], "libro_id": libros[i]["id"]})
        assert resp.status_code == 201

    # El 4to prestamo debe ser rechazado con 409 Conflict
    cuarto_intento = cliente.post("/prestamos", json={"socio_id": socio["id"], "libro_id": libros[3]["id"]})
    assert cuarto_intento.status_code == 409
    assert cuarto_intento.json()["detail"] == "El socio no puede tener más de 3 préstamos activos"


# REGLA 2: No se presta un libro sin stock; al prestar se descuenta 1 (409)
def test_regla_2_descuenta_stock_y_falla_sin_stock(cliente):
    """Prueba que se descuenta 1 de stock al prestar y si no hay stock da 409"""
    socio1 = crear_socio_aux(cliente, email="s1@test.com")
    socio2 = crear_socio_aux(cliente, email="s2@test.com")
    # Creamos libro con stock = 1
    libro = crear_libro_aux(cliente, "Ultimo Ejemplar", "ISBN-ULTIMO", stock=1)

    # 1er prestamo: debe tener exito y dejar el stock en 0
    resp1 = cliente.post("/prestamos", json={"socio_id": socio1["id"], "libro_id": libro["id"]})
    assert resp1.status_code == 201

    # Verificamos que el stock del libro bajo a 0
    libro_actualizado = cliente.get(f"/libros/{libro['id']}").json()
    assert libro_actualizado["stock"] == 0

    # 2do prestamo sobre el mismo libro: debe fallar con 409 porque no hay stock
    resp2 = cliente.post("/prestamos", json={"socio_id": socio2["id"], "libro_id": libro["id"]})
    assert resp2.status_code == 409
    assert resp2.json()["detail"] == "No se presta un libro sin stock disponible"


# REGLA 3: Un socio inactivo no puede pedir prestamos (403)
def test_regla_3_socio_inactivo_no_puede_pedir_prestamo(cliente):
    """Prueba que un socio inactivo (activo=False) recibe 403 Forbidden"""
    socio_inactivo = crear_socio_aux(cliente, "Socio Bloqueado", "inactivo@test.com", activo=False)
    libro = crear_libro_aux(cliente, "Libro X", "ISBN-X", stock=5)

    respuesta = cliente.post("/prestamos", json={"socio_id": socio_inactivo["id"], "libro_id": libro["id"]})
    assert respuesta.status_code == 403
    assert respuesta.json()["detail"] == "Un socio inactivo no puede pedir préstamos"


# REGLA 4: El plazo es de 14 dias (fecha_vencimiento = fecha_prestamo + 14 dias)
def test_regla_4_plazo_de_14_dias(cliente):
    """Prueba que la fecha de vencimiento es exactamente 14 dias despues de la de prestamo"""
    socio = crear_socio_aux(cliente, email="lector14@test.com")
    libro = crear_libro_aux(cliente, "Libro 14", "ISBN-14", stock=5)

    fecha_inicio = date(2026, 5, 1)
    fecha_esperada_vencimiento = fecha_inicio + timedelta(days=14)  # 2026-05-15

    respuesta = cliente.post("/prestamos", json={
        "socio_id": socio["id"],
        "libro_id": libro["id"],
        "fecha_prestamo": str(fecha_inicio)
    })
    assert respuesta.status_code == 201
    datos = respuesta.json()
    assert datos["fecha_prestamo"] == str(fecha_inicio)
    assert datos["fecha_vencimiento"] == str(fecha_esperada_vencimiento)


# REGLA 5: Al devolver se repone el stock y se calcula la multa: $100 x dias de atraso (0 a tiempo)
def test_regla_5_devolucion_a_tiempo_sin_multa_y_repone_stock(cliente):
    """Prueba devolver a tiempo: multa = $0 y el stock sube en 1"""
    socio = crear_socio_aux(cliente, email="puntual@test.com")
    libro = crear_libro_aux(cliente, "Libro Stock", "ISBN-PUNTUAL", stock=2)

    fecha_p = date(2026, 6, 1)
    # Pedimos prestado -> stock baja de 2 a 1
    prestamo = cliente.post("/prestamos", json={
        "socio_id": socio["id"],
        "libro_id": libro["id"],
        "fecha_prestamo": str(fecha_p)
    }).json()

    assert cliente.get(f"/libros/{libro['id']}").json()["stock"] == 1

    # Devolvemos a tiempo (dia 10, antes de los 14 dias)
    fecha_dev = date(2026, 6, 11)
    devolucion = cliente.post(f"/prestamos/{prestamo['id']}/devolucion", json={
        "fecha_devolucion": str(fecha_dev)
    })
    assert devolucion.status_code == 200
    datos = devolucion.json()
    assert datos["fecha_devolucion"] == str(fecha_dev)
    assert datos["multa"] == 0.0

    # Comprobamos que el stock volvio a subir a 2
    assert cliente.get(f"/libros/{libro['id']}").json()["stock"] == 2


def test_regla_5_devolucion_con_atraso_calcula_multa(cliente):
    """Prueba devolver con atraso: $100 por dia de atraso"""
    socio = crear_socio_aux(cliente, email="demorado@test.com")
    libro = crear_libro_aux(cliente, "Libro Multa", "ISBN-MULTA", stock=3)

    fecha_p = date(2026, 6, 1)
    # Vencimiento sera 2026-06-15 (14 dias)
    prestamo = cliente.post("/prestamos", json={
        "socio_id": socio["id"],
        "libro_id": libro["id"],
        "fecha_prestamo": str(fecha_p)
    }).json()

    # Devolvemos 5 dias despues del vencimiento: el 2026-06-20
    # Multa esperada: 5 dias x $100 = $500
    fecha_dev = date(2026, 6, 20)
    devolucion = cliente.post(f"/prestamos/{prestamo['id']}/devolucion", json={
        "fecha_devolucion": str(fecha_dev)
    })
    assert devolucion.status_code == 200
    datos = devolucion.json()
    assert datos["multa"] == 500.0


# REGLA 6: No se puede devolver un prestamo ya devuelto (409)
def test_regla_6_no_se_puede_devolver_prestamo_ya_devuelto(cliente):
    """Prueba que intentar devolver por segunda vez da 409 Conflict"""
    socio = crear_socio_aux(cliente, email="devuelto@test.com")
    libro = crear_libro_aux(cliente, "Libro Devuelto", "ISBN-DEV", stock=3)

    prestamo = cliente.post("/prestamos", json={"socio_id": socio["id"], "libro_id": libro["id"]}).json()

    # Primera devolucion: OK
    primera_vez = cliente.post(f"/prestamos/{prestamo['id']}/devolucion")
    assert primera_vez.status_code == 200

    # Segunda devolucion: debe fallar con 409
    segunda_vez = cliente.post(f"/prestamos/{prestamo['id']}/devolucion")
    assert segunda_vez.status_code == 409
    assert segunda_vez.json()["detail"] == "No se puede devolver un préstamo ya devuelto"


# REGLA 7: Recurso inexistente (404)
def test_regla_7_recursos_inexistentes_en_prestamos(cliente):
    """Prueba que IDs inexistentes en prestamo y devolucion dan 404"""
    socio = crear_socio_aux(cliente, email="existe@test.com")
    libro = crear_libro_aux(cliente, "Existe", "ISBN-EXISTE", stock=2)

    # Socio que no existe al pedir prestamo -> 404
    resp1 = cliente.post("/prestamos", json={"socio_id": 9999, "libro_id": libro["id"]})
    assert resp1.status_code == 404
    assert resp1.json()["detail"] == "Socio no encontrado"

    # Libro que no existe al pedir prestamo -> 404
    resp2 = cliente.post("/prestamos", json={"socio_id": socio["id"], "libro_id": 9999})
    assert resp2.status_code == 404
    assert resp2.json()["detail"] == "Libro no encontrado"

    # Prestamo que no existe al devolver -> 404
    resp3 = cliente.post("/prestamos/9999/devolucion")
    assert resp3.status_code == 404
    assert resp3.json()["detail"] == "Préstamo no encontrado"


# ENDPOINT: GET /socios/{id}/prestamos?activos=true
def test_prestamos_de_socio_filtro_activos(cliente):
    """Prueba consultar los prestamos de un socio y filtrar solo los activos"""
    socio = crear_socio_aux(cliente, email="historial@test.com")
    l1 = crear_libro_aux(cliente, "Libro A", "ISBN-A", stock=2)
    l2 = crear_libro_aux(cliente, "Libro B", "ISBN-B", stock=2)

    # El socio pide 2 prestamos
    p1 = cliente.post("/prestamos", json={"socio_id": socio["id"], "libro_id": l1["id"]}).json()
    p2 = cliente.post("/prestamos", json={"socio_id": socio["id"], "libro_id": l2["id"]}).json()

    # Devuelve el primer prestamo
    cliente.post(f"/prestamos/{p1['id']}/devolucion")

    # 1. Sin filtro: deben aparecer los 2 prestamos (el devuelto y el activo)
    todos = cliente.get(f"/socios/{socio['id']}/prestamos").json()
    assert len(todos) == 2

    # 2. Con ?activos=true: solo debe aparecer 1 prestamo (el activo p2)
    activos = cliente.get(f"/socios/{socio['id']}/prestamos?activos=true").json()
    assert len(activos) == 1
    assert activos[0]["id"] == p2["id"]
    assert activos[0]["fecha_devolucion"] is None

    # 3. Socio inexistente da 404 (Regla 7)
    assert cliente.get("/socios/9999/prestamos").status_code == 404
