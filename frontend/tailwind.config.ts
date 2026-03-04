import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          dark: '#09637E',
          DEFAULT: '#088395',
          light: '#7AB2B2',
          lighter: '#EBF4F6',
        },
      },
      fontSize: {
        base: '16px', // Minimum font size for accessibility
      },
      screens: {
        // Mobile-first responsive breakpoints
        // Mobile: < 768px (default)
        // Tablet: >= 768px
        // Desktop: >= 1024px
        'tablet': '768px',
        'desktop': '1024px',
        'wide': '1280px',
      },
    },
  },
  plugins: [],
}

export default config
