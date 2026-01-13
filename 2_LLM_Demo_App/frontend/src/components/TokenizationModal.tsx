import React from 'react';
import type { TokenizeResponse } from '../services/api';

interface TokenizationModalProps {
  isOpen: boolean;
  onClose: () => void;
  data: TokenizeResponse | null;
}

export const TokenizationModal: React.FC<TokenizationModalProps> = ({ isOpen, onClose, data }) => {
  if (!isOpen || !data) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>Tokenization Breakdown</h2>
          <button className="close-button" onClick={onClose}>×</button>
        </div>
        <div className="modal-body">
          <div className="tokenization-section">
            <h3>Original Text</h3>
            <div className="original-text">{data.original_text}</div>
          </div>

          <div className="tokenization-section">
            <h3>Statistics</h3>
            <div className="stats-grid">
              <div className="stat-item">
                <span className="stat-label">Token Count (with special):</span>
                <span className="stat-value">{data.token_count}</span>
              </div>
              <div className="stat-item">
                <span className="stat-label">Token Count (no special):</span>
                <span className="stat-value">{data.token_count_no_special}</span>
              </div>
              <div className="stat-item">
                <span className="stat-label">Word Count:</span>
                <span className="stat-value">{data.word_count}</span>
              </div>
              <div className="stat-item">
                <span className="stat-label">Character Count:</span>
                <span className="stat-value">{data.character_count}</span>
              </div>
            </div>
          </div>

          <div className="tokenization-section">
            <h3>Tokens (with special tokens)</h3>
            <div className="tokens-display">
              {data.tokens_with_special.map((token, idx) => {
                const isSpecial = token === '[CLS]' || token === '[SEP]' || 
                                  data.token_ids[idx] === 101 || data.token_ids[idx] === 102;
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

          <div className="tokenization-section">
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
                {data.token_mapping.map((item, idx) => (
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
    </div>
  );
};
