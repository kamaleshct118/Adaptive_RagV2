# 🏥 Adaptive RAG Client

Modern Next.js frontend for the Adaptive RAG medical guideline assistant.

## 🚀 Quick Start

### 1. Install Dependencies
```bash
cd client
npm install
```

### 2. Start Development Server
```bash
npm run dev
```

### 3. Open in Browser
Navigate to [http://localhost:3000](http://localhost:3000)

> **Note:** Make sure the backend server is running on `http://localhost:8000` before using the frontend.

## 🎨 Features

- **Modern Chat Interface** - Clean, medical-themed design
- **Real-time Responses** - Async API communication with loading states
- **Markdown Rendering** - Rich text display for AI responses
- **Category & Tone Display** - Shows response metadata
- **Fallback Indicators** - Clear notices when KB coverage is limited
- **Responsive Design** - Works on desktop and mobile
- **Dark Mode** - Easy on the eyes

## 📁 Project Structure

```
client/
├── src/
│   └── app/
│       ├── layout.tsx    # Root layout with metadata
│       ├── page.tsx      # Main chat interface
│       └── globals.css   # Design system & styles
├── package.json
├── tsconfig.json
├── next.config.js
└── README.md
```

## 🔧 Configuration

The frontend proxies API requests to the backend. You can configure the backend URL in `.env.local`:

```bash
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
```

The configuration in `next.config.js` automatically loads this environment variable:

```javascript
async rewrites() {
  return [
    {
      source: '/api/:path*',
      destination: `${process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000'}/api/:path*`,
    },
  ];
}
```

To change the backend URL, simply update the `NEXT_PUBLIC_API_URL` variable in `.env.local`.

## 📦 Build for Production

```bash
npm run build
npm start
```
