import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import { SearchForm } from './components/SearchForm';
import { Results } from './components/Results';
import { AdminPanel } from './components/AdminPanel';
import { PipelineDemo } from './components/PipelineDemo';
import type { SearchResponse } from './services/api';
import './index.css';

const Navigation: React.FC = () => {
  const location = useLocation();
  
  return (
    <nav className="main-nav">
      <div className="nav-container">
        <Link to="/" className={location.pathname === '/' ? 'nav-link active' : 'nav-link'}>
          Search
        </Link>
        <Link to="/admin" className={location.pathname === '/admin' ? 'nav-link active' : 'nav-link'}>
          Admin
        </Link>
        <Link to="/demo" className={location.pathname === '/demo' ? 'nav-link active' : 'nav-link'}>
          Pipeline Demo
        </Link>
      </div>
    </nav>
  );
};

const SearchPage: React.FC = () => {
  const [searchResponse, setSearchResponse] = useState<SearchResponse | null>(null);

  return (
    <div className="page-container">
      <h1>Outdoor Adventure Gear Search</h1>
      <SearchForm onSearch={setSearchResponse} searchResponse={searchResponse} />
      <Results searchResponse={searchResponse} />
    </div>
  );
};

function App() {
  return (
    <Router>
      <div className="app">
        <Navigation />
        <main className="main-content">
          <Routes>
            <Route path="/" element={<SearchPage />} />
            <Route path="/admin" element={<AdminPanel />} />
            <Route path="/demo" element={<PipelineDemo />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
