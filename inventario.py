import json
from pathlib import Path
import numpy as np
from enums import CategoriasVuln, Severidades, Status
from equipamentos import Equipamento , Notebook, Impressora, Servidor_Web, Roteador
from vulnerabilidades import Vulnerabilidade


class Inventario:
    def __init__ (self): 
    
        self.ARQUIVOS_DADOS = Path(__file__).resolve().parent/"ativos.json"
        self.equipamentos = []
        self.vulnerabilidades = [] 
        self.carregar()

    def adicionar_equipamento(self,equipamento):
        self.equipamentos.append(equipamento)
        self.salvar()

    def adicionar_vulnerabilidade(self,vulnerabilidade):
        self.vulnerabilidades.append(vulnerabilidade)
        self.salvar()

    def listar_equipamento(self):
        return self.equipamentos

    def listar_vulnerabilidades(self):
        return self.vulnerabilidades

    def buscar_equipamento(self, id_ativo):
        for equipamento in self.equipamentos:
            if equipamento.id_ativo == id_ativo:
                return equipamento
            
        return None 
 
    def buscar_vulnerabilidade(self, id_vuln):
        for vulnerabilidade in self.vulnerabilidades:
            if vulnerabilidade.id_vuln == id_vuln:
                return vulnerabilidade
            
        return None 

    def remover_equipamento(self, id_ativo):
        alvo = self.buscar_equipamento(id_ativo)
        if alvo is not None:    
            self.equipamentos.remove(alvo)
            self.salvar()
            return True
        return False
                       

    def remover_vulnerabilidade(self,id_vuln):
        alvo = self.buscar_vulnerabilidade(id_vuln)
        if alvo is not None:
            self.vulnerabilidades.remove(alvo)
            self.salvar()
            return True
        return False

    def vincular_vulnerabilidade(self, id_vuln, id_ativo):
        equipamento = self.buscar_equipamento(id_ativo)
        vulnerabilidade = self.buscar_vulnerabilidade(id_vuln)
        
        if equipamento is None or vulnerabilidade is None:
            return False

       
        if equipamento.ids_vulnerabilidades is None:
            equipamento.ids_vulnerabilidades = []

      
        if id_vuln not in equipamento.ids_vulnerabilidades:
            equipamento.ids_vulnerabilidades.append(id_vuln)
        self.salvar()
        return True

    def editar_equipamento(self, id_ativo, id_ativo_novo=None, nome_novo=None, responsavel_novo=None, ip_novo=None):
        alvo = self.buscar_equipamento(id_ativo)
        if alvo is not None:
            if id_ativo_novo:
                alvo.id_ativo = id_ativo_novo 
            if nome_novo:
                alvo.nome = nome_novo 
            if responsavel_novo:
                alvo.responsavel = responsavel_novo 
            if ip_novo:
                alvo.ip = ip_novo
            self.salvar()
            return True
        return False

    def editar_vulnerabilidade(self,id_vuln, id_vuln_novo=None, descricao_novo=None, categoria_nova=None, severidade_nova=None, status_novo=None):
        alvo = self.buscar_vulnerabilidade(id_vuln)
        if alvo is not None:
            if id_vuln_novo:
                alvo.id_vuln = id_vuln_novo 
            if descricao_novo:
                alvo.descricao = descricao_novo 
            if categoria_nova:
                alvo.categoria = categoria_nova 
            if severidade_nova:
                alvo.severidade = severidade_nova 
            if status_novo:
                alvo.status = status_novo
            self.salvar() 
            return True
        return False


    def vincular_dependencia(self, id_alvo, id_origem, peso):
        alvo = self.buscar_equipamento(id_alvo)
        origem = self.buscar_equipamento(id_origem)

        if alvo is None or origem is None:
            print("=== Ativo alvo ou de origem nao encontrados ===")
            return False

        if id_alvo == id_origem:
            print("=== Um ativo nao pode depender de si mesmo ===")
            return False

        soma_atual = sum(alvo.dependencia.values())
        peso_antigo = alvo.dependencia.get(id_origem, 0.0)
        nova_soma = soma_atual - peso_antigo + peso

        if nova_soma >= 1.0:
            print("=== Os valores dos pesos nao podem exceder 100% ===")
            return False
        alvo.dependencia[id_origem] = peso
        self.salvar()
        return True 

    def vetor_risco_propio (self):
        riscos = []

        for eq in self.equipamentos:
            risco_acumulado = 0.0
            for id_vuln in eq.ids_vulnerabilidades:
                vuln = self.buscar_vulnerabilidade(id_vuln)
                if vuln:
                    risco_acumulado += float(vuln.severidade.value)


            fator = getattr (eq, "fator_exposicao", 1.0)
            risco_acumulado *= fator

            riscos.append(risco_acumulado)

            return np.array(riscos, dtype=float)
 
    def gerar_matriz_dependencia(self):
        n = len(self.equipamentos)

        matriz_A = np.zeros((n, n), dtype=float)

        id_para_indice = {}
        for i, equipamento in enumerate(self.equipamentos):
            id_para_indice[equipamento.id_ativo] = i

        for id_origem, peso in equipamento.dependencia.items():
            j = id_para_indice[id_origem]

            matriz_A[i, j ] = peso

        return matriz_A

    def   matriz_I_A(self):
        N = len(self.equipamentos)

        b = self.vetor_risco_proprio()
        a = self.gerar_matriz_dependencia()

        i = np.eye(N, dtype=float)

        matriz_sistema = i - a

        det = np.linalg.det(matriz_sistema)

        if det == 0:
            print("Aviso o sistema nao possui uma solucao unica")
            return None 

        x = np.linalg.solve(matriz_sistema, b)
        return x
    
    def salvar (self):
        dados = {
        "equipamentos": [],
        "vulnerabilidades":[]
    }
    
        for vuln in self.vulnerabilidades:
            dados["vulnerabilidades"].append(vuln.para_dict())

        for eq in self.equipamentos:
            eq_dict = eq.para_dict()

            vulns_aninhadas = []
            for id_v in eq.ids_vulnerabilidades:
                v_obj = self.buscar_vulnerabilidade(id_v)
                if v_obj:
                    vulns_aninhadas.append(v_obj.para_dict())
            eq_dict["vulnerabilidades_detalhadas"] = vulns_aninhadas
            dados["equipamentos"].append(eq_dict)


        with open(self.ARQUIVOS_DADOS, "w", encoding="utf-8") as arquivo:
            json.dump(dados, arquivo, ensure_ascii= False, indent=4)


    def carregar(self):
       self.equipamentos.clear()
       self.vulnerabilidades.clear()
       if not self.ARQUIVOS_DADOS.exists(): 
           return
       with open(self.ARQUIVOS_DADOS, "r", encoding="utf-8") as arquivo:
           dados = json.load(arquivo)
           for item in dados["vulnerabilidades"]:
               v =Vulnerabilidade(item["id_vuln"], item["descricao"], CategoriasVuln(item ["categoria"]), Severidades[item["severidade"]], Status(item ["status"]))
               self.vulnerabilidades.append(v)
           for item in dados ["equipamentos"]:
               if item["tipo"] == "Notebook":
                   e = Notebook(item["id_ativo"], item["nome"], item ["responsavel"], item ["ip"], item["ids_vulnerabilidades"], item["dependencia"])
               elif item["tipo"] == "Roteador":
                   e = Roteador(item["id_ativo"], item["nome"], item ["responsavel"], item ["ip"], item["ids_vulnerabilidades"], item["dependencia"])
               elif item["tipo"] == "Servidor_Web":
                   e = Servidor_Web(item["id_ativo"], item["nome"], item ["responsavel"], item ["ip"], item["ids_vulnerabilidades"], item["dependencia"])
               elif item["tipo"] == "Impressora":
                   e = Impressora(item["id_ativo"], item["nome"], item ["responsavel"], item ["ip"], item["ids_vulnerabilidades"],item["dependencia"])
               else:
                   continue 
               self.equipamentos.append(e)