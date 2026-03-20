# Importa a classe ULA do módulo ula
# ULA (Unidade Lógica Aritmética) é responsável por decodificar instruções e executar operações
from ula import ULA

# Função principal que executa o programa simulado
# Lê instruções de um arquivo, processa cada uma usando a ULA e gera um log de saída
def executar_programa():
    # Instancia a ULA para usar suas funcionalidades
    ula = ULA()

    # Valores iniciais para os operandos A e B
    # A é definido como 0xFFFFFFFF (32 bits de '1' em hexadecimal, representando o valor máximo de 32 bits)
    # B é definido como 1 (um valor simples para operações)
    A = 0xFFFFFFFF  # Representa 32 bits de '1'
    B = 1

    # Caminhos relativos para os arquivos de entrada e saída
    # O arquivo de entrada contém as instruções a serem executadas
    # O arquivo de saída receberá o log detalhado da execução
    arquivo_entrada = 'arquivos/programa_etapa1.txt'
    arquivo_saida = 'arquivos/saida_etapa1.txt'

    # Bloco try-except para lidar com possíveis erros de arquivo
    try:
        # Abre os arquivos: entrada para leitura e saída para escrita
        with open(arquivo_entrada, 'r') as file_in, open(arquivo_saida, 'w') as file_out:

            # Escreve o cabeçalho no arquivo de saída, conforme o padrão solicitado
            # Mostra os valores iniciais de b e a em binário de 32 bits
            file_out.write(f"b = {B:032b}\n")
            file_out.write(f"a = {A:032b}\n\n")
            file_out.write("Start of Program\n")
            file_out.write("============================================================\n")

            # Inicializa contadores para o ciclo de execução e o contador de programa (PC)
            ciclo = 1
            PC = 1

            # Lê todas as linhas do arquivo de entrada e adiciona uma linha vazia ao final
            # A linha vazia serve como condição de parada
            linhas = file_in.readlines()
            linhas.append("")

            # Loop que processa cada linha do arquivo de entrada
            for linha in linhas:
                # Remove espaços em branco da linha (strip) para obter a instrução (IR - Instruction Register)
                IR = linha.strip()

                # Escreve o cabeçalho do ciclo atual no arquivo de saída
                file_out.write(f"Cycle {ciclo}\n\n")
                file_out.write(f"PC = {PC}\n")

                # Condição de parada: se a linha estiver vazia, indica fim do programa (EOP - End of Program)
                if not IR:
                    file_out.write("> Line is empty, EOP.\n")
                    break

                # Processa a instrução usando a ULA:
                # 1. Decodifica a instrução (interpreta o código binário)
                ula.decodificar_instrucao(IR)
                # 2. Carrega os valores de entrada A e B na ULA
                ula.carregar_entradas(A, B)
                # 3. Executa a operação definida pela instrução
                ula.executar()

                # Escreve os resultados da execução no arquivo de saída
                # Todos os valores são formatados em binário com 32 posições
                file_out.write(f"IR = {IR}\n")  # Instrução atual
                file_out.write(f"b = {ula.b_interno:032b}\n")  # Valor de B interno da ULA
                file_out.write(f"a = {ula.a_interno:032b}\n")  # Valor de A interno da ULA
                file_out.write(f"s = {ula.saida_s:032b}\n")  # Saída S da ULA (resultado da operação)
                file_out.write(f"co = {ula.vai_um}\n")  # Carry out (vai-um, sinal de overflow)
                file_out.write("============================================================\n")

                # Incrementa os contadores para o próximo ciclo
                ciclo += 1
                PC += 1

        # Mensagem de sucesso após processar todo o programa
        print(f"Log gerado com sucesso em '{arquivo_saida}'!")

    # Trata o erro caso o arquivo de entrada não seja encontrado
    except FileNotFoundError:
        print(f"Erro: Crie o arquivo '{arquivo_entrada}' com as instruções.")

# Bloco padrão em Python para executar a função principal apenas se o script for rodado diretamente
# (não importado como módulo)
if __name__ == "__main__":
    executar_programa()