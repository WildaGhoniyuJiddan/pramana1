/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{svelte,js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        stone: '#e6e4de',
        paper: '#f2f0ea',
        sand: '#ddd7c8',
        rule: '#c8c4ba',
        cobalt: '#0c249c',
        navy: '#091b75',
        ink: {
          900: '#0a0a0a',
          700: '#333330',
          500: '#5e5d58',
          400: '#8a8880',
        }
      },
      fontFamily: {
        serif: ['"Newsreader"', 'Georgia', 'serif'],
        sans: ['"Plus Jakarta Sans"', '-apple-system', 'BlinkMacSystemFont', 'system-ui', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'monospace'],
      }
    },
  },
  plugins: [],
};
