import { ReactNode } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../auth';

interface DashboardLayoutProps {
    children: ReactNode;
}

export function DashboardLayout({ children }: DashboardLayoutProps) {
    const { user, logout } = useAuth();
    const navigate = useNavigate();
    const location = useLocation();

    const handleLogout = () => {
        logout();
        navigate('/login');
    };

    const isActive = (path: string) => location.pathname === path;

    return (
        <div className="dashboard-layout">
            <nav className="sidebar">
                <div className="sidebar-header">
                    <h2>ESP32 Fall Detector</h2>
                    {user && <p className="user-info">{user.username}</p>}
                </div>
                <ul className="nav-links">
                    <li className={isActive('/dashboard') ? 'active' : ''}>
                        <Link to="/dashboard">Dashboard</Link>
                    </li>
                    <li className={isActive('/devices') ? 'active' : ''}>
                        <Link to="/devices">Devices</Link>
                    </li>
                    <li className={isActive('/events') ? 'active' : ''}>
                        <Link to="/events">Events</Link>
                    </li>
                </ul>
                <button className="btn btn-secondary logout-btn" onClick={handleLogout}>
                    Logout
                </button>
            </nav>
            <main className="main-content">
                <div className="content-wrapper">{children}</div>
            </main>
        </div>
    );
}
