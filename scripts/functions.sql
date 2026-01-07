CREATE OR REPLACE FUNCTION generate_id()
RETURNS BIGINT
LANGUAGE plpgsql
AS $$
DECLARE
    v_epoch_ms BIGINT;
    v_tail BIGINT;
    v_id BIGINT;
BEGIN
    -- milliseconds since 2020-01-01 00:00:00 UTC
    v_epoch_ms :=
        FLOOR(
            (
                EXTRACT(EPOCH FROM clock_timestamp())
                - EXTRACT(EPOCH FROM TIMESTAMP '2020-01-01 00:00:00 UTC')
            ) * 1000
        );

    -- next 12-bit tail value
    v_tail := nextval('snowflake_id_tail');

    -- construct snowflake id: upper 52 bits | lower 12 bits
    v_id := (v_epoch_ms << 12) | v_tail;

    RETURN v_id;
END;
$$;

CREATE OR REPLACE FUNCTION create_user(
    p_username VARCHAR,
    p_discord_channel_id BIGINT,
    p_hashed_password VARCHAR
)
RETURNS TABLE (
    user_id BIGINT,
    user_username VARCHAR,
    user_discord_channel_id BIGINT,
    user_hashed_password VARCHAR
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    INSERT INTO Users (id, username, discord_channel_id, hashed_password)
    VALUES (generate_id(), p_username, p_discord_channel_id, p_hashed_password)
    RETURNING
        id AS user_id,
        username AS user_username,
        discord_channel_id AS user_discord_channel_id,
        hashed_password AS user_hashed_password;
END;
$$;

CREATE OR REPLACE FUNCTION create_device(
    p_name VARCHAR,
    p_hashed_token VARCHAR,
    p_user_id BIGINT
)
RETURNS TABLE (
    device_id BIGINT,
    device_name VARCHAR,
    device_hashed_token VARCHAR,
    user_id BIGINT,
    user_username VARCHAR,
    user_discord_channel_id BIGINT,
    user_hashed_password VARCHAR
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    WITH inserted AS (
        INSERT INTO Devices (id, name, hashed_token, user_id)
        VALUES (generate_id(), p_name, p_hashed_token, p_user_id)
        RETURNING *
    )
    SELECT 
        i.id AS device_id,
        i.name AS device_name,
        i.hashed_token AS device_hashed_token,
        u.user_id,
        u.user_username,
        u.user_discord_channel_id,
        u.user_hashed_password
    FROM inserted i
    JOIN view_users u ON u.user_id = i.user_id;
END;
$$;

CREATE OR REPLACE FUNCTION create_event(
    p_category SMALLINT,
    p_accel_x REAL,
    p_accel_y REAL,
    p_accel_z REAL,
    p_gyro_x REAL,
    p_gyro_y REAL,
    p_gyro_z REAL,
    p_heart_rate_bpm SMALLINT,
    p_spo2 SMALLINT,
    p_latitude REAL,
    p_longitude REAL,
    p_neo6m_altitude_meter REAL,
    p_pressure_pa REAL,
    p_bmp280_altitude_meter REAL,
    p_device_id BIGINT
)
RETURNS TABLE (
    event_id BIGINT,
    event_category SMALLINT,
    event_accel_x REAL,
    event_accel_y REAL,
    event_accel_z REAL,
    event_gyro_x REAL,
    event_gyro_y REAL,
    event_gyro_z REAL,
    event_heart_rate_bpm SMALLINT,
    event_spo2 SMALLINT,
    event_latitude REAL,
    event_longitude REAL,
    event_neo6m_altitude_meter REAL,
    event_pressure_pa REAL,
    event_bmp280_altitude_meter REAL,
    device_id BIGINT,
    device_name VARCHAR,
    device_hashed_token VARCHAR,
    user_id BIGINT,
    user_username VARCHAR,
    user_discord_channel_id BIGINT,
    user_hashed_password VARCHAR
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    WITH inserted AS (
        INSERT INTO Events (
            id,
            category,
            accel_x,
            accel_y,
            accel_z,
            gyro_x,
            gyro_y,
            gyro_z,
            heart_rate_bpm,
            spo2,
            latitude,
            longitude,
            neo6m_altitude_meter,
            pressure_pa,
            bmp280_altitude_meter,
            device_id
        )
        VALUES (
            generate_id(),
            p_category,
            p_accel_x,
            p_accel_y,
            p_accel_z,
            p_gyro_x,
            p_gyro_y,
            p_gyro_z,
            p_heart_rate_bpm,
            p_spo2,
            p_latitude,
            p_longitude,
            p_neo6m_altitude_meter,
            p_pressure_pa,
            p_bmp280_altitude_meter,
            p_device_id
        )
        RETURNING *
    )
    SELECT 
        i.id AS event_id,
        i.category AS event_category,
        i.accel_x AS event_accel_x,
        i.accel_y AS event_accel_y,
        i.accel_z AS event_accel_z,
        i.gyro_x AS event_gyro_x,
        i.gyro_y AS event_gyro_y,
        i.gyro_z AS event_gyro_z,
        i.heart_rate_bpm AS event_heart_rate_bpm,
        i.spo2 AS event_spo2,
        i.latitude AS event_latitude,
        i.longitude AS event_longitude,
        i.neo6m_altitude_meter AS event_neo6m_altitude_meter,
        i.pressure_pa AS event_pressure_pa,
        i.bmp280_altitude_meter AS event_bmp280_altitude_meter,
        d.device_id,
        d.device_name,
        d.device_hashed_token,
        d.user_id,
        d.user_username,
        d.user_discord_channel_id,
        d.user_hashed_password
    FROM inserted i
    JOIN view_devices d ON d.device_id = i.device_id;
END;
$$;
