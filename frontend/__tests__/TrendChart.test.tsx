import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import TrendChart from '@/components/TrendChart';

// Mock Recharts components to avoid rendering issues in tests
jest.mock('recharts', () => {
  const OriginalModule = jest.requireActual('recharts');
  return {
    ...OriginalModule,
    ResponsiveContainer: ({ children }: any) => (
      <div data-testid="responsive-container">{children}</div>
    ),
    ComposedChart: ({ children, data }: any) => (
      <div data-testid="composed-chart" data-chart-data={JSON.stringify(data)}>
        {children}
      </div>
    ),
    LineChart: ({ children, data }: any) => (
      <div data-testid="line-chart" data-chart-data={JSON.stringify(data)}>
        {children}
      </div>
    ),
    Line: ({ dataKey, stroke }: any) => (
      <div data-testid={`line-${dataKey}`} data-stroke={stroke} />
    ),
    Area: ({ dataKey, fill }: any) => (
      <div data-testid={`area-${dataKey}`} data-fill={fill} />
    ),
    XAxis: () => <div data-testid="x-axis" />,
    YAxis: () => <div data-testid="y-axis" />,
    CartesianGrid: () => <div data-testid="cartesian-grid" />,
    Tooltip: () => <div data-testid="tooltip" />,
    Legend: () => <div data-testid="legend" />,
    ReferenceLine: ({ y }: any) => <div data-testid="reference-line" data-y={y} />,
  };
});

