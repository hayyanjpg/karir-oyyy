/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      fontFamily: {
        sans: [
          'Inter',
          'ui-sans-serif',
          'system-ui',
          '-apple-system',
          'Segoe UI',
          'Roboto',
          'sans-serif',
        ],
      },
      boxShadow: {
        glow: '0 0 0 1px rgba(56, 189, 248, 0.18), 0 20px 45px -25px rgba(56, 189, 248, 0.45)',
      },
    },
  },
  plugins: [],
}
