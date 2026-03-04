# TrendChart Component

## Overview

The `TrendChart` component displays parameter trends across multiple lab reports using the Recharts library. It provides visual insights into how medical parameters change over time, helping users understand their health trajectory.

## Features

- **Line Chart**: Displays parameter values over time with clear data points
- **Normal Range Visualization**: Shows the normal range as a shaded area on the chart
- **Trend Direction Indicator**: Displays an arrow and label indicating whether the trend is improving, worsening, or stable
- **Responsive Design**: Automatically adjusts to different screen sizes
- **Interactive Tooltips**: Shows detailed information when hovering over data points
- **Accessibility**: Includes proper ARIA labels and semantic HTML

## Requirements

Validates Requirements:
- **11.7**: Provide a health trends page displaying multi-report comparisons
- **8.6**: Display trend indicators (arrows or graphs) for each tracked parameter

## Props

```typescript
interface TrendChartProps {
  parameterName: string;
  dataPoints: Array<{
    date: string;           // ISO date string (e.g., "2024-01-15")
    value: number;          // Parameter value
    normalRange: {
      min: number;          // Minimum normal value
      max: number;          // Maximum normal value
    };
  }>;
}
```

## Usage

### Basic Example

```tsx
import TrendChart from '@/components/TrendChart';

export default function TrendsPage() {
  const hemoglobinData = [
    {
      date: '2024-01-15',
      value: 11.5,
      normalRange: { min: 12.0, max: 16.0 },
    },
    {
      date: '2024-02-20',
      value: 12.5,
      normalRange: { min: 12.0, max: 16.0 },
    },
    {
      date: '2024-03-25',
      value: 13.8,
      normalRange: { min: 12.0, max: 16.0 },
    },
  ];

  return (
    <TrendChart
      parameterName="Hemoglobin"
      dataPoints={hemoglobinData}
    />
  );
}
```

### With API Data

```tsx
import TrendChart from '@/components/TrendChart';
import useSWR from 'swr';

export default function TrendsPage() {
  const { data: trends } = useSWR('/api/trends');

  if (!trends) return <div>Loading...</div>;

  return (
    <div className="space-y-6">
      {trends.parameters.map((param) => (
        <TrendChart
          key={param.parameter_name}
          parameterName={param.parameter_name}
          dataPoints={param.data_points.map((point) => ({
            date: point.date,
            value: point.value,
            normalRange: {
              min: point.normal_range.min,
              max: point.normal_range.max,
            },
          }))}
        />
      ))}
    </div>
  );
}
```

## Trend Direction Logic

The component automatically calculates the trend direction based on the last two data points:

### Improving Trend (↑)
- Values are moving **toward** the normal range
- Distance from normal range is decreasing
- Displayed with green styling

### Worsening Trend (↓)
- Values are moving **away from** the normal range
- Distance from normal range is increasing
- Displayed with red styling

### Stable Trend (→)
- Values remain relatively constant (within 5% threshold)
- Minimal change in distance from normal range
- Displayed with blue styling

### Calculation Example

```typescript
// For a value below normal range:
// Previous: 10.0 (normal: 12.0-16.0) → distance = 2.0
// Current:  11.5 (normal: 12.0-16.0) → distance = 0.5
// Change: -1.5 → Improving ↑

// For a value above normal range:
// Previous: 17.0 (normal: 12.0-16.0) → distance = 1.0
// Current:  18.5 (normal: 12.0-16.0) → distance = 2.5
// Change: +1.5 → Worsening ↓
```

## Visual Design

### Color Scheme
- **Primary Line**: `#088395` (primary color from Tailwind config)
- **Normal Range Shaded Area**: `#7AB2B2` with 20% opacity
- **Reference Lines**: `#7AB2B2` with dashed pattern
- **Improving Badge**: Green background with green text
- **Worsening Badge**: Red background with red text
- **Stable Badge**: Blue background with blue text

### Responsive Behavior
- Chart automatically adjusts to container width
- Fixed height of 300px for consistent appearance
- Mobile-friendly with readable font sizes (minimum 12px)

## Empty State

When no data points are provided, the component displays a friendly empty state:

```
┌─────────────────────────────────────┐
│  No trend data available for        │
│  [Parameter Name]                   │
└─────────────────────────────────────┘
```

## Accessibility

- **ARIA Labels**: Trend indicator includes `aria-label` describing the trend
- **Semantic HTML**: Uses proper heading hierarchy
- **Keyboard Navigation**: Chart tooltips are accessible via keyboard
- **Screen Reader Support**: All important information is available to screen readers

## Testing

The component includes comprehensive unit tests covering:
- Rendering with various data configurations
- Trend direction calculation (improving, worsening, stable)
- Normal range visualization
- Empty state handling
- Edge cases (values above/below/within normal range)
- Accessibility features
- Responsive design

Run tests:
```bash
npm test -- TrendChart.test.tsx
```

## Dependencies

- **recharts**: ^2.10.3 - Charting library
- **react**: ^18.2.0
- **tailwindcss**: ^3.4.0

## Browser Support

The component works in all modern browsers that support:
- ES6+ JavaScript
- SVG rendering
- CSS Grid and Flexbox

## Performance Considerations

- Uses `ResponsiveContainer` for efficient resizing
- Memoization not required for typical use cases (< 100 data points)
- For large datasets (> 100 points), consider data sampling or pagination

## Future Enhancements

Potential improvements for future iterations:
- Export chart as image (PNG/SVG)
- Zoom and pan functionality for large datasets
- Multiple parameter comparison on single chart
- Customizable date range filtering
- Animation on initial render
- Print-friendly styling

## Related Components

- **ParameterCard**: Displays individual parameter details
- **DisclaimerBanner**: Shows medical disclaimers
- **Header**: Navigation and user profile

## Support

For issues or questions about the TrendChart component, refer to:
- Design Document: `.kiro/specs/labinsight/design.md`
- Requirements: `.kiro/specs/labinsight/requirements.md`
- Task List: `.kiro/specs/labinsight/tasks.md`
