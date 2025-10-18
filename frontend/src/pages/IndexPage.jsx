import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './index.css';
import { fetchJsonSafe } from '../fetchUtils';

const IndexPage = () => {
  const [cardSlogan, setCardSlogan] = useState('');
  const [giftReceiverName, setGiftReceiverName] = useState('');
  const [currentUser, setCurrentUser] = useState('');
  const [receiverImageFailed, setReceiverImageFailed] = useState(false);
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

  // reset image-failed flag when receiver changes
  useEffect(() => {
    setReceiverImageFailed(false);
  }, [giftReceiverName]);

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

  useEffect(() => {
    const getCurrentUserFromCookie = () => {
      const match = document.cookie.match(/(?:^|; )APP_USER=([^;]*)/);
      return match ? decodeURIComponent(match[1]) : null;
    };

    setCurrentUser(getCurrentUserFromCookie());
  }, []);

  const handleWeiter = () => {
    navigate('/gift-lists');
  };

  return (
    <div className="container">
        <div className="static-card">
          <div className="card-slogan">
            <p className="card-text">Ho Ho Ho {currentUser}</p>
            <p className="card-slogan-text">{cardSlogan} dieses Jahr ist:</p>
          </div>
          <div className="card-receiver">
            {giftReceiverName && !receiverImageFailed && (
              <img
                src={`/static/users/${giftReceiverName.toLowerCase()}.png`}
                alt={giftReceiverName}
                className="receiver-image"
                width={80}
                height={80}
                onLoad={() => console.log('Receiver image loaded for', giftReceiverName)}
                onError={(e) => {
                  console.error('Receiver image failed to load for', giftReceiverName, e);
                  setReceiverImageFailed(true);
                }}
              />
            )}
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
