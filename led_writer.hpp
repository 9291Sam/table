#pragma once

#include "common.hpp"
#include <FastLED.h>

class LEDWriter
{
public:
    LEDWriter();

    void writeChanges();

    size_t getNumberOfLEDS() const;

    void writeLED(uint8_t i, CRGB c);

private:
    static const int8_t dataPin              = 3;
    static const size_t numberOfPhysicalLEDS = 90;
    static const size_t firstValidLED        = 5;
    static const size_t lastValidLED         = 83;
    static const size_t numberOfLogicalLEDS  = lastValidLED - firstValidLED;

    Array<CRGB, numberOfPhysicalLEDS> leds;
};
