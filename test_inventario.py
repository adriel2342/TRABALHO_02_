import unittest
from menu import Menu
from inventario import Inventario
from equipamentos import Servidor_Web, Notebook, Roteador
from unittest.mock import patch
from pathlib import Path
from vulnerabilidades import Vulnerabilidade
import numpy as np
import tempfile

from enums import CategoriasVuln, Status, Severidades

class TesteInventario(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.arquivo_temp = Path(self.temp_dir.name) / "teste_ativos.json"
        
        self.inv = Inventario()
        self.inv.ARQUIVOS_DADOS = self.arquivo_temp
        self.inv.equipamentos.clear()
        self.inv.vulnerabilidades.clear()




    def tearDown(self):
        if self.arquivo_temp.exists():
            self.temp_dir.cleanup()

    def teste_busca_ativos(self):

        servidor = Servidor_Web("1",'PC-FINANCEIRO-01',"adriel","192.168.100.10")

        self.inv.adicionar_equipamento(servidor)

        encontrado = self.inv.buscar_equipamento("1")

        self.assertIsNotNone(encontrado)
        self.assertEqual(encontrado.nome, 'PC-FINANCEIRO-01')


    def teste_busca_vulnerabilidade(self):

        vulnerabilidade = Vulnerabilidade ("1", "teclado com defeito",CategoriasVuln.Hardware, Severidades.ALTA, Status.em_aberto)

        self.inv.adicionar_vulnerabilidade(vulnerabilidade)

        encontrado = self.inv.buscar_vulnerabilidade("1")

        self.assertIsNotNone(encontrado)

        self.assertEqual(encontrado.descricao, "teclado com defeito")
        nao_econtrado = self.inv.buscar_vulnerabilidade("2")
        self.assertIsNone(nao_econtrado)

        with self.assertRaises(ValueError):
            Status("em_aberto")

        vuln_econtrada = self.inv.buscar_vulnerabilidade("1")

        self.assertIsNotNone(vuln_econtrada)
        self.assertEqual(vuln_econtrada.severidade.name, "ALTA")



    def teste_criar_remover_ativo(self):

        equipamento = Notebook("2", "PC-FINANCEIRO-03","Adriel","192.168.100.5")
        self.inv.adicionar_equipamento(equipamento)


        self.assertEqual(equipamento.id_ativo, "2")

        self.assertIsNotNone(equipamento)

        removeu = self.inv.remover_equipamento("2")

        self.assertTrue(removeu)


        self.assertIsNone(self.inv.buscar_equipamento("2"))



    def teste_criar_remover_vulnerabilidade(self):

        vulnerabilidade = Vulnerabilidade("1", "software desuatulizado", CategoriasVuln.Software, Severidades.ALTA,Status.em_aberto)

        self.inv.adicionar_vulnerabilidade(vulnerabilidade)

        self.assertIsNotNone(self.inv.buscar_vulnerabilidade("1"))

        self.assertEqual(vulnerabilidade.categoria.value, "software"  )


        removeu = self.inv.remover_vulnerabilidade("1")

        self.assertTrue(removeu)

        self.assertIsNone(self.inv.buscar_vulnerabilidade("1"))



    def teste_editar_vulnerabilidade(self):
        vulnerabilidade = Vulnerabilidade("1", "software desuatulizado",CategoriasVuln.Software, Severidades.ALTA, Status.em_aberto )

        self.inv.adicionar_vulnerabilidade(vulnerabilidade)

        self.assertEqual(vulnerabilidade.id_vuln, "1")

        editar = self.inv.editar_vulnerabilidade("1", descricao_novo="software com falhas")
        self.assertTrue(editar)


           
        editado = self.inv.buscar_vulnerabilidade("1")
        self.assertEqual(editado.descricao, "software com falhas")


        self.assertEqual(editado.categoria.value, "software")

        with self.assertRaises(ValueError):
            CategoriasVuln("pc")



    def teste_editar_equipamento(self):

        equipamento = Notebook("1","PC-FINANCEIRO-01", "adriel","192.168.100.10")

        self.inv.adicionar_equipamento(equipamento)

        encontrado = self.inv.buscar_equipamento("1")

        self.assertEqual(encontrado.nome, "PC-FINANCEIRO-01")

        editar = self.inv.editar_equipamento("1", nome_novo="PC-FINANCEIRO-02")

        self.assertTrue(editar)


        editado = self.inv.buscar_equipamento("1")

        self.assertEqual(editado.nome, "PC-FINANCEIRO-02")

        self.assertNotEqual(editado.nome, "PC-FINANCEIRO-01")

        self.assertEqual(editado.responsavel, "adriel")



    def teste_risco_proprio(self):
        ativo = Notebook("1","PC-FINANCEIRO-03", "adriel", "192.168.100.12")
        vulnerabilidade = Vulnerabilidade("1", "teclado com problema", CategoriasVuln.Hardware, Severidades.BAIXA, Status.em_aberto)

        ativo2 = Servidor_Web("2", "MAIN_WEB", "alexandre", "192.168.100.4" )
        vulnerabillidade2 = Vulnerabilidade("2", "servidor fora do ar", CategoriasVuln.Software, Severidades.CRITICA, Status.em_tratamento)

        notebook_limpo = Notebook("3", "NB_LIMPO", "adriel", "192.168.100.45")

        self.inv.adicionar_equipamento(ativo)
        self.inv.adicionar_vulnerabilidade(vulnerabilidade)

        self.inv.adicionar_equipamento(ativo2)
        self.inv.adicionar_vulnerabilidade(vulnerabillidade2)

        self.inv.adicionar_equipamento(notebook_limpo)

        vinculado = self.inv.vincular_vulnerabilidade("1","1")
        vinculado2 = self.inv.vincular_vulnerabilidade("2","2")

        self.assertTrue(vinculado)
        self.assertTrue(vinculado2)

        risco = self.inv.vetor_risco_proprio()

        self.assertAlmostEqual(risco[0], 2.00)

        self.assertNotAlmostEqual(risco[0], 3.40)
        
        self.assertAlmostEqual(risco[1], 14.25)

        self.assertNotAlmostEqual(risco[1], 15.25)

        self.assertAlmostEqual(risco[2], 0.0)


    def teste_vincular_dependencia(self):

        note = Notebook("1", "PC-FINANCEIRO-02", "adriel", "192.168.100.10")

        rote= Roteador("2", "ROTEADOR-SECRETARIA", "katiane", "192.168.100.1")

        sw = Servidor_Web("3", "MAIN-SERVER", "alexandre", "192.168.100.65")


        self.inv.adicionar_equipamento(note)

        self.inv.adicionar_equipamento(rote)

        self.inv.adicionar_equipamento(sw)


        self.assertTrue(self.inv.vincular_dependencia("2","1",0.4))

        self.assertFalse(self.inv.vincular_dependencia("1","1",0.2))

        self.assertFalse(self.inv.vincular_dependencia("2","3",0.6))

        self.assertTrue(self.inv.vincular_dependencia("2","3", 0.5  ))




    def propagacao_de_risco_numpy(self):

        web = Servidor_Web("1","MAIN-SERVER","adriel","192.168.100.10")
        nt = Notebook("2", "NB-O1", "adriel", "192.168.100.5")

        vuln = Vulnerabilidade("1","falha ssl", CategoriasVuln.Software, Severidades.MEDIA, Status.em_tratamento)


        self.inv.adicionar_equipamento(web)

        self.inv.adicionar_equipamento(nt)

        self.inv.adicionar_vulnerabilidade(vuln)

        self.inv.vincular_vulnerabilidade("1","2")

        self.inv.c=self.teste_vincular_dependencia*("2","1",0.5)

        risco_total = (self.inv.matriz_I_A())

        self.assertAlmostEqual(risco_total[0], 7.5)  # ---> mantem 7.5 pois nao tem uma deoendencia em si para ser multiplicada
        self.assertAlmostEqual(risco_total[1], 3.75) #--> tem uma dependencia 0.5 * 7.5 (3.75)

        


        self.inv.vincular_dependencia()
        
        



            

    



if __name__ == "__main__":
    unittest.main()




