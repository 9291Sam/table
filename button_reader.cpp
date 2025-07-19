#include "button_reader.hpp"

static const Array<int8_t, 4> ButtonReader::rows    = {4, 5, 6, 7};
static const Array<int8_t, 4> ButtonReader::columns = {8, 9, 10, 11};

ButtonReader::ButtonReader()
{
    for (int i = 0; i < this->rows.size(); i++)
    {
        pinMode(this->rows[i], OUTPUT);
        digitalWrite(this->rows[i], HIGH);
    }

    for (int i = 0; i < this->columns.size(); i++)
    {
        pinMode(this->columns[i], INPUT_PULLUP);
    }
}

ButtonReader::ButtonReadResult ButtonReader::read() const
{
    for (int row = 0; row < this->rows.size(); row++)
    {
        for (int i = 0; i < this->rows.size(); i++)
        {
            digitalWrite(this->rows[i], (i == row) ? LOW : HIGH);
        }

        for (int col = 0; col < this->columns.size(); col++)
        {
            if (digitalRead(this->columns[col]) == LOW)
            {
                uint8_t buttonPressed = row * 4 + col;
                return ButtonReadResult(buttonPressed);
            }
        }
    }

    for (int i = 0; i < this->rows.size(); i++)
    {
        digitalWrite(this->rows[i], HIGH);
    }

    return ButtonReadResult {};
}