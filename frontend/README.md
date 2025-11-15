# IoT Monitoring Frontend

A modern IoT monitoring application built with Vue 3, TypeScript, and Tailwind CSS.

## Tech Stack

- **Vue 3** - Progressive JavaScript framework
- **TypeScript** - Type-safe JavaScript
- **Tailwind CSS** - Utility-first CSS framework
- **Pinia** - State management
- **Vue Router** - Client-side routing
- **Axios** - HTTP client
- **Chart.js** - Data visualization
- **Vite** - Build tool

## Features

- ✅ Modern, responsive UI design
- ✅ Dark mode support
- ✅ TypeScript for type safety
- ✅ Component-based architecture
- ✅ State management with Pinia
- ✅ Route guards and authentication
- ✅ Real-time data updates (WebSocket ready)
- ✅ Comprehensive dashboard
- ✅ Device management
- ✅ Alert system
- ✅ Analytics and reporting

## Project Structure

```
src/
├── assets/           # Static assets
├── components/       # Vue components
│   ├── base/        # Reusable base components
│   └── modules/     # Feature-specific components
├── core/            # Core types, enums, constants
├── pages/           # Page components
├── router/          # Vue Router configuration
├── store/           # Pinia stores
├── styles/          # Global styles
└── utils/           # Utility functions
```

## Getting Started

### Prerequisites

- Node.js 18+
- npm or yarn

### Installation

```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## Environment Variables

Create `.env.development` and `.env.production` files:

```env
VITE_API_BASE_URL=http://localhost:3000/api
VITE_WS_URL=ws://localhost:3000
```

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build

## Design System

### Colors

- **Primary**: Blue (#3b82f6)
- **Secondary**: Slate (#64748b)
- **Success**: Green (#22c55e)
- **Warning**: Yellow (#eab308)
- **Danger**: Red (#ef4444)

### Breakpoints

- **sm**: 640px
- **md**: 768px
- **lg**: 1024px
- **xl**: 1280px
- **2xl**: 1536px

## Authentication

The application uses a mock authentication system. Default credentials:

- Email: any valid email
- Password: any password

## Contributing

1. Create a feature branch
2. Make your changes
3. Submit a pull request

## License

MIT
