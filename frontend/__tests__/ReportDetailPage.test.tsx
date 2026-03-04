import { render, screen, waitFor } from '@testing-library/react';
import { useParams, useRouter } from 'next/navigation';
import ReportDetailPage from '@/app/reports/[id]/page';
import { useAuth } from '@/lib/use-auth';
import { useReport } from '@/lib/use-api';

// Mock Next.js navigation
jest.mock('next/navigation', () => ({
  useParams: jest.fn(),
  useRouter: jest.fn(),
}));

// Mock authentication hook
jest.mock('@/lib/use-auth', () => ({
  useAuth: jest.fn(),
}));

// Mock API hook
jest.mock('@/lib/use-api', () => ({
  useReport: jest.fn(),
}));

// Mock components
jest.mock('@/components/Header', () => {
  return function MockHeader() {
    return <div data-testid="mock-header">Header</div>;
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

jest.mock('@/components/DisclaimerBanner', () => {
  return function MockDisclaimerBanner({ type }: any) {
    return <div data-testid={`disclaimer-${type}`}>Disclaimer: {type}</div>;
  };
});

jest.mock('@/components/ParameterCard', () => {
  return function MockParameterCard({ name, value, unit, riskLevel }: any) {
    return (
      <div data-testid={`parameter-${name}`}>
        {name}: {value} {unit} - {riskLevel}
      </div>
    );
  };
});

describe('ReportDetailPage', () => {
  const mockRouter = {
    push: jest.fn(),
    back: jest.fn(),
  };

  const mockRevalidate = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
    (useRouter as jest.Mock).mockReturnValue(mockRouter);
    (useParams as jest.Mock).mockReturnValue({ id: 'test-report-123' });
  });

  describe('Loading states', () => {
    it('displays loading spinner when authentication is loading', () => {
      (useAuth as jest.Mock).mockReturnValue({
        user: null,
        isLoading: true,
      });
      (useReport as jest.Mock).mockReturnValue({
        report: null,
        isLoading: false,
        isError: false,
        revalidate: mockRevalidate,
      });

      render(<ReportDetailPage />);
      expect(screen.getByTestId('loading-spinner')).toBeInTheDocument();
    });

    it('displays loading spinner when report is loading', () => {
      (useAuth as jest.Mock).mockReturnValue({
        user: { id: 'user-123', email: 'test@example.com' },
        isLoading: false,
      });
      (useReport as jest.Mock).mockReturnValue({
        report: null,
        isLoading: true,
        isError: false,
        revalidate: mockRevalidate,
      });

      render(<ReportDetailPage />);
      expect(screen.getByTestId('loading-spinner')).toBeInTheDocument();
    });
  });

  describe('Error states', () => {
    it('displays error message when report fails to load', () => {
      (useAuth as jest.Mock).mockReturnValue({
        user: { id: 'user-123', email: 'test@example.com' },
        isLoading: false,
      });
      (useReport as jest.Mock).mockReturnValue({
        report: null,
        isLoading: false,
        isError: true,
        error: new Error('Failed to fetch'),
        revalidate: mockRevalidate,
      });

      render(<ReportDetailPage />);
      expect(screen.getByTestId('error-message')).toBeInTheDocument();
      expect(screen.getByText(/Failed to load report details/)).toBeInTheDocument();
    });
  });

  describe('Parameter display', () => {
    it('displays all parameters from the report', () => {
      const mockReport = {
        id: 'test-report-123',
        file_name: 'lab_results.pdf',
        upload_date: '2024-01-15T10:30:00Z',
        processing_status: 'completed' as const,
        file_size: 1024,
        file_type: 'application/pdf',
        parameters: [
          {
            name: 'Hemoglobin',
            value: 14.5,
            unit: 'g/dL',
            normal_range: { min: 13.5, max: 17.5 },
            risk_level: 'Normal' as const,
            explanation: 'Your hemoglobin is normal.',
            lifestyle_recommendations: [],
            organ_system: 'blood',
          },
          {
            name: 'Cholesterol',
            value: 220,
            unit: 'mg/dL',
            normal_range: { min: 125, max: 200 },
            risk_level: 'Mild Abnormal' as const,
            explanation: 'Your cholesterol is slightly elevated.',
            lifestyle_recommendations: ['Reduce saturated fat intake'],
            organ_system: 'cardiovascular',
          },
        ],
        summary: 'Overall, your results show mostly normal values.',
        overall_assessment: 'Continue monitoring your cholesterol.',
      };

      (useAuth as jest.Mock).mockReturnValue({
        user: { id: 'user-123', email: 'test@example.com' },
        isLoading: false,
      });
      (useReport as jest.Mock).mockReturnValue({
        report: mockReport,
        isLoading: false,
        isError: false,
        revalidate: mockRevalidate,
      });

      render(<ReportDetailPage />);

      // Check that both parameters are displayed
      expect(screen.getByTestId('parameter-Hemoglobin')).toBeInTheDocument();
      expect(screen.getByTestId('parameter-Cholesterol')).toBeInTheDocument();
      
      // Verify parameter details
      expect(screen.getByText(/Hemoglobin: 14.5 g\/dL - Normal/)).toBeInTheDocument();
      expect(screen.getByText(/Cholesterol: 220 mg\/dL - Mild Abnormal/)).toBeInTheDocument();
    });

    it('filters out parameters with Unknown risk level', () => {
      const mockReport = {
        id: 'test-report-123',
        file_name: 'lab_results.pdf',
        upload_date: '2024-01-15T10:30:00Z',
        processing_status: 'completed' as const,
        file_size: 1024,
        file_type: 'application/pdf',
        parameters: [
          {
            name: 'Hemoglobin',
            value: 14.5,
            unit: 'g/dL',
            normal_range: { min: 13.5, max: 17.5 },
            risk_level: 'Normal' as const,
            explanation: 'Your hemoglobin is normal.',
            lifestyle_recommendations: [],
            organ_system: 'blood',
          },
          {
            name: 'Unknown Parameter',
            value: 100,
            unit: 'units',
            normal_range: { min: 0, max: 0 },
            risk_level: 'Unknown' as const,
            explanation: 'No reference range available.',
            lifestyle_recommendations: [],
            organ_system: 'unknown',
          },
        ],
        summary: 'Overall results.',
        overall_assessment: 'Continue monitoring.',
      };

      (useAuth as jest.Mock).mockReturnValue({
        user: { id: 'user-123', email: 'test@example.com' },
        isLoading: false,
      });
      (useReport as jest.Mock).mockReturnValue({
        report: mockReport,
        isLoading: false,
        isError: false,
        revalidate: mockRevalidate,
      });

      render(<ReportDetailPage />);

      // Should display the normal parameter
      expect(screen.getByTestId('parameter-Hemoglobin')).toBeInTheDocument();
      
      // Should NOT display the unknown parameter
      expect(screen.queryByTestId('parameter-Unknown Parameter')).not.toBeInTheDocument();
    });

    it('displays message when no parameters are detected', () => {
      const mockReport = {
        id: 'test-report-123',
        file_name: 'lab_results.pdf',
        upload_date: '2024-01-15T10:30:00Z',
        processing_status: 'completed' as const,
        file_size: 1024,
        file_type: 'application/pdf',
        parameters: [],
        summary: '',
        overall_assessment: '',
      };

      (useAuth as jest.Mock).mockReturnValue({
        user: { id: 'user-123', email: 'test@example.com' },
        isLoading: false,
      });
      (useReport as jest.Mock).mockReturnValue({
        report: mockReport,
        isLoading: false,
        isError: false,
        revalidate: mockRevalidate,
      });

      render(<ReportDetailPage />);

      expect(screen.getByText(/No parameters were detected in this report/)).toBeInTheDocument();
    });
  });

  describe('Disclaimer visibility', () => {
    it('always displays general disclaimer', () => {
      const mockReport = {
        id: 'test-report-123',
        file_name: 'lab_results.pdf',
        upload_date: '2024-01-15T10:30:00Z',
        processing_status: 'completed' as const,
        file_size: 1024,
        file_type: 'application/pdf',
        parameters: [
          {
            name: 'Hemoglobin',
            value: 14.5,
            unit: 'g/dL',
            normal_range: { min: 13.5, max: 17.5 },
            risk_level: 'Normal' as const,
            explanation: 'Your hemoglobin is normal.',
            lifestyle_recommendations: [],
            organ_system: 'blood',
          },
        ],
        summary: 'All normal.',
        overall_assessment: 'Good health.',
      };

      (useAuth as jest.Mock).mockReturnValue({
        user: { id: 'user-123', email: 'test@example.com' },
        isLoading: false,
      });
      (useReport as jest.Mock).mockReturnValue({
        report: mockReport,
        isLoading: false,
        isError: false,
        revalidate: mockRevalidate,
      });

      render(<ReportDetailPage />);

      expect(screen.getByTestId('disclaimer-general')).toBeInTheDocument();
    });

    it('displays critical disclaimer when critical parameters exist', () => {
      const mockReport = {
        id: 'test-report-123',
        file_name: 'lab_results.pdf',
        upload_date: '2024-01-15T10:30:00Z',
        processing_status: 'completed' as const,
        file_size: 1024,
        file_type: 'application/pdf',
        parameters: [
          {
            name: 'Blood Glucose',
            value: 250,
            unit: 'mg/dL',
            normal_range: { min: 70, max: 100 },
            risk_level: 'Critical' as const,
            explanation: 'Your blood glucose is critically high.',
            lifestyle_recommendations: ['Consult doctor immediately'],
            organ_system: 'endocrine',
          },
        ],
        summary: 'Critical values detected.',
        overall_assessment: 'Seek medical attention.',
      };

      (useAuth as jest.Mock).mockReturnValue({
        user: { id: 'user-123', email: 'test@example.com' },
        isLoading: false,
      });
      (useReport as jest.Mock).mockReturnValue({
        report: mockReport,
        isLoading: false,
        isError: false,
        revalidate: mockRevalidate,
      });

      render(<ReportDetailPage />);

      expect(screen.getByTestId('disclaimer-general')).toBeInTheDocument();
      expect(screen.getByTestId('disclaimer-critical')).toBeInTheDocument();
    });

    it('displays mild disclaimer when only mild abnormal parameters exist', () => {
      const mockReport = {
        id: 'test-report-123',
        file_name: 'lab_results.pdf',
        upload_date: '2024-01-15T10:30:00Z',
        processing_status: 'completed' as const,
        file_size: 1024,
        file_type: 'application/pdf',
        parameters: [
          {
            name: 'Cholesterol',
            value: 220,
            unit: 'mg/dL',
            normal_range: { min: 125, max: 200 },
            risk_level: 'Mild Abnormal' as const,
            explanation: 'Your cholesterol is slightly elevated.',
            lifestyle_recommendations: ['Reduce saturated fat'],
            organ_system: 'cardiovascular',
          },
        ],
        summary: 'Mild abnormalities detected.',
        overall_assessment: 'Monitor your cholesterol.',
      };

      (useAuth as jest.Mock).mockReturnValue({
        user: { id: 'user-123', email: 'test@example.com' },
        isLoading: false,
      });
      (useReport as jest.Mock).mockReturnValue({
        report: mockReport,
        isLoading: false,
        isError: false,
        revalidate: mockRevalidate,
      });

      render(<ReportDetailPage />);

      expect(screen.getByTestId('disclaimer-general')).toBeInTheDocument();
      expect(screen.getByTestId('disclaimer-mild')).toBeInTheDocument();
      expect(screen.queryByTestId('disclaimer-critical')).not.toBeInTheDocument();
    });

    it('does not display mild disclaimer when critical parameters exist', () => {
      const mockReport = {
        id: 'test-report-123',
        file_name: 'lab_results.pdf',
        upload_date: '2024-01-15T10:30:00Z',
        processing_status: 'completed' as const,
        file_size: 1024,
        file_type: 'application/pdf',
        parameters: [
          {
            name: 'Cholesterol',
            value: 220,
            unit: 'mg/dL',
            normal_range: { min: 125, max: 200 },
            risk_level: 'Mild Abnormal' as const,
            explanation: 'Your cholesterol is slightly elevated.',
            lifestyle_recommendations: [],
            organ_system: 'cardiovascular',
          },
          {
            name: 'Blood Glucose',
            value: 250,
            unit: 'mg/dL',
            normal_range: { min: 70, max: 100 },
            risk_level: 'Critical' as const,
            explanation: 'Your blood glucose is critically high.',
            lifestyle_recommendations: [],
            organ_system: 'endocrine',
          },
        ],
        summary: 'Mixed results.',
        overall_assessment: 'Seek medical attention.',
      };

      (useAuth as jest.Mock).mockReturnValue({
        user: { id: 'user-123', email: 'test@example.com' },
        isLoading: false,
      });
      (useReport as jest.Mock).mockReturnValue({
        report: mockReport,
        isLoading: false,
        isError: false,
        revalidate: mockRevalidate,
      });

      render(<ReportDetailPage />);

      expect(screen.getByTestId('disclaimer-general')).toBeInTheDocument();
      expect(screen.getByTestId('disclaimer-critical')).toBeInTheDocument();
      // Mild disclaimer should not be shown when critical exists
      expect(screen.queryByTestId('disclaimer-mild')).not.toBeInTheDocument();
    });
  });

  describe('Recommendations display', () => {
    it('displays lifestyle recommendations when present', () => {
      const mockReport = {
        id: 'test-report-123',
        file_name: 'lab_results.pdf',
        upload_date: '2024-01-15T10:30:00Z',
        processing_status: 'completed' as const,
        file_size: 1024,
        file_type: 'application/pdf',
        parameters: [
          {
            name: 'Cholesterol',
            value: 220,
            unit: 'mg/dL',
            normal_range: { min: 125, max: 200 },
            risk_level: 'Mild Abnormal' as const,
            explanation: 'Your cholesterol is slightly elevated.',
            lifestyle_recommendations: [
              'Reduce saturated fat intake',
              'Exercise 30 minutes daily',
            ],
            organ_system: 'cardiovascular',
          },
        ],
        summary: 'Mild abnormalities.',
        overall_assessment: 'Monitor cholesterol.',
      };

      (useAuth as jest.Mock).mockReturnValue({
        user: { id: 'user-123', email: 'test@example.com' },
        isLoading: false,
      });
      (useReport as jest.Mock).mockReturnValue({
        report: mockReport,
        isLoading: false,
        isError: false,
        revalidate: mockRevalidate,
      });

      render(<ReportDetailPage />);

      expect(screen.getByText('Lifestyle Recommendations')).toBeInTheDocument();
      expect(screen.getByText('Reduce saturated fat intake')).toBeInTheDocument();
      expect(screen.getByText('Exercise 30 minutes daily')).toBeInTheDocument();
      expect(screen.getAllByText(/Related to: Cholesterol/)).toHaveLength(2);
    });

    it('does not display recommendations section when no recommendations exist', () => {
      const mockReport = {
        id: 'test-report-123',
        file_name: 'lab_results.pdf',
        upload_date: '2024-01-15T10:30:00Z',
        processing_status: 'completed' as const,
        file_size: 1024,
        file_type: 'application/pdf',
        parameters: [
          {
            name: 'Hemoglobin',
            value: 14.5,
            unit: 'g/dL',
            normal_range: { min: 13.5, max: 17.5 },
            risk_level: 'Normal' as const,
            explanation: 'Your hemoglobin is normal.',
            lifestyle_recommendations: [],
            organ_system: 'blood',
          },
        ],
        summary: 'All normal.',
        overall_assessment: 'Good health.',
      };

      (useAuth as jest.Mock).mockReturnValue({
        user: { id: 'user-123', email: 'test@example.com' },
        isLoading: false,
      });
      (useReport as jest.Mock).mockReturnValue({
        report: mockReport,
        isLoading: false,
        isError: false,
        revalidate: mockRevalidate,
      });

      render(<ReportDetailPage />);

      expect(screen.queryByText('Lifestyle Recommendations')).not.toBeInTheDocument();
    });

    it('removes duplicate recommendations', () => {
      const mockReport = {
        id: 'test-report-123',
        file_name: 'lab_results.pdf',
        upload_date: '2024-01-15T10:30:00Z',
        processing_status: 'completed' as const,
        file_size: 1024,
        file_type: 'application/pdf',
        parameters: [
          {
            name: 'Cholesterol',
            value: 220,
            unit: 'mg/dL',
            normal_range: { min: 125, max: 200 },
            risk_level: 'Mild Abnormal' as const,
            explanation: 'Your cholesterol is slightly elevated.',
            lifestyle_recommendations: ['Exercise 30 minutes daily'],
            organ_system: 'cardiovascular',
          },
          {
            name: 'Triglycerides',
            value: 180,
            unit: 'mg/dL',
            normal_range: { min: 0, max: 150 },
            risk_level: 'Mild Abnormal' as const,
            explanation: 'Your triglycerides are elevated.',
            lifestyle_recommendations: ['Exercise 30 minutes daily'],
            organ_system: 'cardiovascular',
          },
        ],
        summary: 'Cardiovascular markers elevated.',
        overall_assessment: 'Improve lifestyle.',
      };

      (useAuth as jest.Mock).mockReturnValue({
        user: { id: 'user-123', email: 'test@example.com' },
        isLoading: false,
      });
      (useReport as jest.Mock).mockReturnValue({
        report: mockReport,
        isLoading: false,
        isError: false,
        revalidate: mockRevalidate,
      });

      render(<ReportDetailPage />);

      // Should only display the recommendation once
      const recommendations = screen.getAllByText('Exercise 30 minutes daily');
      expect(recommendations).toHaveLength(1);
    });

    it('displays disclaimer note with recommendations', () => {
      const mockReport = {
        id: 'test-report-123',
        file_name: 'lab_results.pdf',
        upload_date: '2024-01-15T10:30:00Z',
        processing_status: 'completed' as const,
        file_size: 1024,
        file_type: 'application/pdf',
        parameters: [
          {
            name: 'Cholesterol',
            value: 220,
            unit: 'mg/dL',
            normal_range: { min: 125, max: 200 },
            risk_level: 'Mild Abnormal' as const,
            explanation: 'Your cholesterol is slightly elevated.',
            lifestyle_recommendations: ['Reduce saturated fat intake'],
            organ_system: 'cardiovascular',
          },
        ],
        summary: 'Mild abnormalities.',
        overall_assessment: 'Monitor cholesterol.',
      };

      (useAuth as jest.Mock).mockReturnValue({
        user: { id: 'user-123', email: 'test@example.com' },
        isLoading: false,
      });
      (useReport as jest.Mock).mockReturnValue({
        report: mockReport,
        isLoading: false,
        isError: false,
        revalidate: mockRevalidate,
      });

      render(<ReportDetailPage />);

      expect(screen.getByText(/These are general suggestions based on your results, not medical advice/)).toBeInTheDocument();
      expect(screen.getByText(/Always consult with your healthcare provider/)).toBeInTheDocument();
    });
  });

  describe('Report metadata display', () => {
    it('displays report file name', () => {
      const mockReport = {
        id: 'test-report-123',
        file_name: 'my_lab_results.pdf',
        upload_date: '2024-01-15T10:30:00Z',
        processing_status: 'completed' as const,
        file_size: 1024,
        file_type: 'application/pdf',
        parameters: [],
        summary: '',
        overall_assessment: '',
      };

      (useAuth as jest.Mock).mockReturnValue({
        user: { id: 'user-123', email: 'test@example.com' },
        isLoading: false,
      });
      (useReport as jest.Mock).mockReturnValue({
        report: mockReport,
        isLoading: false,
        isError: false,
        revalidate: mockRevalidate,
      });

      render(<ReportDetailPage />);

      expect(screen.getByText('my_lab_results.pdf')).toBeInTheDocument();
    });

    it('displays formatted upload date', () => {
      const mockReport = {
        id: 'test-report-123',
        file_name: 'lab_results.pdf',
        upload_date: '2024-01-15T10:30:00Z',
        processing_status: 'completed' as const,
        file_size: 1024,
        file_type: 'application/pdf',
        parameters: [],
        summary: '',
        overall_assessment: '',
      };

      (useAuth as jest.Mock).mockReturnValue({
        user: { id: 'user-123', email: 'test@example.com' },
        isLoading: false,
      });
      (useReport as jest.Mock).mockReturnValue({
        report: mockReport,
        isLoading: false,
        isError: false,
        revalidate: mockRevalidate,
      });

      render(<ReportDetailPage />);

      // Date should be formatted (exact format depends on locale)
      expect(screen.getByText(/January 15, 2024/)).toBeInTheDocument();
    });
  });

  describe('Summary display', () => {
    it('displays overall summary when present', () => {
      const mockReport = {
        id: 'test-report-123',
        file_name: 'lab_results.pdf',
        upload_date: '2024-01-15T10:30:00Z',
        processing_status: 'completed' as const,
        file_size: 1024,
        file_type: 'application/pdf',
        parameters: [],
        summary: 'Your lab results show mostly normal values with some areas to monitor.',
        overall_assessment: 'Continue with regular checkups.',
      };

      (useAuth as jest.Mock).mockReturnValue({
        user: { id: 'user-123', email: 'test@example.com' },
        isLoading: false,
      });
      (useReport as jest.Mock).mockReturnValue({
        report: mockReport,
        isLoading: false,
        isError: false,
        revalidate: mockRevalidate,
      });

      render(<ReportDetailPage />);

      expect(screen.getByText('Overall Summary')).toBeInTheDocument();
      expect(screen.getByText('Your lab results show mostly normal values with some areas to monitor.')).toBeInTheDocument();
      expect(screen.getByText('Continue with regular checkups.')).toBeInTheDocument();
    });

    it('does not display summary section when summary is empty', () => {
      const mockReport = {
        id: 'test-report-123',
        file_name: 'lab_results.pdf',
        upload_date: '2024-01-15T10:30:00Z',
        processing_status: 'completed' as const,
        file_size: 1024,
        file_type: 'application/pdf',
        parameters: [],
        summary: '',
        overall_assessment: '',
      };

      (useAuth as jest.Mock).mockReturnValue({
        user: { id: 'user-123', email: 'test@example.com' },
        isLoading: false,
      });
      (useReport as jest.Mock).mockReturnValue({
        report: mockReport,
        isLoading: false,
        isError: false,
        revalidate: mockRevalidate,
      });

      render(<ReportDetailPage />);

      expect(screen.queryByText('Overall Summary')).not.toBeInTheDocument();
    });
  });
});
