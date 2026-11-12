from vulnerabilidades import Vulnerabilidade

class Equipamento:
    def __init__  (self, id_ativo, nome, responsavel, ip, ids_vulnerabilidades=None, dependencia=None): #utilizamos o None pois seria obrigat
      self.id_ativo = id_ativo
      self.nome = nome
      self.responsavel = responsavel
      self.ip = ip
      self.dependencia = dependencia or {}
      self.ids_vulnerabilidades = ids_vulnerabilidades or []
      self.tipo = type(self).__name__

    def descrever_equipamento(self):
        return f"|esse é o id: {self.id_ativo}, \n|esse é o nome: {self.nome}, \n|esse é o responsavel: {self.responsavel}, \n|esse é o ip: {self.ip}"
    #criar aqui o fator de exposição também
    def para_dict(self):
        return {"id_ativo": self.id_ativo, "nome": self.nome, "responsavel": self.responsavel, "ip": self.ip, "ids_vulnerabilidades": self.ids_vulnerabilidades, "tipo": self.tipo, "dependencia": self.dependencia}


#Fatores de exposicao baseado na exposicao a internet
class Notebook (Equipamento):
    fator_exposicao = 1.0

class Roteador(Equipamento):
    fator_exposicao = 1.2

class Servidor_Web(Equipamento):
    fator_exposicao = 1.5

class Impressora(Equipamento):
    fator_exposicao = 0.8
