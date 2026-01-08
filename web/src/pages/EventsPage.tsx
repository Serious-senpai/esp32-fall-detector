import { useEffect, useState } from 'react';
import { DashboardLayout } from '../components/DashboardLayout';
import { apiClient } from '../api';
import type { Device, Event } from '../types';
import { SUCCESS } from '../types';

export function EventsPage() {
    const [devices, setDevices] = useState<Device[]>([]);
    const [selectedDeviceId, setSelectedDeviceId] = useState<number | null>(null);
    const [events, setEvents] = useState<Event[]>([]);
    const [loading, setLoading] = useState(true);
    const [eventsLoading, setEventsLoading] = useState(false);

    useEffect(() => {
        loadDevices();
    }, []);

    useEffect(() => {
        if (selectedDeviceId !== null) {
            loadEvents(selectedDeviceId);
        }
    }, [selectedDeviceId]);

    const loadDevices = async () => {
        setLoading(true);
        try {
            const result = await apiClient.getDevices();
            if (result.code === SUCCESS) {
                setDevices(result.data);
                if (result.data.length > 0) {
                    setSelectedDeviceId(result.data[0].id);
                }
            }
        } catch (error) {
            console.error('Failed to load devices:', error);
        } finally {
            setLoading(false);
        }
    };

    const loadEvents = async (deviceId: number) => {
        setEventsLoading(true);
        try {
            const result = await apiClient.getDeviceEvents(deviceId);
            if (result.code === SUCCESS) {
                // Sort events by ID (descending - most recent first)
                setEvents(result.data.sort((a, b) => b.id - a.id));
            }
        } catch (error) {
            console.error('Failed to load events:', error);
        } finally {
            setEventsLoading(false);
        }
    };

    const getCategoryLabel = (category: number): string => {
        const categories: Record<number, string> = {
            0: 'Normal',
            1: 'Fall Detected',
            2: 'Low Heart Rate',
            3: 'High Heart Rate',
        };
        return categories[category] || `Category ${category}`;
    };

    const getCategoryClass = (category: number): string => {
        const classes: Record<number, string> = {
            0: 'category-normal',
            1: 'category-fall',
            2: 'category-warning',
            3: 'category-warning',
        };
        return classes[category] || 'category-normal';
    };

    return (
        <DashboardLayout>
            <h1>Events</h1>

            {loading ? (
                <div className="loading">Loading...</div>
            ) : devices.length === 0 ? (
                <div className="empty-state">
                    <p>No devices found. Add a device first to view events.</p>
                </div>
            ) : (
                <>
                    <div className="filter-bar">
                        <label htmlFor="device-select">Filter by device:</label>
                        <select
                            id="device-select"
                            value={selectedDeviceId || ''}
                            onChange={(e) => setSelectedDeviceId(Number(e.target.value))}
                        >
                            {devices.map((device) => (
                                <option key={device.id} value={device.id}>
                                    {device.name}
                                </option>
                            ))}
                        </select>
                    </div>

                    {eventsLoading ? (
                        <div className="loading">Loading events...</div>
                    ) : events.length === 0 ? (
                        <div className="empty-state">
                            <p>No events found for this device.</p>
                        </div>
                    ) : (
                        <div className="events-table-container">
                            <table className="events-table">
                                <thead>
                                    <tr>
                                        <th>ID</th>
                                        <th>Category</th>
                                        <th>Heart Rate</th>
                                        <th>SpO2</th>
                                        <th>Acceleration</th>
                                        <th>Gyroscope</th>
                                        <th>Location</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {events.map((event) => (
                                        <tr key={event.id}>
                                            <td>{event.id}</td>
                                            <td>
                                                <span className={`category-badge ${getCategoryClass(event.category)}`}>
                                                    {getCategoryLabel(event.category)}
                                                </span>
                                            </td>
                                            <td>
                                                {event.heart_rate_bpm !== null
                                                    ? `${event.heart_rate_bpm} BPM`
                                                    : '-'}
                                            </td>
                                            <td>
                                                {event.spo2 !== null ? `${event.spo2}%` : '-'}
                                            </td>
                                            <td>
                                                {event.accel_x !== null &&
                                                    event.accel_y !== null &&
                                                    event.accel_z !== null
                                                    ? `${event.accel_x.toFixed(2)}, ${event.accel_y.toFixed(2)}, ${event.accel_z.toFixed(2)}`
                                                    : '-'}
                                            </td>
                                            <td>
                                                {event.gyro_x !== null &&
                                                    event.gyro_y !== null &&
                                                    event.gyro_z !== null
                                                    ? `${event.gyro_x.toFixed(2)}, ${event.gyro_y.toFixed(2)}, ${event.gyro_z.toFixed(2)}`
                                                    : '-'}
                                            </td>
                                            <td>
                                                {event.latitude !== null && event.longitude !== null ? (
                                                    <a
                                                        href={`https://www.google.com/maps?q=${event.latitude},${event.longitude}`}
                                                        target="_blank"
                                                        rel="noopener noreferrer"
                                                    >
                                                        View Map
                                                    </a>
                                                ) : (
                                                    '-'
                                                )}
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    )}
                </>
            )}
        </DashboardLayout>
    );
}
