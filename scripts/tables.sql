CREATE SEQUENCE IF NOT EXISTS snowflake_id_tail
    AS BIGINT
    START WITH 0
    INCREMENT BY 1
    MINVALUE 0
    MAXVALUE 4095 -- 12 bits tail
    CYCLE;

CREATE TABLE IF NOT EXISTS Users (
    id BIGINT PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    discord_channel_id BIGINT NOT NULL,
    hashed_password VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS Devices (
    id BIGINT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    hashed_token VARCHAR(255) NOT NULL,
    user_id BIGINT REFERENCES Users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Events (
    id BIGINT PRIMARY KEY,
    category SMALLINT NOT NULL,
    accel_x REAL,
    accel_y REAL,
    accel_z REAL,
    gyro_x REAL,
    gyro_y REAL,
    gyro_z REAL,
    heart_rate_bpm SMALLINT,
    spo2 SMALLINT,
    latitude REAL,
    longitude REAL,
    neo6m_altitude_meter REAL,
    pressure_pa REAL,
    bmp280_altitude_meter REAL,
    device_id BIGINT REFERENCES Devices(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_devices_user_id ON Devices(user_id);
CREATE INDEX IF NOT EXISTS idx_events_device_id ON Events(device_id);
