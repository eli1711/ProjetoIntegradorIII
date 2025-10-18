from enum import Enum

class Cargo(Enum):
    ADMINISTRADOR = "administrador"
    COORDENADOR = "coordenador"
    ANALISTA = "analista"

    @classmethod
    def from_str(cls, valor):
        for cargo in cls:
            if cargo.value == valor:
                return cargo
        raise ValueError(f"Cargo inválido: {valor}")
