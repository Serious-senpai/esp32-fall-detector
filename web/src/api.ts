import axios, { AxiosError, AxiosInstance } from 'axios';
import type {
    Result,
    User,
    Device,
    Event,
    LoginRequest,
    LoginResponse,
    RegisterRequest,
    CreateDeviceRequest,
} from './types';

class ApiClient {
    private client: AxiosInstance;
    private token: string | null = null;

    constructor() {
        this.client = axios.create({
            baseURL: '/api',
            headers: {
                'Content-Type': 'application/json',
            },
        });

        // Load token from localStorage
        const storedToken = localStorage.getItem('token');
        if (storedToken) {
            this.setToken(storedToken);
        }

        // Add response interceptor for error handling
        this.client.interceptors.response.use(
            (response) => response,
            (error: AxiosError) => {
                if (error.response?.status === 401) {
                    this.clearToken();
                    window.location.href = '/login';
                }
                return Promise.reject(error);
            }
        );
    }

    setToken(token: string) {
        this.token = token;
        this.client.defaults.headers.common['Authorization'] = `Bearer ${token}`;
        localStorage.setItem('token', token);
    }

    clearToken() {
        this.token = null;
        delete this.client.defaults.headers.common['Authorization'];
        localStorage.removeItem('token');
    }

    getToken(): string | null {
        return this.token;
    }

    // Authentication endpoints
    async login(data: LoginRequest): Promise<LoginResponse> {
        const formData = new URLSearchParams();
        formData.append('username', data.username);
        formData.append('password', data.password);

        const response = await this.client.post<LoginResponse>('/login', formData, {
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
        });
        this.setToken(response.data.access_token);
        return response.data;
    }

    async getCurrentUser(): Promise<Result<User>> {
        const response = await this.client.get<Result<User>>('/@me');
        return response.data;
    }

    // User endpoints
    async registerUser(data: RegisterRequest): Promise<Result<User | null>> {
        const response = await this.client.post<Result<User | null>>('/users', data);
        return response.data;
    }

    async getUser(id: number): Promise<Result<User | null>> {
        const response = await this.client.get<Result<User | null>>(`/users/${id}`);
        return response.data;
    }

    // Device endpoints
    async getDevices(): Promise<Result<Device[]>> {
        const response = await this.client.get<Result<Device[]>>('/devices');
        return response.data;
    }

    async getDevice(id: number): Promise<Result<Device | null>> {
        const response = await this.client.get<Result<Device | null>>(`/devices/${id}`);
        return response.data;
    }

    async createDevice(data: CreateDeviceRequest): Promise<Result<Device | null>> {
        const response = await this.client.post<Result<Device | null>>('/devices', data);
        return response.data;
    }

    async getDeviceEvents(deviceId: number): Promise<Result<Event[]>> {
        const response = await this.client.get<Result<Event[]>>(`/devices/${deviceId}/events`);
        return response.data;
    }

    // Health check
    async healthCheck(): Promise<Result<null>> {
        const response = await this.client.get<Result<null>>('/');
        return response.data;
    }
}

export const apiClient = new ApiClient();
