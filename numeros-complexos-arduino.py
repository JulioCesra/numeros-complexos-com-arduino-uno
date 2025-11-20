import serial                       # Leitura e comunicação com o Arduino
import numpy as np                  # Manipulação de operações matemáticas (magnitude, ângulo)
import matplotlib.pyplot as plt     # Criação gráfica principal
from matplotlib.animation import FuncAnimation # Animação gráfica em tempo real
from matplotlib.patches import Arc  # Desenho do arco de ângulo (argumento)
import sys                          # Controle de sistema (uso principal: sys.exit para encerrar o script)

# --- Configuração da Porta Serial ---
PORT = 'COM3'                       # Porta serial utilizada
BAUDRATE = 9600                     # Taxa de transmissão de dados (deve ser a mesma do Arduino)
TIMEOUT = 0.1                       # Tempo máximo de espera para leitura de dados

# Tentativa de conexão com a porta serial
try:
    conexao = serial.Serial(
        port=PORT,
        baudrate=BAUDRATE,
        timeout=TIMEOUT
    )
    print("Conexão estabelecida com sucesso!")
except serial.SerialException as e:
    print(f"Erro na conexão com a porta serial '{PORT}': {e}")
    sys.exit() # O código é encerrado caso ocorra algum erro na tentativa de conexão com o Arduino

# --- Configuração do Gráfico ---
# Criação da figura e do eixo para o Plano Complexo 
fig, ax_complexo = plt.subplots(
    figsize=(7, 7)
    )
# Parte real fixa para simulação (Eixo X)
PARTE_REAL_FIXA = 50.0 

# --- Função de Plotagem do Plano Complexo ---
def plotar_plano_complexo(ax, numero_complexo):
    
    parte_real = numero_complexo.real           # Parte real do número complexo (Eixo X)
    parte_imaginaria = numero_complexo.imag     # Parte imaginária do número complexo (Eixo Y)
    
    # Calculo da magnitude (comprimento do vetor): r = sqrt(Real² + Imaginário²)
    magnitude = np.abs(numero_complexo)
    
    # Calculo do ângulo em radianos (Argumento)
    angulo_radianos = np.angle(numero_complexo)
    
    # Transformação do ângulo radiano para graus
    angulo_graus = np.degrees(angulo_radianos)
    
    ax.cla() # Limpa o eixo (área de plotagem) a cada nova iteração da animação
    
    # Plotagem do vetor (Reta) da origem (0,0) até o número complexo (Real, Imaginário)
    # ax.quiver é usado para desenhar o vetor/seta
    ax.quiver(
        0, 0,                      # Origem 
        parte_real, parte_imaginaria, # Ponto final 
        angles='xy',
        scale_units='xy',
        scale=1,
        color='blue',
        width=0.005,
        )

    # Configuração dos limites e eixos
    coordenada_maxima = max(abs(parte_real),
                             abs(parte_imaginaria)) * 1.2
    
    if coordenada_maxima < 100: # Garante um limite mínimo visual
        coordenada_maxima = 100 
        
    ax.set_xlim(0, coordenada_maxima) # Limite do eixo dos reais (X)
    
    ax.set_ylim(0, coordenada_maxima) # Limite do eixo dos imaginários (Y)
    
    ax.axhline(0, color='gray', linestyle='--') # Desenha a linha do Eixo Real (X)
    
    ax.axvline(0, color='gray', linestyle='--') # Desenha a linha do Eixo Imaginário (Y)
    
    # Desenhar o arco do Ângulo (Raio adaptativo)
    angulo = np.min([parte_real, parte_imaginaria]) * 0.3 if np.min([parte_real, parte_imaginaria]) > 0 else 10 
    
    arco = Arc((0, 0),                      # Origem
               2 * angulo,                  # Largura (2 * raio)
               2 * angulo,                  # Altura (2 * raio)
               angle=0, 
               theta1=0,                    # Ângulo inicial (começa no eixo real)
               theta2=angulo_graus,         # Ângulo final (vai até o argumento de z)
               color='red',
               linestyle=':'
               )
    
    # Adiciona a forma do arco na plotagem
    ax.add_patch(arco)
    
    # --- Anotações no Gráfico ---
    
    # Posição da anotação do Ângulo (centralizada no arco)
    texto_eixo_reais = angulo * 0.7 * np.cos(angulo_radianos / 2)
    texto_eixo_imaginarios = angulo * 0.7 * np.sin(angulo_radianos / 2)
    ax.text(texto_eixo_reais,
             texto_eixo_imaginarios,
             f'$\\theta = {angulo_graus:.2f}°$',
             color='red',
             fontsize=14)
    
    # Anotação da Magnitude (centralizada no vetor)
    ax.text(parte_real/2,
             parte_imaginaria/2,
             f'$|r| = {magnitude:.2f}$',
             color='blue',
             fontsize=14, 
             ha='center',
             va='center',
             bbox=dict(facecolor='white',
                       alpha=0.8,
                       edgecolor='none'))

    # --- Títulos e Legendas ---
    ax.set_xlabel('Eixo Real (cm)')
    ax.set_ylabel('Eixo Imaginário (Distância) cm')
    ax.set_title(f'Estudo da luminosidade com números complexos na forma polar | $\\theta$: {angulo_graus:.2f}°')
    ax.set_aspect('equal', adjustable='box') 
    ax.grid(True, linestyle='dotted')
    
    # Legenda fixa no canto
    rotulo = f'z = {parte_real:.2f} + {parte_imaginaria:.2f}j'      # Rótulo que será exibido
    handle_invisivel, = ax.plot([], [], 'o', color='blue', visible=False) # Cria um handle invisível para a legenda
    ax.legend([handle_invisivel], [rotulo], loc='upper left') # Exibe a legenda na posição superior esquerda

