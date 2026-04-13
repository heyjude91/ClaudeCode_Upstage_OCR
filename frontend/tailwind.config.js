/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        // 카테고리별 차트 컬러 (PRD 7.2)
        category: {
          식료품: '#6366F1',
          외식: '#F97316',
          쇼핑: '#EC4899',
          교통: '#14B8A6',
          의료: '#EF4444',
          문화: '#A855F7',
          기타: '#9CA3AF',
        },
      },
      fontFamily: {
        sans: [
          '-apple-system',
          'BlinkMacSystemFont',
          'Segoe UI',
          'sans-serif',
        ],
      },
    },
  },
  plugins: [],
}
