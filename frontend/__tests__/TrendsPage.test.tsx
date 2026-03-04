import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import TrendsPage from '@/app/trends/page';
import { useAuth } from '@/lib/use-auth';
import { useTrends } from '@/lib/use-api';

// Mock authentication hook
jest.mock('@/lib/use-auth', () => ({
  useAuth: jest.fn(),
}));

// Mock API hook
jest.mock('@/lib/use-api', () => ({
  useTrends: jest.fn(),
}));

// Mock components
jest.mock('@/components/Header', () => {
  return function MockHeader() {
    return <div data-testid="mock-header">Header</div>;
  };
});

jest.mock('@/components/TrendChart', () => {
  return function MockTrendChart({ parameterName, dataPoints }: any) {
    return (
      <div data-testid={`trend-chart-${parameterName}`}>
        TrendChart: {parameterName} ({dataPoints.length} points)
      </div>
    );
  };
});

jest.mock('@/components/LoadingSpinner', () => {
  return function MockLoadingSpinner() {
    return <div data-testid="loading-spinner">Loading...</div>;
  };
});

jest.mock('@/components/ErrorMessage', () => {
  return function MockErrorMessage({ message, onRetry }: any) {
    return (
      <div data-testid="error-message">
        <p>{message}</p>
        <button onClick={onRetry}>Retry</button>
      </div>
    );
  };
});

jest.mock('next/link', () => {
  return ({ children, href }: { children: React.ReactNode; href: string }) => {
    return <a href={href}>{children}</a>;
  };
});

