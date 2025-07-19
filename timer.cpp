#include "timer.hpp"

Timer::Timer()
{
    this->start();
}

void Timer::start()
{
    this->start_time = ::micros();
}

unsigned long Timer::getTimeSinceLastStart()
{
    unsigned long current = micros();
    if (current >= start_time)
    {
        return current - start_time;
    }
    else
    {
        return (0xFFFFFFFFu - start_time) + current + 1;
    }
}

float Timer::getSecondsElapsedSinceLastStart()
{
    return this->getTimeSinceLastStart() / 1000000.0;
}

static_assert(4 == sizeof(unsigned long));