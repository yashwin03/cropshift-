/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#f1f8e9',
          100: '#dcedc8',
          200: '#c5e1a5',
          300: '#aed581',
          400: '#9ccc65',
          500: '#8bc34a',
          600: '#7cb342',
          700: '#689f38',
          800: '#558b2f',
          900: '#33691e',
          DEFAULT: '#2e7d32', // Earthy green primary
        },
        success: {
          light: '#e8f5e9',
          DEFAULT: '#2e7d32',
        },
        warning: {
          light: '#fff8e1',
          DEFAULT: '#ffb300', // Amber
        },
        danger: {
          light: '#ffebee',
          DEFAULT: '#c62828', // Red
        }
      },
      fontSize: {
        base: '1rem', // 16px default
      },
    },
  },
  plugins: [],
}
