import json
from enum import Enum
from pathlib import Path


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


class Vulnerabilidade:
    def __init__(self, id_vuln, descricao, categoria, severidade, status):
        self.id_vuln = id_vuln
        self.descricao = descricao
        self.categoria = categoria
        self.severidade = severidade    
        self.status = status

    def descrever_vuln (self):
        return f"|esse é o id: {self.id_vuln}, \n|essa é a descricao: {self.descricao}, \n|essa é a categoria: {self.categoria},\n|essa é a severidade: {self.severidade.name}, \n|esse é o status: {self.status}"
    
    def para_dict (self):
        return {"id_vuln": self.id_vuln, "descricao": self.descricao, "categoria": self.categoria.value, "severidade": self.severidade.name, "status": self.status.value}     

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


#Nessas classes depois colocar o fator de exposição 
class Notebook (Equipamento):
    pass

class Roteador(Equipamento):
    pass

class Servidor_Web(Equipamento):
    pass

class Impressora(Equipamento):
    pass

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


class Menu:
    def __init__(self, inventario):
        self.inventario = inventario 

    def id_ativo_mostrar_ativo(self):
       equipamentos = self.inventario.listar_equipamento()

       if not equipamentos:
           print("=== Nenhum id cadastrado ===")
           return

       print("=== ID's cadastrados para os ativos ===")
       for eq in equipamentos:
           print(f"ID: {eq.id_ativo} | NOME: {eq.nome}")


    def id_vuln_mostrar_vuln(self):
        vulnerabilidades = self.inventario.listar_vulnerabilidades()

        if not vulnerabilidades:
            print("=== Nenhum ID cadastrado ===")
            return
        print("=== ID's cadastrados para vulnerabilidades ===")
        for vuln in vulnerabilidades:
            print(f"ID: {vuln.id_vuln}")


    def confirmar(self, pergunta):
            confirmacao = input( pergunta + " (s/n): ").strip().lower()
            if confirmacao == "s" or confirmacao == "sim":

                return True
            elif confirmacao == "n" or confirmacao == "nao":
                return False
            else:
                print("=== Opcao invalida ===")
                return None

    def exibir_menu(self):
        print("=== MENU ===")
        print("-- Adicionar ativo -- (1)")
        print("-- Buscar ativos -- (2)")
        print("-- Remover/Editar ativos -- (3)")
        print("-- Adicionar vulnerabilidades -- (4)")
        print("-- Buscar vulnerabilidades -- (5)")
        print("-- Remover/Editar vulnerabilidades -- (6)")
        print("-- Vincular vulnerabilidades -- (7)")
        print("-- Vincular dependencia de ativos -- (8)")
        print("-- Sair -- (0) ")

    def opcao_selecionada(self):
        while True: 
            self.exibir_menu()
            opcao = input("=== Selecione uma das opcoes acima: ").strip()
            if opcao == "1":
                self.tela_cadastrar_equipamento()
            elif opcao == "2":
                self.tela_busca_de_ativos()
            elif opcao == "3":
                self.tela_editar_remover_ativo()
            elif opcao == "4":
                self.tela_cadastrar_vulnerabilidade()
            elif opcao == "5":
                self.tela_busca_vulnerabilidade()
            elif opcao == "6":
                self.tela_editar_remover_vulnerabilidade()
            elif opcao == "7":
                self.tela_vincular_vulnerabilidades()
            elif opcao == "8":
                self.tela_vincular_dependencia()

            elif opcao == "0":
                print("=== OBRIGADO PELO USO ===")
                break
            else:
                print("=== ESCOLHA UMA OPCAO DE 0 A 7 ===")

    def tela_cadastrar_equipamento(self):
        equipamentos = self.inventario.listar_equipamento()

        print("=== CADASTRO DE ATIVOS ===")
        print("=== Esses são os IDS cadastrados ===")
        self.id_ativo_mostrar_ativo()
        id_ativo = input("Adicione um ID relacionado ao seu ativo: ").strip().lower()
        for eq in equipamentos:
            if eq.id_ativo == id_ativo:
                print("=== ID previamente cadastrado ===")
                return
            
        nome = input("Adicione um NOME relacionado ao seu ativo: ").strip().upper()
        responsavel  = input("Adicione um RESPONSAVEL relacionado ao seu ativo: ").strip().lower()
        ip = input("Adicione um IP relacionado ao seu ativo: ").strip().lower()

        print("=== TIPOS DISPONÍVEIS ===")
        for ativo in TipoAtivo:
            print(ativo.value, "-", ativo.name)

        try:
            codigo_tipo = int(input("Digite um dos números inteiros acima: "))
            tipo = TipoAtivo(codigo_tipo)

        except ValueError:
            print("=== Tipo não identificado tente novamente ===")
            return
        if not id_ativo or not nome or not responsavel or not ip:
            print("=== Os campos acima não devem ficar em branco ===")
            return
        print("=== Confirmacao dos dados ===")
        print(f"O ID do ativo está correto? -> {id_ativo}?\n O NOME do ativo está correto? -> {nome}?\n O RESPONSAVEL pelo ativo está correto? -> {responsavel}?\n O IP do ativo está correto? -> {ip}?\n O TIPO do ativo está correto? -> {codigo_tipo}?")

        if not self.confirmar("=== Os dados acima estão correto? ==="):
            print("=== Cadastro cancelado ===")
            return

        if tipo ==TipoAtivo.Notebook:

            novo_ativo = Notebook(id_ativo, nome, responsavel, ip)
        elif tipo == TipoAtivo.Impressora:
            novo_ativo = Impressora(id_ativo, nome, responsavel, ip)
        elif tipo == TipoAtivo.Roteador:
            novo_ativo = Roteador(id_ativo,nome, responsavel, ip)
        elif tipo == TipoAtivo.Servidor_Web:
            novo_ativo = Servidor_Web(id_ativo, nome, responsavel, ip)
        
        self.inventario.adicionar_equipamento(novo_ativo)
        print("=== ATIVO ADICIONADO ===")

    def tela_busca_de_ativos(self):
        self.id_ativo_mostrar_ativo()
        print("=== Esses sao os IDs cadastrados ===")
        id_busca = input("=== Escolha um dos IDs acima para visualizar: ").strip().lower()
        if not id_busca:
            print("=== Esse campo nao pode ficar em branco tente novamente ===")
            return
        resultado = self.inventario.buscar_equipamento(id_busca)
        if not resultado:
            print("=== ID nao identificado ===")
            return
        print(resultado.descrever_equipamento())
        

    def tela_editar_remover_ativo(self):
        print("=== Esses são os IDS disponíveis ===")
        self.id_ativo_mostrar_ativo()
        id_ativo = input("=== Selecione o ID do ativo:").strip()

        if not id_ativo:
            print("=== Esse campo não deve ficar em branco ===")
            return
        ativo = self.inventario.buscar_equipamento(id_ativo)
        if not ativo: 
            print("=== ID não identificado ===")
            return
        print(ativo.descrever_equipamento())

        opcao = input("Oque você deseja fazer?\n EDITAR(1) | REMOVER(2) -> ").strip()
        if opcao == "1":
            id_ativo_novo = input("Deseja editar o id? (caso não queira pressione enter): ").strip() or None
            if id_ativo_novo and id_ativo_novo != id_ativo:
                if self.inventario.buscar_equipamento(id_ativo_novo):
                    print("=== ID já cadastrado ===")
                    return
            nome_novo = input("Deseja editar o nome?(caso não queira pressione enter): ").strip().upper() or None
            responsavel_novo = input("Deseja editar o responsavel?(caso não queira pressione enter): ").strip().lower() or None
            ip_novo = input("Deseja editar o ip?(caso não queira pressione enter): ").strip() or None

            id_exibir = id_ativo_novo or ativo.id_ativo
            nome_exibir = nome_novo or ativo.nome
            responsavel_exibir = responsavel_novo or ativo.responsavel
            ip_exibir = ip_novo or ativo.ip
            print("= CONFIRMACAO =")
            print(f"O id esta correto? -> {id_exibir}\n O nome esta correto? -> {nome_exibir}\n O responsavel está correto? -> {responsavel_exibir}\n O ip está correto? -> {ip_exibir} ")
            if not self.confirmar("Os dados foram editados corretamente?"):
                print("=== Edição cancelada tente novamente ===")
                return
            if self.inventario.editar_equipamento(id_ativo, id_ativo_novo, nome_novo, responsavel_novo, ip_novo):
                print("== Ativo editado ==")
            else:
                print("== Nao foi possivel editar o ativo ==")
            
        elif opcao == "2":
            if not self.confirmar("Deseja realmente apagar o ativo?"):
                print("=== Remoção cancelada ===")
                return
            if self.inventario.remover_equipamento(id_ativo):
                print ("== Ativo removido ==")
            else:
                print("== Nao foi possivel remover o ativo ==")
           

        else: 
            print("=== Opcao invalida digite 1 ou 2 ===")
           
           
         

    def tela_cadastrar_vulnerabilidade(self):
        vulnerabilidades = self.inventario.listar_vulnerabilidades()
        print("== CADASTRO DE VULNERABILIDADES ==")
        print("== Esses são os IDs cadastrados ==")
        self.id_vuln_mostrar_vuln()
        id_vuln = input("Adicione um ID relacionado a sua vulnerabilidade: ").strip()
        for vuln in vulnerabilidades:
            if vuln.id_vuln == id_vuln:
                print("== ID previamente cadastrado ==")
                return
            
        descricao = input("== Digite a descricao para a vulnerabilidade: ").strip().lower()

        for c in CategoriasVuln:
             print(c.name)

        try:
            codigo_categoria = input("Digite uma das categorias acima: ").strip().lower()
            tipo_categoria = CategoriasVuln(codigo_categoria)

        except ValueError:
            print("== Tipo nao identificado ==")
            return

        for s in Severidades:
            print(s.name, )

        try:
            codigo_severidade = input("Digite uma das severidades acima: ").strip().upper()
            tipo_severidade = Severidades[codigo_severidade]

        except KeyError:
            print("== Tipo nao identificado ==")
            return

        for st in Status:
            print(st.value)
        try:
            codigo_status = input("Digite um dos Status acima: ").strip().lower()
            tipo_status = Status(codigo_status)

        except ValueError:
            print("== Tipo nao identificado ==")
            return

        if not id_vuln or not descricao:
            print("== Esse campo nao deve ficar em branco ==")
            return

        print("== Confirmacao de dados ==")
        print(
        f"ID: {id_vuln}\n"
        f"Descricao: {descricao}\n"
        f"Categoria: {tipo_categoria.value}\n"
        f"Severidade: {tipo_severidade.name}\n"
        f"Status: {tipo_status.value}"
    )

        if not self.confirmar("=== Os dados acima estao corretos? ==="):
            print("== Cadastro cancelado ==")
            return

        nova_vuln = Vulnerabilidade(
            id_vuln,
            descricao,
            tipo_categoria,
            tipo_severidade,
            tipo_status
    )
        self.inventario.adicionar_vulnerabilidade(nova_vuln)
        print("== Vulnerabilidade adcionada com sucesso ==")

    def tela_busca_vulnerabilidade(self):
        self.id_vuln_mostrar_vuln()
        print("=== Esses são os ID's cadastrados ===")
        id_busca = input("=== Escolha um dos IDs acima para visualizar: ").strip()
        if not id_busca:
            print("=== Esse campo não pode ficar em branco tente novamente ===")
            return
        resultado = self.inventario.buscar_vulnerabilidade(id_busca)
        if not resultado:
            print("=== ID nao identificado ===")
            return
        print(resultado.descrever_vuln())    

    def tela_editar_remover_vulnerabilidade(self):
        print("Esses sao os IDs disponiveis para serem editados ou removidos:")
        self.id_vuln_mostrar_vuln()
        id_vuln = input("Escolha alguma das opcoes acima: ").strip()
        if not id_vuln:
            print("== Esse campo nao pode ficar em branco ==")
            return
        vuln = self.inventario.vulnerabilidade(id_vuln)

        if not vuln:
            print("== ID de vulnerabilidade nao encontrado ==")
            return
        print(vuln.descrever_vuln())

        opcao = input("Oque voce deseja fazer?\n EDITAR(1) | REMOVER (2) ").strip()

        if opcao == "1":
            id_vuln_novo = input("Escolha um novo iD para a vulnerabilidade(Caso queira manter pressione enter): ").strip() or None
            if id_vuln_novo and id_vuln_novo != id_vuln:
                if self.inventario.buscar_vulnerabilidade(id_vuln_novo):
                    print("== ID previamente cadastrado")
                    return
            descricao_novo = input("Coloque uma nova descricao para a vulnerabilidade(Caso queira manter pressione enter):  ").strip().lower() or None
            print("== Essas sao as categorias disponiveis ==")
            for c in CategoriasVuln:
                print(c.name)
            categoria_nova = input("Coloque uma nova categoria para a vulnerabilidade(Caso queira manter pressione enter): ").strip().lower() or None
            tipo_categoria = None
            if categoria_nova:
                try:
                    tipo_categoria = CategoriasVuln(categoria_nova)
                except ValueError:
                    print("=== Categoria nao identificada ==")
                    return
            print("== Esses sao os tipos disponiveis ==")    
            for sev in Severidades:
                print(sev.name )

            severidade_nova = input("Coloque uma nova severidade para a vulnerabilidade(Caso queira manter pressione enter): ").strip().upper()
            tipo_severidade = None
            if severidade_nova:
                try: 
                    tipo_severidade = Severidades(severidade_nova)
                except ValueError:
                    print("=== Categoria nao identificada ===")
                    return

            print("== Esses sao os tipos disponiveis ==")

            for st in Status:
                print(st.value)

            status_novo = input("== Coloque um novo status para a vulnerabilidade(Caso queira manter pressione enter): ").strip().lower()
            tipo_status = None

            if status_novo:
                try:
                    tipo_status = Status(status_novo)
                except ValueError:
                    print("=== Categoria nao identificada ===")
                    return

            id_exibir_vuln = id_vuln_novo or vuln.id_vuln
            descricao_exibir = descricao_novo or vuln.descricao
            categoria_exibir = categoria_nova or vuln.categoria
            severidade_exibir = severidade_nova or vuln.severidade
            status_exibir = status_novo or vuln.status

            print("== Confirmacao de dados ==")
            print(f"O id da vulnerabilidade está correto -> {id_exibir_vuln}?\n A descricao esta correta -> {descricao_exibir}?\n A categoria esta correta -> {categoria_exibir}?\n A severidade esta correta {severidade_exibir}?\n O status esta correto?{status_exibir}")
            if not self.confirmar("== Os dados estao corretos? =="):
                print("=== Edicao cancelada ===")
                return
            if self.inventario.editar_vulnerabilidade(id_vuln,id_vuln_novo,descricao_novo,categoria_nova, severidade_nova, status_novo):
                print("== Vulnerabilidade editada ==")
            else:
                print("=== Nao foi possivel editar a vulnerabilidade ===")
                return

        elif opcao == "2":
            if not self.confirmar("== Deseja realmente deletar a vulnerabilidade? =="):
                print("=== Remocao cancelada ===")
                return
            if self.inventario.remover_vulnerabilidade(id_vuln):
                print("== Vulnerabilidade removida ==")
            else:
                print("=== Nao foi possivel remover a vulnerabilidade ===")
                return
        else:
            print("=== Opcao invalida ===")
  
    def tela_vincular_vulnerabilidades(self):
        self.id_vuln_mostrar_vuln()
        self.id_ativo_mostrar_ativo()
        id_ativo = input("Digite o ID do ativo: ").strip()
        id_vuln = input("Digite o ID da vulnerabilidade: ").strip()

        if not id_vuln or not id_ativo:
            print("== Esses campos não podem ficar em branco ==")
            return

        if not self.confirmar("Vincular? "):
            print("== Cancelado ==")
            return

        if self.inventario.vincular_vulnerabilidade(id_vuln, id_ativo):
            print("== Vinculado! ==")

        else: print("== ID não encontrado ==")


    def tela_vincular_dependencia(self):

        

        print("=== Vinculo de dependencias ===")
        print("=== ID`s disponiveis -->")
        self.id_ativo_mostrar_ativo()

        id_alvo = input("escolha o ID da vulnerabilidade para ser cadastrado alguma dependencia: ").strip().lower()
        id_origem = input("escolha o ID da vulnerabilidade para dependencia do ativo acima: ").strip().lower()

        if not id_alvo or not id_origem:
            print("=== esses campos nao podem ficar em branco ===")
            return

        ativo_alvo = self.inventario.buscar_equipamento(id_alvo)
        ativo_origem = self.inventario.buscar_equipamento(id_origem)

        if not ativo_alvo or not ativo_origem:
            print("=== Um ativo ou ambos nao identificados ===")
            return 
        try:
            peso = float(input("Adicione um peso para vulnerabilidade EX: 0.3, (O valor nao pode ser igual ou maior que 1): ") ).strip()

        except ValueError:
            print("== O valor tem que estar em decimal ex: 0.3 == ")
            return
            
        self.inventario.vincular_dependencia(id_alvo, id_origem, peso)
        print("== Dependencia cadastrada com sucesso ==")
        
        






inventario = Inventario()
menu = Menu(inventario)
menu.opcao_selecionada()    
