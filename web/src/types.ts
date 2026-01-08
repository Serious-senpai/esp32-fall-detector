export interface Result<T> {
    code: number;
    data: T;
}

export interface User {
    id: number;
    username: string;
    discord_channel_id: number;
    hashed_password: string;
}

export interface Device {
    id: number;
    name: string;
    hashed_token: string;
    user: User;
}

export interface Event {
    id: number;
    category: number;
    accel_x: number | null;
    accel_y: number | null;
    accel_z: number | null;
    gyro_x: number | null;
    gyro_y: number | null;
    gyro_z: number | null;
    heart_rate_bpm: number | null;
    spo2: number | null;
    latitude: number | null;
    longitude: number | null;
    neo6m_altitude_meter: number | null;
    pressure_pa: number | null;
    bmp280_altitude_meter: number | null;
    device: Device;
}

export interface LoginRequest {
    username: string;
    password: string;
}

export interface LoginResponse {
    access_token: string;
    token_type: string;
}

export interface RegisterRequest {
    username: string;
    discord_user_id: string;
    password: string;
}

export interface CreateDeviceRequest {
    name: string;
    token: string;
}

export const SUCCESS = 0;
export const DATABASE_FAILURE = 1;
export const USER_NOT_FOUND = 2;
export const DEVICE_NOT_FOUND = 3;
export const INCORRECT_CREDENTIALS = 4;
export const DUPLICATE_USERNAME = 5;
export const INVALID_DISCORD_USER_ID = 6;
export const DISCORD_API_ERROR = 7;

export const ERROR_MESSAGES: Record<number, string> = {
    [SUCCESS]: 'Success',
    [DATABASE_FAILURE]: 'Database operation failed',
    [USER_NOT_FOUND]: 'User not found',
    [DEVICE_NOT_FOUND]: 'Device not found',
    [INCORRECT_CREDENTIALS]: 'Incorrect credentials',
    [DUPLICATE_USERNAME]: 'Username already exists',
    [INVALID_DISCORD_USER_ID]: 'Invalid Discord user ID',
    [DISCORD_API_ERROR]: 'Discord API error',
};

export function getErrorMessage(code: number): string {
    return ERROR_MESSAGES[code] || `Unknown error (code: ${code})`;
}
