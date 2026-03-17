from ula import ULA

def executar_programa():
    ula = ULA()
    
    A = 0xFFFFFFFF  # Representa 32 bits de '1'
    B = 1
    
    arquivo_entrada = 'arquivos/programa_etapa1.txt'
    arquivo_saida = 'arquivos/saida_etapa1.txt'
    
    try:
        with open(arquivo_entrada, 'r') as file_in, open(arquivo_saida, 'w') as file_out:
            
            # Escreve o cabeçalho no padrão solicitado
            file_out.write(f"b = {B:032b}\n")
            file_out.write(f"a = {A:032b}\n\n")
            file_out.write("Start of Program\n")
            file_out.write("============================================================\n")
            
            ciclo = 1
            PC = 1
            
            # lemos todas as linhas e adicionamos uma string vazia ao final
            linhas = file_in.readlines()
            linhas.append("") 
            
            for linha in linhas:
                IR = linha.strip()
                
                file_out.write(f"Cycle {ciclo}\n\n")
                file_out.write(f"PC = {PC}\n")
                
                # Condição de parada
                if not IR:
                    file_out.write("> Line is empty, EOP.\n")
                    break
                
                ula.decodificar_instrucao(IR)
                ula.carregar_entradas(A, B)
                ula.executar()
                
                # Escreve os resultados formatados em binário com 32 posições numéricas
                file_out.write(f"IR = {IR}\n")
                file_out.write(f"b = {ula.b_interno:032b}\n")
                file_out.write(f"a = {ula.a_interno:032b}\n")
                file_out.write(f"s = {ula.saida_s:032b}\n")
                file_out.write(f"co = {ula.vai_um}\n")
                file_out.write("============================================================\n")
                
                ciclo += 1
                PC += 1
                
        print(f"Log gerado com sucesso em '{arquivo_saida}'!")
        
    except FileNotFoundError:
        print(f"Erro: Crie o arquivo '{arquivo_entrada}' com as instruções.")

if __name__ == "__main__":
    executar_programa()