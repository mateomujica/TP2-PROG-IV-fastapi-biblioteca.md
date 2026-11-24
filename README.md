# Sistema de Gestión de Biblioteca (FastAPI + SQLModel)

## Trabajo Práctico para Programación IV. Consiste en una API REST para administrar el catálogo de una biblioteca (autores y libros), los socios y el sistema de préstamos y devoluciones con cálculo de multas y control de stock.

## Cómo correr la aplicación

### 1. Instalar las dependencias

Abre una terminal en la carpeta del proyecto y ejecuta:

```bash
pip install -r requirements.txt
```

### 2. Iniciar el servidor

```bash
uvicorn main:app --reload
```

- El servidor arrancará en: `http://127.0.0.1:8000`
- **Documentación interactiva (Swagger):** entra desde tu navegador a `http://127.0.0.1:8000/docs` para probar todos los endpoints visualmente.

---

## Cómo correr los Tests

```bash
pytest --cov=. --cov-report=term-missing
```
---

## Endpoints Principales

| Método                   | Ruta                                  | Descripción                                                         |
| ------------------------ | ------------------------------------- | ------------------------------------------------------------------- |
| `GET` / `POST`           | `/autores`                            | Listar y crear autores                                              |
| `GET` / `PUT` / `DELETE` | `/autores/{id}`                       | Ver, modificar y eliminar un autor                                  |
| `GET` / `POST`           | `/libros`                             | Listar libros y crear un libro                                      |
| `GET`                    | `/libros?disponibles=true`            | Filtra solo los libros con stock > 0                                |
| `GET` / `PUT` / `DELETE` | `/libros/{id}`                        | Ver, editar y eliminar un libro                                     |
| `POST`                   | `/libros/{id}/autores/{autor_id}`     | Asocia un autor a un libro (relación N:N)                           |
| `GET` / `POST`           | `/socios`                             | Listar y registrar socios                                           |
| `GET` / `PUT` / `DELETE` | `/socios/{id}`                        | Ver, actualizar y dar de baja un socio                              |
| `GET`                    | `/socios/{id}/prestamos?activos=true` | Ver préstamos activos de un socio                                   |
| `POST`                   | `/prestamos`                          | Registrar un préstamo (aplica reglas 1, 2, 3 y 4)                   |
| `POST`                   | `/prestamos/{id}/devolucion`          | Registrar devolución, reponer stock y calcular multa (reglas 5 y 6) |
