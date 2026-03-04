# LabInsight Frontend

Next.js frontend for the LabInsight health intelligence platform.

## Project Structure

```
frontend/
├── app/                    # Next.js app router
│   ├── auth/              # Authentication pages
│   ├── dashboard/         # Dashboard page
│   ├── upload/            # Upload page
│   ├── reports/           # Report detail pages
│   ├── trends/            # Trends page
│   ├── layout.tsx         # Root layout
│   ├── page.tsx           # Home page
│   └── globals.css        # Global styles
├── components/            # React components
│   ├── Header.tsx
│   ├── ParameterCard.tsx
│   ├── TrendChart.tsx
│   └── DisclaimerBanner.tsx
├── lib/                   # Utility functions
│   ├── api.ts            # API client
│   └── auth.ts           # Auth utilities
└── public/               # Static assets
```

## Running the Frontend

### Development Mode

```bash
npm run dev
```

Open http://localhost:3000

### Production Build

```bash
npm run build
npm start
```

## Environment Variables

Copy `.env.local.template` to `.env.local` and configure:

```bash
# Required
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=your-secret-key-here
```

## Design System

### Colors

The application uses a custom color palette:

- **Primary Dark**: `#09637E` - Headers, important text
- **Primary**: `#088395` - Links, buttons
- **Primary Light**: `#7AB2B2` - Accents, hover states
- **Primary Lighter**: `#EBF4F6` - Backgrounds

### Typography

- **Base Font Size**: 16px (for accessibility)
- **Font Family**: System fonts for performance
- **Line Height**: 1.5 for readability

### Accessibility

- **Contrast Ratio**: Minimum 4.5:1 for all text
- **Focus Indicators**: Visible on all interactive elements
- **Keyboard Navigation**: Full support
- **Screen Reader**: ARIA labels on all components
- **Mobile**: Responsive design for screens <768px

## Components

### Header
Navigation header with user profile and logout.

### ParameterCard
Displays a medical parameter with value, normal range, and risk level.

**Props:**
- `name`: Parameter name
- `value`: Numeric value
- `unit`: Unit of measurement
- `normalRange`: { min, max }
- `riskLevel`: 'Normal' | 'Mild Abnormal' | 'Critical'
- `explanation`: AI-generated explanation

### TrendChart
Line chart showing parameter trends over time.

**Props:**
- `parameterName`: Parameter name
- `dataPoints`: Array of { date, value, normalRange }

### DisclaimerBanner
Medical disclaimer banner.

**Props:**
- `type`: 'general' | 'critical' | 'mild'
- `message`: Disclaimer text

## Pages

### Home (`/`)
Landing page with platform overview.

### Login (`/auth/login`)
User login with email and password.

### Signup (`/auth/signup`)
User registration with medical disclaimer acknowledgment.

### Dashboard (`/dashboard`)
List of uploaded reports with status.

### Upload (`/app/upload`)
Drag-and-drop file upload with validation.

### Report Detail (`/reports/[id]`)
Detailed view of a single report with parameters and explanations.

### Trends (`/trends`)
Multi-report trend analysis with charts.

## API Integration

The frontend communicates with the backend API using:

- **SWR**: Data fetching with caching and revalidation
- **Axios**: HTTP client with interceptors
- **NextAuth**: Authentication and session management

### API Client

```typescript
import { apiClient } from '@/lib/api'

// GET request
const reports = await apiClient.get('/api/reports')

// POST request
const result = await apiClient.post('/api/reports/upload', formData)
```

## Testing

### Run Tests

```bash
npm test
```

### Run Tests in Watch Mode

```bash
npm run test:watch
```

### Test Coverage

```bash
npm test -- --coverage
```

## Code Quality

### Linting

```bash
npm run lint
```

### Type Checking

```bash
npx tsc --noEmit
```

## Styling

The application uses Tailwind CSS for styling.

### Custom Classes

```css
/* Primary button */
.btn-primary {
  @apply bg-primary hover:bg-primary-dark text-white px-4 py-2 rounded;
}

/* Card */
.card {
  @apply bg-white shadow-md rounded-lg p-6;
}
```

## Performance

- **Code Splitting**: Automatic with Next.js
- **Image Optimization**: Next.js Image component
- **Font Optimization**: System fonts
- **Bundle Size**: Monitored with webpack-bundle-analyzer

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Mobile Support

The application is fully responsive and optimized for:

- Mobile phones (320px - 767px)
- Tablets (768px - 1023px)
- Desktops (1024px+)

## Deployment

### Vercel (Recommended)

```bash
npm run build
vercel deploy
```

### Docker

```bash
docker build -t labinsight-frontend .
docker run -p 3000:3000 labinsight-frontend
```

### Static Export

```bash
npm run build
npm run export
```

## Security

- **HTTPS**: Required in production
- **CSP**: Content Security Policy headers
- **XSS Protection**: Input sanitization
- **CSRF Protection**: NextAuth CSRF tokens
- **Secure Cookies**: HttpOnly, Secure, SameSite
