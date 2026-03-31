from caminho_de_dados import CaminhoDeDados

def traduzir_instrucao(linha_asm):
    """Traduz uma instrução Assembly IJVM para uma lista de microinstruções de 23 bits."""
    partes = linha_asm.strip().split()
    cmd = partes[0].upper()
    micros = []

    if cmd == "ILOAD":
        x = int(partes[1])
        # 1. H = LV (S=B, B=LV, C=H)
        micros.append("00110100100000000000101")
        # 2. H = H + 1 (repetido x vezes) (S=A+1, C=H)
        for _ in range(x):
            micros.append("00111001100000000000000")
        # 3. MAR = H; rd (S=A, C=MAR, MEM=01)
        micros.append("00111000000000001010000")
        # 4. MAR = SP = SP + 1; wr (S=B+1, B=SP, C=MAR e SP, MEM=10)
        micros.append("00110101000001001100100")
        # 5. TOS = MDR (S=B, B=MDR, C=TOS)
        micros.append("00110100001000000000000")

    elif cmd == "DUP":
        # 1. MAR = SP = SP + 1 (S=B+1, B=SP, C=MAR e SP)
        micros.append("00110101000001001000100")
        # 2. MDR = TOS; wr (S=B, B=TOS, C=MDR, MEM=10)
        micros.append("00110100000000010100111")

    elif cmd == "BIPUSH":
        # Extrai o byte (suporta tanto binário direto quanto decimal)
        arg = partes[1]
        byte_bin = arg if set(arg).issubset({'0', '1'}) and len(arg) == 8 else format(int(arg), '08b')
        
        # 1. SP = MAR = SP + 1 (S=B+1, B=SP, C=MAR e SP)
        micros.append("00110101000001001000100")
        # 2. Fetch Especial (BYTE vai no lugar do ULA_CTRL, MEM=11)
        micros.append(f"{byte_bin}000000000110000")
        # 3. MDR = TOS = H; wr (S=A, A=H, C=MDR e TOS, MEM=10)
        micros.append("00111000001000010100000")
        
    return micros

def executar_entregavel():
    cd = CaminhoDeDados()
    
    # Arquivos de IO
    arq_dados = 'arquivos/dados_etapa3_tarefa1.txt'
    arq_regs = 'arquivos/registradores_etapa3_tarefa1.txt'
    arq_asm = 'arquivos/instrucoes.txt'
    arq_saida = 'arquivos/saida_entregavel.txt'
    
    cd.carregar_memoria(arq_dados)
    cd.carregar_registradores(arq_regs)
    
    try:
        with open(arq_asm, 'r') as f_in, open(arq_saida, 'w') as f_out:
            instrucoes_asm = [linha.strip() for linha in f_in.readlines() if linha.strip()]
            
            f_out.write("============================================================\n")
            f_out.write("INICIO DA EXECUCAO DO PROGRAMA IJVM\n")
            f_out.write("============================================================\n")
            
            ciclo_global = 1
            
            for linha_asm in instrucoes_asm:
                f_out.write(f"\n>> EXECUTANDO INSTRUCAO: {linha_asm} <<\n")
                f_out.write("------------------------------------------------------------\n")
                
                microinstrucoes = traduzir_instrucao(linha_asm)
                
                for micro in microinstrucoes:
                    f_out.write(f"Cycle {ciclo_global}\n")
                    cd.executar_ciclo(micro, f_out)
                    ciclo_global += 1
                    
        print(f"Sucesso! Código IJVM traduzido e executado. Log salvo em '{arq_saida}'.")
        
    except FileNotFoundError as e:
        print(f"Erro: Crie o arquivo '{e.filename}' com as instruções IJVM (ex: ILOAD 1).")

if __name__ == "__main__":
    executar_entregavel()