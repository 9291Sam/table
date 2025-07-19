#include "button_reader.hpp"
#include "common.hpp"
#include "led_patterns.hpp"
#include "led_writer.hpp"
#include "timer.hpp"
#include <Arduino.h>


int main()
{
    init(); 

    Serial.begin(2000000);
    Serial.setTimeout(1000);
    while (!Serial) {};

    Serial.println("\nStandard Arduino Serial Test");

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

        if (Serial.available() > 0)
        {
            Array<char, 64> buf {};
            buf.fill(0);

            Serial.readBytes(buf.data(), Serial.available());
            
            Serial.print(buf.data());
        }
        if (iters == 0)
        {
            if (const ButtonReader::ButtonReadResult r = buttonReader.read(); r.is_valid())
            {
                Serial.print("Button: ");
                Serial.println(r.maybe_button);
                currentEffect = r.maybe_button;
            }

            // LED operation remains unchanged.
            getLedDelegateFunction(currentEffect)(ledWriter, timeAlive);
            ledWriter.writeChanges();
        }

    }
}