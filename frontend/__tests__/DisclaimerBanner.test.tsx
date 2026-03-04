import { render, screen } from '@testing-library/react';
import DisclaimerBanner from '@/components/DisclaimerBanner';

describe('DisclaimerBanner', () => {
  describe('General disclaimer type', () => {
    it('renders with default general message', () => {
      render(<DisclaimerBanner type="general" />);
      
      const banner = screen.getByRole('alert');
      expect(banner).toBeInTheDocument();
      expect(banner).toHaveTextContent('This is not medical advice');
      expect(banner).toHaveTextContent('informational purposes only');
    });

    it('renders with custom message', () => {
      const customMessage = 'Custom general disclaimer message';
      render(<DisclaimerBanner type="general" message={customMessage} />);
      
      expect(screen.getByText(customMessage)).toBeInTheDocument();
    });

    it('applies correct styling for general type', () => {
      render(<DisclaimerBanner type="general" />);
      
      const banner = screen.getByRole('alert');
      expect(banner).toHaveClass('bg-blue-50', 'border-blue-200');
    });

    it('has polite aria-live for general type', () => {
      render(<DisclaimerBanner type="general" />);
      
      const banner = screen.getByRole('alert');
      expect(banner).toHaveAttribute('aria-live', 'polite');
    });
  });

  describe('Critical disclaimer type', () => {
    it('renders with default critical message', () => {
      render(<DisclaimerBanner type="critical" />);
      
      const banner = screen.getByRole('alert');
      expect(banner).toBeInTheDocument();
      expect(banner).toHaveTextContent('Consult your doctor immediately');
      expect(banner).toHaveTextContent('urgent medical attention');
    });

    it('renders with custom message', () => {
      const customMessage = 'Custom critical disclaimer message';
      render(<DisclaimerBanner type="critical" message={customMessage} />);
      
      expect(screen.getByText(customMessage)).toBeInTheDocument();
    });

    it('applies correct styling for critical type', () => {
      render(<DisclaimerBanner type="critical" />);
      
      const banner = screen.getByRole('alert');
      expect(banner).toHaveClass('bg-red-50', 'border-red-300');
    });

    it('has assertive aria-live for critical type', () => {
      render(<DisclaimerBanner type="critical" />);
      
      const banner = screen.getByRole('alert');
      expect(banner).toHaveAttribute('aria-live', 'assertive');
    });

    it('renders warning icon for critical type', () => {
      const { container } = render(<DisclaimerBanner type="critical" />);
      
      // Check for SVG with warning icon path
      const svg = container.querySelector('svg');
      expect(svg).toBeInTheDocument();
      expect(svg).toHaveClass('text-red-600');
    });
  });

  describe('Mild disclaimer type', () => {
    it('renders with default mild message', () => {
      render(<DisclaimerBanner type="mild" />);
      
      const banner = screen.getByRole('alert');
      expect(banner).toBeInTheDocument();
      expect(banner).toHaveTextContent('Discuss with your doctor');
      expect(banner).toHaveTextContent('healthcare professional');
    });

    it('renders with custom message', () => {
      const customMessage = 'Custom mild disclaimer message';
      render(<DisclaimerBanner type="mild" message={customMessage} />);
      
      expect(screen.getByText(customMessage)).toBeInTheDocument();
    });

    it('applies correct styling for mild type', () => {
      render(<DisclaimerBanner type="mild" />);
      
      const banner = screen.getByRole('alert');
      expect(banner).toHaveClass('bg-yellow-50', 'border-yellow-200');
    });

    it('has polite aria-live for mild type', () => {
      render(<DisclaimerBanner type="mild" />);
      
      const banner = screen.getByRole('alert');
      expect(banner).toHaveAttribute('aria-live', 'polite');
    });

    it('renders info icon for mild type', () => {
      const { container } = render(<DisclaimerBanner type="mild" />);
      
      // Check for SVG with info icon
      const svg = container.querySelector('svg');
      expect(svg).toBeInTheDocument();
      expect(svg).toHaveClass('text-yellow-600');
    });
  });

  describe('Accessibility', () => {
    it('has role="alert" for all types', () => {
      const { rerender } = render(<DisclaimerBanner type="general" />);
      expect(screen.getByRole('alert')).toBeInTheDocument();

      rerender(<DisclaimerBanner type="critical" />);
      expect(screen.getByRole('alert')).toBeInTheDocument();

      rerender(<DisclaimerBanner type="mild" />);
      expect(screen.getByRole('alert')).toBeInTheDocument();
    });

    it('has aria-hidden on icons', () => {
      const { container } = render(<DisclaimerBanner type="general" />);
      
      const svg = container.querySelector('svg');
      expect(svg).toHaveAttribute('aria-hidden', 'true');
    });

    it('uses minimum 16px font size for readability', () => {
      render(<DisclaimerBanner type="general" />);
      
      const text = screen.getByText(/This is not medical advice/);
      expect(text).toHaveClass('text-base'); // text-base is 16px in Tailwind
    });
  });

  describe('Visual prominence', () => {
    it('has prominent border styling', () => {
      render(<DisclaimerBanner type="general" />);
      
      const banner = screen.getByRole('alert');
      expect(banner).toHaveClass('border-l-4', 'p-4', 'rounded-md');
    });

    it('has margin for spacing', () => {
      render(<DisclaimerBanner type="general" />);
      
      const banner = screen.getByRole('alert');
      expect(banner).toHaveClass('mb-4');
    });

    it('uses font-medium for emphasis', () => {
      render(<DisclaimerBanner type="general" />);
      
      const text = screen.getByText(/This is not medical advice/);
      expect(text).toHaveClass('font-medium');
    });
  });
});
