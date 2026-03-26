from ula import ULA

class CaminhoDeDados:
    """
    Gerencia o caminho de dados (datapath) conectando os registradores à ULA
    através dos barramentos B e C, interpretando microinstruções de 21 bits.
    """
    def __init__(self):
        self.ula = ULA()
        
        # A ordem desta lista foi definida para garantir que a saída de formatação (log) 
        # obedeça exatamente a sequência requisitada pelo avaliador/projeto.
        self.ordem_regs = ['mar', 'mdr', 'pc', 'mbr', 'sp', 'lv', 'cpp', 'tos', 'opc', 'h']
        
        # Inicializa todos os 10 registradores com o valor 0.
        self.regs = {reg.upper(): 0 for reg in self.ordem_regs}

    def formatar_regs(self):
        """
        Formata o estado atual de todos os registradores para exibição no log.
        Os registradores de 32 bits são exibidos em formato binário de 32 posições.
        O registrador MBR é formatado para 8 bits, refletindo seu tamanho físico arquitetural.
        """
        linhas = []
        for reg in self.ordem_regs:
            val = self.regs[reg.upper()]
            if reg == 'mbr':
                linhas.append(f"{reg} = {val:08b}")
            else:
                linhas.append(f"{reg} = {val & 0xFFFFFFFF:032b}")
        return "\n".join(linhas)

    def decodificar_barramento_b(self, bits_b):
        """
        Decodificador de 4 bits responsável por habilitar um registrador
        a escrever o seu valor no Barramento B (Entrada B da ULA).
        """
        codigo = int(bits_b, 2)
        
        # Tabela de mapeamento do código de 4 bits para o respectivo registrador.
        tabela_b = {
            0: 'mdr', 1: 'pc', 2: 'mbr', 3: 'mbru', 
            4: 'sp', 5: 'lv', 6: 'cpp', 7: 'tos', 8: 'opc'
        }
        nome_reg = tabela_b.get(codigo, None)
        valor_b = 0

        # Tratamento especial para o registrador MBR que tem apenas 8 bits
        # e precisa ser expandido para 32 bits antes de entrar na ULA.
        if nome_reg == 'mbr':
            # MBR: Expansão com extensão de sinal. 
            # Se o bit mais significativo (bit 7) for 1, preenche os bits superiores com 1.
            mbr_val = self.regs['MBR']
            if mbr_val & 0x80: 
                valor_b = mbr_val | 0xFFFFFF00
            else:
                valor_b = mbr_val
        elif nome_reg == 'mbru':
            # MBRU: Expansão sem sinal.
            # Preenche os bits superiores (bits de 8 a 31) com zeros.
            valor_b = self.regs['MBR']
            
        elif nome_reg is not None:
            # Para todos os outros registradores de 32 bits, o valor passa diretamente.
            valor_b = self.regs[nome_reg.upper()]

        return nome_reg, valor_b

    def escrever_barramento_c(self, bits_c, valor):
        """
        Seletor de 9 bits responsável por habilitar múltiplos registradores
        para armazenarem a saída produzida pela ULA (Barramento C).
        """
        regs_escritos = []
        # Convenção do mapeamento de leitura: o bit do índice 0 da string 
        # (bit 8 do valor numérico) corresponde a H, e assim sucessivamente.
        mapeamento = ['h', 'opc', 'tos', 'cpp', 'lv', 'sp', 'pc', 'mdr', 'mar']
        
        for i in range(9):
            if bits_c[i] == '1':
                nome_reg = mapeamento[i]
                self.regs[nome_reg.upper()] = valor
                
                # Garante fisicamente que o MBR mantenha apenas sua largura de 8 bits
                # mesmo se for escrito através de um barramento de 32 bits.
                if nome_reg == 'mbr':
                    self.regs['MBR'] &= 0xFF 
                    
                regs_escritos.append(nome_reg)
                
        return regs_escritos

    def carregar_registradores(self, caminho_arquivo):
        """
        Lê um arquivo de configuração para injetar os estados iniciais dos registradores.
        Assume que as linhas do arquivo possuem o formato 'REG = VALOR_BINARIO'.
        """
        try:
            with open(caminho_arquivo, 'r') as f:
                for linha in f:
                    linha = linha.strip()
                    if linha and '=' in linha:
                        reg, val = linha.split('=')
                        # Converte a representação de texto binária para valor inteiro
                        self.regs[reg.strip().upper()] = int(val.strip(), 2)
        except FileNotFoundError:
            # Caso não exista arquivo, utiliza os registradores zerados da inicialização
            pass

    def executar_ciclo(self, instrucao_21_bits, file_out):
        """
        Executa um ciclo completo de instrução manipulando o Caminho de Dados.
        """
        # Divisão da instrução de 21 bits em seções de controle:
        # 8 bits para controle ULA, 9 bits para escrita (C), 4 bits para leitura (B).
        ctrl_ula = instrucao_21_bits[0:8]
        ctrl_c = instrucao_21_bits[8:17]
        ctrl_b = instrucao_21_bits[17:21]

        # Inicia a anotação de log do ciclo atual
        file_out.write(f"ir = {ctrl_ula} {ctrl_c} {ctrl_b}\n\n")

        # Configura Barramento B (quem envia os dados para a entrada B)
        reg_b_nome, valor_b = self.decodificar_barramento_b(ctrl_b)
        file_out.write(f"b_bus = {reg_b_nome}\n")
        
        # Identifica e lista os registradores habilitados pelo Barramento C
        regs_c_nomes = [nome for i, nome in enumerate(['h', 'opc', 'tos', 'cpp', 'lv', 'sp', 'pc', 'mdr', 'mar']) if ctrl_c[i] == '1']
        file_out.write(f"c_bus = {', '.join(regs_c_nomes) if regs_c_nomes else 'none'}\n\n")

        # Exibe o estado da máquina antes da operação da ULA
        file_out.write("> Registers before instruction\n")
        file_out.write(self.formatar_regs() + "\n\n")

        # Configuração das entradas da ULA. 
        # A entrada A é conectada fisicamente ao registrador H em todos os ciclos.
        # A entrada B recebe o valor derivado do Barramento B.
        self.ula.carregar_entradas(self.regs['H'], valor_b)
        
        # Execução do processamento de dados (ULA + Shifter)
        self.ula.decodificar_instrucao(ctrl_ula)
        self.ula.executar()

        # O resultado da ULA é enviado pelo Barramento C para sobrescrever os registradores habilitados.
        self.escrever_barramento_c(ctrl_c, self.ula.saida_s)

        # Exibe o estado da máquina após o processamento da instrução
        file_out.write("> Registers after instruction\n")
        file_out.write(self.formatar_regs() + "\n")