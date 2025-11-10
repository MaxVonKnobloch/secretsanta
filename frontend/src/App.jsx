import React, { useEffect } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import IndexPage from './pages/IndexPage';
import GiftListsPage from './pages/GiftListsPage';

const App = () => {
  useEffect(() => {
    // Token auth: ensure token is in URL for backend middleware
    const urlParams = new URLSearchParams(window.location.search);
    let token = urlParams.get('token');
    if (!token) {
      token = localStorage.getItem('token');
      if (token) {
        window.location.search = `?token=${token}`;
      }
    } else {
      localStorage.setItem('token', token);
    }
  }, []);

  return (
    <BrowserRouter basename="/secretsanta">
      <Routes>
        <Route path="/" element={<IndexPage />} />
        <Route path="/gift-lists" element={<GiftListsPage />} />
        {/* Catch-all fallback */}
        <Route path="*" element={<div>Not Found</div>} />
      </Routes>
    </BrowserRouter>
  );
};

export default App;
