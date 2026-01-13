import React, { useState } from 'react';
import { searchByText, searchByImage, tokenizeText } from '../services/api';
import type { SearchResponse, TokenizeResponse } from '../services/api';
import { TokenizationModal } from './TokenizationModal';

interface SearchFormProps {
  onSearch: (response: SearchResponse) => void;
  searchResponse: SearchResponse | null;
}

export const SearchForm: React.FC<SearchFormProps> = ({ onSearch, searchResponse }) => {
  const [searchType, setSearchType] = useState<'text' | 'image'>('text');
  const [textQuery, setTextQuery] = useState('');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showTokenization, setShowTokenization] = useState(false);
  const [tokenizationData, setTokenizationData] = useState<TokenizeResponse | null>(null);

  const validateFile = (file: File): string | null => {
    // Check file type
    const validTypes = ['image/jpeg', 'image/jpg', 'image/png'];
    if (!validTypes.includes(file.type)) {
      const ext = file.name.split('.').pop()?.toLowerCase();
      if (ext !== 'jpg' && ext !== 'jpeg' && ext !== 'png') {
        return 'File must be JPG or PNG';
      }
    }

    // Check file size (5MB)
    const maxSize = 5 * 1024 * 1024;
    if (file.size > maxSize) {
      return 'File size must be less than 5MB';
    }

    return null;
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      const validationError = validateFile(file);
      if (validationError) {
        setError(validationError);
        setSelectedFile(null);
        return;
      }
      setError(null);
      setSelectedFile(file);
    }
  };

  const handleSearch = async () => {
    setError(null);
    setLoading(true);

    try {
      if (searchType === 'text') {
        if (!textQuery.trim()) {
          setError('Please enter a search query');
          setLoading(false);
          return;
        }
        const response = await searchByText(textQuery);
        onSearch(response);
      } else {
        if (!selectedFile) {
          setError('Please select an image file');
          setLoading(false);
          return;
        }
        const response = await searchByImage(selectedFile);
        onSearch(response);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred during search');
    } finally {
      setLoading(false);
    }
  };

  const handleShowTokenization = async () => {
    if (!textQuery.trim()) {
      setError('Please enter a search query first');
      return;
    }

    try {
      const data = await tokenizeText(textQuery);
      setTokenizationData(data);
      setShowTokenization(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to tokenize text');
    }
  };

  return (
    <div className="search-form-container">
      <div className="search-type-selector">
        <label>
          <input
            type="radio"
            value="text"
            checked={searchType === 'text'}
            onChange={() => setSearchType('text')}
          />
          Text Search
        </label>
        <label>
          <input
            type="radio"
            value="image"
            checked={searchType === 'image'}
            onChange={() => setSearchType('image')}
          />
          Image Search
        </label>
      </div>

      {searchType === 'text' ? (
        <div className="form-group">
          <label htmlFor="text-query">Search Query</label>
          <input
            id="text-query"
            type="text"
            value={textQuery}
            onChange={(e) => setTextQuery(e.target.value)}
            placeholder="e.g., lightweight backpacking tent"
            onKeyPress={(e) => {
              if (e.key === 'Enter' && !loading) {
                handleSearch();
              }
            }}
            disabled={loading}
          />
        </div>
      ) : (
        <div className="form-group">
          <label htmlFor="image-file">Upload Image</label>
          <input
            id="image-file"
            type="file"
            accept="image/jpeg,image/png"
            onChange={handleFileChange}
            disabled={loading}
          />
          {selectedFile && (
            <div className="file-info">
              Selected: {selectedFile.name} ({(selectedFile.size / 1024).toFixed(2)} KB)
            </div>
          )}
        </div>
      )}

      {error && <div className="error-message">{error}</div>}

      <div className="button-container">
        <button
          className="primary-button"
          onClick={handleSearch}
          disabled={loading}
        >
          {loading ? 'Searching...' : 'Search'}
        </button>
        {searchType === 'text' && searchResponse && (
          <button
            className="secondary-button"
            onClick={handleShowTokenization}
            disabled={loading}
          >
            Show Tokenization
          </button>
        )}
      </div>

      <TokenizationModal
        isOpen={showTokenization}
        onClose={() => setShowTokenization(false)}
        data={tokenizationData}
      />
    </div>
  );
};
