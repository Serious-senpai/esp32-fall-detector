#include "state.hpp"

bool SystemState::_initialize_accel_transform(uint32_t iterations, uint32_t delay_per_iteration_ms)
{
    LedGuard led(this);

    MPU6050Data data;
    float average[3] = {0.0, 0.0, 0.0};
    for (uint32_t i = 0; i < iterations; i++)
    {
        if (read(data))
        {
            average[0] += data.acceleration.x;
            average[1] += data.acceleration.y;
            average[2] += data.acceleration.z;
            delay(delay_per_iteration_ms);
        }
        else
        {
            return false;
        }
    }

    average[0] /= iterations;
    average[1] /= iterations;
    average[2] /= iterations;

    const float norm = sqrt(average[0] * average[0] + average[1] * average[1] + average[2] * average[2]);
    if (norm < 1e-6f)
    {
        return false;
    }

    float roll = atan2(average[1], average[2]);
    float pitch = atan2(-average[0], sqrt(average[1] * average[1] + average[2] * average[2]));

    _accel_transform.cr = cos(roll);
    _accel_transform.sr = sin(roll);
    _accel_transform.cp = cos(pitch);
    _accel_transform.sp = sin(pitch);
    _accel_transform.scale = -1.0f / norm;

    return true;
}

SystemState::SystemState(const char *url, uint8_t buzz_pin)
    : _gps(2),
      _buzz_pin(buzz_pin),
      _accel_transform{1.0, 0.0, 1.0, 0.0, 1.0} // identity transform (+ no scaling)
{
    Wire.begin(21, 22);

    _gps.begin(9600, SERIAL_8N1, 16, 17);

    _http.begin(url);
    _http.addHeader("Content-Type", "application/json");

    if (!_mpu6050.begin())
    {
        Serial.println("Failed to find MPU6050 chip.");
        while (true)
        {
            delay(500);
        }
    }

    Serial.println("MPU6050 found.");

    if (!_max30102.begin(Wire, I2C_SPEED_FAST))
    {
        Serial.println("MAX30102 not found!");
        while (true)
        {
            delay(500);
        }
    }

    // _max30102.setup(
    //     0x1F,     // power level
    //     MA4_SIZE, // sample average
    //     2,        // led mode
    //     FreqS,    // sample rate
    //     411,      // pulse width
    //     4096      // adc range
    // );
    _max30102.setup();
    _max30102.setPulseAmplitudeIR(0x1F);
    _max30102.setPulseAmplitudeRed(0x1F);

    Serial.println("MAX30102 initialized");

    if (!_bmp280.begin(0x76)) // or 0x77 depending on SDO
    {
        Serial.println("BMP280 not found!");
        while (true)
        {
            delay(500);
        }
    }

    _bmp280.setSampling(
        Adafruit_BMP280::MODE_NORMAL,
        Adafruit_BMP280::SAMPLING_X2,  // temperature
        Adafruit_BMP280::SAMPLING_X16, // pressure
        Adafruit_BMP280::FILTER_X16,
        Adafruit_BMP280::STANDBY_MS_500);

    Serial.println("BMP280 initialized");

    pinMode(_buzz_pin, OUTPUT);
    silent();

    pinMode(LED_BUILTIN, OUTPUT);

    if (!_initialize_accel_transform(10))
    {
        Serial.println("Failed to initialize accelerometer transform.");
        while (true)
        {
            delay(500);
        }
    }

    Serial.println("Acceleration transform initialized.");
}

bool SystemState::read(MPU6050Data &result)
{
    sensors_event_t accel, gyro, temp;
    if (_mpu6050.getEvent(&accel, &gyro, &temp))
    {
        result.acceleration = _accel_transform.apply(
            accel.acceleration.x,
            accel.acceleration.y,
            accel.acceleration.z);

        result.gyroscope.x = gyro.gyro.x;
        result.gyroscope.y = gyro.gyro.y;
        result.gyroscope.z = gyro.gyro.z;
        return true;
    }

    return false;
}

bool SystemState::read(MAX30102Data &result)
{
    static uint32_t ir[BUFFER_SIZE];
    static uint32_t red[BUFFER_SIZE];

    int32_t spo2;
    int8_t spo2_valid;
    int32_t heart_rate;
    int8_t hr_valid;

    // See https://github.com/sparkfun/SparkFun_MAX3010x_Sensor_Library/blob/master/examples/Example6_FIFO_Readings/Example6_FIFO_Readings.ino
    size_t index = 0;
    while (index < BUFFER_SIZE)
    {
        _max30102.check();
        while (_max30102.available() && index < BUFFER_SIZE)
        {
            ir[index] = _max30102.getFIFOIR();
            red[index] = _max30102.getFIFORed();
            _max30102.nextSample();
            index++;
        }
    }

    maxim_heart_rate_and_oxygen_saturation(
        ir,
        BUFFER_SIZE,
        red,
        &spo2,
        &spo2_valid,
        &heart_rate,
        &hr_valid);

    if (spo2_valid && hr_valid)
    {
        result.spo2 = spo2;
        result.heart_rate = heart_rate;
        return true;
    }

    return false;
}

bool SystemState::read(NEO6MData &result)
{
    while (_gps.available())
    {
        _neo6m.encode(_gps.read());
    }

    if (_neo6m.location.isValid())
    {
        result.latitude = _neo6m.location.lat();
        result.longitude = _neo6m.location.lng();
        result.altitude = _neo6m.altitude.meters();
        return true;
    }

    return false;
}

bool SystemState::read(BMP280Data &result)
{
    result.pressure = _bmp280.readPressure();
    result.altitude = _bmp280.readAltitude();
    return true;
}

void SystemState::silent()
{
    digitalWrite(_buzz_pin, HIGH);
}

void SystemState::buzz(uint32_t milliseconds)
{
    digitalWrite(_buzz_pin, LOW);
    delay(milliseconds);
    digitalWrite(_buzz_pin, HIGH);
}

void SystemState::led_on()
{
    digitalWrite(LED_BUILTIN, HIGH);
}

void SystemState::led_off()
{
    digitalWrite(LED_BUILTIN, LOW);
}

void SystemState::http_post(const String &payload)
{
    int status = _http.POST(payload);
    if (status > 0)
    {
        Serial.printf("HTTP Response code: %d\n", status);
    }
    else
    {
        Serial.printf("Error on sending POST: %s\n", _http.errorToString(status).c_str());
    }
}
