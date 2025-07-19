#pragma once

#include "common.hpp"
#include <Arduino.h>

class Timer
{
public:
    Timer();
    void          start();
    unsigned long getTimeSinceLastStart();
    float         getSecondsElapsedSinceLastStart();

private:
    unsigned long start_time;
};