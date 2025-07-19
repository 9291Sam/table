#include "led_patterns.hpp"
#include <FastLed.h>

// D&D Table LED Effects Implementation

void dungeon(LEDWriter& writer, float timeAlive)
{
    const size_t numberOfLEDS = writer.getNumberOfLEDS();
    for (int i = 0; i < numberOfLEDS; i++)
    {
        // Base orange torch color with random flickering
        float flicker =
            (sinf(timeAlive * 8.0f + i * 0.5f) * 0.3f + 0.7f) * (sinf(timeAlive * 15.0f + i * 1.2f) * 0.2f + 0.8f);
        uint8_t brightness = flicker * 200 + 55;
        writer.writeLED(i, CRGB(brightness, brightness * 0.4f, 0));
    }
}

void combat(LEDWriter& writer, float timeAlive)
{
    const size_t numberOfLEDS = writer.getNumberOfLEDS();
    float        pulse        = sinf(timeAlive * 4.0f) * 0.5f + 0.5f;
    uint8_t      brightness   = pulse * 200 + 55;

    for (int i = 0; i < numberOfLEDS; i++)
    {
        writer.writeLED(i, CRGB(brightness, 0, 0));
    }
}

void tavern(LEDWriter& writer, float timeAlive)
{
    const size_t numberOfLEDS = writer.getNumberOfLEDS();
    for (int i = 0; i < numberOfLEDS; i++)
    {
        // Warm yellow-orange with gentle flickering
        float   flicker = sinf(timeAlive * 3.0f + i * 0.3f) * 0.15f + 0.85f;
        uint8_t red     = flicker * 255;
        uint8_t green   = flicker * 180;
        uint8_t blue    = flicker * 20;
        writer.writeLED(i, CRGB(red, green, blue));
    }
}

void darkness(LEDWriter& writer, float timeAlive)
{
    const size_t numberOfLEDS = writer.getNumberOfLEDS();
    for (int i = 0; i < numberOfLEDS; i++)
    {
        writer.writeLED(i, CRGB(5, 0, 10)); // Very dim purple edge lighting
    }
}

void forest(LEDWriter& writer, float timeAlive)
{
    const size_t numberOfLEDS = writer.getNumberOfLEDS();
    for (int i = 0; i < numberOfLEDS; i++)
    {
        // Dappled green light with moving shadows
        float   dapple = sinf(timeAlive * 2.0f + i * 0.4f) * 0.3f + cosf(timeAlive * 1.5f + i * 0.6f) * 0.2f + 0.5f;
        uint8_t green  = dapple * 150 + 50;
        uint8_t red    = dapple * 80 + 30;
        writer.writeLED(i, CRGB(red, green, 10));
    }
}

void stealth(LEDWriter& writer, float timeAlive)
{
    const size_t numberOfLEDS = writer.getNumberOfLEDS();
    for (int i = 0; i < numberOfLEDS; i++)
    {
        writer.writeLED(i, CRGB(0, 5, 25)); // Very dim blue
    }
}

void fire(LEDWriter& writer, float timeAlive)
{
    const size_t numberOfLEDS = writer.getNumberOfLEDS();
    for (int i = 0; i < numberOfLEDS; i++)
    {
        // Intense flickering flames
        float   flame = sinf(timeAlive * 12.0f + i * 0.8f) * 0.4f + cosf(timeAlive * 20.0f + i * 1.1f) * 0.3f + 0.6f;
        uint8_t red   = flame * 255;
        uint8_t green = flame * 100;
        writer.writeLED(i, CRGB(red, green, 0));
    }
}

void lightning(LEDWriter& writer, float timeAlive)
{
    const size_t numberOfLEDS = writer.getNumberOfLEDS();
    // Random lightning flashes
    float        flashTime    = fmod(timeAlive * 3.0f, 2.0f);
    bool         flash        = (flashTime > 1.8f && flashTime < 1.95f) || (flashTime > 0.3f && flashTime < 0.35f);

    for (int i = 0; i < numberOfLEDS; i++)
    {
        if (flash)
        {
            writer.writeLED(i, CRGB(255, 255, 255)); // Bright white flash
        }
        else
        {
            writer.writeLED(i, CRGB(20, 10, 40)); // Dark purple-gray
        }
    }
}

