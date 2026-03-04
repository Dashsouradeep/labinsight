"use client";

interface DisclaimerBannerProps {
  type: 'general' | 'critical' | 'mild';
  message?: string;
}

/**
 * DisclaimerBanner Component
 * Displays medical disclaimers with appropriate styling based on severity
 * Requirements: 10.1, 10.2, 10.3
 */
export default function DisclaimerBanner({ type, message }: DisclaimerBannerProps) {
  // Default messages based on type
  const defaultMessages = {
    general: "This is not medical advice. This analysis is for informational purposes only and should not replace professional medical consultation.",
    critical: "Consult your doctor immediately. These results require urgent medical attention.",
    mild: "Discuss with your doctor. These results should be reviewed with a healthcare professional."
  };

  const displayMessage = message || defaultMessages[type];

  // Styling based on type
  const typeStyles = {
    general: {
      container: "bg-blue-50 border-blue-200",
      icon: "text-blue-600",
      text: "text-blue-900"
    },
    critical: {
      container: "bg-red-50 border-red-300",
      icon: "text-red-600",
      text: "text-red-900"
    },
    mild: {
      container: "bg-yellow-50 border-yellow-200",
      icon: "text-yellow-600",
      text: "text-yellow-900"
    }
  };

  const styles = typeStyles[type];

  // Icon based on type
  const renderIcon = () => {
    if (type === 'critical') {
      return (
        <svg
          className={`h-6 w-6 ${styles.icon} flex-shrink-0`}
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
    } else if (type === 'mild') {
      return (
        <svg
          className={`h-6 w-6 ${styles.icon} flex-shrink-0`}
          fill="none"
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth="2"
          viewBox="0 0 24 24"
          stroke="currentColor"
          aria-hidden="true"
        >
          <path d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      );
    } else {
      return (
        <svg
          className={`h-6 w-6 ${styles.icon} flex-shrink-0`}
          fill="none"
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth="2"
          viewBox="0 0 24 24"
          stroke="currentColor"
          aria-hidden="true"
        >
          <path d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      );
    }
  };

  return (
    <div
      className={`${styles.container} border-l-4 p-4 rounded-md mb-4`}
      role="alert"
      aria-live={type === 'critical' ? 'assertive' : 'polite'}
    >
      <div className="flex items-start">
        <div className="flex-shrink-0">
          {renderIcon()}
        </div>
        <div className="ml-3">
          <p className={`text-base font-medium ${styles.text}`}>
            {displayMessage}
          </p>
        </div>
      </div>
    </div>
  );
}
