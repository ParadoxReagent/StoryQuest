# StoryQuest Frontend

Interactive web UI for the StoryQuest kids' text adventure game.

## Tech Stack

- **React 18** - UI library
- **TypeScript** - Type safety
- **Vite** - Build tool and dev server
- **Tailwind CSS** - Styling
- **Axios** - HTTP client

## Features

- 🎨 Beautiful storybook-themed interface with fantasy aesthetics
- 🎚️ Age slider (5-18) with four reading levels
- 🎮 Dynamically generated adventure themes
- ⌨️ Support for both suggested choices and custom input
- 🔊 Text-to-speech narration (Kokoro/Chatterbox TTS)
- 📖 Collapsible story history
- 🔄 Loading states and error handling
- ♿ Accessibility features (ARIA labels, keyboard navigation)
- 📱 Responsive design (mobile-friendly)
- ⚡ Performance optimized (streaming throttling, CSS animations)

## Getting Started

> **💡 Recommended**: Use Docker for the easiest setup. See the main [README.md](../README.md) and [DOCKER.md](../DOCKER.md) for Docker instructions.

### 🐳 With Docker (Recommended)

**Run the entire application (frontend + backend):**
```bash
# From project root
docker-compose up -d
```

**Access the frontend:**
- Frontend: http://localhost:3000
- The backend API is automatically available to the frontend

**View frontend logs:**
```bash
docker-compose logs -f frontend
```

**Rebuild after code changes:**
```bash
docker-compose build frontend
docker-compose up -d frontend
```

**Production build:**

The Docker setup automatically builds the frontend for production using multi-stage builds with Nginx.

---

### 📦 Manual Installation (Advanced)

> **⚠️ Note**: Manual installation is only recommended for frontend development. For production, use Docker.

<details>
<summary>Click to expand manual installation instructions</summary>

**Prerequisites:**
- Node.js 18+ and npm
- StoryQuest backend running on `http://localhost:8000`

**Installation:**

1. Install dependencies:
```bash
npm install
```

2. Create environment file (optional):
```bash
cp .env.example .env
```

3. Edit `.env` if your backend is running on a different URL:
```
VITE_API_URL=http://localhost:8000
```

**Development:**

Start the development server:
```bash
npm run dev
```

The app will be available at `http://localhost:3000`

**Building for Production:**

Build the app:
```bash
npm run build
```

Preview the production build:
```bash
npm run preview
```

</details>

## Project Structure

```
frontend/
├── src/
│   ├── components/         # React components
│   │   ├── ThemeSelection.tsx  # Start screen with theme picker
│   │   ├── StoryView.tsx       # Main story display
│   │   ├── ChoiceButton.tsx    # Individual choice button
│   │   ├── CustomInput.tsx     # Free-form input component
│   │   └── StoryHistory.tsx    # Collapsible history viewer
│   ├── services/          # API integration
│   │   └── api.ts         # Backend API client
│   ├── types/             # TypeScript definitions
│   │   └── api.ts         # API type definitions
│   ├── App.tsx            # Main application component
│   ├── main.tsx           # Application entry point
│   └── index.css          # Global styles (Tailwind)
├── index.html             # HTML template
├── vite.config.ts         # Vite configuration
├── tailwind.config.js     # Tailwind CSS configuration
├── tsconfig.json          # TypeScript configuration
└── package.json           # Dependencies and scripts
```

## Available Scripts

### With Docker

- `docker-compose logs -f frontend` - View frontend logs
- `docker-compose build frontend` - Rebuild frontend image
- `docker-compose exec frontend /bin/sh` - Access frontend container shell

### Manual Development

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

## Usage

1. **Start a New Story:**
   - Enter your name
   - Use the age slider (5-18) to set your reading level:
     - **5-7**: Early Reader (Wonder & Friendship)
     - **8-10**: Middle Reader (Action & Bravery)
     - **11-13**: Tween (Moral Dilemmas)
     - **14-18**: Young Adult (Complex Themes)
   - Choose from the generated adventure themes
   - Click "Begin Your Quest!"

2. **Play the Story:**
   - Read the scene text (or click the speaker button for narration)
   - Either:
     - Click one of the suggested choices, or
     - Type your own creative idea (max 200 characters)
   - The story continues based on your choice!

3. **View History:**
   - Click the "Story So Far" button to see all previous turns
   - Review what you've chosen and where the story has gone

4. **Start Over:**
   - Click the "New Story" button to begin a fresh adventure

## Accessibility

The app includes several accessibility features:

- Semantic HTML elements
- ARIA labels for screen readers
- Keyboard navigation support
- High contrast text and backgrounds
- Large, readable fonts (Comic Sans MS for kid-friendliness)
- Clear focus indicators

## Browser Support

- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)

## Development Notes

### With Docker

- Frontend runs on Nginx in production mode
- Backend API is accessed at `http://backend:8000` from within the Docker network
- Frontend is served at `http://localhost:3000` on the host
- CORS is configured on the backend to allow frontend requests
- Multi-stage build optimizes the production image size
- Static assets are cached with appropriate headers

### Manual Development

- The app uses Vite's proxy feature to avoid CORS issues during development
- All API calls go through `/api` which is proxied to the backend
- Error handling includes user-friendly messages and retry options
- Loading states prevent duplicate requests

## License

TBD
