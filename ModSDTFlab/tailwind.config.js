/** @type {import('tailwindcss').Config} */
export default {
  content: [
    './index.html',
    './src/**/*.{js,jsx,ts,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        // Design System — "The Observational Engine"
        surface: {
          base:     '#0B1326',
          low:      '#131B2E',
          standard: '#171F33',
          high:     '#222A3D',
          inset:    '#060E20',
          popover:  '#2D3449',
        },
        primary:   '#89CEFF',
        secondary: '#4EDEA3',
        tertiary:  '#FFB95F',
        error:     '#FFB4AB',
        text: {
          primary:   '#DAE2FD',
          secondary: '#BEC8D2',
        },
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
      letterSpacing: {
        tight: '-0.02em',
      },
      backdropBlur: {
        glass: '12px',
      },
      boxShadow: {
        modal: '0 20px 40px rgba(6, 14, 32, 0.5)',
      },
      borderRadius: {
        btn: '4px',
      },
    },
  },
  plugins: [],
}
