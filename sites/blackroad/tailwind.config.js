import { defineConfig } from 'tailwindcss';

export default defineConfig({
  content: ['./index.html', './src/**/*.{js,jsx,ts,tsx}'],
  theme: {
    extend: {
      colors: {
        brand: {
          pink: '#FF4FD8',
          blue: '#0096FF',
          gold: '#FDBA2D',
        },
      },
    },
  },
  plugins: [],
}
    extend: {},
  },
  plugins: [],
});
