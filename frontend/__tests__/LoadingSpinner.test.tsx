import { render, screen } from '@testing-library/react';
import LoadingSpinner from '@/components/LoadingSpinner';

describe('LoadingSpinner', () => {
  describe('Rendering', () => {
    it('renders with default props', () => {
      render(<LoadingSpinner />);
      
      const status = screen.getByRole('status');
      expect(status).toBeInTheDocument();
    });

    it('renders with default label "Loading..."', () => {
      render(<LoadingSpinner />);
      
      const status = screen.getByRole('status');
      expect(status).toHaveAttribute('aria-label', 'Loading...');
    });

    it('renders with custom label', () => {
      const customLabel = 'Processing your report...';
      render(<LoadingSpinner label={customLabel} />);
      
      const status = screen.getByRole('status');
      expect(status).toHaveAttribute('aria-label', customLabel);
    });

    it('renders screen reader text', () => {
      render(<LoadingSpinner label="Loading data" />);
      
      const srText = screen.getByText('Loading data');
      expect(srText).toHaveClass('sr-only');
    });
  });

  describe('Size variants', () => {
    it('renders small size spinner', () => {
      const { container } = render(<LoadingSpinner size="sm" />);
      
      const spinner = container.querySelector('[aria-hidden="true"]');
      expect(spinner).toHaveClass('h-6', 'w-6', 'border-2');
    });

    it('renders medium size spinner (default)', () => {
      const { container } = render(<LoadingSpinner size="md" />);
      
      const spinner = container.querySelector('[aria-hidden="true"]');
      expect(spinner).toHaveClass('h-10', 'w-10', 'border-3');
    });

    it('renders large size spinner', () => {
      const { container } = render(<LoadingSpinner size="lg" />);
      
      const spinner = container.querySelector('[aria-hidden="true"]');
      expect(spinner).toHaveClass('h-16', 'w-16', 'border-4');
    });

    it('defaults to medium size when size prop is omitted', () => {
      const { container } = render(<LoadingSpinner />);
      
      const spinner = container.querySelector('[aria-hidden="true"]');
      expect(spinner).toHaveClass('h-10', 'w-10', 'border-3');
    });
  });

  describe('Styling', () => {
    it('applies primary color to spinner', () => {
      const { container } = render(<LoadingSpinner />);
      
      const spinner = container.querySelector('[aria-hidden="true"]');
      expect(spinner).toHaveClass('border-primary');
    });

    it('has transparent top border for animation effect', () => {
      const { container } = render(<LoadingSpinner />);
      
      const spinner = container.querySelector('[aria-hidden="true"]');
      expect(spinner).toHaveClass('border-t-transparent');
    });

    it('has rounded-full class for circular shape', () => {
      const { container } = render(<LoadingSpinner />);
      
      const spinner = container.querySelector('[aria-hidden="true"]');
      expect(spinner).toHaveClass('rounded-full');
    });

    it('has animate-spin class for rotation animation', () => {
      const { container } = render(<LoadingSpinner />);
      
      const spinner = container.querySelector('[aria-hidden="true"]');
      expect(spinner).toHaveClass('animate-spin');
    });

    it('centers the spinner with flex layout', () => {
      const { container } = render(<LoadingSpinner />);
      
      const wrapper = container.querySelector('[role="status"]');
      expect(wrapper).toHaveClass('flex', 'items-center', 'justify-center');
    });
  });

  describe('Accessibility', () => {
    it('has role="status" for screen readers', () => {
      render(<LoadingSpinner />);
      
      const status = screen.getByRole('status');
      expect(status).toBeInTheDocument();
    });

    it('has aria-live="polite" for non-intrusive announcements', () => {
      render(<LoadingSpinner />);
      
      const status = screen.getByRole('status');
      expect(status).toHaveAttribute('aria-live', 'polite');
    });

    it('has aria-label describing the loading state', () => {
      render(<LoadingSpinner label="Uploading file" />);
      
      const status = screen.getByRole('status');
      expect(status).toHaveAttribute('aria-label', 'Uploading file');
    });

    it('hides decorative spinner from screen readers', () => {
      const { container } = render(<LoadingSpinner />);
      
      const spinner = container.querySelector('[aria-hidden="true"]');
      expect(spinner).toHaveAttribute('aria-hidden', 'true');
    });

    it('provides screen reader only text', () => {
      render(<LoadingSpinner label="Processing" />);
      
      const srText = screen.getByText('Processing');
      expect(srText).toHaveClass('sr-only');
      expect(srText).toBeInTheDocument();
    });
  });

  describe('Use cases', () => {
    it('can be used for page loading', () => {
      render(<LoadingSpinner size="lg" label="Loading page..." />);
      
      const status = screen.getByRole('status');
      expect(status).toHaveAttribute('aria-label', 'Loading page...');
    });

    it('can be used for button loading state', () => {
      render(<LoadingSpinner size="sm" label="Submitting..." />);
      
      const status = screen.getByRole('status');
      expect(status).toHaveAttribute('aria-label', 'Submitting...');
    });

    it('can be used for data fetching', () => {
      render(<LoadingSpinner label="Fetching reports..." />);
      
      const status = screen.getByRole('status');
      expect(status).toHaveAttribute('aria-label', 'Fetching reports...');
    });
  });
});
