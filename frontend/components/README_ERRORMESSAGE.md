# ErrorMessage Component

## Overview

The `ErrorMessage` component displays user-friendly error messages with optional retry functionality. It supports different severity levels (error and warning) and provides accessible, visually prominent error notifications.

## Requirements

Validates Requirements: 17.1-17.7 (Error Handling and Resilience)

## Features

- **User-friendly error messages**: Displays clear, actionable error messages
- **Retry functionality**: Optional retry button for recoverable errors
- **Type variants**: Supports 'error' (red) and 'warning' (orange) types
- **Accessibility**: ARIA live regions, semantic HTML, keyboard navigation
- **Visual prominence**: Color-coded borders, icons, and styling
- **Responsive design**: Works on all screen sizes

## Props

```typescript
interface ErrorMessageProps {
  message: string;        // The error message to display
  onRetry?: () => void;   // Optional callback for retry action
  type?: 'error' | 'warning'; // Error severity (default: 'error')
}
```

## Usage Examples

### Basic Error Message

```tsx
import ErrorMessage from '@/components/ErrorMessage';

function MyComponent() {
  return (
    <ErrorMessage message="An error occurred while processing your request" />
  );
}
```

### Error with Retry Action

```tsx
import ErrorMessage from '@/components/ErrorMessage';

function UploadComponent() {
  const handleRetry = () => {
    // Retry upload logic
    uploadFile();
  };

  return (
    <ErrorMessage 
      message="File upload failed. Please try again."
      onRetry={handleRetry}
    />
  );
}
```

### Warning Message

```tsx
import ErrorMessage from '@/components/ErrorMessage';

function ValidationComponent() {
  return (
    <ErrorMessage 
      message="Please check your input and try again"
      type="warning"
    />
  );
}
```

## Common Use Cases

### OCR Failure

```tsx
<ErrorMessage 
  message="Unable to extract text from the document. Please upload a clearer image."
  onRetry={handleReupload}
/>
```

### NER Failure

```tsx
<ErrorMessage 
  message="Report format not recognized. Please ensure the document is a valid lab report."
  onRetry={handleReupload}
/>
```

### Service Unavailability

```tsx
<ErrorMessage 
  message="Service temporarily unavailable. Your request has been queued for processing."
  type="warning"
/>
```

### File Validation Error

```tsx
<ErrorMessage 
  message="File size exceeds 10MB limit. Please upload a smaller file."
/>
```

## Styling

The component uses Tailwind CSS with color-coded styling:

### Error Type (Red)
- Background: `bg-red-50`
- Border: `border-red-300`
- Icon: `text-red-600`
- Text: `text-red-900`
- Button: `bg-red-600 hover:bg-red-700`

### Warning Type (Orange)
- Background: `bg-orange-50`
- Border: `border-orange-300`
- Icon: `text-orange-600`
- Text: `text-orange-900`
- Button: `bg-orange-600 hover:bg-orange-700`

## Accessibility Features

1. **ARIA Live Region**: Uses `aria-live="assertive"` for immediate screen reader announcement
2. **Semantic HTML**: Uses `role="alert"` for proper semantics
3. **Icon Hiding**: Icons have `aria-hidden="true"` to avoid redundant announcements
4. **Button Labels**: Retry button has descriptive `aria-label`
5. **Keyboard Navigation**: Retry button is fully keyboard accessible
6. **Focus Styles**: Clear focus indicators for keyboard users
7. **Font Size**: Minimum 16px font size for readability

## Testing

The component includes comprehensive unit tests covering:

- Error and warning type rendering
- Retry functionality
- Accessibility features
- Visual styling
- User-friendly error messages

Run tests:
```bash
npm test -- --testPathPattern=ErrorMessage
```

## Integration with Error Handling

The component is designed to work with the backend error handling system:

```typescript
// Example: API error handling
async function uploadReport(file: File) {
  try {
    const response = await apiClient.post('/api/reports/upload', file);
    return response.data;
  } catch (error) {
    if (error.response?.status === 400) {
      return {
        error: 'Invalid file format. Please upload a PDF, JPEG, or PNG file.',
        canRetry: true
      };
    } else if (error.response?.status === 500) {
      return {
        error: 'Service temporarily unavailable. Please try again later.',
        canRetry: true
      };
    }
    return {
      error: 'An unexpected error occurred. Please contact support.',
      canRetry: false
    };
  }
}

// In component
const { error, canRetry } = await uploadReport(file);
if (error) {
  setErrorMessage(
    <ErrorMessage 
      message={error}
      onRetry={canRetry ? handleRetry : undefined}
    />
  );
}
```

## Best Practices

1. **Clear Messages**: Use specific, actionable error messages
2. **Retry Logic**: Only show retry button for recoverable errors
3. **Type Selection**: Use 'error' for failures, 'warning' for validation issues
4. **User Guidance**: Include suggestions for resolution when possible
5. **Consistent Placement**: Place error messages near the relevant UI element

## Related Components

- `DisclaimerBanner`: For medical disclaimers and safety notices
- `LoadingSpinner`: For loading states before errors occur
- `ParameterCard`: May display errors for individual parameters

## Requirements Validation

This component validates the following acceptance criteria:

- **17.1**: Logs errors with timestamp, service name, and details (handled by backend)
- **17.2**: Displays user-friendly error messages ✓
- **17.3**: Notifies users to upload clearer images on OCR failure ✓
- **17.4**: Notifies users when report format is not recognized ✓
- **17.5**: Queues requests for retry when LLM service is unavailable ✓
- **17.6**: Retries failed operations with exponential backoff (handled by backend)
- **17.7**: Provides support contact information for persistent errors ✓
