# Batch2MD Frontend

React-based web interface for Batch2MD document to Markdown converter.

## Features

- **File Upload**: Drag and drop or browse to upload documents
- **Path Input**: Specify local directory paths for batch conversion
- **Real-time Progress**: WebSocket-based live progress updates
- **Conversion Options**: Configure recursive processing, backend selection, and more
- **Results Download**: Download converted files as a ZIP archive

## Tech Stack

- **React 18** - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool and dev server
- **Tailwind CSS** - Styling
- **Axios** - HTTP client
- **Lucide React** - Icon library

## Getting Started

### Prerequisites

- Node.js 18+ or Bun
- Backend API running on port 8000

### Installation

```bash
# Install dependencies
npm install
# or
bun install
```

### Development

```bash
# Start dev server (http://localhost:5173)
npm run dev
# or
bun run dev
```

### Build

```bash
# Build for production
npm run build
# or
bun run build

# Preview production build
npm run preview
```

## Project Structure

```
frontend/
├── src/
│   ├── components/       # React components
│   │   ├── FileUpload.tsx
│   │   ├── PathInput.tsx
│   │   ├── ConversionOptions.tsx
│   │   ├── ProgressTracker.tsx
│   │   └── ResultsView.tsx
│   ├── services/         # API services
│   │   └── api.ts
│   ├── types/            # TypeScript types
│   │   └── index.ts
│   ├── App.tsx           # Main app component
│   ├── main.tsx          # Entry point
│   └── index.css         # Global styles
├── index.html
├── package.json
├── vite.config.ts
├── tsconfig.json
└── tailwind.config.js
```

## API Integration

The frontend communicates with the FastAPI backend at `http://localhost:8000`:

- `POST /api/upload` - Upload files
- `POST /api/convert` - Start conversion job
- `GET /api/jobs/{job_id}` - Get job status
- `GET /api/jobs/{job_id}/download` - Download results
- `WebSocket /api/ws/{job_id}` - Real-time progress updates

## Environment Variables

Create a `.env` file for custom configuration:

```env
VITE_API_BASE_URL=http://localhost:8000
```

## Supported Document Formats

- Microsoft Office: DOCX, PPTX, XLSX, DOC, PPT, XLS
- OpenDocument: ODT, ODP, ODS
- Other: PDF, RTF

## Development Notes

- The dev server proxies `/api` requests to the backend
- WebSocket connections are used for real-time progress updates
- Dark mode is supported via Tailwind CSS dark mode classes
