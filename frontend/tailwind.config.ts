import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './index.html',
    './src/**/*.{ts,tsx}',
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      colors: {
        sidebar: {
          bg: '#0f0f10',
          text: '#8b8b9e',
          active: '#ffffff',
          hover: '#1a1a1f',
          border: '#1f1f26',
        },
        accent: {
          DEFAULT: '#5e6ad2',
          hover: '#6b77db',
          light: '#e8eaf6',
        },
        brand: {
          DEFAULT: '#5e6ad2',
        },
      },
    },
  },
  plugins: [],
}

export default config
