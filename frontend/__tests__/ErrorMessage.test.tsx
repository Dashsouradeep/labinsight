import { render, screen, fireEvent } from '@testing-library/react';
import ErrorMessage from '@/components/ErrorMessage';

describe('ErrorMessage', () => {
  describe('Error type', () => {
    it('renders with error message', () => {
      const message = 'An error occurred while processing your request';
      render(<ErrorMessage message={message} />);
      
      const alert = screen.getByRole('alert');
      expect(alert).toBeInTheDocument();
      expect(alert).toHaveTextContent(message);
    });

    it('applies correct styling for error type', () => {
      render(<ErrorMessage message="Error message" />);
      
      const alert = screen.getByRole('alert');
      expect(alert).toHaveClass('bg-red-50', 'border-red-300');
    });

    it('renders error icon with correct styling', () => {
      const { container } = render(<ErrorMessage message="Error message" />);
      
      const svg = container.querySelector('svg');
      expect(svg).toBeInTheDocument();
      expect(svg).toHaveClass('text-red-600');
    });

    it('has assertive aria-live for immediate announcement', () => {
      render(<ErrorMessage message="Error message" />);
      
      const alert = screen.getByRole('alert');
      expect(alert).toHaveAttribute('aria-live', 'assertive');
    });
  });

  describe('Warning type', () => {
    it('renders with warning message', () => {
      const message = 'Please check your input';
      render(<ErrorMessage message={message} type="warning" />);
      
      const alert = screen.getByRole('alert');
      expect(alert).toBeInTheDocument();
      expect(alert).toHaveTextContent(message);
    });

    it('applies correct styling for warning type', () => {
      render(<ErrorMessage message="Warning message" type="warning" />);
      
      const alert = screen.getByRole('alert');
      expect(alert).toHaveClass('bg-orange-50', 'border-orange-300');
    });

    it('renders warning icon with correct styling', () => {
      const { container } = render(<ErrorMessage message="Warning message" type="warning" />);
      
      const svg = container.querySelector('svg');
      expect(svg).toBeInTheDocument();
      expect(svg).toHaveClass('text-orange-600');
    });
  });

  describe('Retry functionality', () => {
    it('renders retry button when onRetry is provided', () => {
      const onRetry = jest.fn();
      render(<ErrorMessage message="Error message" onRetry={onRetry} />);
      
      const retryButton = screen.getByRole('button', { name: /retry action/i });
      expect(retryButton).toBeInTheDocument();
      expect(retryButton).toHaveTextContent('Try Again');
    });

    it('does not render retry button when onRetry is not provided', () => {
      render(<ErrorMessage message="Error message" />);
      
      const retryButton = screen.queryByRole('button', { name: /retry action/i });
      expect(retryButton).not.toBeInTheDocument();
    });

    it('calls onRetry when retry button is clicked', () => {
      const onRetry = jest.fn();
      render(<ErrorMessage message="Error message" onRetry={onRetry} />);
      
      const retryButton = screen.getByRole('button', { name: /retry action/i });
      fireEvent.click(retryButton);
      
      expect(onRetry).toHaveBeenCalledTimes(1);
    });

    it('applies correct button styling for error type', () => {
      const onRetry = jest.fn();
      render(<ErrorMessage message="Error message" onRetry={onRetry} />);
      
      const retryButton = screen.getByRole('button', { name: /retry action/i });
      expect(retryButton).toHaveClass('bg-red-600', 'hover:bg-red-700');
    });

    it('applies correct button styling for warning type', () => {
      const onRetry = jest.fn();
      render(<ErrorMessage message="Warning message" type="warning" onRetry={onRetry} />);
      
      const retryButton = screen.getByRole('button', { name: /retry action/i });
      expect(retryButton).toHaveClass('bg-orange-600', 'hover:bg-orange-700');
    });
  });

  describe('Accessibility', () => {
    it('has role="alert" for screen readers', () => {
      render(<ErrorMessage message="Error message" />);
      
      expect(screen.getByRole('alert')).toBeInTheDocument();
    });

    it('has aria-hidden on icon', () => {
      const { container } = render(<ErrorMessage message="Error message" />);
      
      const svg = container.querySelector('svg');
      expect(svg).toHaveAttribute('aria-hidden', 'true');
    });

    it('retry button has accessible label', () => {
      const onRetry = jest.fn();
      render(<ErrorMessage message="Error message" onRetry={onRetry} />);
      
      const retryButton = screen.getByRole('button', { name: /retry action/i });
      expect(retryButton).toHaveAttribute('aria-label', 'Retry action');
    });

    it('uses minimum 16px font size for readability', () => {
      render(<ErrorMessage message="Error message" />);
      
      const text = screen.getByText('Error message');
      expect(text).toHaveClass('text-base'); // text-base is 16px in Tailwind
    });

    it('retry button has focus styles', () => {
      const onRetry = jest.fn();
      render(<ErrorMessage message="Error message" onRetry={onRetry} />);
      
      const retryButton = screen.getByRole('button', { name: /retry action/i });
      expect(retryButton).toHaveClass('focus:outline-none', 'focus:ring-2', 'focus:ring-offset-2');
    });
  });

  describe('Visual prominence', () => {
    it('has prominent border styling', () => {
      render(<ErrorMessage message="Error message" />);
      
      const alert = screen.getByRole('alert');
      expect(alert).toHaveClass('border-l-4', 'p-4', 'rounded-md');
    });

    it('has margin for spacing', () => {
      render(<ErrorMessage message="Error message" />);
      
      const alert = screen.getByRole('alert');
      expect(alert).toHaveClass('mb-4');
    });

    it('uses font-medium for emphasis', () => {
      render(<ErrorMessage message="Error message" />);
      
      const text = screen.getByText('Error message');
      expect(text).toHaveClass('font-medium');
    });
  });

  describe('User-friendly error messages', () => {
    it('displays clear error message for file upload failure', () => {
      const message = 'File upload failed. Please try again.';
      render(<ErrorMessage message={message} />);
      
      expect(screen.getByText(message)).toBeInTheDocument();
    });

    it('displays clear error message for OCR failure', () => {
      const message = 'Unable to extract text from the document. Please upload a clearer image.';
      render(<ErrorMessage message={message} />);
      
      expect(screen.getByText(message)).toBeInTheDocument();
    });

    it('displays clear error message for NER failure', () => {
      const message = 'Report format not recognized. Please ensure the document is a valid lab report.';
      render(<ErrorMessage message={message} />);
      
      expect(screen.getByText(message)).toBeInTheDocument();
    });

    it('displays clear error message for service unavailability', () => {
      const message = 'Service temporarily unavailable. Your request has been queued for processing.';
      render(<ErrorMessage message={message} />);
      
      expect(screen.getByText(message)).toBeInTheDocument();
    });
  });
});
