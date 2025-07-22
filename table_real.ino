#include "button_reader.hpp"
#include "common.hpp"
#include "led_patterns.hpp"
#include "led_writer.hpp"
#include "timer.hpp"
#include <Arduino.h>

#include "Adafruit_seesaw.h"
#include <seesaw_neopixel.h>
#include <Wire.h>


// Add these defines
#define SS_NEO_PIN       18
#define SS_ENC0_SWITCH   12
#define SS_ENC1_SWITCH   14
#define SS_ENC2_SWITCH   17
#define SS_ENC3_SWITCH   9
#define SEESAW_ADDR      0x49

// Add these global variables
Adafruit_seesaw ss = Adafruit_seesaw(&Wire);
seesaw_NeoPixel pixels = seesaw_NeoPixel(4, SS_NEO_PIN, NEO_GRB + NEO_KHZ800);
int32_t enc_positions[4] = {0, 0, 0, 0};

// Add this color wheel function
uint32_t Wheel(byte WheelPos) {
  WheelPos = 255 - WheelPos;
  if (WheelPos < 85) {
    return seesaw_NeoPixel::Color(255 - WheelPos * 3, 0, WheelPos * 3);
  }
  if (WheelPos < 170) {
    WheelPos -= 85;
    return seesaw_NeoPixel::Color(0, WheelPos * 3, 255 - WheelPos * 3);
  }
  WheelPos -= 170;
  return seesaw_NeoPixel::Color(WheelPos * 3, 255 - WheelPos * 3, 0);
}

bool initSeesaw() {
    if (!ss.begin(SEESAW_ADDR) || !pixels.begin(SEESAW_ADDR)) {
        Serial.println("Couldn't find seesaw on default address");
        return false;
    }
    
    Serial.println("seesaw started");
    uint32_t version = ((ss.getVersion() >> 16) & 0xFFFF);
    if (version != 5752) {
        Serial.print("Wrong firmware loaded? ");
        Serial.println(version);
        return false;
    }
    
    Serial.println("Found Product 5752");
    
    // Setup switch pins
    ss.pinMode(SS_ENC0_SWITCH, INPUT_PULLUP);
    ss.pinMode(SS_ENC1_SWITCH, INPUT_PULLUP);
    ss.pinMode(SS_ENC2_SWITCH, INPUT_PULLUP);
    ss.pinMode(SS_ENC3_SWITCH, INPUT_PULLUP);
    
    // Enable interrupts
    ss.setGPIOInterrupts(1UL << SS_ENC0_SWITCH | 1UL << SS_ENC1_SWITCH | 
                         1UL << SS_ENC2_SWITCH | 1UL << SS_ENC3_SWITCH, 1);
    
    // Get starting positions and enable encoder interrupts
    for (int e = 0; e < 4; e++) {
        enc_positions[e] = ss.getEncoderPosition(e);
        ss.enableEncoderInterrupt(e);
    }
    
    pixels.setBrightness(255);
    pixels.show();
    
    return true;
}

// Add this function to read encoders and buttons
void updateSeesawInputs() {
    // Check button presses
    if (!ss.digitalRead(SS_ENC0_SWITCH)) {
        Serial.println("ENC0 pressed!");
    }
    if (!ss.digitalRead(SS_ENC1_SWITCH)) {
        Serial.println("ENC1 pressed!");
    }
    if (!ss.digitalRead(SS_ENC2_SWITCH)) {
        Serial.println("ENC2 pressed!");
    }
    if (!ss.digitalRead(SS_ENC3_SWITCH)) {
        Serial.println("ENC3 pressed!");
    }
    
    // Check encoder positions
    for (int e = 0; e < 4; e++) {
        int32_t new_enc_position = ss.getEncoderPosition(e);
        if (enc_positions[e] != new_enc_position) {
            Serial.print("Encoder #");
            Serial.print(e);
            Serial.print(" -> ");
            Serial.println(new_enc_position);
            enc_positions[e] = new_enc_position;
            
            // // Update NeoPixel color
            // pixels.setPixelColor(e, Wheel((new_enc_position * 4) & 0xFF));
            // pixels.show();
        }
    }
}


int main()
{
    init(); 

    Serial.begin(2000000);
    Serial.setTimeout(1000);
    while (!Serial) {};

    Serial.println("\nStandard Arduino Serial Test");

     // Initialize seesaw board
    if (!initSeesaw()) {
        Serial.println("Failed to initialize seesaw!");
        while(1) delay(10);
    }


    ButtonReader buttonReader{};
    LEDWriter ledWriter{};
    Timer timer{};

    float timeAlive = 0.0f;
    uint8_t currentEffect = 0;
    
    uint8_t iters = 0;
    while (true)
    {
        const float deltaTime = timer.getSecondsElapsedSinceLastStart();
        timer.start();
        timeAlive += deltaTime;
        iters += 1;


        // Update seesaw inputs (encoders and buttons)
        updateSeesawInputs();

        if (Serial.available() > 0)
        {
            Array<char, 64> buf {};
            buf.fill(0);

            Serial.readBytes(buf.data(), Serial.available());
            
            Serial.print(buf.data());
        }
        
        if (const ButtonReader::ButtonReadResult r = buttonReader.read(); r.is_valid())
        {
            Serial.print("Button: ");
            Serial.println(r.maybe_button);
            currentEffect = r.maybe_button;
        }


        // if (iters == 0)
        // {
            // LED operation remains unchanged.
            getLedDelegateFunction(currentEffect)(ledWriter, timeAlive);
            ledWriter.writeChanges();
        // }

    }
}