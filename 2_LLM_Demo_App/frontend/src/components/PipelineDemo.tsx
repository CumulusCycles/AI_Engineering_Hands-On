import React, { useState } from 'react';
import { searchByText, tokenizeText, generateEmbedding } from '../services/api';
import type { TokenizeResponse, EmbeddingResponse, SearchResponse } from '../services/api';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

export const PipelineDemo: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [step, setStep] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [tokenizationResult, setTokenizationResult] = useState<TokenizeResponse | null>(null);
  const [embeddingResult, setEmbeddingResult] = useState<EmbeddingResponse | null>(null);
  const [searchResult, setSearchResult] = useState<SearchResponse | null>(null);

  const loadExampleQuery = () => {
    setSearchQuery('lightweight backpacking tent');
  };

  const processPipeline = async () => {
    if (!searchQuery.trim()) {
      setError('Please enter a search query');
      return;
    }

    setError(null);
    setLoading(true);
    setStep(0);
    setTokenizationResult(null);
    setEmbeddingResult(null);
    setSearchResult(null);

    try {
      // Step 1: Tokenization
      setStep(1);
      const tokenData = await tokenizeText(searchQuery);
      setTokenizationResult(tokenData);

      // Step 2: Embedding Generation
      setStep(2);
      const embeddingData = await generateEmbedding(searchQuery);
      setEmbeddingResult(embeddingData);

      // Step 3: Similarity Search
      setStep(3);
      const searchData = await searchByText(searchQuery, 5);
      setSearchResult(searchData);

      // Step 4: Complete
      setStep(4);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred during processing');
      setLoading(false);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !loading && searchQuery.trim()) {
      processPipeline();
    }
  };

  // Prepare chart data for similarity scores
  const chartData = searchResult?.results.map((product, idx) => ({
    name: product.name.length > 20 ? `${product.name.substring(0, 20)}...` : product.name,
    fullName: product.name,
    score: product.score || 0,
    category: product.category,
  })) || [];

  return (
    <div className="pipeline-demo-container">
      <h1>LLM Pipeline Demo</h1>
      <p className="demo-description">
        This interactive demonstration shows how semantic search works under the hood:
        from text input through tokenization, embedding generation, and similarity search.
      </p>

      {error && <div className="error-message">{error}</div>}

      {/* Step 1: Search Query Input */}
      <div className="pipeline-step">
        <h2>Step 1: Search Query Input</h2>
        <div className="query-input-section">
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="e.g., lightweight backpacking tent"
            disabled={loading}
            className="query-input"
          />
          <div className="button-container">
            <button
              className="secondary-button"
              onClick={loadExampleQuery}
              disabled={loading}
            >
              Load Example Query
            </button>
            <button
              className="primary-button"
              onClick={processPipeline}
              disabled={loading || !searchQuery.trim()}
            >
              {loading ? 'Processing...' : 'Process Pipeline'}
            </button>
          </div>
        </div>
      </div>

      {/* Step 2: Tokenization */}
      {step >= 1 && tokenizationResult && (
        <div className="pipeline-step">
          <h2>Step 2: Tokenization</h2>
          <div className="step-content">
            <p className="step-explanation">
              The search query is broken down into tokens - smaller units that the model can understand.
              Each token is mapped to a numerical ID.
            </p>

            <div className="query-display">
              <strong>Original Query:</strong> {tokenizationResult.original_text}
            </div>

            <div className="tokenization-stats">
              <div className="stat-item">
                <span className="stat-label">Token Count (with special):</span>
                <span className="stat-value">{tokenizationResult.token_count}</span>
              </div>
              <div className="stat-item">
                <span className="stat-label">Token Count (no special):</span>
                <span className="stat-value">{tokenizationResult.token_count_no_special}</span>
              </div>
              <div className="stat-item">
                <span className="stat-label">Word Count:</span>
                <span className="stat-value">{tokenizationResult.word_count}</span>
              </div>
              <div className="stat-item">
                <span className="stat-label">Character Count:</span>
                <span className="stat-value">{tokenizationResult.character_count}</span>
              </div>
            </div>

            <div className="tokens-display-section">
              <h3>Token Breakdown</h3>
              <div className="tokens-display">
                {tokenizationResult.tokens_with_special.map((token, idx) => {
                  const isSpecial = token === '[CLS]' || token === '[SEP]' ||
                                    tokenizationResult.token_ids[idx] === 101 ||
                                    tokenizationResult.token_ids[idx] === 102;
                  return (
                    <span
                      key={idx}
                      className={isSpecial ? 'token-special' : 'token-normal'}
                    >
                      {token}
                    </span>
                  );
                })}
              </div>
            </div>

            <div className="token-mapping-section">
              <h3>Token-to-ID Mapping</h3>
              <table className="token-mapping-table">
                <thead>
                  <tr>
                    <th>Position</th>
                    <th>Token</th>
                    <th>Token ID</th>
                  </tr>
                </thead>
                <tbody>
                  {tokenizationResult.token_mapping.map((item, idx) => (
                    <tr key={idx}>
                      <td>{item.position}</td>
                      <td>{item.token}</td>
                      <td>{item.token_id}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* Step 3: Embedding Generation */}
      {step >= 2 && embeddingResult && (
        <div className="pipeline-step">
          <h2>Step 3: Embedding Generation</h2>
          <div className="step-content">
            <p className="step-explanation">
              The tokenized query is converted into a 384-dimensional vector that captures
              the semantic meaning of the text. This high-dimensional representation allows
              the model to understand relationships between words and concepts.
            </p>

            <div className="embedding-stats">
              <div className="stat-item">
                <span className="stat-label">Dimension:</span>
                <span className="stat-value">{embeddingResult.dimension}</span>
              </div>
              <div className="stat-item">
                <span className="stat-label">Min Value:</span>
                <span className="stat-value">{embeddingResult.statistics.min.toFixed(4)}</span>
              </div>
              <div className="stat-item">
                <span className="stat-label">Max Value:</span>
                <span className="stat-value">{embeddingResult.statistics.max.toFixed(4)}</span>
              </div>
              <div className="stat-item">
                <span className="stat-label">Mean Value:</span>
                <span className="stat-value">{embeddingResult.statistics.mean.toFixed(4)}</span>
              </div>
              <div className="stat-item">
                <span className="stat-label">Std Deviation:</span>
                <span className="stat-value">{embeddingResult.statistics.std.toFixed(4)}</span>
              </div>
            </div>

            <div className="embedding-preview">
              <h3>First 10 Dimensions (Preview)</h3>
              <div className="dimensions-list">
                {embeddingResult.first_n_dimensions.map((value, idx) => (
                  <span key={idx} className="dimension-value">
                    [{idx}]: {value.toFixed(4)}
                  </span>
                ))}
              </div>
              <p className="note">
                <em>Note: The full 384-dimensional vector is used internally for similarity search.</em>
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Step 4: Similarity Search */}
      {step >= 3 && searchResult && (
        <div className="pipeline-step">
          <h2>Step 4: Similarity Search</h2>
          <div className="step-content">
            <p className="step-explanation">
              The query embedding is compared against all product embeddings in the database
              using cosine similarity. Products with higher similarity scores are better matches.
            </p>

            {searchResult.results.length === 0 ? (
              <div className="empty-results">
                <p>No products found matching your search.</p>
              </div>
            ) : (
              <>
                <div className="similarity-chart-section">
                  <h3>Similarity Scores</h3>
                  <ResponsiveContainer width="100%" height={300}>
                    <BarChart data={chartData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="name" angle={-45} textAnchor="end" height={100} />
                      <YAxis domain={[0, 1]} />
                      <Tooltip
                        formatter={(value: number, name: string, props: any) => [
                          `${(value * 100).toFixed(1)}%`,
                          'Similarity',
                        ]}
                        labelFormatter={(label, payload) => {
                          const data = payload?.[0]?.payload;
                          return data?.fullName || label;
                        }}
                        contentStyle={{
                          backgroundColor: '#fff',
                          border: '1px solid #ddd',
                          borderRadius: '4px',
                        }}
                      />
                      <Bar dataKey="score" fill="#4A90E2" />
                    </BarChart>
                  </ResponsiveContainer>
                </div>

                <div className="search-results-section">
                  <h3>Ranked Results</h3>
                  <div className="results-list">
                    {searchResult.results.map((product) => (
                      <div key={product.id} className="result-card">
                        <div className="result-header">
                          <h4>{product.name}</h4>
                          <span className={`category-badge category-${product.category.toLowerCase().replace(' ', '-')}`}>
                            {product.category}
                          </span>
                        </div>
                        <div className="similarity-score-box">
                          <strong>Similarity:</strong> {(product.score || 0).toFixed(2)}
                          <span className="score-explanation">
                            {' '}(scores closer to 1.0 = better matches)
                          </span>
                        </div>
                        <p className="result-description">{product.description}</p>
                        {product.price !== null && (
                          <div className="result-price">Price: ${product.price.toFixed(2)}</div>
                        )}
                        {product.features && product.features.length > 0 && (
                          <div className="result-features">
                            <strong>Features:</strong> {product.features.join(', ')}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              </>
            )}
          </div>
        </div>
      )}

      {/* Completion Message */}
      {step >= 4 && !loading && (
        <div className="completion-message">
          <h2>✓ Pipeline Complete!</h2>
          <p>
            The complete pipeline flow: <strong>Text → Tokens → Embeddings → Similarity Search → Ranked Results</strong>
          </p>
          <p>
            This demonstrates how semantic search works by converting text into numerical
            representations (embeddings) and finding similar products through vector similarity.
          </p>
        </div>
      )}
    </div>
  );
};
