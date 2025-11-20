// --- Definição de Pinos e Variáveis ---
int pinLED = 11;    // Pino digital para o LED (PWM) - Saída de brilho
int pinTrig = 6;    // Pino digital para o Trigger (acionamento) do sensor ultrassônico
int pinEcho = 5;    // Pino digital para o Echo (resposta) do sensor ultrassônico

// Valor fixo que representa a Parte Real (Re(z)) do número complexo
// Este valor é constante para a simulação do plano complexo
int valorReal = 50; 

// --- Configuração Inicial ---
void setup() {
  Serial.begin(9600);      // Inicia a comunicação serial a 9600 baud rate para enviar dados ao Python
  
  // Configura os pinos do sensor ultrassônico
  pinMode(pinTrig, OUTPUT); // O Trig envia o pulso de som (Saída)
  pinMode(pinEcho, INPUT);  // O Echo recebe o retorno do som (Entrada)
  
  pinMode(pinLED, OUTPUT);  // Configura o pino do LED como Saída
}

// --- Loop Principal (Execução Contínua) ---
void loop() {
  // 1. Geração do Pulso de Trigger para iniciar a medição 
  digitalWrite(pinTrig, LOW);      // Garante que o Trig esteja baixo
  delayMicroseconds(2);            // Pequena pausa
  digitalWrite(pinTrig, HIGH);     // Envia um pulso alto
  delayMicroseconds(10);           // Dura 10 microssegundos
  digitalWrite(pinTrig, LOW);      // Finaliza o pulso
  
  // 2. Medição do Tempo de Viagem do Som (Duração)
  // pulseIn mede a duração em microssegundos do pino Echo estar em HIGH
  long duracao_sinal = pulseIn(pinEcho, HIGH);
  
  // 3. Cálculo da Distância (Parte Imaginária)
  // Distância = (Tempo * Velocidade do Som) / 2
  // Velocidade do Som ≈ 0.034 cm/µs 340ms
  float distancia_cm = (duracao_sinal * 0.034) / 2;
  
  // 4. Filtragem/Tratamento de Erros de Leitura (Garantia de 0 a 400 cm)
  if (distancia_cm == 0 || distancia_cm > 400) {
    distancia_cm = 0; // Se a leitura for inválida, define a distância como zero
  }
  
  // --- Simulação do Número Complexo: z = valorReal + j * distancia_cm ---
  
  // 5. Cálculo da Magnitude (|Z|)
  // Fórmula: |z| = sqrt(Real² + Imaginário²)
  float magnitude = sqrt(sq(valorReal) + sq(distancia_cm));
  
  // 6. Cálculo do Ângulo (Fase) em Radianos
  // Fórmula: θ = atan(Imaginário / Real)
  float angulo_radianos = atan(distancia_cm / valorReal);
  
  // 7. Conversão do Ângulo para Graus
  // Fórmula: Graus = Radianos * (180 / PI)
  float angulo_graus = (angulo_radianos * 180.0) / PI;
  
  // --- Controle do LED com base na Magnitude ---
  
  // 8. Mapeamento da Magnitude para o Brilho (0-255)
  // Mapeia a magnitude de um intervalo esperado (50 a 300) para o PWM (0 a 255)
  float brilho = map(magnitude, 50, 300, 0, 255);
  
  // 9. Restrição do Brilho
  // Garante que o valor de brilho esteja dentro dos limites válidos (0-255)
  brilho = constrain(brilho, 0, 255);
  
  // 10. Escrita do Brilho no LED
  analogWrite(pinLED, (int)brilho); // Usa PWM para variar o brilho do LED
  
  // --- Envio de Dados pela Serial para o Python ---
  
  // Parte Imaginária (Distância)
  Serial.print("Distancia (Imaginario): "); 
  Serial.print(distancia_cm);
  Serial.print(" cm | ");
  
  // Magnitude (|Z|)
  Serial.print("Magnitude (|Z|): "); 
  Serial.print(magnitude);
  Serial.print(" | ");
  
  // Ângulo (Fase)
  Serial.print("Angulo (Graus): "); 
  Serial.println(angulo_graus); 
  
  // 11. Pausa antes da próxima leitura
  delay(100); // Aguarda 100ms para estabilizar e não sobrecarregar a porta serial
}