import React from 'react';
import type { SearchResponse } from '../services/api';

interface ResultsProps {
  searchResponse: SearchResponse | null;
}

export const Results: React.FC<ResultsProps> = ({ searchResponse }) => {
  if (!searchResponse) {
    return (
      <div className="results-container">
        <div className="empty-state">
          <p>No search performed yet. Enter a query or upload an image to search.</p>
        </div>
      </div>
    );
  }

  if (searchResponse.results.length === 0) {
    return (
      <div className="results-container">
        <div className="query-caption">
          <strong>Searching for:</strong> {searchResponse.query_caption}
        </div>
        <div className="empty-results">
          <p>No products found matching your search.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="results-container">
      <div className="query-caption">
        <strong>Searching for:</strong> {searchResponse.query_caption}
      </div>
      <div className="results-grid">
        {searchResponse.results.map((product) => (
          <div key={product.id} className="product-card">
            <div className="product-image">
              <img
                src={`http://localhost:8000/${product.image_path}`}
                alt={product.name}
                onError={(e) => {
                  (e.target as HTMLImageElement).src = 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" width="400" height="300"><rect fill="%23ddd" width="400" height="300"/><text x="50%25" y="50%25" text-anchor="middle" dy=".3em" fill="%23999">Image not available</text></svg>';
                }}
              />
            </div>
            <div className="product-info">
              <div className="product-header">
                <h3>{product.name}</h3>
                <span className={`category-badge category-${product.category.toLowerCase().replace(' ', '-')}`}>
                  {product.category}
                </span>
              </div>
              <p className="product-description">
                {product.description.length > 150
                  ? `${product.description.substring(0, 150)}...`
                  : product.description}
              </p>
              {product.price !== null && (
                <div className="product-price">${product.price.toFixed(2)}</div>
              )}
              {product.features && product.features.length > 0 && (
                <div className="product-features">
                  <strong>Features:</strong> {product.features.join(', ')}
                </div>
              )}
              {product.score !== undefined && (
                <div className="product-score">
                  <strong>Similarity Score:</strong> {product.score.toFixed(2)}
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
