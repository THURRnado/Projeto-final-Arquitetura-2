from ula import ULA

def executar_tarefa1():
    """
    Controlador exclusivo para a Tarefa 1 da Etapa 2.
    Testa apenas a ULA com palavras de 8 bits, aplicando os deslocamentos e
    capturando os erros de sinais inválidos.
    """
    # Instancia apenas a ULA, pois o Caminho de Dados não é usado nesta tarefa
    ula = ULA()
    
    # Valores iniciais de teste (extraídos do seu log de exemplo da Tarefa 1)
    # A = 1 e B = 2147483648 (que é o bit mais significativo ligado em 32 bits, ou 0x80000000)
    A = 1
    B = 0x80000000 

    arquivo_entrada = 'arquivos/programa_etapa2_tarefa1.txt'
    # Salvando com o nome exato que aparece na sua imagem
    arquivo_saida = 'arquivos/saída_etapa2_tarefa1.txt'

    try:
        with open(arquivo_entrada, 'r') as file_in, open(arquivo_saida, 'w') as file_out:
            # --- Cabeçalho de Inicialização ---
            file_out.write(f"b = {B:032b}\n")
            file_out.write(f"a = {A:032b}\n\n")
            file_out.write("Start of Program\n")
            file_out.write("============================================================\n")

            # Lê todas as linhas e adiciona uma string vazia ao final para simular a condição EOP (End of Program)
            linhas = [linha.strip() for linha in file_in.readlines()]
            linhas.append("") 
            
            # --- Laço de Execução da ULA ---
            pc = 1
            for linha in linhas:
                file_out.write(f"Cycle {pc}\n\n")
                file_out.write(f"PC = {pc}\n")

                # Se a linha for a string vazia adicionada, finaliza o log
                if not linha:
                    file_out.write("> Line is empty, EOP.\n")
                    break
                    
                file_out.write(f"IR = {linha}\n")
                
                try:
                    # Carrega as entradas fixas
                    ula.carregar_entradas(A, B)
                    # Decodifica os 8 bits de controle da instrução atual
                    ula.decodificar_instrucao(linha)
                    # Executa o processamento. O bloco try/except captura a exceção 
                    # levantada pela ULA caso SLL8 e SRA1 sejam 1 simultaneamente.
                    ula.executar()
                    
                    # Log de sucesso com os estados internos e saídas da ULA
                    file_out.write(f"b = {ula.b_interno:032b}\n")
                    file_out.write(f"a = {ula.a_interno:032b}\n")
                    file_out.write(f"s = {ula.saida_bruta:032b}\n")
                    file_out.write(f"sd = {ula.saida_s:032b}\n")
                    file_out.write(f"n = {ula.n}\n")
                    file_out.write(f"z = {ula.z}\n")
                    file_out.write(f"co = {ula.vai_um}\n")
                    
                except ValueError as e:
                    # Registra a mensagem de erro formatada exatamente como o esperado (> Error, invalid...)
                    file_out.write(f"{str(e)}\n")
                    
                file_out.write("============================================================\n")
                pc += 1

        print(f"Log gerado com sucesso em '{arquivo_saida}'!")

    except FileNotFoundError as e:
        print(f"Erro: O arquivo '{e.filename}' não foi encontrado.")

if __name__ == "__main__":
    executar_tarefa1()