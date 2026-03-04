import { render, screen } from '@testing-library/react';
import ParameterCard from '@/components/ParameterCard';

describe('ParameterCard', () => {
  const mockNormalParameter = {
    name: 'Hemoglobin',
    value: 14.5,
    unit: 'g/dL',
    normalRange: { min: 13.5, max: 17.5 },
    riskLevel: 'Normal' as const,
    explanation: 'Your hemoglobin level is within the normal range. This indicates healthy red blood cell count.'
  };

  const mockMildParameter = {
    name: 'Cholesterol',
    value: 220,
    unit: 'mg/dL',
    normalRange: { min: 125, max: 200 },
    riskLevel: 'Mild Abnormal' as const,
    explanation: 'Your cholesterol is slightly elevated. Consider dietary changes and discuss with your doctor.'
  };

  const mockCriticalParameter = {
    name: 'Blood Glucose',
    value: 250,
    unit: 'mg/dL',
    normalRange: { min: 70, max: 100 },
    riskLevel: 'Critical' as const,
    explanation: 'Your blood glucose is significantly elevated. Consult your doctor immediately for proper evaluation.'
  };

  describe('Normal risk level', () => {
    it('renders parameter name, value, and unit', () => {
      render(<ParameterCard {...mockNormalParameter} />);
      
      expect(screen.getByText('Hemoglobin')).toBeInTheDocument();
      expect(screen.getByText('14.5')).toBeInTheDocument();
      expect(screen.getByText('g/dL')).toBeInTheDocument();
    });

    it('displays normal range', () => {
      render(<ParameterCard {...mockNormalParameter} />);
      
      expect(screen.getByText(/Normal Range:/)).toBeInTheDocument();
      expect(screen.getByText(/13.5 - 17.5 g\/dL/)).toBeInTheDocument();
    });

    it('displays risk level badge', () => {
      render(<ParameterCard {...mockNormalParameter} />);
      
      const badge = screen.getByText('Normal');
      expect(badge).toBeInTheDocument();
      expect(badge).toHaveAttribute('aria-label', 'Risk level: Normal');
    });

    it('displays explanation text', () => {
      render(<ParameterCard {...mockNormalParameter} />);
      
      expect(screen.getByText(/Your hemoglobin level is within the normal range/)).toBeInTheDocument();
    });

    it('applies green color styling for Normal risk level', () => {
      const { container } = render(<ParameterCard {...mockNormalParameter} />);
      
      const card = container.firstChild as HTMLElement;
      expect(card).toHaveClass('border-green-200', 'bg-green-50');
      
      const badge = screen.getByText('Normal');
      expect(badge).toHaveClass('bg-green-100', 'text-green-800');
    });

    it('renders checkmark icon for Normal risk level', () => {
      const { container } = render(<ParameterCard {...mockNormalParameter} />);
      
      const svg = container.querySelector('svg');
      expect(svg).toBeInTheDocument();
      expect(svg).toHaveClass('text-green-600');
    });
  });

  describe('Mild Abnormal risk level', () => {
    it('renders parameter name, value, and unit', () => {
      render(<ParameterCard {...mockMildParameter} />);
      
      expect(screen.getByText('Cholesterol')).toBeInTheDocument();
      expect(screen.getByText('220')).toBeInTheDocument();
      expect(screen.getByText('mg/dL')).toBeInTheDocument();
    });

    it('displays normal range', () => {
      render(<ParameterCard {...mockMildParameter} />);
      
      expect(screen.getByText(/Normal Range:/)).toBeInTheDocument();
      expect(screen.getByText(/125 - 200 mg\/dL/)).toBeInTheDocument();
    });

    it('displays risk level badge', () => {
      render(<ParameterCard {...mockMildParameter} />);
      
      const badge = screen.getByText('Mild Abnormal');
      expect(badge).toBeInTheDocument();
      expect(badge).toHaveAttribute('aria-label', 'Risk level: Mild Abnormal');
    });

    it('displays explanation text', () => {
      render(<ParameterCard {...mockMildParameter} />);
      
      expect(screen.getByText(/Your cholesterol is slightly elevated/)).toBeInTheDocument();
    });

    it('applies yellow color styling for Mild Abnormal risk level', () => {
      const { container } = render(<ParameterCard {...mockMildParameter} />);
      
      const card = container.firstChild as HTMLElement;
      expect(card).toHaveClass('border-yellow-200', 'bg-yellow-50');
      
      const badge = screen.getByText('Mild Abnormal');
      expect(badge).toHaveClass('bg-yellow-100', 'text-yellow-800');
    });

    it('renders warning icon for Mild Abnormal risk level', () => {
      const { container } = render(<ParameterCard {...mockMildParameter} />);
      
      const svg = container.querySelector('svg');
      expect(svg).toBeInTheDocument();
      expect(svg).toHaveClass('text-yellow-600');
    });
  });

  describe('Critical risk level', () => {
    it('renders parameter name, value, and unit', () => {
      render(<ParameterCard {...mockCriticalParameter} />);
      
      expect(screen.getByText('Blood Glucose')).toBeInTheDocument();
      expect(screen.getByText('250')).toBeInTheDocument();
      expect(screen.getByText('mg/dL')).toBeInTheDocument();
    });

    it('displays normal range', () => {
      render(<ParameterCard {...mockCriticalParameter} />);
      
      expect(screen.getByText(/Normal Range:/)).toBeInTheDocument();
      expect(screen.getByText(/70 - 100 mg\/dL/)).toBeInTheDocument();
    });

    it('displays risk level badge', () => {
      render(<ParameterCard {...mockCriticalParameter} />);
      
      const badge = screen.getByText('Critical');
      expect(badge).toBeInTheDocument();
      expect(badge).toHaveAttribute('aria-label', 'Risk level: Critical');
    });

    it('displays explanation text', () => {
      render(<ParameterCard {...mockCriticalParameter} />);
      
      expect(screen.getByText(/Your blood glucose is significantly elevated/)).toBeInTheDocument();
    });

    it('applies red color styling for Critical risk level', () => {
      const { container } = render(<ParameterCard {...mockCriticalParameter} />);
      
      const card = container.firstChild as HTMLElement;
      expect(card).toHaveClass('border-red-200', 'bg-red-50');
      
      const badge = screen.getByText('Critical');
      expect(badge).toHaveClass('bg-red-100', 'text-red-800');
    });

    it('renders alert icon for Critical risk level', () => {
      const { container } = render(<ParameterCard {...mockCriticalParameter} />);
      
      const svg = container.querySelector('svg');
      expect(svg).toBeInTheDocument();
      expect(svg).toHaveClass('text-red-600');
    });
  });

  describe('Accessibility', () => {
    it('has role="article" for semantic structure', () => {
      render(<ParameterCard {...mockNormalParameter} />);
      
      const card = screen.getByRole('article');
      expect(card).toBeInTheDocument();
    });

    it('has descriptive aria-label', () => {
      render(<ParameterCard {...mockNormalParameter} />);
      
      const card = screen.getByRole('article');
      expect(card).toHaveAttribute('aria-label', 'Hemoglobin parameter card');
    });

    it('has aria-hidden on icons', () => {
      const { container } = render(<ParameterCard {...mockNormalParameter} />);
      
      const svg = container.querySelector('svg');
      expect(svg).toHaveAttribute('aria-hidden', 'true');
    });

    it('uses minimum 16px font size for explanation text', () => {
      render(<ParameterCard {...mockNormalParameter} />);
      
      const explanation = screen.getByText(/Your hemoglobin level is within the normal range/);
      expect(explanation).toHaveClass('text-base'); // text-base is 16px in Tailwind
    });

    it('has proper heading hierarchy', () => {
      render(<ParameterCard {...mockNormalParameter} />);
      
      const heading = screen.getByRole('heading', { level: 3 });
      expect(heading).toHaveTextContent('Hemoglobin');
    });
  });

  describe('Visual styling', () => {
    it('has prominent border and rounded corners', () => {
      const { container } = render(<ParameterCard {...mockNormalParameter} />);
      
      const card = container.firstChild as HTMLElement;
      expect(card).toHaveClass('border-l-4', 'rounded-lg', 'shadow-sm');
    });

    it('has proper spacing and padding', () => {
      const { container } = render(<ParameterCard {...mockNormalParameter} />);
      
      const card = container.firstChild as HTMLElement;
      expect(card).toHaveClass('p-4', 'mb-4');
    });

    it('displays value in large bold font', () => {
      render(<ParameterCard {...mockNormalParameter} />);
      
      const value = screen.getByText('14.5');
      expect(value).toHaveClass('text-3xl', 'font-bold');
    });

    it('displays parameter name in semibold font', () => {
      render(<ParameterCard {...mockNormalParameter} />);
      
      const name = screen.getByText('Hemoglobin');
      expect(name).toHaveClass('font-semibold');
    });

    it('has visual separator between range and explanation', () => {
      const { container } = render(<ParameterCard {...mockNormalParameter} />);
      
      const separator = container.querySelector('.border-b');
      expect(separator).toBeInTheDocument();
      expect(separator).toHaveClass('border-gray-200');
    });
  });

  describe('Color coding verification', () => {
    it('uses distinct colors for each risk level', () => {
      const { container: normalContainer } = render(<ParameterCard {...mockNormalParameter} />);
      const { container: mildContainer } = render(<ParameterCard {...mockMildParameter} />);
      const { container: criticalContainer } = render(<ParameterCard {...mockCriticalParameter} />);
      
      const normalCard = normalContainer.firstChild as HTMLElement;
      const mildCard = mildContainer.firstChild as HTMLElement;
      const criticalCard = criticalContainer.firstChild as HTMLElement;
      
      // Verify each has different color classes
      expect(normalCard.className).toContain('green');
      expect(mildCard.className).toContain('yellow');
      expect(criticalCard.className).toContain('red');
    });

    it('applies consistent color scheme across all elements', () => {
      const { container } = render(<ParameterCard {...mockNormalParameter} />);
      
      const card = container.firstChild as HTMLElement;
      const badge = screen.getByText('Normal');
      const icon = container.querySelector('svg');
      
      // All should use green color scheme
      expect(card.className).toContain('green');
      expect(badge.className).toContain('green');
      expect(icon).toHaveClass('text-green-600');
    });
  });

  describe('Content display', () => {
    it('formats normal range with proper units', () => {
      render(<ParameterCard {...mockNormalParameter} />);
      
      // Should display range with unit
      expect(screen.getByText(/13.5 - 17.5 g\/dL/)).toBeInTheDocument();
    });

    it('displays full explanation text', () => {
      render(<ParameterCard {...mockNormalParameter} />);
      
      const explanation = screen.getByText(mockNormalParameter.explanation);
      expect(explanation).toBeInTheDocument();
      expect(explanation).toHaveClass('leading-relaxed'); // Good readability
    });

    it('handles decimal values correctly', () => {
      render(<ParameterCard {...mockNormalParameter} />);
      
      expect(screen.getByText('14.5')).toBeInTheDocument();
    });

    it('handles integer values correctly', () => {
      render(<ParameterCard {...mockMildParameter} />);
      
      expect(screen.getByText('220')).toBeInTheDocument();
    });
  });
});
