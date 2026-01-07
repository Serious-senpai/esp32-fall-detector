#include "initialize.hpp"
#include "state.hpp"

const char *wifi_ssid = "...";
const char *wifi_password = "...";
const uint64_t device_id = 42;
const String device_token = "string";

SystemState *STATE = nullptr;

#define BUZZER_PIN 5

void setup()
{
    Serial.begin(115200);

    initialize::wifi(wifi_ssid, wifi_password);
    STATE = new SystemState("http://192.168.1.142:8000/events/", BUZZER_PIN);
}

void send_payload(void *param)
{
    String *payload = static_cast<String *>(param);
    if (STATE != nullptr)
    {
        STATE->http_post(*payload);
    }

    delete payload;
    vTaskDelete(nullptr);
}

void loop()
{
    static bool alerting = false;
    if (alerting)
    {
        STATE->buzz(500);
        delay(500);
    }
    else
    {
        static TickType_t last_phase_1_tick = 0;
        constexpr TickType_t PHASE_1_TO_2 = 2000 / portTICK_PERIOD_MS;

        TickType_t current_tick = xTaskGetTickCount();
        MPU6050Data mpu5050;
        if (STATE->read(mpu5050))
        {
            if (abs(mpu5050.acceleration.z) < 0.1)
            {
                last_phase_1_tick = current_tick;
            }
            else if (mpu5050.acceleration.z < -1.0 && current_tick - last_phase_1_tick < PHASE_1_TO_2)
            {
                Serial.println("Fall detected! Sending payload:");

                String *payload = new String("{\"category\":1,\"device_id\":");
                *payload += String(device_id) +
                            String(",\"device_token\":\"") + device_token +
                            String("\",\"accel_x\":") + String(mpu5050.acceleration.x) +
                            String(",\"accel_y\":") + String(mpu5050.acceleration.y) +
                            String(",\"accel_z\":") + String(mpu5050.acceleration.z) +
                            String(",\"gyro_x\":") + String(mpu5050.gyroscope.x) +
                            String(",\"gyro_y\":") + String(mpu5050.gyroscope.y) +
                            String(",\"gyro_z\":") + String(mpu5050.gyroscope.z);

                MAX30102Data max30102;
                if (STATE->read(max30102))
                {
                    *payload += String(",\"heart_rate_bpm\":") + String(max30102.heart_rate) +
                                String(",\"spo2\":") + String(max30102.spo2);
                }

                NEO6MData neo6m;
                if (STATE->read(neo6m))
                {
                    *payload += String(",\"latitude\":") + String(neo6m.latitude) +
                                String(",\"longitude\":") + String(neo6m.longitude) +
                                String(",\"neo6m_altitude_meter\":") + String(neo6m.altitude);
                }

                BMP280Data bmp280;
                if (STATE->read(bmp280))
                {
                    *payload += String(",\"pressure_pa\":") + String(bmp280.pressure) +
                                String(",\"bmp280_altitude_meter\":") + String(bmp280.altitude);
                }

                *payload += String("}");

                Serial.println(*payload);

                xTaskCreatePinnedToCore(send_payload, "send_payload", 8192, static_cast<void *>(payload), 1, nullptr, 1);
                alerting = true;
            }
        }

        delay(80);
    }
}
