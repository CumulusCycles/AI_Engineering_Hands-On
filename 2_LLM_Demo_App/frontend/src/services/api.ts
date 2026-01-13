/**
 * API service for communicating with the backend.
 */
const API_BASE_URL = 'http://localhost:8000';

// TypeScript interfaces
export interface Product {
  id: string;
  name: string;
  description: string;
  category: string;
  price: number | null;
  features: string[];
  image_path: string;
}

export interface SearchResponse {
  query_caption: string;
  results: (Product & { score?: number })[];
}

export interface StatsResponse {
  total: number;
  by_category: Record<string, number>;
}

export interface TokenizeResponse {
  original_text: string;
  token_count: number;
  token_count_no_special: number;
  word_count: number;
  character_count: number;
  tokens: string[];
  tokens_with_special: string[];
  token_ids: number[];
  token_ids_no_special: number[];
  token_mapping: Array<{
    token: string;
    token_id: number;
    position: number;
  }>;
}

export interface EmbeddingResponse {
  text: string;
  embedding: number[];
  dimension: number;
  first_n_dimensions: number[];
  statistics: {
    min: number;
    max: number;
    mean: number;
    std: number;
  };
}

export interface SimilarityResponse {
  similarity_matrix: number[][];
  texts: string[];
  pairwise_similarities: Array<{
    text1: string;
    text2: string;
    similarity: number;
  }>;
}

// Helper function for handling responses
async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(error.detail || `HTTP error! status: ${response.status}`);
  }
  return response.json();
}

// API functions
export async function searchByText(query: string, topK: number = 5): Promise<SearchResponse> {
  const response = await fetch(`${API_BASE_URL}/search`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ query, top_k: topK }),
  });
  return handleResponse<SearchResponse>(response);
}

export async function searchByImage(file: File, topK: number = 5): Promise<SearchResponse> {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('top_k', topK.toString());

  const response = await fetch(`${API_BASE_URL}/search/image`, {
    method: 'POST',
    body: formData,
  });
  return handleResponse<SearchResponse>(response);
}

export async function getProductStats(): Promise<StatsResponse> {
  const response = await fetch(`${API_BASE_URL}/admin/stats`);
  return handleResponse<StatsResponse>(response);
}

export async function createProduct(product: {
  name: string;
  description: string;
  category: string;
  price?: number;
  features?: string[];
}): Promise<{ success: boolean; product: Product }> {
  const response = await fetch(`${API_BASE_URL}/admin/products`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(product),
  });
  return handleResponse<{ success: boolean; product: Product }>(response);
}

export async function seedDatabase(): Promise<{
  success: boolean;
  message: string;
  created: number;
  errors: number;
}> {
  const response = await fetch(`${API_BASE_URL}/admin/seed`, {
    method: 'POST',
  });
  return handleResponse<{
    success: boolean;
    message: string;
    created: number;
    errors: number;
  }>(response);
}

export async function tokenizeText(text: string): Promise<TokenizeResponse> {
  const response = await fetch(`${API_BASE_URL}/debug/tokenize`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ text }),
  });
  return handleResponse<TokenizeResponse>(response);
}

export async function generateEmbedding(text: string): Promise<EmbeddingResponse> {
  const response = await fetch(`${API_BASE_URL}/debug/embedding`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ text }),
  });
  return handleResponse<EmbeddingResponse>(response);
}

export async function calculateSimilarity(texts: string[]): Promise<SimilarityResponse> {
  const response = await fetch(`${API_BASE_URL}/debug/similarity`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ texts }),
  });
  return handleResponse<SimilarityResponse>(response);
}
