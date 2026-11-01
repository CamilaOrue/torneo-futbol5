from fastapi import HTTPException


def error_campo(status: int, campo: str, mensaje: str) -> HTTPException:
    """Error asociado a un campo del body, con el mismo formato que los 422 de FastAPI.

    El front lo usa para mostrar el mensaje debajo del campo correspondiente.
    """
    return HTTPException(
        status,
        detail=[{"loc": ["body", campo], "msg": mensaje, "type": "value_error"}],
    )
