"use client";

interface ErrorMessageProps {
  message: string;
  onRetry?: () => void;
  type?: 'error' | 'warning';
}

/**
 * ErrorMessage Component
 * Displays user-friendly error messages with optional retry actions
 * Requirements: 17.1-17.7
 */
export default function ErrorMessage({
  message,
  onRetry,
  type = 'error'
}: ErrorMessageProps) {
  // Styling based on type
  const typeStyles = {
    error: {
      container: "bg-red-50 border-red-300",
      icon: "text-red-600",
      text: "text-red-900",
      button: "bg-red-600 hover:bg-red-700 focus:ring-red-500"
    },
    warning: {
      container: "bg-orange-50 border-orange-300",
      icon: "text-orange-600",
      text: "text-orange-900",
      button: "bg-orange-600 hover:bg-orange-700 focus:ring-orange-500"
    }
  };

  const styles = typeStyles[type];

  return (
    <div
      className={`${styles.container} border-l-4 p-4 rounded-md mb-4`}
      role="alert"
      aria-live="assertive"
    >
      <div className="flex items-start">
        <div className="flex-shrink-0">
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
        </div>
        <div className="ml-3 flex-1">
          <p className={`text-base font-medium ${styles.text}`}>
            {message}
          </p>
          {onRetry && (
            <div className="mt-3">
              <button
                onClick={onRetry}
                className={`${styles.button} text-white px-4 py-2 rounded-md text-sm font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2`}
                aria-label="Retry action"
              >
                Try Again
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
