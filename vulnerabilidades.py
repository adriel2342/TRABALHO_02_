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
