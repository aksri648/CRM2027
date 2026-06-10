/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        accent: {
          DEFAULT: '#0fd4b4',
          hover: '#0eb9a3',
          muted: 'rgba(15, 212, 180, 0.1)'
        },
        sidebar: '#0f1923',
        card: '#ffffff',
        foreground: '#1a1a2e'
      }
    },
  },
  plugins: [],
}