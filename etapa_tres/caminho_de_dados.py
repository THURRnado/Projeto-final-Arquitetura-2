from ula import ULA

class CaminhoDeDados:
    """
    Gerencia o caminho de dados (datapath) conectando os registradores à ULA
    e à Memória Principal, interpretando microinstruções de 23 bits.
    """
    def __init__(self):
        self.ula = ULA()
        
        self.ordem_regs = ['mar', 'mdr', 'pc', 'mbr', 'sp', 'lv', 'cpp', 'tos', 'opc', 'h']
        self.regs = {reg.upper(): 0 for reg in self.ordem_regs}
        
        # Inicia a memória de dados (RAM) vazia
        self.memoria = []

    def formatar_regs(self):
        """Formata o estado atual de todos os registradores para o log."""
        linhas = []
        for reg in self.ordem_regs:
            val = self.regs[reg.upper()]
            if reg == 'mbr':
                linhas.append(f"{reg} = {val:08b}")
            else:
                linhas.append(f"{reg} = {val & 0xFFFFFFFF:032b}")
        return "\n".join(linhas)

    def formatar_memoria(self):
        """Formata o estado atual da memória de dados para o log."""
        return "\n".join(self.memoria)

    def carregar_memoria(self, caminho_arquivo):
        """Lê o arquivo de dados para a memória RAM simulada."""
        try:
            with open(caminho_arquivo, 'r') as f:
                self.memoria = [linha.strip() for linha in f.readlines() if linha.strip()]
        except FileNotFoundError:
            pass

    def carregar_registradores(self, caminho_arquivo):
        """Lê um arquivo de configuração para injetar os estados iniciais."""
        try:
            with open(caminho_arquivo, 'r') as f:
                for linha in f:
                    linha = linha.strip()
                    if linha and '=' in linha:
                        reg, val = linha.split('=')
                        self.regs[reg.strip().upper()] = int(val.strip(), 2)
        except FileNotFoundError:
            pass

    def decodificar_barramento_b(self, bits_b):
        """Decodifica os 4 bits para selecionar quem vai para a entrada B da ULA."""
        codigo = int(bits_b, 2)
        tabela_b = {
            0: 'mdr', 1: 'pc', 2: 'mbr', 3: 'mbru', 
            4: 'sp', 5: 'lv', 6: 'cpp', 7: 'tos', 8: 'opc'
        }
        nome_reg = tabela_b.get(codigo, None)
        valor_b = 0

        if nome_reg == 'mbr':
            # Extensão de sinal para o MBR
            mbr_val = self.regs['MBR']
            if mbr_val & 0x80: 
                valor_b = mbr_val | 0xFFFFFF00
            else:
                valor_b = mbr_val
        elif nome_reg == 'mbru':
            valor_b = self.regs['MBR']
        elif nome_reg is not None:
            valor_b = self.regs[nome_reg.upper()]

        return nome_reg, valor_b

    def escrever_barramento_c(self, bits_c, valor):
        """Escreve a saída da ULA nos registradores habilitados pelos 9 bits."""
        regs_escritos = []
        mapeamento = ['h', 'opc', 'tos', 'cpp', 'lv', 'sp', 'pc', 'mdr', 'mar']
        
        for i in range(9):
            if bits_c[i] == '1':
                nome_reg = mapeamento[i]
                self.regs[nome_reg.upper()] = valor
                
                # Mantém o MBR restrito a 8 bits
                if nome_reg == 'mbr':
                    self.regs['MBR'] &= 0xFF 
                    
                regs_escritos.append(nome_reg)
                
        return regs_escritos

    def executar_ciclo(self, instrucao_23_bits, file_out):
        """Executa um ciclo completo interpretando 23 bits de controle."""
        # Fatiamento da instrução de 23 bits
        ctrl_ula = instrucao_23_bits[0:8]
        ctrl_c   = instrucao_23_bits[8:17]
        ctrl_mem = instrucao_23_bits[17:19]
        ctrl_b   = instrucao_23_bits[19:23]

        # --- CASO ESPECIAL (Entregável: BIPUSH fetch) ---
        if ctrl_mem == '11':
            file_out.write(f"ir = {ctrl_ula} {ctrl_c} {ctrl_mem} {ctrl_b}\n")
            file_out.write("> SPECIAL FETCH INSTRUCTION: H = MBR\n\n")
            
            file_out.write("> Registers before instruction\n*******************************\n")
            file_out.write(self.formatar_regs() + "\n\n")
            
            # O argumento da instrução vem disfarçado nos bits da ULA
            byte_val = int(ctrl_ula, 2)
            self.regs['MBR'] = byte_val
            self.regs['H'] = byte_val
            
            file_out.write("> Registers after instruction\n*******************************\n")
            file_out.write(self.formatar_regs() + "\n\n")
            
            file_out.write("> Memory after instruction\n*******************************\n")
            file_out.write(self.formatar_memoria() + "\n")
            return # Encerra o ciclo antecipadamente
            
        # --- FLUXO NORMAL (Etapa 3 Tarefa 1) ---
        # 1. Configura Barramento B e loga a instrução
        reg_b_nome, valor_b = self.decodificar_barramento_b(ctrl_b)
        
        file_out.write(f"ir = {ctrl_ula} {ctrl_c} {ctrl_mem} {ctrl_b}\n")
        file_out.write(f"b = {reg_b_nome}\n")
        
        regs_c_nomes = [nome for i, nome in enumerate(['h', 'opc', 'tos', 'cpp', 'lv', 'sp', 'pc', 'mdr', 'mar']) if ctrl_c[i] == '1']
        file_out.write(f"c = {', '.join(regs_c_nomes) if regs_c_nomes else 'none'}\n\n")

        # 2. Fotografia antes da execução
        file_out.write("> Registers before instruction\n")
        file_out.write("*******************************\n")
        file_out.write(self.formatar_regs() + "\n\n")

        # 3. ULA (Entrada A sempre ligada ao registrador H)
        self.ula.carregar_entradas(self.regs['H'], valor_b)
        self.ula.decodificar_instrucao(ctrl_ula)
        self.ula.executar()

        # 4. Barramento C (escrita nos registradores)
        self.escrever_barramento_c(ctrl_c, self.ula.saida_s)

        # 5. Memória (WRITE e READ ocorrem após o cálculo da ULA)
        write_bit = ctrl_mem[0]
        read_bit = ctrl_mem[1]
        mar_val = self.regs['MAR']

        if read_bit == '1': # READ
            if 0 <= mar_val < len(self.memoria):
                self.regs['MDR'] = int(self.memoria[mar_val], 2)
                
        if write_bit == '1': # WRITE
            if 0 <= mar_val < len(self.memoria):
                self.memoria[mar_val] = f"{self.regs['MDR'] & 0xFFFFFFFF:032b}"

        # 6. Fotografias pós-execução
        file_out.write("> Registers after instruction\n")
        file_out.write("*******************************\n")
        file_out.write(self.formatar_regs() + "\n\n")
        
        file_out.write("> Memory after instruction\n")
        file_out.write("*******************************\n")
        file_out.write(self.formatar_memoria() + "\n")