# --- Função de Análise da Leitura Serial ---
def analisar_leitura(leitura):
    dados = {}                      # Dicionário responsável por armazenar as informações chave:valor
    secoes = leitura.split('|')     # Separação dos dados pela barra vertical '|'
    
    for secao in secoes:            # Percorre cada seção (Distancia, Magnitude, Angulo)
        if ':' in secao:
            try:
                chave, valor_completo = secao.split(':', 1)
                valor_limpo = valor_completo.split()[0].strip()
                chave_limpa = chave.split('(')[0].strip()
                dados[chave_limpa] = float(valor_limpo) # Armazena a chave limpa e o valor convertido para float
            except Exception:
                continue # Ignora se a seção não puder ser analisada/convertida
    return dados

# --- Função de Animação Principal ---
def grafico_animado(i):
    try:
        valorLDRbytes = conexao.readline() # Leitura da linha de dados completa do Arduino
        if valorLDRbytes:
            valorLDRformatado = valorLDRbytes.decode("utf-8").strip() # Decodifica bytes para string e remove espaços/quebras de linha
        
            dados_analisados = analisar_leitura(valorLDRformatado) # Extrai os valores numéricos da string
            
            # Verifica se a Parte Imaginária (Distancia) está presente
            if 'Distancia' in dados_analisados:
                parte_imaginaria = dados_analisados['Distancia']
                
                # Cria o número complexo com a parte Real fixa e a Imaginária lida
                numero_complexo = complex(PARTE_REAL_FIXA, parte_imaginaria)
                
                # Plota o novo estado do número complexo no gráfico
                plotar_plano_complexo(ax=ax_complexo,
                                      numero_complexo=numero_complexo)
            
    except serial.SerialException as e: # Captura erros de comunicação serial
        print(f"Erro de leitura serial: {e}") 
        conexao.close() # Interrompe a conexão
        sys.exit() # Sai do script
    except Exception as e: # Captura quaisquer outros erros inesperados
        # É útil saber qual dado gerou o erro, se possível
        print(f"Erro ao processar dado: {valorLDRformatado} - {e}")

# --- Execução da Animação ---
animacao = FuncAnimation(
    fig,
    grafico_animado,
    interval=100  # Intervalo de atualização (100 ms)
    ) 

# Mostra o gráfico e lida com a interrupção pelo usuário
try:
    plt.tight_layout()
    plt.show()
except KeyboardInterrupt:
    print("\nGráfico interrompido pelo usuário.")
finally:
    # Garante que a conexão serial seja fechada ao terminar o script
    if 'conexao' in locals() and conexao.is_open: # Verifica se a conexão ainda está aberta
        conexao.close() # Interrompe a conexão
        print("Conexão serial fechada.")