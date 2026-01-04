/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      fontFamily: {
        // Existing fonts
        'kid': ['"Comic Sans MS"', '"Comic Sans"', 'cursive', 'sans-serif'],
        'heading': ['"Fredoka"', '"Comic Sans MS"', 'cursive', 'sans-serif'],
        'body': ['"Nunito"', '"Comic Sans MS"', 'sans-serif'],
        // Storybook fonts
        'storybook-title': ['"Cinzel Decorative"', 'Georgia', 'serif'],
        'storybook-heading': ['"Cinzel"', 'Georgia', 'serif'],
        'storybook-body': ['"Crimson Text"', 'Georgia', 'serif'],
        'storybook-fancy': ['"EB Garamond"', 'Georgia', 'serif'],
      },
      fontSize: {
        'xs': ['0.75rem', { lineHeight: '1rem' }],
        'sm': ['0.875rem', { lineHeight: '1.25rem' }],
        'base': ['1rem', { lineHeight: '1.5rem' }],
        'lg': ['1.125rem', { lineHeight: '1.75rem' }],
        'xl': ['1.25rem', { lineHeight: '1.75rem' }],
        '2xl': ['1.5rem', { lineHeight: '2rem' }],
        '3xl': ['1.875rem', { lineHeight: '2.25rem' }],
        '4xl': ['2.25rem', { lineHeight: '2.5rem' }],
        '5xl': ['3rem', { lineHeight: '1.2' }],
        '6xl': ['3.75rem', { lineHeight: '1.1' }],
        '7xl': ['4.5rem', { lineHeight: '1.1' }],
      },
      colors: {
        primary: {
          50: '#f0f9ff',
          100: '#e0f2fe',
          200: '#bae6fd',
          300: '#7dd3fc',
          400: '#38bdf8',
          500: '#0ea5e9',
          600: '#0284c7',
          700: '#0369a1',
          800: '#075985',
          900: '#0c4a6e',
          950: '#0a3a56',
        },
        // Storybook color palette
        storybook: {
          // Leather/cover colors
          leather: {
            50: '#fdf6f3',
            100: '#f9e8e1',
            200: '#f2cfc2',
            300: '#e9ad99',
            400: '#dc8269',
            500: '#c75f43',
            600: '#b04735',
            700: '#8f3729',
            800: '#6b1d2b',  // Deep burgundy - main leather
            900: '#5a1a25',
            950: '#320d13',
          },
          // Gold/embossing colors
          gold: {
            50: '#fdfbf3',
            100: '#faf3da',
            200: '#f4e5b4',
            300: '#edd284',
            400: '#e4b94f',
            500: '#c5a572',  // Antique gold - main
            600: '#b08d4a',
            700: '#926d3d',
            800: '#785736',
            900: '#64492f',
            950: '#382618',
          },
          // Parchment/page colors
          parchment: {
            50: '#fefdfb',
            100: '#fcf9f2',
            200: '#f5e6c8',  // Main parchment
            300: '#ecdcb5',
            400: '#e0c89a',
            500: '#d4b37f',
            600: '#c59a5f',
            700: '#a87d47',
            800: '#89653d',
            900: '#715435',
            950: '#3d2b1a',
          },
          // Forest green accents
          forest: {
            50: '#f3faf6',
            100: '#e0f2e8',
            200: '#c3e4d3',
            300: '#97cfb4',
            400: '#65b38f',
            500: '#439672',
            600: '#317859',
            700: '#1d4d3e',  // Deep forest - main
            800: '#234d3e',
            900: '#1f4035',
            950: '#0d251e',
          },
          // Ink/text colors
          ink: {
            50: '#f7f6f5',
            100: '#eceae7',
            200: '#d8d4ce',
            300: '#beb7ad',
            400: '#a29789',
            500: '#8c7e6e',
            600: '#796a5c',
            700: '#63574c',
            800: '#544a42',
            900: '#2c1810',  // Dark brown ink - main
            950: '#1a0f0a',
          },
        },
        dark: {
          bg: {
            primary: '#0f172a',
            secondary: '#1e293b',
            tertiary: '#334155',
          },
          text: {
            primary: '#f1f5f9',
            secondary: '#cbd5e1',
            tertiary: '#94a3b8',
          },
          border: {
            primary: '#475569',
            secondary: '#334155',
          }
        }
      },
      boxShadow: {
        'card': '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
        'card-hover': '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
        'card-dark': '0 4px 6px -1px rgba(0, 0, 0, 0.3), 0 2px 4px -1px rgba(0, 0, 0, 0.2)',
        'card-hover-dark': '0 10px 15px -3px rgba(0, 0, 0, 0.4), 0 4px 6px -2px rgba(0, 0, 0, 0.3)',
        // Storybook shadows
        'book': '0 25px 50px -12px rgba(0, 0, 0, 0.5), 0 0 40px rgba(107, 29, 43, 0.3)',
        'book-hover': '0 35px 60px -15px rgba(0, 0, 0, 0.6), 0 0 50px rgba(197, 165, 114, 0.4)',
        'page': 'inset 0 0 30px rgba(0, 0, 0, 0.1), 0 2px 10px rgba(0, 0, 0, 0.1)',
        'emboss': 'inset 0 2px 4px rgba(0, 0, 0, 0.3), inset 0 -1px 2px rgba(255, 255, 255, 0.1)',
        'gold-glow': '0 0 20px rgba(197, 165, 114, 0.6), 0 0 40px rgba(197, 165, 114, 0.3)',
      },
      transitionDuration: {
        '250': '250ms',
        '350': '350ms',
        '1500': '1500ms',
        '2000': '2000ms',
      },
      animation: {
        'float': 'float 3s ease-in-out infinite',
        'sparkle': 'sparkle 2s ease-in-out infinite',
        'glow': 'glow 2s ease-in-out infinite',
        'page-turn': 'pageTurn 0.8s ease-in-out forwards',
        'book-open': 'bookOpen 1.5s ease-out forwards',
        'fade-in': 'fadeIn 0.5s ease-out forwards',
        'slide-up': 'slideUp 0.5s ease-out forwards',
        'pulse-soft': 'pulseSoft 2s ease-in-out infinite',
      },
      keyframes: {
        float: {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-10px)' },
        },
        sparkle: {
          '0%, 100%': { opacity: '0.3', transform: 'scale(0.8)' },
          '50%': { opacity: '1', transform: 'scale(1.2)' },
        },
        glow: {
          '0%, 100%': { boxShadow: '0 0 20px rgba(197, 165, 114, 0.4)' },
          '50%': { boxShadow: '0 0 40px rgba(197, 165, 114, 0.8)' },
        },
        pageTurn: {
          '0%': { transform: 'rotateY(0deg)' },
          '100%': { transform: 'rotateY(-180deg)' },
        },
        bookOpen: {
          '0%': { transform: 'rotateX(0deg)' },
          '100%': { transform: 'rotateX(-180deg)' },
        },
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { opacity: '0', transform: 'translateY(20px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        pulseSoft: {
          '0%, 100%': { opacity: '0.7' },
          '50%': { opacity: '1' },
        },
      },
      backgroundImage: {
        'parchment-texture': "url(\"data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)' opacity='0.08'/%3E%3C/svg%3E\")",
        'leather-grain': "url(\"data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='grain'%3E%3CfeTurbulence type='turbulence' baseFrequency='0.9' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23grain)' opacity='0.12'/%3E%3C/svg%3E\")",
      },
      perspective: {
        '1000': '1000px',
        '1500': '1500px',
        '2000': '2000px',
      },
    },
  },
  plugins: [],
}
