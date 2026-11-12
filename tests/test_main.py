def test_inicio(cliente):
    respuesta = cliente.get("/")
    assert respuesta.status_code == 200
    assert "Bienvenido" in respuesta.json()["mensaje"]
