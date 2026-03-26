class ULA:
    """
    Simula a Unidade Lógica Aritmética (ULA) da máquina Mic-1 modificada.
    Responsável por processar dados de 32 bits através de operações lógicas, 
    aritméticas e de deslocamento de bits (shift).
    """
    def __init__(self):
        # Sinais de controle extraídos da palavra de 8 bits
        self.sll8 = 0  # Deslocamento lógico para a esquerda em 8 bits
        self.sra1 = 0  # Deslocamento aritmético para a direita em 1 bit
        self.f0 = 0    # Bit 0 de seleção da função principal
        self.f1 = 0    # Bit 1 de seleção da função principal
        self.ena = 0   # Habilita a entrada A (se 0, a entrada A é tratada como 0)
        self.enb = 0   # Habilita a entrada B (se 0, a entrada B é tratada como 0)
        self.inva = 0  # Inverte os bits da entrada A (complemento de 1)
        self.inc = 0   # Incrementa o resultado (soma 1, equivalente ao carry-in)

        # Entradas de dados (operandos de 32 bits)
        self.a = 0     
        self.b = 0     

        # Estados internos após a aplicação dos sinais ENA, ENB e INVA
        self.a_interno = 0  
        self.b_interno = 0  

        # Saídas
        self.saida_bruta = 0  # Resultado da operação antes do deslocamento
        self.saida_s = 0      # Resultado final após o deslocador (saída deslocada)
        self.vai_um = 0       # Carry-out (estouro de limite de 32 bits)
        self.n = 0            # Flag de Negativo (1 se o resultado final for negativo)
        self.z = 0            # Flag de Zero (1 se o resultado final for igual a zero)

        # Máscara utilizada para restringir os valores ao limite de 32 bits (evita overflow do Python)
        self.MASK_32 = 0xFFFFFFFF  

    def decodificar_instrucao(self, instrucao_bits):
        """
        Recebe uma string de 8 caracteres contendo '0's e '1's e distribui
        cada bit para seu respectivo sinal de controle interno.
        A ordem segue a arquitetura especificada: SLL8, SRA1, F0, F1, ENA, ENB, INVA, INC.
        """
        self.sll8 = int(instrucao_bits[0])
        self.sra1 = int(instrucao_bits[1])
        self.f0 = int(instrucao_bits[2])
        self.f1 = int(instrucao_bits[3])
        self.ena = int(instrucao_bits[4])
        self.enb = int(instrucao_bits[5])
        self.inva = int(instrucao_bits[6])
        self.inc = int(instrucao_bits[7])

    def carregar_entradas(self, valor_a, valor_b):
        """
        Carrega os valores vindos dos registradores/barramentos para a ULA.
        """
        self.a = valor_a
        self.b = valor_b

    def executar(self):
        """
        Executa a sequência completa de operações da ULA em um único ciclo:
        1. Verificação de regras arquiteturais restritas.
        2. Aplicação de habilitações e inversões nas entradas.
        3. Cálculo principal (Lógico ou Aritmético).
        4. Operação do deslocador (Shifter).
        5. Atualização das flags de status (Z e N).
        """
        # Regra da arquitetura: SLL8 e SRA1 não podem estar ativos simultaneamente.
        if self.sll8 == 1 and self.sra1 == 1:
            raise ValueError("> Error, invalid control signals.")

        # Tratamento da Entrada A: 
        # Passa pelo Enable (se 0, zera o valor) e depois pelo Inversor (se 1, faz o complemento NOT).
        a_ativo = self.a if self.ena else 0
        self.a_interno = (~a_ativo & self.MASK_32) if self.inva else a_ativo
        
        # Tratamento da Entrada B:
        # Passa apenas pelo Enable.
        self.b_interno = self.b if self.enb else 0
        
        # Reinicia o carry-out
        self.vai_um = 0

        # Lógica central baseada nos sinais F0 e F1
        if self.f0 == 0 and self.f1 == 0:
            # Função Lógica AND
            self.saida_bruta = (self.a_interno & self.b_interno) & self.MASK_32
        elif self.f0 == 0 and self.f1 == 1:
            # Função Lógica OR
            self.saida_bruta = (self.a_interno | self.b_interno) & self.MASK_32
        elif self.f0 == 1 and self.f1 == 0:
            # Função Lógica NOT B (Inverte a entrada B, ignora a entrada A)
            self.saida_bruta = (~self.b_interno) & self.MASK_32
        elif self.f0 == 1 and self.f1 == 1:
            # Função Aritmética de Soma: A + B + INC
            soma = self.a_interno + self.b_interno + self.inc
            self.saida_bruta = soma & self.MASK_32
            # Se a soma pura exceder o valor máximo de 32 bits, ativa o carry-out
            if soma > self.MASK_32:
                self.vai_um = 1

        # Etapa do Deslocador (Shifter)
        # O deslocamento ocorre após o cálculo do resultado bruto.
        saida_deslocada = self.saida_bruta
        
        if self.sll8 == 1:
            # Deslocamento Lógico para a Esquerda em 8 bits (Shift Left Logical).
            # Preenche os novos bits à direita com zeros.
            saida_deslocada = (self.saida_bruta << 8) & self.MASK_32
        elif self.sra1 == 1:
            # Deslocamento Aritmético para a Direita em 1 bit (Shift Right Arithmetic).
            # Diferente do deslocamento lógico, o aritmético preserva o bit de sinal mais significativo (bit 31).
            bit_sinal = self.saida_bruta & 0x80000000
            saida_deslocada = (self.saida_bruta >> 1) | bit_sinal

        # Define a saída final do ciclo da ULA
        self.saida_s = saida_deslocada

        # Atualização das Flags
        # Z = 1 se todos os bits do resultado final forem 0.
        self.z = 1 if self.saida_s == 0 else 0
        # N = 1 se o resultado final for negativo (ou seja, se o bit mais significativo, bit 31, for 1).
        self.n = 1 if (self.saida_s & 0x80000000) != 0 else 0