#include "led_writer.hpp"

LEDWriter::LEDWriter()
{
    for (size_t i = 0; i < leds.size(); ++i)
    {
        this->leds[i] = CRGB(0, 0, 0);
    }

    FastLED.addLeds<WS2811, LEDWriter::dataPin, RGB>(this->leds.data(), this->leds.size());
}

void LEDWriter::writeChanges()
{
    FastLED.show();
}

size_t LEDWriter::getNumberOfLEDS() const
{
    return this->numberOfLogicalLEDS;
}

void LEDWriter::writeLED(uint8_t i, CRGB c)
{
    const size_t physicalIndex = firstValidLED + static_cast<size_t>(i);

    if (physicalIndex < this->leds.size())
    {
        this->leds[i + firstValidLED] = c;
    }   
}