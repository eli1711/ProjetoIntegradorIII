from enum import Enum

class Cargo(Enum):
    ADMINISTRADOR = "administrador"
    COORDENADOR = "coordenador"
    ANALISTA = "analista"

# Exemplo de uso:
usuario_cargo = Cargo.ADMINISTRADOR
print(usuario_cargo.value)  # saída: administrador
