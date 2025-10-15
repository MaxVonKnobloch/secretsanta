import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './index.css';
import { fetchJsonSafe } from '../fetchUtils';

const IndexPage = () => {
  const [cardSlogan, setCardSlogan] = useState('');
  const [giftReceiverName, setGiftReceiverName] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    // send short request to /api/auth with url parm token as url parameter not in body
    const urlParams = new URLSearchParams(window.location.search);
    const token = urlParams.get('token');
    if (token) {
      fetchJsonSafe(`/api/auth?token=${encodeURIComponent(token)}`)
        .then(data => {
          if (!data.success) {
            console.error('Auth failed:', data.message);
          }
        })
        .catch(err => {
          console.error('Auth request error:', err);
        });
    } else {
      console.warn('No token found in URL parameters.');
    }
    // --- END AUTH REQUEST ---
    fetchJsonSafe('/api/slogan')
      .then(data => setCardSlogan(data.slogan || ''))
      .catch(() => setCardSlogan('Error fetching slogan'));
    fetchJsonSafe('/api/receiver')
      .then(data => setGiftReceiverName(data.gift_receiver_name || '?'))
      .catch(() => setGiftReceiverName('Error fetching receiver'));
  }, []);

  useEffect(() => {
    const card = document.querySelector('.static-card');
    if (card) {
      card.style.opacity = '0';
      card.style.transform = 'translateY(20px)';
      setTimeout(() => {
        card.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        card.style.opacity = '1';
        card.style.transform = 'translateY(0)';
      }, 100);
    }
  }, [cardSlogan, giftReceiverName]);

  const handleWeiter = () => {
    navigate('/gift-lists');
  };

  return (
    <div className="container">
        <div className="static-card">
          <div className="card-slogan">
            <p className="card-text">{cardSlogan}</p>
          </div>
          <div className="card-receiver">
            <p className="receiver-name">{giftReceiverName}</p>
          </div>
          <div className="card-button-container">
            <button className="weiter-button" onClick={handleWeiter} tabIndex={0}>
              weiter
            </button>
          </div>
        </div>
    </div>
  );
};

export default IndexPage;
