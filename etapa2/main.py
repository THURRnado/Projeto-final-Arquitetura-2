from caminho_de_dados import CaminhoDeDados

def executar_programa():
    """
    Controlador principal da simulação. 
    Lê os arquivos de configuração, inicializa a arquitetura, gerencia o laço de ciclos
    e lida com a escrita do log de saída formatado.
    """
    # Instancia todo o caminho de dados da máquina, que por sua vez inicializa os registradores e a ULA.
    cd = CaminhoDeDados()
    
    # Caminhos relativos padrão do ambiente
    arquivo_regs = 'arquivos/registradores_etapa2_tarefa2.txt'
    arquivo_programa = 'arquivos/programa_etapa2_tarefa2.txt'
    arquivo_saida = 'arquivos/saida_etapa2_tarefa2.txt'

    # Popula os registradores com o estado fornecido pelo sistema, 
    # garantindo que o ciclo 1 receba os estados adequados para iniciar a simulação.
    cd.carregar_registradores(arquivo_regs)

    try:
        with open(arquivo_programa, 'r') as file_in, open(arquivo_saida, 'w') as file_out:
            # Lê todas as linhas descartando espaços ou quebras vazias, construindo a memória de instruções
            linhas = [linha.strip() for linha in file_in.readlines() if linha.strip()]
            
            # --- Seção de formatação de Cabeçalho do Log ---
            # Requisito do modelo de saída: imprimir todo o programa lido antes da execução
            for linha in linhas:
                file_out.write(linha + "\n")
            
            file_out.write("\n") 
            
            file_out.write("=====================================================\n")
            file_out.write("> Initial register states\n")
            # Salva no log o estado de inicialização antes do início do primeiro ciclo do Datapath
            file_out.write(cd.formatar_regs() + "\n\n")
            
            file_out.write("=====================================================\n")
            file_out.write("Start of program\n")
            file_out.write("=====================================================\n")
            
            # --- Seção de Execução do Pipeline ---
            # Processa sequencialmente as linhas de instrução, avançando um ciclo por vez.
            # Como a arquitetura apresentada até o momento não tem saltos (jumps) via PC controlados internamente
            # pelo próprio código de usuário de forma realimentada, o loop corre na ordem do txt iterativamente.
            for ciclo, instrucao in enumerate(linhas, 1):
                file_out.write(f"Cycle {ciclo}\n")
                
                # Aciona o Datapath passando a instrução de 21 bits para fluir através das portas lógicas simuladas.
                cd.executar_ciclo(instrucao, file_out)
                
                file_out.write("=====================================================\n")
            
            # Notificação de fim do processamento do arquivo de programa
            file_out.write(f"Cycle {len(linhas)}\n")
            file_out.write("No more lines, EOP.\n")
                
        print(f"Log gerado com sucesso em '{arquivo_saida}'!")

    except FileNotFoundError as e:
        print(f"Erro: O arquivo esperado não foi encontrado - {e.filename}")

if __name__ == "__main__":
    executar_programa()