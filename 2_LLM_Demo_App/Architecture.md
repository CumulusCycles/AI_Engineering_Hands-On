# Technical Architecture

## System Overview

The Outdoor Adventure Gear Catalog Search is a semantic search/retrieval system (NOT RAG) that returns ranked product results based on embedding similarity. The system does not generate text - it only retrieves and ranks existing products.

## Architecture Diagram

```
┌─────────────┐
│   Frontend  │  React + TypeScript (Port 3000)
│  (Vite)     │
└──────┬──────┘
       │ HTTP/REST
       │
┌──────▼──────┐
│   Backend   │  FastAPI (Port 8000)
│   (API)     │
└──────┬──────┘
       │
       ├──► Embeddings Module ──► sentence-transformers/all-MiniLM-L6-v2
       │
       ├──► Captioning Module ──► Salesforce/blip-image-captioning-base
       │
       └──► Search Module ──────► ChromaDB (Vector Database)
```

## Data Flow

### Product Creation Flow

```
Admin Panel
    │
    ├─► Create Product (name, description, category, price, features)
    │
    ├─► Generate Placeholder Image (800x600, category-colored)
    │   └─► Save to backend/static/products/{product_id}.jpg
    │
    ├─► Generate Embedding from Description
    │   └─► all-MiniLM-L6-v2 → 384-dimensional vector
    │
    └─► Store in ChromaDB
        ├─► Embedding vector
        ├─► Metadata (name, description, category, price, features, image_path)
        └─► Product ID
```

### Search Flow (Text)

```
User Query (Text)
    │
    ├─► Generate Embedding
    │   └─► all-MiniLM-L6-v2 → 384-dimensional vector
    │
    ├─► ChromaDB Similarity Search
    │   └─► Cosine similarity (distance → score: 1 - distance)
    │
    └─► Return Top-K Results
        ├─► Product metadata
        ├─► Similarity scores
        └─► Image paths
```

### Search Flow (Image)

```
User Upload (Image)
    │
    ├─► Validate (JPG/PNG, <5MB)
    │
    ├─► Generate Caption (BLIP)
    │   └─► Text description of image
    │
    ├─► Generate Embedding from Caption
    │   └─► all-MiniLM-L6-v2 → 384-dimensional vector
    │
    ├─► ChromaDB Similarity Search
    │   └─► Cosine similarity
    │
    └─► Return Top-K Results
        ├─► Product metadata
        ├─► Similarity scores
        └─► Generated caption
```

## Component Architecture

### Backend Modules

#### `embeddings.py`
- **Purpose**: Text embedding generation
- **Model**: `sentence-transformers/all-MiniLM-L6-v2`
- **Output**: 384-dimensional vectors
- **Functions**:
  - `encode(text: str) -> List[float]`: Generate embedding
  - `tokenize(text: str) -> Dict`: Tokenize text for educational purposes

#### `captioning.py`
- **Purpose**: Image-to-text captioning
- **Model**: `Salesforce/blip-image-captioning-base` (BLIP)
- **Output**: Text caption (max 50 tokens)
- **Functions**:
  - `generate_caption(image: Image.Image) -> str`: Generate caption from image

#### `search.py`
- **Purpose**: Vector similarity search
- **Database**: ChromaDB (PersistentClient)
- **Collection**: "products"
- **Storage**: `backend/.chroma/`
- **Functions**:
  - `add_product()`: Add product to database
  - `search_products()`: Search with cosine similarity
  - `get_product_count()`: Get total count
  - `get_product_count_by_category()`: Get counts by category

#### `admin.py`
- **Purpose**: Product creation and management
- **Functions**:
  - `create_product()`: Create product with image generation and embedding

#### `api.py`
- **Purpose**: FastAPI REST API
- **Endpoints**: See API Specification in Agents.md
- **Features**:
  - CORS middleware
  - Static file serving
  - Request/response validation (Pydantic v1)

### Frontend Components

#### `App.tsx`
- **Purpose**: Main application with routing
- **Routes**:
  - `/` - Search page
  - `/admin` - Admin panel
  - `/demo` - Pipeline demo

#### `SearchForm.tsx`
- **Purpose**: Search input (text or image)
- **Features**:
  - Text/image mode switching
  - File validation
  - Tokenization visualization

#### `Results.tsx`
- **Purpose**: Display search results
- **Features**:
  - Product cards with images
  - Similarity scores
  - Category badges

#### `AdminPanel.tsx`
- **Purpose**: Product management
- **Features**:
  - Statistics dashboard
  - Product creation form
  - Category breakdown

