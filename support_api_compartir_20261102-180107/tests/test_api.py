"""Pruebas de aceptacion para operaciones y reglas de negocio de la API."""

from fastapi.testclient import TestClient


def create_request(client: TestClient, payload: dict[str, str]) -> dict:
    """Crea una solicitud de prueba y devuelve el objeto de respuesta."""
    response = client.post("/api/v1/solicitudes", json=payload)
    assert response.status_code == 201
    return response.json()


def test_create_request_starts_as_new(
    client: TestClient, create_payload: dict[str, str]
) -> None:
    """RF-01: una solicitud valida recibe ID y estado NUEVA."""
    response = client.post("/api/v1/solicitudes", json=create_payload)

    assert response.status_code == 201
    assert response.json()["id_solicitud"].startswith("SOL-")
    assert response.json()["estado"] == "NUEVA"


def test_description_length_boundaries(
    client: TestClient, create_payload: dict[str, str]
) -> None:
    """RN-01: acepta descripciones de 10 y 500 caracteres, no otras longitudes."""
    for length in (10, 500):
        payload = {**create_payload, "descripcion": "x" * length}
        assert client.post("/api/v1/solicitudes", json=payload).status_code == 201

    for length in (9, 501):
        payload = {**create_payload, "descripcion": "x" * length}
        assert client.post("/api/v1/solicitudes", json=payload).status_code == 422

    assert len(
        client.get("/api/v1/solicitudes", params={"estado": "NUEVA"}).json()
    ) == 2


def test_rejected_create_does_not_persist(
    client: TestClient, create_payload: dict[str, str]
) -> None:
    """RN-06: descripcion corta o usuario desconocido no crea registros."""
    short_description = {**create_payload, "descripcion": "Error"}
    unknown_user = {**create_payload, "id_usuario": "USR-99"}

    assert client.post("/api/v1/solicitudes", json=short_description).status_code == 422
    assert client.post("/api/v1/solicitudes", json=unknown_user).status_code == 422
    assert client.get("/api/v1/solicitudes", params={"estado": "NUEVA"}).json() == []


def test_rejects_invalid_enums(
    client: TestClient, create_payload: dict[str, str]
) -> None:
    """Rechaza categorias y prioridades fuera de sus enumeraciones."""
    invalid_category = {**create_payload, "categoria": "OTRA"}
    invalid_priority = {**create_payload, "prioridad": "URGENTE"}

    assert client.post("/api/v1/solicitudes", json=invalid_category).status_code == 422
    assert client.post("/api/v1/solicitudes", json=invalid_priority).status_code == 422


def test_get_request_and_handle_invalid_ids(
    client: TestClient, create_payload: dict[str, str]
) -> None:
    """RF-02: consulta por ID y diferencia formato invalido de ID inexistente."""
    created = create_request(client, create_payload)
    request_id = created["id_solicitud"]

    assert client.get(f"/api/v1/solicitudes/{request_id}").json() == created
    assert client.get(
        "/api/v1/solicitudes/consulta", params={"id_solicitud": request_id}
    ).json() == created
    empty_id = client.get(
        "/api/v1/solicitudes/consulta", params={"id_solicitud": ""}
    )
    assert empty_id.status_code == 422
    assert empty_id.json()["detail"] == "Formato de id_solicitud invalido"
    assert client.get("/api/v1/solicitudes/consulta").status_code == 422
    assert client.get("/api/v1/solicitudes/SOL-999").status_code == 404
    assert client.get("/api/v1/solicitudes/not-an-id").status_code == 422


def test_list_requests_by_status(
    client: TestClient, create_payload: dict[str, str]
) -> None:
    """RF-03: filtra por estado, acepta resultados vacios y rechaza filtros invalidos."""
    first = create_request(client, create_payload)
    second = create_request(client, create_payload)
    matching = client.get(
        "/api/v1/solicitudes", params={"estado": "NUEVA"}
    ).json()

    assert [request["id_solicitud"] for request in matching] == [
        first["id_solicitud"],
        second["id_solicitud"],
    ]
    assert client.get("/api/v1/solicitudes", params={"estado": "PENDIENTE"}).status_code == 422
    assert client.get("/api/v1/solicitudes", params={"estado": "RESUELTA"}).json() == []


