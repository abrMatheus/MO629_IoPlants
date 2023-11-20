/*
 * This ESP32 code is created by esp32io.com
 *
 * This ESP32 code is released in the public domain
 *
 * For more detail (instruction and wiring diagram), visit https://esp32io.com/tutorials/esp32-lm35-temperature-sensor
 */
#include "DHT.h"

#define ADC_VREF_mV    5000.0 // in millivolt
#define ADC_RESOLUTION 4096.0
#define PIN_LM35       34 // ESP32 pin GIOP36 (ADC0) connected to LM35
#define PIN_DTH        32 // ESP32 pin GIOP36 (ADC0) connected to DTH11

#define PIN_HUM        35 // ESP32 pin GIOP36 (ADC0) connected to HUM

#define PIN_UV         33 // ESP32 pin GIOP36 (ADC0) connected to UV

#define DHTTYPE DHT11   // DHT 11

DHT dht(PIN_DTH, DHTTYPE);

void setup() {
  Serial.begin(9600);
  dht.begin();
}


float mapfloat(float x, float in_min, float in_max, float out_min, float out_max)
{
  return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min;
}

void loop() {
  // read the ADC value from the temperature sensor
//  int adcVal = analogRead(PIN_LM35);
//  // convert the ADC value to voltage in millivolt
//  float milliVolt = adcVal * (ADC_VREF_mV / ADC_RESOLUTION);
//  // convert the voltage to the temperature in °C
//  float tempC = milliVolt / 10;
//  // convert the °C to °F
//  float tempF = tempC * 9 / 5 + 32;

  float h = dht.readHumidity();
  // Read temperature as Celsius (the default)
  float t = dht.readTemperature();

  Serial.print(F("Humidity: "));
  Serial.print(h);
  Serial.print(F("%  Temperature: "));
  Serial.print(t);


  float sensor_analog = analogRead(PIN_HUM);
  float _moisture = ( 100 - ( (sensor_analog/4095.00) * 100 ) );
  Serial.print("Moisture = ");
  Serial.print(_moisture);  /* Print Temperature on the serial window */

  float uvLevel = analogRead(PIN_UV);
//  float outputVoltage = 3.3 / refLevel * uvLevel;
  float uvIntensity = mapfloat(uvLevel/1000, 0.0, 2.8, 240, 370.0); //Convert the voltage to a UV intensity level

  Serial.print("ML8511 output: ");
  Serial.print(uvLevel);
 
  Serial.print(" / UV Intensity (mW/cm^2): ");
  Serial.println(uvIntensity);
  

  // print the temperature in the Serial Monitor:
//  Serial.print("adcV: ");
//  Serial.print(adcVal);   // print the temperature in °C
//  Serial.print("Temperature: ");
//  Serial.print(tempC);   // print the temperature in °C
//  Serial.print("°C");
//  Serial.print("  ~  "); // separator between °C and °F
//  Serial.print(tempF);   // print the temperature in °F
//  Serial.println("°F");

  delay(500);
}
