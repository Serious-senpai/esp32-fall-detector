import { useEffect, useState, FormEvent } from 'react';
import { DashboardLayout } from '../components/DashboardLayout';
import { apiClient } from '../api';
import type { Device } from '../types';
import { getErrorMessage, SUCCESS } from '../types';

export function DevicesPage() {
    const [devices, setDevices] = useState<Device[]>([]);
    const [loading, setLoading] = useState(true);
    const [showModal, setShowModal] = useState(false);
    const [name, setName] = useState('');
    const [token, setToken] = useState('');
    const [error, setError] = useState('');
    const [submitting, setSubmitting] = useState(false);

    useEffect(() => {
        loadDevices();
    }, []);

    const loadDevices = async () => {
        setLoading(true);
        try {
            const result = await apiClient.getDevices();
            if (result.code === SUCCESS) {
                setDevices(result.data);
            }
        } catch (error) {
            console.error('Failed to load devices:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleSubmit = async (e: FormEvent) => {
        e.preventDefault();
        setError('');
        setSubmitting(true);

        try {
            const result = await apiClient.createDevice({ name, token });

            if (result.code !== SUCCESS) {
                setError(getErrorMessage(result.code));
                return;
            }

            if (!result.data) {
                setError('Failed to create device');
                return;
            }

            setShowModal(false);
            setName('');
            setToken('');
            await loadDevices();
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Failed to create device');
        } finally {
            setSubmitting(false);
        }
    };

    const generateToken = () => {
        const randomToken = Array.from(crypto.getRandomValues(new Uint8Array(32)))
            .map(b => b.toString(16).padStart(2, '0'))
            .join('');
        setToken(randomToken);
    };

    return (
        <DashboardLayout>
            <div className="page-header">
                <h1>Devices</h1>
                <button className="btn btn-primary" onClick={() => setShowModal(true)}>
                    Add Device
                </button>
            </div>

            {loading ? (
                <div className="loading">Loading...</div>
            ) : devices.length === 0 ? (
                <div className="empty-state">
                    <p>No devices found. Add your first device to get started!</p>
                </div>
            ) : (
                <div className="devices-grid">
                    {devices.map((device) => (
                        <div key={device.id} className="device-card">
                            <h3>{device.name}</h3>
                            <p className="device-id">ID: {device.id}</p>
                            <p className="device-owner">Owner: {device.user.username}</p>
                        </div>
                    ))}
                </div>
            )}

            {showModal && (
                <div className="modal-overlay" onClick={() => setShowModal(false)}>
                    <div className="modal" onClick={(e) => e.stopPropagation()}>
                        <div className="modal-header">
                            <h2>Add New Device</h2>
                            <button className="close-btn" onClick={() => setShowModal(false)}>
                                ×
                            </button>
                        </div>
                        <form onSubmit={handleSubmit}>
                            <div className="form-group">
                                <label htmlFor="name">Device Name</label>
                                <input
                                    id="name"
                                    type="text"
                                    value={name}
                                    onChange={(e) => setName(e.target.value)}
                                    required
                                    disabled={submitting}
                                    placeholder="My ESP32 Device"
                                />
                            </div>
                            <div className="form-group">
                                <label htmlFor="token">Device Token</label>
                                <div className="input-with-button">
                                    <input
                                        id="token"
                                        type="text"
                                        value={token}
                                        onChange={(e) => setToken(e.target.value)}
                                        required
                                        disabled={submitting}
                                        placeholder="Enter or generate a secure token"
                                    />
                                    <button
                                        type="button"
                                        className="btn btn-secondary"
                                        onClick={generateToken}
                                        disabled={submitting}
                                    >
                                        Generate
                                    </button>
                                </div>
                                <small>This token will be used by your ESP32 device to authenticate</small>
                            </div>
                            {error && <div className="error-message">{error}</div>}
                            <div className="modal-actions">
                                <button
                                    type="button"
                                    className="btn btn-secondary"
                                    onClick={() => setShowModal(false)}
                                    disabled={submitting}
                                >
                                    Cancel
                                </button>
                                <button type="submit" className="btn btn-primary" disabled={submitting}>
                                    {submitting ? 'Creating...' : 'Create Device'}
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
        </DashboardLayout>
    );
}