def test_valid_transition_and_required_resolution_note(
    client: TestClient, create_payload: dict[str, str]
) -> None:
    """RF-04: permite avanzar y exige nota antes de pasar a RESUELTA."""
    created = create_request(client, create_payload)
    request_id = created["id_solicitud"]

    in_progress = client.patch(
        f"/api/v1/solicitudes/{request_id}/estado",
        json={"nuevo_estado": "EN_PROCESO"},
    )
    assert in_progress.status_code == 200
    assert in_progress.json()["estado"] == "EN_PROCESO"

    rejected = client.patch(
        f"/api/v1/solicitudes/{request_id}/estado",
        json={"nuevo_estado": "RESUELTA"},
    )
    assert rejected.status_code == 422
    assert client.get(f"/api/v1/solicitudes/{request_id}").json()["estado"] == "EN_PROCESO"

    resolved = client.patch(
        f"/api/v1/solicitudes/{request_id}/estado",
        json={
            "nuevo_estado": "RESUELTA",
            "nota_resolucion": "Se reemplazo el cable USB defectuoso",
        },
    )
    assert resolved.status_code == 200
    assert resolved.json()["estado"] == "RESUELTA"


def test_rejects_invalid_transition_without_mutation(
    client: TestClient, create_payload: dict[str, str]
) -> None:
    """RN-03 y RN-06: rechaza saltos de estado y conserva el registro intacto."""
    created = create_request(client, create_payload)
    request_id = created["id_solicitud"]
    response = client.patch(
        f"/api/v1/solicitudes/{request_id}/estado",
        json={
            "nuevo_estado": "RESUELTA",
            "nota_resolucion": "El problema fue corregido correctamente",
        },
    )

    assert response.status_code == 409
    assert client.get(f"/api/v1/solicitudes/{request_id}").json()["estado"] == "NUEVA"


def test_closed_request_is_immutable(
    client: TestClient, create_payload: dict[str, str]
) -> None:
    """RN-05: permite cerrar desde NUEVA con nota e impide cambios posteriores."""
    created = create_request(client, create_payload)
    request_id = created["id_solicitud"]
    closed = client.patch(
        f"/api/v1/solicitudes/{request_id}/estado",
        json={
            "nuevo_estado": "CERRADA",
            "nota_resolucion": "Cancelacion solicitada por el usuario",
        },
    )
    assert closed.status_code == 200

    closed_update = client.patch(
        f"/api/v1/solicitudes/{request_id}/estado",
        json={"nuevo_estado": "EN_PROCESO"},
    )
    assert closed_update.status_code == 409
    assert client.get(f"/api/v1/solicitudes/{request_id}").json()["estado"] == "CERRADA"


def test_resolution_note_must_be_at_least_ten_characters(
    client: TestClient, create_payload: dict[str, str]
) -> None:
    """RN-04: rechaza una nota corta y mantiene el estado EN_PROCESO."""
    created = create_request(client, create_payload)
    request_id = created["id_solicitud"]
    client.patch(
        f"/api/v1/solicitudes/{request_id}/estado",
        json={"nuevo_estado": "EN_PROCESO"},
    )

    response = client.patch(
        f"/api/v1/solicitudes/{request_id}/estado",
        json={"nuevo_estado": "RESUELTA", "nota_resolucion": "corta"},
    )

    assert response.status_code == 422
    assert client.get(f"/api/v1/solicitudes/{request_id}").json()["estado"] == "EN_PROCESO"


def test_remaining_transition_rules_and_minimum_note(
    client: TestClient, create_payload: dict[str, str]
) -> None:
    """RN-03 y RN-04: verifica transiciones restantes y nota de exactamente 10 caracteres."""
    created = create_request(client, create_payload)
    request_id = created["id_solicitud"]
    client.patch(
        f"/api/v1/solicitudes/{request_id}/estado",
        json={"nuevo_estado": "EN_PROCESO"},
    )

    invalid_close = client.patch(
        f"/api/v1/solicitudes/{request_id}/estado",
        json={
            "nuevo_estado": "CERRADA",
            "nota_resolucion": "Cancelacion solicitada",
        },
    )
    assert invalid_close.status_code == 409
    assert client.get(f"/api/v1/solicitudes/{request_id}").json()["estado"] == "EN_PROCESO"

    resolved = client.patch(
        f"/api/v1/solicitudes/{request_id}/estado",
        json={"nuevo_estado": "RESUELTA", "nota_resolucion": "1234567890"},
    )
    assert resolved.status_code == 200
    assert resolved.json()["estado"] == "RESUELTA"

    closed = client.patch(
        f"/api/v1/solicitudes/{request_id}/estado",
        json={"nuevo_estado": "CERRADA", "nota_resolucion": "1234567890"},
    )
    assert closed.status_code == 200
    assert closed.json()["estado"] == "CERRADA"
