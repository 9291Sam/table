#pragma once
#include "common.hpp"
#include <Arduino.h>

class ButtonReader
{
public:
    struct ButtonReadResult
    {
    public:
        static constexpr uint8_t NoButton = 255;
    public:
        ButtonReadResult()
            : maybe_button {NoButton}
        {}
        ButtonReadResult(uint8_t b)
            : maybe_button {b}
        {}

        bool is_valid() const
        {
            return this->maybe_button != NoButton;
        }

        uint8_t maybe_button;
    };
public:
    ButtonReader();

    ButtonReadResult read() const;

private:
    static const Array<int8_t, 4> rows;
    static const Array<int8_t, 4> columns;
};