describe('TrendChart Component', () => {
  const mockDataPoints = [
    {
      date: '2024-01-01',
      value: 13.5,
      normalRange: { min: 12.0, max: 16.0 },
    },
    {
      date: '2024-02-01',
      value: 14.0,
      normalRange: { min: 12.0, max: 16.0 },
    },
    {
      date: '2024-03-01',
      value: 14.5,
      normalRange: { min: 12.0, max: 16.0 },
    },
  ];

  describe('Rendering', () => {
    it('should render the component with parameter name', () => {
      render(
        <TrendChart parameterName="Hemoglobin" dataPoints={mockDataPoints} />
      );

      expect(screen.getByText('Hemoglobin')).toBeInTheDocument();
    });

    it('should render chart components', () => {
      render(
        <TrendChart parameterName="Hemoglobin" dataPoints={mockDataPoints} />
      );

      expect(screen.getByTestId('responsive-container')).toBeInTheDocument();
      expect(screen.getByTestId('composed-chart')).toBeInTheDocument();
      expect(screen.getByTestId('x-axis')).toBeInTheDocument();
      expect(screen.getByTestId('y-axis')).toBeInTheDocument();
      expect(screen.getByTestId('cartesian-grid')).toBeInTheDocument();
    });

    it('should display data points summary', () => {
      render(
        <TrendChart parameterName="Hemoglobin" dataPoints={mockDataPoints} />
      );

      expect(screen.getByText(/3 reports/i)).toBeInTheDocument();
      expect(screen.getByText(/14.5/)).toBeInTheDocument();
    });

    it('should render empty state when no data points', () => {
      render(<TrendChart parameterName="Hemoglobin" dataPoints={[]} />);

      expect(
        screen.getByText(/No trend data available for Hemoglobin/i)
      ).toBeInTheDocument();
    });
  });

  describe('Trend Direction Indicator', () => {
    it('should show improving trend when values move toward normal range', () => {
      const improvingData = [
        {
          date: '2024-01-01',
          value: 18.0, // Above normal
          normalRange: { min: 12.0, max: 16.0 },
        },
        {
          date: '2024-02-01',
          value: 17.0, // Moving toward normal
          normalRange: { min: 12.0, max: 16.0 },
        },
      ];

      render(
        <TrendChart parameterName="Hemoglobin" dataPoints={improvingData} />
      );

      expect(screen.getByText('Improving')).toBeInTheDocument();
      expect(screen.getByText('↑')).toBeInTheDocument();
    });

    it('should show worsening trend when values move away from normal range', () => {
      const worseningData = [
        {
          date: '2024-01-01',
          value: 16.5, // Slightly above normal
          normalRange: { min: 12.0, max: 16.0 },
        },
        {
          date: '2024-02-01',
          value: 18.0, // Moving further from normal
          normalRange: { min: 12.0, max: 16.0 },
        },
      ];

      render(
        <TrendChart parameterName="Hemoglobin" dataPoints={worseningData} />
      );

      expect(screen.getByText('Worsening')).toBeInTheDocument();
      expect(screen.getByText('↓')).toBeInTheDocument();
    });

    it('should show stable trend when values remain relatively constant', () => {
      const stableData = [
        {
          date: '2024-01-01',
          value: 14.0,
          normalRange: { min: 12.0, max: 16.0 },
        },
        {
          date: '2024-02-01',
          value: 14.1, // Minimal change
          normalRange: { min: 12.0, max: 16.0 },
        },
      ];

      render(
        <TrendChart parameterName="Hemoglobin" dataPoints={stableData} />
      );

      expect(screen.getByText('Stable')).toBeInTheDocument();
      expect(screen.getByText('→')).toBeInTheDocument();
    });

    it('should show stable trend with single data point', () => {
      const singleDataPoint = [
        {
          date: '2024-01-01',
          value: 14.0,
          normalRange: { min: 12.0, max: 16.0 },
        },
      ];

      render(
        <TrendChart parameterName="Hemoglobin" dataPoints={singleDataPoint} />
      );

      expect(screen.getByText('Stable')).toBeInTheDocument();
    });
  });

  describe('Normal Range Display', () => {
    it('should render normal range areas', () => {
      render(
        <TrendChart parameterName="Hemoglobin" dataPoints={mockDataPoints} />
      );

      expect(screen.getByTestId('area-normalMax')).toBeInTheDocument();
      expect(screen.getByTestId('area-normalMin')).toBeInTheDocument();
    });

    it('should render reference lines for normal range boundaries', () => {
      render(
        <TrendChart parameterName="Hemoglobin" dataPoints={mockDataPoints} />
      );

      const referenceLines = screen.getAllByTestId('reference-line');
      expect(referenceLines.length).toBeGreaterThanOrEqual(2);
    });
  });

  describe('Accessibility', () => {
    it('should have accessible trend indicator label', () => {
      render(
        <TrendChart parameterName="Hemoglobin" dataPoints={mockDataPoints} />
      );

      const trendIndicator = screen.getByLabelText(/Trend:/i);
      expect(trendIndicator).toBeInTheDocument();
    });

    it('should display parameter name as heading', () => {
      render(
        <TrendChart parameterName="Hemoglobin" dataPoints={mockDataPoints} />
      );

      const heading = screen.getByText('Hemoglobin');
      expect(heading).toHaveClass('text-lg', 'font-semibold');
    });
  });

  describe('Responsive Design', () => {
    it('should use ResponsiveContainer for chart', () => {
      render(
        <TrendChart parameterName="Hemoglobin" dataPoints={mockDataPoints} />
      );

      expect(screen.getByTestId('responsive-container')).toBeInTheDocument();
    });
  });

  describe('Data Formatting', () => {
    it('should format dates correctly in chart data', () => {
      render(
        <TrendChart parameterName="Hemoglobin" dataPoints={mockDataPoints} />
      );

      const chartElement = screen.getByTestId('composed-chart');
      const chartData = JSON.parse(
        chartElement.getAttribute('data-chart-data') || '[]'
      );

      expect(chartData[0]).toHaveProperty('date');
      expect(chartData[0]).toHaveProperty('value');
      expect(chartData[0]).toHaveProperty('normalMin');
      expect(chartData[0]).toHaveProperty('normalMax');
    });

    it('should include all data points in chart', () => {
      render(
        <TrendChart parameterName="Hemoglobin" dataPoints={mockDataPoints} />
      );

      const chartElement = screen.getByTestId('composed-chart');
      const chartData = JSON.parse(
        chartElement.getAttribute('data-chart-data') || '[]'
      );

      expect(chartData.length).toBe(mockDataPoints.length);
    });
  });

  describe('Edge Cases', () => {
    it('should handle values below normal range', () => {
      const belowNormalData = [
        {
          date: '2024-01-01',
          value: 10.0, // Below normal
          normalRange: { min: 12.0, max: 16.0 },
        },
        {
          date: '2024-02-01',
          value: 11.0, // Still below but improving
          normalRange: { min: 12.0, max: 16.0 },
        },
      ];

      render(
        <TrendChart parameterName="Hemoglobin" dataPoints={belowNormalData} />
      );

      expect(screen.getByText('Improving')).toBeInTheDocument();
    });

    it('should handle values above normal range', () => {
      const aboveNormalData = [
        {
          date: '2024-01-01',
          value: 17.0, // Above normal
          normalRange: { min: 12.0, max: 16.0 },
        },
        {
          date: '2024-02-01',
          value: 18.0, // Further above
          normalRange: { min: 12.0, max: 16.0 },
        },
      ];

      render(
        <TrendChart parameterName="Hemoglobin" dataPoints={aboveNormalData} />
      );

      expect(screen.getByText('Worsening')).toBeInTheDocument();
    });

    it('should handle values within normal range', () => {
      const normalData = [
        {
          date: '2024-01-01',
          value: 13.0,
          normalRange: { min: 12.0, max: 16.0 },
        },
        {
          date: '2024-02-01',
          value: 14.0,
          normalRange: { min: 12.0, max: 16.0 },
        },
      ];

      render(
        <TrendChart parameterName="Hemoglobin" dataPoints={normalData} />
      );

      // Should show stable since both are within normal range
      expect(screen.getByText('Stable')).toBeInTheDocument();
    });
  });
});
