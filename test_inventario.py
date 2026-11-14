import unittest
from menu import Menu
from inventario import Inventario
from equipamentos import Servidor_Web, Notebook
from unittest.mock import patch
import numpy as np
from pathlib import Path
from vulnerabilidades import Vulnerabilidade

from enums import CategoriasVuln, Status, Severidades

class TesteInventario(unittest.TestCase):

    def setUp(self):
        self.arquivo_temp = Path("teste_ativos.json")
        if self.arquivo_temp.exists():
            self.arquivo_temp.unlink()


        self.inv = Inventario()
        self.inv.ARQUIVOS_DADOS = self.arquivo_temp
        self.inv.equipamentos.clear()
        self.inv.vulnerabilidades.clear()




    def tearDown(self):
        if self.arquivo_temp.exists():
            self.arquivo_temp.unlink()

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


        self.assertIsNone(self.inv.buscar_vulnerabilidade("2"))



    def teste_criar_remover_vulnerabilidade(self):

        vulnerabilidade = Vulnerabilidade("1", "software desuatulizado", CategoriasVuln.Software, Severidades.ALTA,Status.em_aberto)

        self.inv.adicionar_vulnerabilidade(vulnerabilidade)

        self.assertIsNotNone(self.inv.buscar_vulnerabilidade("1"))

        self.assertEqual(vulnerabilidade.categoria.value, "software"  )




    



if __name__ == "__main__":
    unittest.main()




