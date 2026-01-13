# Outdoor Adventure Gear Catalog Search

A semantic search engine for outdoor and adventure gear products that allows users to search by text queries or uploaded images, returning ranked product results with relevance scores.

## Features

- **Text Search**: Search products using natural language queries
- **Image Search**: Upload images to find similar products using AI-powered image captioning
- **Admin Panel**: Create and manage products with automatic image generation
- **Pipeline Demo**: Interactive demonstration of the LLM pipeline (tokenization, embeddings, similarity search)
- **Semantic Search**: Uses vector embeddings to find products based on meaning, not just keywords

## Prerequisites

- **Python 3.12** (required, no fallback)
- **uv** (Python package installer) or standard `venv` module
- **Node.js 18+** and npm
- **Internet connection** for initial model downloads (~3-4GB)

## Quick Start

1. **Deploy the application:**
   ```bash
   ./deploy.sh
   ```

2. **Seed the database** (in a new terminal):
   ```bash
   python -m backend.seed
   ```

3. **Access the application:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Health Check: http://localhost:8000/health

4. **Stop and clean up:**
   ```bash
   ./destroy.sh
   ```

## Project Structure

```
[Project Root]/
  ├── backend/                 # Python FastAPI backend
  │   ├── api.py              # FastAPI endpoints
  │   ├── embeddings.py       # Text embedding generation
  │   ├── captioning.py       # Image captioning (BLIP)
  │   ├── search.py           # ChromaDB similarity search
  │   ├── admin.py            # Product creation
  │   ├── seed.py             # Database seeding script
  │   ├── data/               # Seed data
  │   └── static/products/    # Product images
  ├── frontend/               # React + TypeScript frontend
  │   ├── src/
  │   │   ├── components/     # React components
  │   │   └── services/       # API service layer
  │   └── package.json
  ├── deploy.sh               # Deployment script
  ├── destroy.sh              # Teardown script
  └── README.md               # This file
```

## Usage

### Search Products

1. Navigate to the **Search** page (default route)
2. Choose **Text Search** or **Image Search**
3. Enter a query or upload an image
4. View ranked results with similarity scores

### Admin Panel

1. Navigate to **Admin** page
2. View product statistics
3. Create new products with:
   - Name and description
   - Category (Tent, Backpack, Sleeping Bag, Cooking)
   - Optional price and features
4. Products are automatically assigned generated images and embeddings

### Pipeline Demo

1. Navigate to **Pipeline Demo** page
2. Enter a search query or load the example
3. Click "Process Pipeline" to see:
   - Tokenization breakdown
   - Embedding generation
   - Similarity search results
   - Visual similarity score chart

## API Endpoints

### Health & Stats
- `GET /health` - Health check with product count
- `GET /admin/stats` - Product statistics by category

### Search
- `POST /search` - Text-based search
- `POST /search/image` - Image-based search

### Admin
- `POST /admin/products` - Create a new product
- `POST /admin/seed` - Seed database with sample products

### Debug (Educational)
- `POST /debug/tokenize` - Tokenize text
- `POST /debug/embedding` - Generate embedding
- `POST /debug/similarity` - Calculate similarity matrix

## Technology Stack

### Backend
- **FastAPI** - Web framework
- **ChromaDB** - Vector database for similarity search
- **sentence-transformers** - Text embeddings (all-MiniLM-L6-v2)
- **transformers** - Image captioning (BLIP)
- **PyTorch** - Deep learning framework

### Frontend
- **React 18** - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool
- **React Router** - Routing
- **Recharts** - Data visualization

## Models

- **Text Embeddings**: `sentence-transformers/all-MiniLM-L6-v2` (384 dimensions)
- **Image Captioning**: `Salesforce/blip-image-captioning-base` (BLIP)

## Development

### Backend Development

```bash
cd backend
source venv/bin/activate
python -m uvicorn backend.api:app --host 0.0.0.0 --port 8000 --reload
```

### Frontend Development

```bash
cd frontend
npm run dev
```

## Troubleshooting

### Port Already in Use
The deploy script will automatically stop processes on ports 8000 and 3000. If issues persist:
```bash
lsof -ti:8000 | xargs kill -9
lsof -ti:3000 | xargs kill -9
```

### Model Download Issues
Models are downloaded automatically on first use. Ensure you have:
- Internet connection
- ~3-4GB disk space
- Sufficient memory for model loading

### Database Issues
If the database becomes corrupted:
```bash
./destroy.sh
./deploy.sh
python -m backend.seed
```

## License

This project is for educational purposes.
