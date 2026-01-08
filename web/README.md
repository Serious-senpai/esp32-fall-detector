# ESP32 Fall Detector - Web Frontend

A modern web frontend application built with React, TypeScript, and Vite for the ESP32 Fall Detector system.

## Features

- 🔐 User authentication (login/register)
- 📱 Device management
- 📊 Event monitoring and visualization
- 🎨 Responsive design
- ⚡ Fast development with Vite

## Tech Stack

- **React 18** - UI library
- **TypeScript** - Type safety
- **Vite** - Build tool
- **React Router** - Client-side routing
- **Axios** - HTTP client

## Getting Started

### Prerequisites

- Node.js 18+ and npm
- Backend API server running

### Installation

1. Install dependencies:

```bash
npm install
```

2. Start the development server:

```bash
npm run dev
```

The application will be available at `http://localhost:3000`

### Building for Production

```bash
npm run build
```

This will create an optimized production build in the `dist` folder.

### Preview Production Build

```bash
npm run preview
```

## Project Structure

```
web/
├── src/
│   ├── components/       # Reusable UI components
│   │   ├── DashboardLayout.tsx
│   │   └── ProtectedRoute.tsx
│   ├── pages/           # Page components
│   │   ├── LoginPage.tsx
│   │   ├── RegisterPage.tsx
│   │   ├── DashboardPage.tsx
│   │   ├── DevicesPage.tsx
│   │   └── EventsPage.tsx
│   ├── api.ts           # API client
│   ├── auth.tsx         # Authentication context
│   ├── types.ts         # TypeScript types
│   ├── App.tsx          # Main app component
│   ├── App.css          # Global styles
│   └── main.tsx         # Entry point
├── index.html
├── package.json
├── tsconfig.json
└── vite.config.ts
```

## API Integration

The frontend connects to the FastAPI backend at `/api` through a Vite proxy configuration. The API client handles:

- JWT authentication
- User management
- Device management
- Event retrieval

## Development

### Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

### Environment Variables

The proxy configuration in `vite.config.ts` automatically routes API requests to the backend server when running in Docker Compose.

## Docker Integration

This application is designed to run in a Docker container alongside the backend API. The `compose.yml` in the root directory handles orchestration.

## Authentication Flow

1. User logs in with username and password
2. Backend returns JWT token
3. Token is stored in localStorage
4. Token is included in Authorization header for authenticated requests
5. Auto-redirect to login on 401 responses

## Features Details

### Dashboard
- Overview of devices and recent events
- Quick stats display

### Devices
- List all registered devices
- Add new devices with generated tokens
- View device details

### Events
- Filter events by device
- View detailed sensor data
- Google Maps integration for location data
- Color-coded event categories

## License

This project is part of the ESP32 Fall Detector system.
