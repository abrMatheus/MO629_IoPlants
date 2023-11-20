/*
  Exemplo básico de conexão a Konker Plataform via MQTT, 
  baseado no https://github.com/knolleary/pubsubclient/blob/master/examples/mqtt_auth/mqtt_auth.ino. 
  Este exemplo se utiliza das bibliotecas do ESP8266 programado via Arduino IDE 
  (https://github.com/esp8266/Arduino) e a biblioteca PubSubClient que pode ser 
  obtida em: https://github.com/knolleary/pubsubclient/
*/


#include "DHT.h"

#define AMOSTRAS 1 //numero de amostras

#define ADC_VREF_mV    5000.0 // in millivolt
#define ADC_RESOLUTION 4096.0
#define PIN_LM35       34 // ESP32 pin GIOP36 (ADC0) connected to LM35
#define PIN_DTH        25 // ESP32 pin GIOP36 (ADC0) connected to DTH11
#define PIN_HUM        35 // ESP32 pin GIOP36 (ADC0) connected to HUM
#define PIN_UV         33 // ESP32 pin GIOP36 (ADC0) connected to UV

#define DHTTYPE DHT11   // DHT 11

DHT dht(PIN_DTH, DHTTYPE);

#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h> 

// Vamos primeiramente conectar o ESP8266 com a rede Wireless (mude os parâmetros abaixo para sua rede).

// Dados da rede WiFi
const char* ssid = "";
const char* password = "";

// Dados do servidor MQTT
const char* mqtt_server = "mqtt.prod.konkerlabs.net";
//const char* mqtt_server = "0.0.0.0";

const char* USER = "";  
const char* PWD = "";
  
const char* PUB = "data//pub/teste";
const char* SUB = "data//sub/configuration";

//Variaveis gloabais desse codigo
char bufferJ[256];
char *mensagem;

//Variaveis do termometro
float temperature;
float tensao;
float humidity;
float soil;
float uv;

int i = 0;

//Vamos criar uma funcao para formatar os dados no formato JSON
char *jsonMQTTmsgDATA(const char *device_id, float temp, float hum, float soil, float lum) {
  const int capacity = JSON_OBJECT_SIZE(5);
  StaticJsonDocument<capacity> jsonMSG;
  jsonMSG["deviceId"] = device_id;
  jsonMSG["temp"] = temp;
  jsonMSG["hum"] = hum;
  jsonMSG["soil"] = soil;
  jsonMSG["lum"] = lum;
  
  serializeJson(jsonMSG, bufferJ);
  return bufferJ;
}

//Criando os objetos de conexão com a rede e com o servidor MQTT.
WiFiClient espClient;
PubSubClient client(espClient);

//Criando a funcao de callback
//Essa funcao eh rodada quando uma mensagem eh recebida via MQTT.
//Nesse caso ela eh muito simples: imprima via serial o que voce recebeu
void callback(char* topic, byte* payload, unsigned int length) {
  Serial.print("Message arrived [");
  Serial.print(topic);
  Serial.print("] ");
  for (int i = 0; i < length; i++) {
    Serial.print((char)payload[i]);
  }
  Serial.println();
}

void reconnect() {
   ////Entra no Loop ate estar conectado
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    // Usando um ID unico (Nota: IDs iguais causam desconexao no Mosquito)
    // Tentando conectar
     if (client.connect(USER, USER, PWD)) {
      Serial.println("connected");
      // Subscrevendo no topico esperado
      client.subscribe(SUB);
    } else {
      Serial.print("Falhou! Codigo rc=");
      Serial.print(client.state());
      Serial.println(" Tentando novamente em 5 segundos");
      // Esperando 5 segundos para tentar novamente
      delay(5000);
    }
  }
}

void setup_wifi() {
  delay(10);
  // Agora vamos nos conectar em uma rede Wifi
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);

  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    //Imprimindo pontos na tela ate a conexao ser estabelecida!
    Serial.print(".");
  }

  Serial.println("");
  Serial.println("WiFi conectado");
  Serial.println("Endereco de IP: ");
  Serial.println(WiFi.localIP());
}


float readMean(float pin){
  float temp = 0;
  
  //Tirando a media do valor lido no ADC
  for (i=0; i< AMOSTRAS; i++) {
   temp += analogRead(pin)/AMOSTRAS;
   delay(10);
  }

  return temp;
}


float readTemp(DHT dht){
  float temp=0;
  for(i=0; i<AMOSTRAS;i++){
    temp+= dht.readTemperature()/AMOSTRAS;
    delay(10);
  }
  return temp;
}

float readHum(DHT dht){
  float temp=0;
  for(i=0; i<AMOSTRAS;i++){
    temp+= dht.readHumidity()/AMOSTRAS;
    delay(10);
  }
  return temp;
}

float mapfloat(float x, float in_min, float in_max, float out_min, float out_max)
{
  return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min;
}

void setup()
{
  //Configurando a porta Serial e escolhendo o servidor MQTT
  Serial.begin(9600);
  setup_wifi();
  client.setServer(mqtt_server, 1883);
  client.setCallback(callback);
}

void loop()
{
  //O programa em si eh muito simples: 
  //se nao estiver conectado no Broker MQTT, se conecte!
  if (!client.connected()) {
    reconnect();
  }
  
  
  //leitura temperatura e umidade do ar
  //temperature = readTemp(dht);
  temperature = dht.readTemperature();
  //humidity = readHum(dht);
  humidity =  dht.readHumidity();
  tensao = readMean(PIN_HUM);
  soil = ( 100 - ( (tensao/4095.00) * 100 ) );
  tensao = readMean(PIN_UV);
  uv = mapfloat(tensao/1000, 0.0, 2.8, 240, 370.0); //Convert the voltage to a UV intensity level

  if(temperature > 20){
    Serial.print("Temperatura (C): ");
    Serial.print(temperature);
    Serial.print(" Umidade Ar(%): ");
    Serial.print(humidity);
    Serial.print(" Umidade solo (%): ");
    Serial.print(soil);
    Serial.print(" UV (nm): ");
    Serial.println(uv);

    //Enviando via MQTT o resultado calculado da temperatura
    mensagem = jsonMQTTmsgDATA("My_favorite_thermometer", temperature, humidity, soil, uv);
    
    client.publish(PUB, mensagem); 
  }
  client.loop();
  
  //Gerando um delay de 2 segundos antes do loop recomecar
  delay(500);
}
