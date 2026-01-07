#include "initialize.hpp"

namespace initialize
{
    void wifi(const char *ssid, const char *password)
    {
        WiFi.mode(WIFI_STA);
        WiFi.begin(ssid, password);

        Serial.print("Connecting to WiFi network \"");
        Serial.print(ssid);
        Serial.println("\"...");

        while (WiFi.status() != WL_CONNECTED)
        {
            delay(500);
        }

        Serial.print("Connected to WiFi network with IP Address: ");
        Serial.println(WiFi.localIP());
    }
}