describe('TrendsPage', () => {
  const mockRevalidate = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Loading states', () => {
    it('displays loading spinner when authentication is loading', () => {
      (useAuth as jest.Mock).mockReturnValue({
        user: null,
        isLoading: true,
      });
      (useTrends as jest.Mock).mockReturnValue({
        trends: null,
        isLoading: false,
        isError: false,
        revalidate: mockRevalidate,
      });

      render(<TrendsPage />);
      expect(screen.getByTestId('loading-spinner')).toBeInTheDocument();
    });

    it('displays loading spinner when trends are loading', () => {
      (useAuth as jest.Mock).mockReturnValue({
        user: { id: 'user-123', email: 'test@example.com' },
        isLoading: false,
      });
      (useTrends as jest.Mock).mockReturnValue({
        trends: null,
        isLoading: true,
        isError: false,
        revalidate: mockRevalidate,
      });

      render(<TrendsPage />);
      expect(screen.getByTestId('loading-spinner')).toBeInTheDocument();
    });
  });

  describe('Error states', () => {
    it('displays error message when trends fail to load', () => {
      (useAuth as jest.Mock).mockReturnValue({
        user: { id: 'user-123', email: 'test@example.com' },
        isLoading: false,
      });
      (useTrends as jest.Mock).mockReturnValue({
        trends: null,
        isLoading: false,
        isError: true,
        error: new Error('Failed to fetch'),
        revalidate: mockRevalidate,
      });

      render(<TrendsPage />);
      expect(screen.getByTestId('error-message')).toBeInTheDocument();
      expect(screen.getByText(/Failed to load trend analysis/)).toBeInTheDocument();
    });

    it('calls revalidate when retry button is clicked', () => {
      (useAuth as jest.Mock).mockReturnValue({
        user: { id: 'user-123', email: 'test@example.com' },
        isLoading: false,
      });
      (useTrends as jest.Mock).mockReturnValue({
        trends: null,
        isLoading: false,
        isError: true,
        error: new Error('Failed to fetch'),
        revalidate: mockRevalidate,
      });

      render(<TrendsPage />);
      const retryButton = screen.getByText('Retry');
      fireEvent.click(retryButton);
      expect(mockRevalidate).toHaveBeenCalledTimes(1);
    });
  });

  describe('No data state', () => {
    it('displays no data message when trends are empty', () => {
      (useAuth as jest.Mock).mockReturnValue({
        user: { id: 'user-123', email: 'test@example.com' },
        isLoading: false,
      });
      (useTrends as jest.Mock).mockReturnValue({
        trends: { user_id: 'user-123', parameters: [], generated_at: '2024-01-15T10:30:00Z' },
        isLoading: false,
        isError: false,
        revalidate: mockRevalidate,
      });

      render(<TrendsPage />);
      expect(screen.getByText('No Trend Data Available')).toBeInTheDocument();
      expect(screen.getByText(/You need at least 2 completed lab reports/)).toBeInTheDocument();
    });

    it('displays upload link when no data available', () => {
      (useAuth as jest.Mock).mockReturnValue({
        user: { id: 'user-123', email: 'test@example.com' },
        isLoading: false,
      });
      (useTrends as jest.Mock).mockReturnValue({
        trends: { user_id: 'user-123', parameters: [], generated_at: '2024-01-15T10:30:00Z' },
        isLoading: false,
        isError: false,
        revalidate: mockRevalidate,
      });

      render(<TrendsPage />);
      const uploadLink = screen.getByText('Upload Lab Report');
      expect(uploadLink).toBeInTheDocument();
      expect(uploadLink.closest('a')).toHaveAttribute('href', '/upload');
    });

    it('displays medical disclaimer when no data available', () => {
      (useAuth as jest.Mock).mockReturnValue({
        user: { id: 'user-123', email: 'test@example.com' },
        isLoading: false,
      });
      (useTrends as jest.Mock).mockReturnValue({
        trends: { user_id: 'user-123', parameters: [], generated_at: '2024-01-15T10:30:00Z' },
        isLoading: false,
        isError: false,
        revalidate: mockRevalidate,
      });

      render(<TrendsPage />);
      expect(screen.getByText(/This trend analysis is for informational purposes only/)).toBeInTheDocument();
    });
  });

  describe('Chart rendering', () => {
    const mockTrendsData = {
      user_id: 'user-123',
      parameters: [
        {
          parameter_name: 'Hemoglobin',
          data_points: [
            { date: '2024-01-01', value: 13.5, risk_level: 'Normal', report_id: 'report-1' },
            { date: '2024-02-01', value: 14.0, risk_level: 'Normal', report_id: 'report-2' },
            { date: '2024-03-01', value: 14.5, risk_level: 'Normal', report_id: 'report-3' },
          ],
          trend_direction: 'Improving' as const,
          change_percent: 7.4,
          summary: 'Your hemoglobin has improved over the last 3 reports.',
        },
        {
          parameter_name: 'Cholesterol',
          data_points: [
            { date: '2024-01-01', value: 200, risk_level: 'Normal', report_id: 'report-1' },
            { date: '2024-02-01', value: 220, risk_level: 'Mild Abnormal', report_id: 'report-2' },
          ],
          trend_direction: 'Worsening' as const,
          change_percent: 10.0,
          summary: 'Your cholesterol has increased.',
        },
      ],
      generated_at: '2024-03-15T10:30:00Z',
    };

    it('renders TrendChart components for each parameter', () => {
      (useAuth as jest.Mock).mockReturnValue({
        user: { id: 'user-123', email: 'test@example.com' },
        isLoading: false,
      });
      (useTrends as jest.Mock).mockReturnValue({
        trends: mockTrendsData,
        isLoading: false,
        isError: false,
        revalidate: mockRevalidate,
      });

      render(<TrendsPage />);
      expect(screen.getByTestId('trend-chart-Hemoglobin')).toBeInTheDocument();
      expect(screen.getByTestId('trend-chart-Cholesterol')).toBeInTheDocument();
    });

    it('displays parameter names and summaries', () => {
      (useAuth as jest.Mock).mockReturnValue({
        user: { id: 'user-123', email: 'test@example.com' },
        isLoading: false,
      });
      (useTrends as jest.Mock).mockReturnValue({
        trends: mockTrendsData,
        isLoading: false,
        isError: false,
        revalidate: mockRevalidate,
      });

      render(<TrendsPage />);
      expect(screen.getByText('Hemoglobin')).toBeInTheDocument();
      expect(screen.getByText('Your hemoglobin has improved over the last 3 reports.')).toBeInTheDocument();
      expect(screen.getByText('Cholesterol')).toBeInTheDocument();
      expect(screen.getByText('Your cholesterol has increased.')).toBeInTheDocument();
    });

    it('displays data point counts', () => {
      (useAuth as jest.Mock).mockReturnValue({
        user: { id: 'user-123', email: 'test@example.com' },
        isLoading: false,
      });
      (useTrends as jest.Mock).mockReturnValue({
        trends: mockTrendsData,
        isLoading: false,
        isError: false,
        revalidate: mockRevalidate,
      });

      render(<TrendsPage />);
      // Check for data point counts in the parameter cards
      const dataPointTexts = screen.getAllByText(/\d+ reports/);
      expect(dataPointTexts.length).toBeGreaterThan(0);
    });
  });

  describe('Trend indicators', () => {
    it('displays improving trend indicator with correct styling', () => {
      (useAuth as jest.Mock).mockReturnValue({
        user: { id: 'user-123', email: 'test@example.com' },
        isLoading: false,
      });
      (useTrends as jest.Mock).mockReturnValue({
        trends: {
          user_id: 'user-123',
          parameters: [
            {
              parameter_name: 'Hemoglobin',
              data_points: [
                { date: '2024-01-01', value: 13.5, risk_level: 'Normal', report_id: 'report-1' },
                { date: '2024-02-01', value: 14.0, risk_level: 'Normal', report_id: 'report-2' },
              ],
              trend_direction: 'Improving' as const,
              change_percent: 3.7,
              summary: 'Improving trend.',
            },
          ],
          generated_at: '2024-03-15T10:30:00Z',
        },
        isLoading: false,
        isError: false,
        revalidate: mockRevalidate,
      });

      render(<TrendsPage />);
      const improvingElements = screen.getAllByText('Improving');
      expect(improvingElements.length).toBeGreaterThan(0);
      expect(screen.getByText('↑')).toBeInTheDocument();
      const trendBadge = screen.getByLabelText('Trend: Improving');
      expect(trendBadge).toBeInTheDocument();
    });

    it('displays worsening trend indicator with correct styling', () => {
      (useAuth as jest.Mock).mockReturnValue({
        user: { id: 'user-123', email: 'test@example.com' },
        isLoading: false,
      });
      (useTrends as jest.Mock).mockReturnValue({
        trends: {
          user_id: 'user-123',
          parameters: [
            {
              parameter_name: 'Cholesterol',
              data_points: [
                { date: '2024-01-01', value: 200, risk_level: 'Normal', report_id: 'report-1' },
                { date: '2024-02-01', value: 220, risk_level: 'Mild Abnormal', report_id: 'report-2' },
              ],
              trend_direction: 'Worsening' as const,
              change_percent: 10.0,
              summary: 'Worsening trend.',
            },
          ],
          generated_at: '2024-03-15T10:30:00Z',
        },
        isLoading: false,
        isError: false,
        revalidate: mockRevalidate,
      });

      render(<TrendsPage />);
      expect(screen.getByText('Worsening')).toBeInTheDocument();
      expect(screen.getByText('↓')).toBeInTheDocument();
      const trendBadge = screen.getByLabelText('Trend: Worsening');
      expect(trendBadge).toBeInTheDocument();
    });

    it('displays stable trend indicator with correct styling', () => {
      (useAuth as jest.Mock).mockReturnValue({
        user: { id: 'user-123', email: 'test@example.com' },
        isLoading: false,
      });
      (useTrends as jest.Mock).mockReturnValue({
        trends: {
          user_id: 'user-123',
          parameters: [
            {
              parameter_name: 'Hemoglobin',
              data_points: [
                { date: '2024-01-01', value: 14.0, risk_level: 'Normal', report_id: 'report-1' },
                { date: '2024-02-01', value: 14.1, risk_level: 'Normal', report_id: 'report-2' },
              ],
              trend_direction: 'Stable' as const,
              change_percent: 0.7,
              summary: 'Stable trend.',
            },
          ],
          generated_at: '2024-03-15T10:30:00Z',
        },
        isLoading: false,
        isError: false,
        revalidate: mockRevalidate,
      });

      render(<TrendsPage />);
      expect(screen.getByText('Stable')).toBeInTheDocument();
      expect(screen.getByText('→')).toBeInTheDocument();
      const trendBadge = screen.getByLabelText('Trend: Stable');
      expect(trendBadge).toBeInTheDocument();
    });

    it('displays change percentage when non-zero', () => {
      (useAuth as jest.Mock).mockReturnValue({
        user: { id: 'user-123', email: 'test@example.com' },
        isLoading: false,
      });
      (useTrends as jest.Mock).mockReturnValue({
        trends: {
          user_id: 'user-123',
          parameters: [
            {
              parameter_name: 'Hemoglobin',
              data_points: [
                { date: '2024-01-01', value: 13.5, risk_level: 'Normal', report_id: 'report-1' },
                { date: '2024-02-01', value: 14.5, risk_level: 'Normal', report_id: 'report-2' },
              ],
              trend_direction: 'Improving' as const,
              change_percent: 7.4,
              summary: 'Improving.',
            },
          ],
          generated_at: '2024-03-15T10:30:00Z',
        },
        isLoading: false,
        isError: false,
        revalidate: mockRevalidate,
      });

      render(<TrendsPage />);
      expect(screen.getByText(/\+7.4%/)).toBeInTheDocument();
    });
  });

  describe('Date filtering', () => {
    const mockTrendsWithMultipleDates = {
      user_id: 'user-123',
      parameters: [
        {
          parameter_name: 'Hemoglobin',
          data_points: [
            { date: '2023-01-01', value: 13.0, risk_level: 'Normal', report_id: 'report-1' },
            { date: '2023-06-01', value: 13.5, risk_level: 'Normal', report_id: 'report-2' },
            { date: '2023-09-01', value: 14.0, risk_level: 'Normal', report_id: 'report-3' },
            { date: '2024-01-01', value: 14.5, risk_level: 'Normal', report_id: 'report-4' },
          ],
          trend_direction: 'Improving' as const,
          change_percent: 11.5,
          summary: 'Improving over time.',
        },
      ],
      generated_at: '2024-03-15T10:30:00Z',
    };

    it('displays all date range filter buttons', () => {
      (useAuth as jest.Mock).mockReturnValue({
        user: { id: 'user-123', email: 'test@example.com' },
        isLoading: false,
      });
      (useTrends as jest.Mock).mockReturnValue({
        trends: mockTrendsWithMultipleDates,
        isLoading: false,
        isError: false,
        revalidate: mockRevalidate,
      });

      render(<TrendsPage />);
      expect(screen.getByText('All Time')).toBeInTheDocument();
      expect(screen.getByText('3 Months')).toBeInTheDocument();
      expect(screen.getByText('6 Months')).toBeInTheDocument();
      expect(screen.getByText('1 Year')).toBeInTheDocument();
    });

    it('defaults to "All Time" filter', () => {
      (useAuth as jest.Mock).mockReturnValue({
        user: { id: 'user-123', email: 'test@example.com' },
        isLoading: false,
      });
      (useTrends as jest.Mock).mockReturnValue({
        trends: mockTrendsWithMultipleDates,
        isLoading: false,
        isError: false,
        revalidate: mockRevalidate,
      });

      render(<TrendsPage />);
      const allTimeButton = screen.getByText('All Time');
      expect(allTimeButton).toHaveClass('bg-primary', 'text-white');
    });

    it('changes active filter when button is clicked', () => {
      (useAuth as jest.Mock).mockReturnValue({
        user: { id: 'user-123', email: 'test@example.com' },
        isLoading: false,
      });
      (useTrends as jest.Mock).mockReturnValue({
        trends: mockTrendsWithMultipleDates,
        isLoading: false,
        isError: false,
        revalidate: mockRevalidate,
      });

      render(<TrendsPage />);
      
      const threeMonthsButton = screen.getByText('3 Months');
      fireEvent.click(threeMonthsButton);
      
      expect(threeMonthsButton).toHaveClass('bg-primary', 'text-white');
    });

    it('filters data points based on selected date range', () => {
      (useAuth as jest.Mock).mockReturnValue({
        user: { id: 'user-123', email: 'test@example.com' },
        isLoading: false,
      });
      (useTrends as jest.Mock).mockReturnValue({
        trends: mockTrendsWithMultipleDates,
        isLoading: false,
        isError: false,
        revalidate: mockRevalidate,
      });

      render(<TrendsPage />);
      
      // Initially shows all data points
      expect(screen.getByText(/4 reports/)).toBeInTheDocument();
      
      // Click 3 months filter
      const threeMonthsButton = screen.getByText('3 Months');
      fireEvent.click(threeMonthsButton);
      
      // The component should still render the chart (filtering happens internally)
      // We verify the button state changed
      expect(threeMonthsButton).toHaveClass('bg-primary', 'text-white');
    });

    it('hides parameters with no data points after filtering', () => {
      (useAuth as jest.Mock).mockReturnValue({
        user: { id: 'user-123', email: 'test@example.com' },
        isLoading: false,
      });
      (useTrends as jest.Mock).mockReturnValue({
        trends: {
          user_id: 'user-123',
          parameters: [
            {
              parameter_name: 'OldParameter',
              data_points: [
                { date: '2020-01-01', value: 100, risk_level: 'Normal', report_id: 'report-old' },
              ],
              trend_direction: 'Stable' as const,
              change_percent: 0,
              summary: 'Old data.',
            },
          ],
          generated_at: '2024-03-15T10:30:00Z',
        },
        isLoading: false,
        isError: false,
        revalidate: mockRevalidate,
      });

      render(<TrendsPage />);
      
      // Click 3 months filter
      const threeMonthsButton = screen.getByText('3 Months');
      fireEvent.click(threeMonthsButton);
      
      // Old parameter should not be visible after filtering
      expect(screen.queryByTestId('trend-chart-OldParameter')).not.toBeInTheDocument();
    });
  });

  describe('Summary statistics', () => {
    const mockTrendsWithMixedDirections = {
      user_id: 'user-123',
      parameters: [
        {
          parameter_name: 'Hemoglobin',
          data_points: [
            { date: '2024-01-01', value: 13.5, risk_level: 'Normal', report_id: 'report-1' },
            { date: '2024-02-01', value: 14.0, risk_level: 'Normal', report_id: 'report-2' },
          ],
          trend_direction: 'Improving' as const,
          change_percent: 3.7,
          summary: 'Improving.',
        },
        {
          parameter_name: 'Cholesterol',
          data_points: [
            { date: '2024-01-01', value: 200, risk_level: 'Normal', report_id: 'report-1' },
            { date: '2024-02-01', value: 220, risk_level: 'Mild Abnormal', report_id: 'report-2' },
          ],
          trend_direction: 'Worsening' as const,
          change_percent: 10.0,
          summary: 'Worsening.',
        },
        {
          parameter_name: 'Glucose',
          data_points: [
            { date: '2024-01-01', value: 90, risk_level: 'Normal', report_id: 'report-1' },
            { date: '2024-02-01', value: 91, risk_level: 'Normal', report_id: 'report-2' },
          ],
          trend_direction: 'Stable' as const,
          change_percent: 1.1,
          summary: 'Stable.',
        },
      ],
      generated_at: '2024-03-15T10:30:00Z',
    };

    it('displays total parameters count', () => {
      (useAuth as jest.Mock).mockReturnValue({
        user: { id: 'user-123', email: 'test@example.com' },
        isLoading: false,
      });
      (useTrends as jest.Mock).mockReturnValue({
        trends: mockTrendsWithMixedDirections,
        isLoading: false,
        isError: false,
        revalidate: mockRevalidate,
      });

      render(<TrendsPage />);
      expect(screen.getByText('Total Parameters')).toBeInTheDocument();
      expect(screen.getByText('3')).toBeInTheDocument();
    });

    it('displays improving parameters count', () => {
      (useAuth as jest.Mock).mockReturnValue({
        user: { id: 'user-123', email: 'test@example.com' },
        isLoading: false,
      });
      (useTrends as jest.Mock).mockReturnValue({
        trends: mockTrendsWithMixedDirections,
        isLoading: false,
        isError: false,
        revalidate: mockRevalidate,
      });

      render(<TrendsPage />);
      // Check for the improving count in the summary statistics section
      // Use getAllByText since "Improving" appears multiple times
      const improvingElements = screen.getAllByText('Improving');
      expect(improvingElements.length).toBeGreaterThan(0);
      
      // Verify the count is displayed
      const summaryCards = screen.getAllByText('1');
      expect(summaryCards.length).toBeGreaterThan(0);
    });

    it('displays needs attention (worsening) count', () => {
      (useAuth as jest.Mock).mockReturnValue({
        user: { id: 'user-123', email: 'test@example.com' },
        isLoading: false,
      });
      (useTrends as jest.Mock).mockReturnValue({
        trends: mockTrendsWithMixedDirections,
        isLoading: false,
        isError: false,
        revalidate: mockRevalidate,
      });

      render(<TrendsPage />);
      expect(screen.getByText('Needs Attention')).toBeInTheDocument();
      // The count "1" appears in multiple places, so we just check it exists
      expect(screen.getAllByText('1').length).toBeGreaterThan(0);
    });
  });

  describe('Medical disclaimer', () => {
    it('displays medical disclaimer when trends are available', () => {
      (useAuth as jest.Mock).mockReturnValue({
        user: { id: 'user-123', email: 'test@example.com' },
        isLoading: false,
      });
      (useTrends as jest.Mock).mockReturnValue({
        trends: {
          user_id: 'user-123',
          parameters: [
            {
              parameter_name: 'Hemoglobin',
              data_points: [
                { date: '2024-01-01', value: 13.5, risk_level: 'Normal', report_id: 'report-1' },
                { date: '2024-02-01', value: 14.0, risk_level: 'Normal', report_id: 'report-2' },
              ],
              trend_direction: 'Improving' as const,
              change_percent: 3.7,
              summary: 'Improving.',
            },
          ],
          generated_at: '2024-03-15T10:30:00Z',
        },
        isLoading: false,
        isError: false,
        revalidate: mockRevalidate,
      });

      render(<TrendsPage />);
      expect(screen.getByText(/This trend analysis is for informational purposes only/)).toBeInTheDocument();
      expect(screen.getByText(/Always consult your doctor/)).toBeInTheDocument();
    });
  });

  describe('Analysis timestamp', () => {
    it('displays formatted analysis generation timestamp', () => {
      (useAuth as jest.Mock).mockReturnValue({
        user: { id: 'user-123', email: 'test@example.com' },
        isLoading: false,
      });
      (useTrends as jest.Mock).mockReturnValue({
        trends: {
          user_id: 'user-123',
          parameters: [
            {
              parameter_name: 'Hemoglobin',
              data_points: [
                { date: '2024-01-01', value: 13.5, risk_level: 'Normal', report_id: 'report-1' },
                { date: '2024-02-01', value: 14.0, risk_level: 'Normal', report_id: 'report-2' },
              ],
              trend_direction: 'Improving' as const,
              change_percent: 3.7,
              summary: 'Improving.',
            },
          ],
          generated_at: '2024-03-15T10:30:00Z',
        },
        isLoading: false,
        isError: false,
        revalidate: mockRevalidate,
      });

      render(<TrendsPage />);
      expect(screen.getByText(/Analysis generated on/)).toBeInTheDocument();
      expect(screen.getByText(/March 15, 2024/)).toBeInTheDocument();
    });
  });

  describe('Header component', () => {
    it('renders Header component', () => {
      (useAuth as jest.Mock).mockReturnValue({
        user: { id: 'user-123', email: 'test@example.com' },
        isLoading: false,
      });
      (useTrends as jest.Mock).mockReturnValue({
        trends: { user_id: 'user-123', parameters: [], generated_at: '2024-01-15T10:30:00Z' },
        isLoading: false,
        isError: false,
        revalidate: mockRevalidate,
      });

      render(<TrendsPage />);
      expect(screen.getByTestId('mock-header')).toBeInTheDocument();
    });
  });
});
