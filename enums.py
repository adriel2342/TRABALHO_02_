from enum import Enum 

class TipoAtivo(Enum):
    Notebook = 1
    Roteador = 2
    Servidor_Web = 3
    Impressora = 4


class Severidades(Enum):
    BAIXA = 2.0
    MEDIA = 5.45
    ALTA = 7.95
    CRITICA = 9.5


class Status (Enum):
    em_aberto = "em aberto"
    em_tratamento = "em tratamento"
    corrigida = "corrigida"
    Risco_aceito = "risco aceito"

class CategoriasVuln(Enum):
    Rede = "rede"
    Software = "software"
    Hardware = "hardware"
    Configuracao = "configuracao"