#### `PipelineDemo.tsx`
- **Purpose**: Educational pipeline demonstration
- **Steps**:
  1. Query input
  2. Tokenization visualization
  3. Embedding generation
  4. Similarity search with chart

#### `TokenizationModal.tsx`
- **Purpose**: Tokenization breakdown display
- **Features**:
  - Token visualization
  - Token-to-ID mapping
  - Statistics

## Data Models

### Product Metadata (ChromaDB Storage)

```python
{
    "name": str,              # Product name
    "description": str,        # Product description (used for embedding)
    "category": str,          # Tent, Backpack, Sleeping Bag, Cooking
    "price": str,             # Stored as string, converted to float in API
    "features": str,          # Comma-separated (no spaces), converted to array in API
    "image_path": str         # Relative path: "static/products/{id}.jpg"
}
```

### API Response Models

#### SearchResponse
```typescript
{
  query_caption: string;
  results: Array<{
    id: string;
    name: string;
    description: string;
    category: string;
    price: number | null;
    features: string[];
    image_path: string;
    score: number;  // Similarity score (0-1)
  }>;
}
```

## Vector Database

### ChromaDB Configuration
- **Type**: PersistentClient
- **Location**: `backend/.chroma/`
- **Collection**: "products"
- **Embedding Dimension**: 384
- **Similarity Metric**: Cosine distance (converted to similarity: 1 - distance)

### Storage Format
- **IDs**: Product UUIDs (strings)
- **Embeddings**: 384-dimensional float vectors
- **Metadata**: Product information (name, description, category, etc.)

## Models & Embeddings

### Text Embedding Model
- **Model**: `sentence-transformers/all-MiniLM-L6-v2`
- **Dimensions**: 384
- **Usage**: Product descriptions and search queries
- **Lazy Loading**: Loaded on first use

### Image Captioning Model
- **Model**: `Salesforce/blip-image-captioning-base` (BLIP)
- **Max Length**: 50 tokens
- **Usage**: Convert uploaded images to text descriptions
- **Pipeline**: Image → BLIP → Text → Embedding → Search

## API Design

### RESTful Endpoints
- **Health**: `GET /health`
- **Stats**: `GET /admin/stats`
- **Search**: `POST /search`, `POST /search/image`
- **Admin**: `POST /admin/products`, `POST /admin/seed`
- **Debug**: `POST /debug/tokenize`, `POST /debug/embedding`, `POST /debug/similarity`

### CORS Configuration
- **Allowed Origins**: `http://localhost:3000`, `http://localhost:5173`
- **Allowed Methods**: GET, POST
- **Allowed Headers**: *

## Static Files

### Product Images
- **Location**: `backend/static/products/`
- **Format**: JPEG
- **Size**: 800x600 pixels
- **Generation**: Automatic placeholder images with category-based colors
- **Serving**: FastAPI StaticFiles at `/static` route

## Performance Considerations

### Model Loading
- **Lazy Loading**: Models load on first use
- **Global Instances**: Models cached in memory after first load
- **CPU Optimization**: BLIP runs with `torch.no_grad()`

### Database
- **Persistent Storage**: ChromaDB persists to disk
- **Query Performance**: Cosine similarity search is optimized by ChromaDB
- **Scalability**: ChromaDB handles large vector collections efficiently

## Security Considerations

### File Upload Validation
- **File Type**: JPG/PNG only
- **File Size**: Max 5MB
- **Validation**: Both content-type and file extension checks

### CORS
- **Restricted Origins**: Only localhost ports allowed
- **Methods**: GET and POST only

## Error Handling

### Backend
- **HTTP Exceptions**: FastAPI HTTPException with appropriate status codes
- **Validation**: Pydantic models for request/response validation
- **Error Messages**: Descriptive error messages returned to client

### Frontend
- **Try/Catch**: All API calls wrapped in try/catch
- **User Feedback**: Error messages displayed in UI
- **Loading States**: Disabled buttons and loading indicators

## Deployment

### Scripts
- **deploy.sh**: Automated setup and service startup
- **destroy.sh**: Graceful teardown and cleanup

### Process Management
- **Background Processes**: Services run in background with nohup
- **PID Files**: Process IDs stored for graceful shutdown
- **Log Files**: Output redirected to log files

## Future Enhancements

Potential improvements:
- User authentication and authorization
- Product image upload (instead of generated placeholders)
- Advanced filtering (price range, category)
- Pagination for large result sets
- Real-time search suggestions
- Product recommendations based on search history
