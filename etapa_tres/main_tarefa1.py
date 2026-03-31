from caminho_de_dados import CaminhoDeDados

def executar_tarefa1():
    # Instancia a arquitetura completa
    cd = CaminhoDeDados()
    
    # Caminhos dos arquivos (ajuste conforme sua estrutura de pastas)
    arq_dados = 'arquivos/dados_etapa3_tarefa1.txt'
    arq_instrucoes = 'arquivos/microinstruções_etapa3_tarefa1.txt'
    arq_regs = 'arquivos/registradores_etapa3_tarefa1.txt'
    arq_saida = 'arquivos/saída_etapa3_tarefa1.txt'
    
    # Carrega a memória e os registradores ANTES de abrir o log [cite: 150]
    cd.carregar_memoria(arq_dados)
    cd.carregar_registradores(arq_regs)
    
    try:
        with open(arq_instrucoes, 'r') as f_in, open(arq_saida, 'w') as f_out:
            linhas = [linha.strip() for linha in f_in.readlines() if linha.strip()]
            
            # --- Cabeçalho Inicial (Idêntico ao gabarito) ---
            f_out.write("============================================================\n")
            f_out.write("Initial memory state\n")
            f_out.write("*******************************\n")
            f_out.write(cd.formatar_memoria() + "\n")
            f_out.write("*******************************\n")
            f_out.write("Initial register state\n")
            f_out.write("*******************************\n")
            f_out.write(cd.formatar_regs() + "\n")
            f_out.write("============================================================\n")
            f_out.write("Start of Program\n")
            f_out.write("============================================================\n")
            
            # --- Execução dos Ciclos ---
            for ciclo, instrucao in enumerate(linhas, 1):
                f_out.write(f"Cycle {ciclo}\n")
                
                # O caminho de dados processa a instrução de 23 bits [cite: 146]
                cd.executar_ciclo(instrucao, f_out)
                
                # Divisor final do ciclo
                if ciclo < len(linhas):
                    f_out.write("============================================================\n")
                else:
                    # O último ciclo tem um divisor ligeiramente diferente no seu gabarito
                    f_out.write("=====================================================\n")
            
            # --- Fim do Programa ---
            f_out.write(f"Cycle {len(linhas) + 1}\n")
            f_out.write("No more lines, EOP.\n")
            
        print(f"Log gerado com sucesso em '{arq_saida}'!")
        
    except FileNotFoundError as e:
        print(f"Erro: O arquivo '{e.filename}' não foi encontrado. Verifique a pasta 'arquivos/'.")

if __name__ == "__main__":
    executar_tarefa1()