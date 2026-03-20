# Classe que representa a Unidade Lógica Aritmética (ULA)
# A ULA é responsável por executar operações lógicas e aritméticas baseadas em sinais de controle
class ULA:
    def __init__(self):
        # Sinais de Controle (extraídos da instrução de 6 bits)
        # Estes sinais determinam qual operação a ULA executará
        self.f0 = 0  # Bit 0 da instrução: parte do código de função (F0)
        self.f1 = 0  # Bit 1 da instrução: parte do código de função (F1)
        self.ena = 0  # Bit 2: Enable A (habilita ou desabilita a entrada A)
        self.enb = 0  # Bit 3: Enable B (habilita ou desabilita a entrada B)
        self.inva = 0  # Bit 4: Inverte A (inverte os bits de A se ativado)
        self.inc = 0  # Bit 5: Incremento (adiciona 1 na soma se ativado)

        # Entradas Originais (valores recebidos do programa principal)
        self.a = 0  # Entrada A (32 bits)
        self.b = 0  # Entrada B (32 bits)

        # Entradas Internas (após aplicação dos sinais de controle ENA, ENB e INVA)
        # Estes valores são salvos para exibir no log de saída
        self.a_interno = 0  # Valor de A após enable e inversão
        self.b_interno = 0  # Valor de B após enable

        # Saídas da ULA
        self.saida_s = 0  # Saída principal S (resultado da operação, 32 bits)
        self.vai_um = 0   # Carry out (vai-um): sinal de overflow na soma

        # Máscara para garantir que todas as operações sejam limitadas a 32 bits
        self.MASK_32 = 0xFFFFFFFF  # 32 bits de '1' em hexadecimal

    # Método que decodifica a instrução binária de 6 bits
    # Extrai os sinais de controle da string de bits fornecida
    def decodificar_instrucao(self, instrucao_bits):
        # Converte cada caractere da string em inteiro e atribui aos sinais
        self.f0 = int(instrucao_bits[0])    # Primeiro bit: F0
        self.f1 = int(instrucao_bits[1])    # Segundo bit: F1
        self.ena = int(instrucao_bits[2])   # Terceiro bit: ENA
        self.enb = int(instrucao_bits[3])   # Quarto bit: ENB
        self.inva = int(instrucao_bits[4])  # Quinto bit: INVA
        self.inc = int(instrucao_bits[5])   # Sexto bit: INC

    # Método que carrega os valores de entrada A e B na ULA
    # Estes valores vêm do programa principal e são armazenados temporariamente
    def carregar_entradas(self, valor_a, valor_b):
        self.a = valor_a  # Carrega o valor para entrada A
        self.b = valor_b  # Carrega o valor para entrada B

    # Método principal que executa a operação baseada nos sinais de controle
    # Aplica enables, inversão e depois executa a função lógica/aritmética
    def executar(self):
        # Aplica os sinais ENA (enable A) e INVA (inverte A), salvando para log
        # Se ENA=0, A é forçado a 0; se INVA=1, A é invertido (NOT)
        a_ativo = self.a if self.ena else 0  # A só passa se ENA=1
        self.a_interno = (~a_ativo & self.MASK_32) if self.inva else a_ativo  # Inverte se INVA=1

        # Aplica o sinal ENB (enable B)
        # Se ENB=0, B é forçado a 0
        self.b_interno = self.b if self.enb else 0  # B só passa se ENB=1

        # Reseta o carry out para a nova operação
        self.vai_um = 0

        # Decodifica a função baseada em F0 e F1 (código de função de 2 bits)
        # F1 F0 | Operação
        #  0  0  | AND (E lógico)
        #  0  1  | OR (OU lógico)
        #  1  0  | NOT B (negação de B)
        #  1  1  | Soma (A + B + INC)

        if self.f0 == 0 and self.f1 == 0:
            # Operação AND: S = A AND B
            self.saida_s = (self.a_interno & self.b_interno) & self.MASK_32
        elif self.f0 == 0 and self.f1 == 1:
            # Operação OR: S = A OR B
            self.saida_s = (self.a_interno | self.b_interno) & self.MASK_32
        elif self.f0 == 1 and self.f1 == 0:
            # Operação NOT B: S = NOT B (ignora A)
            self.saida_s = (~self.b_interno) & self.MASK_32
        elif self.f0 == 1 and self.f1 == 1:
            # Operação Soma: S = A + B + INC (com carry out se overflow)
            soma = self.a_interno + self.b_interno + self.inc  # Soma com possível carry-in
            self.saida_s = soma & self.MASK_32  # Resultado limitado a 32 bits
            if soma > self.MASK_32:  # Se houve overflow (soma > 2^32 - 1)
                self.vai_um = 1  # Seta o carry out