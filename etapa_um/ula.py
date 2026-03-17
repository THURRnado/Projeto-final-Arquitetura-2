class ULA:
    def __init__(self):
        # Sinais de Controle
        self.f0 = 0
        self.f1 = 0
        self.ena = 0
        self.enb = 0
        self.inva = 0
        self.inc = 0
        
        # Entradas Originais
        self.a = 0
        self.b = 0
        
        # Entradas Internas (após ENA, ENB e INVA) para exibir no log
        self.a_interno = 0
        self.b_interno = 0
        
        # Saídas
        self.saida_s = 0
        self.vai_um = 0
        
        self.MASK_32 = 0xFFFFFFFF

    def decodificar_instrucao(self, instrucao_bits):
        self.f0 = int(instrucao_bits[0])
        self.f1 = int(instrucao_bits[1])
        self.ena = int(instrucao_bits[2])
        self.enb = int(instrucao_bits[3])
        self.inva = int(instrucao_bits[4])
        self.inc = int(instrucao_bits[5])

    def carregar_entradas(self, valor_a, valor_b):
        self.a = valor_a
        self.b = valor_b

    def executar(self):
        # Aplica os Enables e INVA, salvando os valores para o log
        a_ativo = self.a if self.ena else 0
        self.b_interno = self.b if self.enb else 0
        
        self.a_interno = (~a_ativo & self.MASK_32) if self.inva else a_ativo

        # Decodificador e Unidade Lógica/Somador
        self.vai_um = 0
        if self.f0 == 0 and self.f1 == 0:
            self.saida_s = (self.a_interno & self.b_interno) & self.MASK_32
        elif self.f0 == 0 and self.f1 == 1:
            self.saida_s = (self.a_interno | self.b_interno) & self.MASK_32
        elif self.f0 == 1 and self.f1 == 0:
            self.saida_s = (~self.b_interno) & self.MASK_32
        elif self.f0 == 1 and self.f1 == 1:
            soma = self.a_interno + self.b_interno + self.inc
            self.saida_s = soma & self.MASK_32
            if soma > self.MASK_32:
                self.vai_um = 1