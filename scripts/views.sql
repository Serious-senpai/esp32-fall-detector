CREATE OR REPLACE VIEW view_users AS
SELECT
    id AS user_id,
    username AS user_username,
    discord_channel_id AS user_discord_channel_id,
    hashed_password AS user_hashed_password
FROM Users;

CREATE OR REPLACE VIEW view_devices AS
SELECT
    d.id AS device_id,
    d.name AS device_name,
    d.hashed_token as device_hashed_token,
    u.user_id,
    u.user_username,
    u.user_discord_channel_id,
    u.user_hashed_password
FROM Devices d
INNER JOIN view_users u ON d.user_id = u.user_id;

CREATE OR REPLACE VIEW view_events AS
SELECT
    e.id AS event_id,
    e.category AS event_category,
    e.accel_x AS event_accel_x,
    e.accel_y AS event_accel_y,
    e.accel_z AS event_accel_z,
    e.gyro_x AS event_gyro_x,
    e.gyro_y AS event_gyro_y,
    e.gyro_z AS event_gyro_z,
    e.heart_rate_bpm AS event_heart_rate_bpm,
    e.spo2 AS event_spo2,
    e.latitude AS event_latitude,
    e.longitude AS event_longitude,
    e.neo6m_altitude_meter AS event_neo6m_altitude_meter,
    e.pressure_pa AS event_pressure_pa,
    e.bmp280_altitude_meter AS event_bmp280_altitude_meter,
    d.device_id,
    d.device_name,
    d.device_hashed_token,
    d.user_id,
    d.user_username,
    d.user_discord_channel_id,
    d.user_hashed_password
FROM Events e
INNER JOIN view_devices d ON e.device_id = d.device_id;
