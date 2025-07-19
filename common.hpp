#pragma once

#include <stddef.h>
#include <stdint.h>

template<class T, size_t N>
struct Array
{
    T raw_array_data[N];

    static size_t size()
    {
        return N;
    }

    T& operator[] (size_t i)
    {
        return this->raw_array_data[i];
    }

    const T& operator[] (size_t i) const
    {
        return this->raw_array_data[i];
    }

    T* data()
    {
        return this->raw_array_data;
    }

    const T* data() const
    {
        return this->raw_array_data;
    }

    void fill(T t)
    {
        for (size_t i = 0; i < N; ++i)
        {
            this->raw_array_data[i] = t;
        }
    }
};

template<class T>
using Fn = T*;