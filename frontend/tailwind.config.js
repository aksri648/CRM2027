/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class',
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Primary accent - teal
        accent: {
          DEFAULT: '#0fd4b4',
          hover: '#0bbfa1',
          foreground: '#ffffff',
        },
        // Sidebar colors
        sidebar: {
          bg: '#0f1923',
          active: '#1a2d3d',
          text: '#cbd5e1',
          'text-active': '#ffffff',
        },
        // Main background
        'main-bg': '#f9fafb',
        // Card
        card: {
          DEFAULT: '#ffffff',
          foreground: '#111827',
        },
        // Text colors
        foreground: {
          DEFAULT: '#111827',
          secondary: '#6b7280',
        },
        // Border
        border: {
          DEFAULT: '#e5e7eb',
        },
        // Status colors
        success: '#10b981',
        warning: '#f59e0b',
        danger: '#ef4444',
        info: '#3b82f6',
        // Channel colors
        whatsapp: '#10b981',
        sms: '#f59e0b',
        email: '#3b82f6',
        rcs: '#8b5cf6',
        // Primary (teal for buttons, badges, highlights)
        primary: {
          DEFAULT: '#0fd4b4',
          hover: '#0bbfa1',
          foreground: '#ffffff',
        },
        // Muted/secondary
        muted: {
          DEFAULT: '#f3f4f6',
          foreground: '#6b7280',
        },
        // Destructive
        destructive: {
          DEFAULT: '#ef4444',
          foreground: '#ffffff',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'Avenir', 'Helvetica', 'Arial', 'sans-serif'],
      },
      spacing: {
        'sidebar': '260px',
      },
      borderRadius: {
        'xl': '0.75rem',
        '2xl': '1rem',
      },
    },
  },
  plugins: [],
}