void desert(LEDWriter& writer, float timeAlive)
{
    const size_t numberOfLEDS = writer.getNumberOfLEDS();
    for (int i = 0; i < numberOfLEDS; i++)
    {
        // Harsh bright light with heat shimmer
        float   shimmer    = sinf(timeAlive * 6.0f + i * 0.3f) * 0.1f + 0.9f;
        uint8_t brightness = shimmer * 255;
        writer.writeLED(i, CRGB(brightness, brightness * 0.9f, brightness * 0.7f));
    }
}

void cave(LEDWriter& writer, float timeAlive)
{
    const size_t numberOfLEDS = writer.getNumberOfLEDS();
    for (int i = 0; i < numberOfLEDS; i++)
    {
        // Dim gray with occasional crystal glints
        float   glint      = sinf(timeAlive * 4.0f + i * 2.0f);
        uint8_t base       = 40;
        uint8_t brightness = (glint > 0.95f) ? 120 : base;
        writer.writeLED(i, CRGB(brightness * 0.7f, brightness * 0.8f, brightness));
    }
}

void healing(LEDWriter& writer, float timeAlive)
{
    const size_t numberOfLEDS = writer.getNumberOfLEDS();
    float        pulse        = sinf(timeAlive * 2.0f) * 0.3f + 0.7f;

    for (int i = 0; i < numberOfLEDS; i++)
    {
        // Warm golden pulses radiating from center
        float   distance   = abs(i - numberOfLEDS / 2) / float(numberOfLEDS / 2);
        float   radiate    = pulse * (1.0f - distance * 0.3f);
        uint8_t brightness = radiate * 200 + 55;
        writer.writeLED(i, CRGB(brightness, brightness * 0.8f, 0));
    }
}

void magic(LEDWriter& writer, float timeAlive)
{
    const size_t numberOfLEDS = writer.getNumberOfLEDS();
    for (int i = 0; i < numberOfLEDS; i++)
    {
        // Purple sparkles and wisps
        float   sparkle    = sinf(timeAlive * 5.0f + i * 1.5f) * 0.4f + cosf(timeAlive * 7.0f + i * 0.8f) * 0.3f + 0.3f;
        uint8_t brightness = sparkle * 180 + 75;
        writer.writeLED(i, CRGB(brightness * 0.8f, brightness * 0.3f, brightness));
    }
}

void city(LEDWriter& writer, float timeAlive)
{
    const size_t numberOfLEDS = writer.getNumberOfLEDS();
    for (int i = 0; i < numberOfLEDS; i++)
    {
        // Clean bright white light
        writer.writeLED(i, CRGB(240, 240, 255));
    }
}

void ocean(LEDWriter& writer, float timeAlive)
{
    const size_t numberOfLEDS = writer.getNumberOfLEDS();
    for (int i = 0; i < numberOfLEDS; i++)
    {
        // Blue-green undulating waves
        float   wave  = sinf(timeAlive * 3.0f + i * 0.2f) * 0.3f + cosf(timeAlive * 2.0f + i * 0.15f) * 0.2f + 0.5f;
        uint8_t blue  = wave * 180 + 75;
        uint8_t green = wave * 120 + 60;
        writer.writeLED(i, CRGB(0, green, blue));
    }
}

void colorWave(LEDWriter& writer, float timeAlive)
{
    const size_t numberOfLEDS = writer.getNumberOfLEDS();
    for (int i = 0; i < numberOfLEDS; i++)
    {
        const uint8_t hue = (sinf(timeAlive * 32 + float(i) / 32.0) * 0.5f + 0.5f) * 255.0f;
        writer.writeLED(i, CHSV(hue, 255, 255));
    }
}
// Updated delegate function to return the correct effect
LEDFunctionType getLedDelegateFunction(uint8_t effectId)
{
    switch (effectId)
    {
    case 0:
        return dungeon;
    case 1:
        return combat;
    case 2:
        return tavern;
    case 3:
        return darkness;
    case 4:
        return forest;
    case 5:
        return stealth;
    case 6:
        return fire;
    case 7:
        return lightning;
    case 8:
        return desert;
    case 9:
        return cave;
    case 10:
        return healing;
    case 11:
        return magic;
    case 12:
        return city;
    case 13:
        return ocean;
    default:
        return colorWave;
    }
}
