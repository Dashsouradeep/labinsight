"use client";

interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg';
  label?: string;
}

/**
 * LoadingSpinner Component
 * Animated spinner for loading states
 * Accessible with aria-label
 * Requirements: 11.1
 */
export default function LoadingSpinner({ 
  size = 'md', 
  label = 'Loading...' 
}: LoadingSpinnerProps) {
  // Size configurations
  const sizeStyles = {
    sm: 'h-6 w-6 border-2',
    md: 'h-10 w-10 border-3',
    lg: 'h-16 w-16 border-4'
  };

  const spinnerSize = sizeStyles[size];

  return (
    <div 
      className="flex items-center justify-center"
      role="status"
      aria-live="polite"
      aria-label={label}
    >
      <div
        className={`${spinnerSize} border-primary border-t-transparent rounded-full animate-spin`}
        aria-hidden="true"
      />
      <span className="sr-only">{label}</span>
    </div>
  );
}
