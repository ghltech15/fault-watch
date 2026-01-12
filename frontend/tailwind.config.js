/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './app/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        background: '#0d0d0d',
        surface: '#141414',
        border: '#2a2a2a',
        danger: '#e31837',
        warning: '#ffc300',
        success: '#4ade80',
        info: '#0066cc',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'glow': 'glow 2s ease-in-out infinite',
      },
      keyframes: {
        glow: {
          '0%, 100%': { boxShadow: '0 0 20px rgba(227, 24, 55, 0.4)' },
          '50%': { boxShadow: '0 0 40px rgba(227, 24, 55, 0.8)' },
        },
      },
    },
  },
  plugins: [],
}
