#pragma once
#include "common.hpp"
#include "led_writer.hpp"

using LEDFunctionType = Fn<void(LEDWriter&, float)>;

LEDFunctionType getLedDelegateFunction(uint8_t button);