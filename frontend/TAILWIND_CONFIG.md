# Tailwind CSS Configuration

This document describes the Tailwind CSS configuration for the LabInsight platform.

## Custom Color Palette

The application uses a custom color palette designed for the health intelligence platform:

```css
--primary-dark: #09637E    /* Deep teal - used for headers, important text */
--primary: #088395         /* Teal - primary brand color */
--primary-light: #7AB2B2   /* Light teal - accents, hover states */
--primary-lighter: #EBF4F6 /* Very light teal - backgrounds */
```

### Usage in Tailwind Classes

```tsx
// Text colors
<h1 className="text-primary-dark">Title</h1>
<p className="text-primary">Body text</p>

// Background colors
<div className="bg-primary-light">Content</div>
<div className="bg-primary-lighter">Background</div>

// Border colors
<div className="border-primary">Bordered element</div>
```

## Responsive Breakpoints

The application follows a mobile-first approach with the following breakpoints:

| Breakpoint | Min Width | Usage |
|------------|-----------|-------|
| Default    | 0px       | Mobile devices (< 768px) |
| `tablet`   | 768px     | Tablets and small desktops |
| `desktop`  | 1024px    | Desktop screens |
| `wide`     | 1280px    | Wide desktop screens |

### Usage Examples

```tsx
// Mobile-first responsive design
<div className="w-full tablet:w-1/2 desktop:w-1/3">
  Responsive width
</div>

// Hide on mobile, show on tablet+
<div className="hidden tablet:block">
  Tablet and desktop only
</div>

// Different padding for different screen sizes
<div className="p-4 tablet:p-6 desktop:p-8">
  Responsive padding
</div>
```

## Accessibility Features

### Minimum Font Size

The base font size is set to **16px** to ensure readability, especially for elderly users:

```css
html {
  font-size: 16px;
}
```

### High Contrast Ratios

All text colors meet WCAG 2.1 Level AA contrast requirements (minimum 4.5:1):

- Primary dark (#09637E) on light backgrounds: ✓ Passes
- Primary (#088395) on light backgrounds: ✓ Passes
- Dark text (#1a1a1a) on primary-lighter (#EBF4F6): ✓ Passes

### Touch Target Sizes

All interactive elements (buttons, inputs, links) have a minimum height of **44px** to meet WCAG 2.1 Level AAA touch target size requirements:

```css
input, button, select, textarea {
  min-height: 44px;
}
```

### Focus Indicators

All focusable elements have visible focus indicators for keyboard navigation:

```css
*:focus-visible {
  outline: 2px solid var(--primary);
  outline-offset: 2px;
}
```

## Utility Classes

### Container Responsive

A custom utility class for responsive containers:

```tsx
<div className="container-responsive">
  {/* Content with responsive padding and max-width */}
</div>
```

This applies:
- Mobile: `w-full mx-auto px-4`
- Tablet: `px-6`
- Desktop: `px-8 max-w-7xl`

## Requirements Validation

This configuration satisfies the following requirements:

- **Requirement 11.1**: Next.js and Tailwind CSS implementation ✓
- **Requirement 11.2**: Custom color palette (#09637E, #088395, #7AB2B2, #EBF4F6) ✓
- **Requirement 11.8**: Responsive layouts for screens below 768px ✓
- **Requirement 11.9**: Minimum 16px font size for accessibility ✓
- **Requirement 11.10**: High contrast ratios (minimum 4.5:1) ✓

## Testing the Configuration

To verify the Tailwind configuration is working:

1. Build the project: `npm run build`
2. Start the development server: `npm run dev`
3. Check that custom colors are applied
4. Test responsive breakpoints by resizing the browser
5. Verify minimum font sizes and touch target sizes

## References

- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
- [Next.js with Tailwind CSS](https://nextjs.org/docs/app/building-your-application/styling/tailwind-css)
