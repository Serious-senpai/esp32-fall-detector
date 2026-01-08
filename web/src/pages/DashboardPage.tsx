import { useEffect, useState } from 'react';
import { DashboardLayout } from '../components/DashboardLayout';
import { apiClient } from '../api';
import type { Device, Event } from '../types';
import { useAuth } from '../auth';

export function DashboardPage() {
    const { user } = useAuth();
    const [devices, setDevices] = useState<Device[]>([]);
    const [recentEvents, setRecentEvents] = useState<Event[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        loadData();
    }, []);

    const loadData = async () => {
        setLoading(true);
        try {
            const devicesResult = await apiClient.getDevices();
            if (devicesResult.code === 0) {
                setDevices(devicesResult.data);

                // Load recent events from all devices
                const allEvents: Event[] = [];
                for (const device of devicesResult.data) {
                    const eventsResult = await apiClient.getDeviceEvents(device.id);
                    if (eventsResult.code === 0) {
                        allEvents.push(...eventsResult.data);
                    }
                }
                // Sort by ID (descending) and take the 10 most recent
                allEvents.sort((a, b) => b.id - a.id);
                setRecentEvents(allEvents.slice(0, 10));
            }
        } catch (error) {
            console.error('Failed to load data:', error);
        } finally {
            setLoading(false);
        }
    };

    return (
        <DashboardLayout>
            <h1>Dashboard</h1>
            <p>Welcome back, {user?.username}!</p>

            {loading ? (
                <div className="loading">Loading...</div>
            ) : (
                <>
                    <div className="stats-grid">
                        <div className="stat-card">
                            <h3>Total Devices</h3>
                            <p className="stat-value">{devices.length}</p>
                        </div>
                        <div className="stat-card">
                            <h3>Total Events</h3>
                            <p className="stat-value">{recentEvents.length}</p>
                        </div>
                    </div>

                    <section className="dashboard-section">
                        <h2>Recent Events</h2>
                        {recentEvents.length === 0 ? (
                            <p>No events recorded yet.</p>
                        ) : (
                            <div className="events-list">
                                {recentEvents.map((event) => (
                                    <div key={event.id} className="event-card">
                                        <div className="event-header">
                                            <h4>{event.device.name}</h4>
                                            <span className="event-id">#{event.id}</span>
                                        </div>
                                        <div className="event-details">
                                            <p><strong>Category:</strong> {event.category}</p>
                                            {event.heart_rate_bpm && (
                                                <p><strong>Heart Rate:</strong> {event.heart_rate_bpm} BPM</p>
                                            )}
                                            {event.spo2 && (
                                                <p><strong>SpO2:</strong> {event.spo2}%</p>
                                            )}
                                            {event.latitude && event.longitude && (
                                                <p>
                                                    <strong>Location:</strong>{' '}
                                                    <a
                                                        href={`https://www.google.com/maps?q=${event.latitude},${event.longitude}`}
                                                        target="_blank"
                                                        rel="noopener noreferrer"
                                                    >
                                                        {event.latitude.toFixed(4)}, {event.longitude.toFixed(4)}
                                                    </a>
                                                </p>
                                            )}
                                        </div>
                                    </div>
                                ))}
                            </div>
                        )}
                    </section>
                </>
            )}
        </DashboardLayout>
    );
}
