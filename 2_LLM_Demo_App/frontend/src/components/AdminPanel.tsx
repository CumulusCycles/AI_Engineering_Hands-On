import React, { useState, useEffect } from 'react';
import { getProductStats, createProduct, seedDatabase } from '../services/api';
import type { StatsResponse } from '../services/api';

export const AdminPanel: React.FC = () => {
  const [stats, setStats] = useState<StatsResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [seeding, setSeeding] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  // Form state
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    category: 'Tent',
    price: '',
    features: '',
  });

  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
    try {
      const data = await getProductStats();
      setStats(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load statistics');
    }
  };

  const handleSeed = async () => {
    setSeeding(true);
    setError(null);
    setSuccess(null);

    try {
      const result = await seedDatabase();
      setSuccess(`Successfully seeded ${result.created} products`);
      await loadStats();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to seed database');
    } finally {
      setSeeding(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setSuccess(null);

    try {
      const price = formData.price ? parseFloat(formData.price) : undefined;
      const features = formData.features
        ? formData.features.split(',').map((f) => f.trim()).filter((f) => f.length > 0)
        : undefined;

      await createProduct({
        name: formData.name,
        description: formData.description,
        category: formData.category,
        price,
        features,
      });

      setSuccess('Product created successfully!');
      setFormData({
        name: '',
        description: '',
        category: 'Tent',
        price: '',
        features: '',
      });
      await loadStats();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create product');
    } finally {
      setLoading(false);
    }
  };

  const getCategoryColor = (category: string): string => {
    const colors: Record<string, string> = {
      Tent: '#4A90E2',
      Backpack: '#50C878',
      'Sleeping Bag': '#FF6B6B',
      Cooking: '#FFA500',
    };
    return colors[category] || '#808080';
  };

  return (
    <div className="admin-container">
      <h1>Admin Panel</h1>

      <div className="admin-layout">
        <div className="admin-stats">
          <div className="stats-card total-card">
            <h2>Total Products</h2>
            <div className="total-number">{stats?.total || 0}</div>
          </div>

          {stats && stats.total === 0 && (
            <button
              className="seed-button"
              onClick={handleSeed}
              disabled={seeding}
            >
              {seeding ? 'Seeding...' : 'Seed Data'}
            </button>
          )}

          <div className="category-stats">
            <h3>By Category</h3>
            <div className="category-grid">
              {stats &&
                Object.entries(stats.by_category).map(([category, count]) => (
                  <div
                    key={category}
                    className="category-card"
                    style={{ borderLeftColor: getCategoryColor(category) }}
                  >
                    <div className="category-name">{category}</div>
                    <div className="category-count">{count}</div>
                  </div>
                ))}
            </div>
          </div>
        </div>

        <div className="admin-form-container">
          <h2>Create New Product</h2>
          {error && <div className="error-message">{error}</div>}
          {success && <div className="success-message">{success}</div>}

          <form onSubmit={handleSubmit} className="product-form">
            <div className="form-group">
              <label htmlFor="name">Product Name *</label>
              <input
                id="name"
                type="text"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                required
                disabled={loading}
              />
            </div>

            <div className="form-group">
              <label htmlFor="description">Description *</label>
              <textarea
                id="description"
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                required
                rows={4}
                disabled={loading}
              />
            </div>

            <div className="form-row">
              <div className="form-group">
                <label htmlFor="category">Category *</label>
                <select
                  id="category"
                  value={formData.category}
                  onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                  required
                  disabled={loading}
                >
                  <option value="Tent">Tent</option>
                  <option value="Backpack">Backpack</option>
                  <option value="Sleeping Bag">Sleeping Bag</option>
                  <option value="Cooking">Cooking</option>
                </select>
              </div>

              <div className="form-group">
                <label htmlFor="price">Price</label>
                <input
                  id="price"
                  type="number"
                  step="0.01"
                  min="0"
                  value={formData.price}
                  onChange={(e) => setFormData({ ...formData, price: e.target.value })}
                  disabled={loading}
                />
              </div>
            </div>

            <div className="form-group">
              <label htmlFor="features">Features (comma-separated)</label>
              <input
                id="features"
                type="text"
                value={formData.features}
                onChange={(e) => setFormData({ ...formData, features: e.target.value })}
                placeholder="e.g., Ultralight, Waterproof, 2-person capacity"
                disabled={loading}
              />
            </div>

            <button
              type="submit"
              className="primary-button"
              disabled={loading}
            >
              {loading ? 'Creating...' : 'Create Product'}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};
