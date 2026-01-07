#pragma once

#include "pch.hpp"

struct Acceleration
{
    float x;
    float y;
    float z;
};

struct MPU6050Data
{
    Acceleration acceleration;
    Acceleration gyroscope;
};

struct MAX30102Data
{
    int32_t heart_rate;
    int32_t spo2;
};

struct NEO6MData
{
    double latitude;
    double longitude;
    double altitude;
};

struct BMP280Data
{
    float pressure;
    float altitude;
};

struct AccelerationTransform
{
    float cr;
    float sr;
    float cp;
    float sp;
    float scale;

    Acceleration apply(const Acceleration &input) const
    {
        return apply(input.x, input.y, input.z);
    }

    Acceleration apply(float x, float y, float z) const
    {
        // Serial.printf("In: %.2f %.2f %.2f\n", x, y, z);
        float x1 = x;
        float y1 = cr * y - sr * z;
        float z1 = sr * y + cr * z;

        Acceleration output;
        output.x = scale * (cp * x1 + sp * z1);
        output.y = scale * y1;
        output.z = scale * (-sp * x1 + cp * z1);
        // Serial.printf("Out: %.2f %.2f %.2f\n", output.x, output.y, output.z);

        return output;
    }
};

class SystemState
{
private:
    HardwareSerial _gps;
    HTTPClient _http;
    Adafruit_MPU6050 _mpu6050;
    MAX30105 _max30102;
    TinyGPSPlus _neo6m;
    Adafruit_BMP280 _bmp280;

    uint8_t _buzz_pin;

    AccelerationTransform _accel_transform;

    bool _initialize_accel_transform(uint32_t iterations, uint32_t delay_per_iteration_ms = 100);

public:
    SystemState() = delete;
    explicit SystemState(const char *url, uint8_t buzz_pin);

    bool read(MPU6050Data &result);
    bool read(MAX30102Data &result);
    bool read(NEO6MData &result);
    bool read(BMP280Data &result);

    void silent();
    void buzz(uint32_t milliseconds);

    void led_on();
    void led_off();

    void http_post(const String &payload);
};

class LedGuard
{
private:
    SystemState *_state;

public:
    explicit LedGuard(SystemState *state) : _state(state)
    {
        if (_state != nullptr)
        {
            _state->led_on();
        }
    }

    ~LedGuard()
    {
        if (_state != nullptr)
        {
            _state->led_off();
        }
    }
};
