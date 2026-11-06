from pydantic import BaseModel, ConfigDict, Field, field_validator


class ComplejoBase(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    nombre: str = Field(..., max_length=100, description="Nombre del complejo deportivo")
    direccion: str = Field(..., max_length=150, description="Dirección del complejo")
    departamento: str = Field(..., max_length=50, description="Departamento donde se ubica")

    @field_validator("nombre", "direccion", "departamento")
    @classmethod
    def validar_texto(cls, valor):
        if not valor:
            raise ValueError("Este campo no puede estar vacío")
        return valor


class ComplejoCreate(ComplejoBase):
    """Datos requeridos para la creación de un complejo."""


class ComplejoUpdate(ComplejoBase):
    """Datos requeridos para modificar un complejo existente."""


class ComplejoOut(ComplejoBase):
    id_complejo: int