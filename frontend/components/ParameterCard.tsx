"use client";

interface ParameterCardProps {
  name: string;
  value: number;
  unit: string;
  normalRange: { min: number; max: number };
  riskLevel: 'Normal' | 'Mild Abnormal' | 'Critical';
  explanation: string;
}

/**
 * ParameterCard Component
 * Displays a medical parameter with value, normal range, and risk level
 * Color-coded by risk level: green=Normal, yellow=Mild, red=Critical
 * Requirements: 11.6
 */
export default function ParameterCard({
  name,
  value,
  unit,
  normalRange,
  riskLevel,
  explanation
}: ParameterCardProps) {
  // Color coding based on risk level
  const riskStyles = {
    'Normal': {
      border: 'border-green-200',
      bg: 'bg-green-50',
      badge: 'bg-green-100 text-green-800',
      icon: 'text-green-600'
    },
    'Mild Abnormal': {
      border: 'border-yellow-200',
      bg: 'bg-yellow-50',
      badge: 'bg-yellow-100 text-yellow-800',
      icon: 'text-yellow-600'
    },
    'Critical': {
      border: 'border-red-200',
      bg: 'bg-red-50',
      badge: 'bg-red-100 text-red-800',
      icon: 'text-red-600'
    }
  };

  const styles = riskStyles[riskLevel];

  // Icon based on risk level
  const renderIcon = () => {
    if (riskLevel === 'Normal') {
      return (
        <svg
          className={`h-6 w-6 ${styles.icon}`}
          fill="none"
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth="2"
          viewBox="0 0 24 24"
          stroke="currentColor"
          aria-hidden="true"
        >
          <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      );
    } else if (riskLevel === 'Mild Abnormal') {
      return (
        <svg
          className={`h-6 w-6 ${styles.icon}`}
          fill="none"
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth="2"
          viewBox="0 0 24 24"
          stroke="currentColor"
          aria-hidden="true"
        >
          <path d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
        </svg>
      );
    } else {
      return (
        <svg
          className={`h-6 w-6 ${styles.icon}`}
          fill="none"
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth="2"
          viewBox="0 0 24 24"
          stroke="currentColor"
          aria-hidden="true"
        >
          <path d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      );
    }
  };

  return (
    <div
      className={`${styles.border} ${styles.bg} border-l-4 rounded-lg p-4 mb-4 shadow-sm`}
      role="article"
      aria-label={`${name} parameter card`}
    >
      {/* Header with icon and risk badge */}
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center space-x-2">
          {renderIcon()}
          <h3 className="text-lg font-semibold text-gray-900">{name}</h3>
        </div>
        <span
          className={`${styles.badge} px-3 py-1 rounded-full text-sm font-medium`}
          aria-label={`Risk level: ${riskLevel}`}
        >
          {riskLevel}
        </span>
      </div>

      {/* Value and Unit */}
      <div className="mb-3">
        <div className="flex items-baseline space-x-2">
          <span className="text-3xl font-bold text-gray-900">
            {value}
          </span>
          <span className="text-lg text-gray-600">{unit}</span>
        </div>
      </div>

      {/* Normal Range */}
      <div className="mb-3 pb-3 border-b border-gray-200">
        <p className="text-sm text-gray-600">
          <span className="font-medium">Normal Range:</span>{' '}
          {normalRange.min} - {normalRange.max} {unit}
        </p>
      </div>

      {/* Explanation */}
      <div>
        <p className="text-base text-gray-700 leading-relaxed">
          {explanation}
        </p>
      </div>
    </div>
  );
}
