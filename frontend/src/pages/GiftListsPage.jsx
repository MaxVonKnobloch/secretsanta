import React, { useEffect, useState, useRef } from 'react';
import './gift_lists.css';

const GiftListsPage = () => {
  const [users, setUsers] = useState([]);
  const [activeUserIdx, setActiveUserIdx] = useState(0);
  const touchStartX = useRef(null);
  const touchEndX = useRef(null);
  const mouseStartX = useRef(null);
  const mouseEndX = useRef(null);
  const listRef = useRef(null);
  const swipeContainerRef = useRef(null);

  useEffect(() => {
    fetch('/api/gift-lists')
      .then(res => res.json())
      .then(data => {
        if (Array.isArray(data)) {
          setUsers(data);
          setActiveUserIdx(0);
        } else {
          setUsers([]);
        }
      })
      .catch(() => setUsers([]));
  }, []);

  // Swipe gesture handlers
  const handleTouchStart = (e) => {
    touchStartX.current = e.touches[0].clientX;
  };
  const handleTouchMove = (e) => {
    touchEndX.current = e.touches[0].clientX;
  };
  const handleTouchEnd = () => {
    if (touchStartX.current === null || touchEndX.current === null) return;
    const deltaX = touchEndX.current - touchStartX.current;
    if (Math.abs(deltaX) > 50) {
      if (deltaX < 0 && activeUserIdx < users.length - 1) {
        setActiveUserIdx(activeUserIdx + 1);
        animateSlide('left');
      } else if (deltaX > 0 && activeUserIdx > 0) {
        setActiveUserIdx(activeUserIdx - 1);
        animateSlide('right');
      }
    }
    touchStartX.current = null;
    touchEndX.current = null;
  };

  // Mouse gesture handlers for desktop
  const handleMouseDown = (e) => {
    mouseStartX.current = e.clientX;
  };
  const handleMouseMove = (e) => {
    if (mouseStartX.current !== null) {
      mouseEndX.current = e.clientX;
    }
  };
  const handleMouseUp = () => {
    if (mouseStartX.current === null || mouseEndX.current === null) return;
    const deltaX = mouseEndX.current - mouseStartX.current;
    if (Math.abs(deltaX) > 50) {
      if (deltaX < 0 && activeUserIdx < users.length - 1) {
        setActiveUserIdx(activeUserIdx + 1);
        animateSlide('left');
      } else if (deltaX > 0 && activeUserIdx > 0) {
        setActiveUserIdx(activeUserIdx - 1);
        animateSlide('right');
      }
    }
    mouseStartX.current = null;
    mouseEndX.current = null;
  };

  // Slide animation
  const animateSlide = (direction) => {
    if (!swipeContainerRef.current) return;
    swipeContainerRef.current.style.transition = 'transform 0.3s ease';
    swipeContainerRef.current.style.transform = direction === 'left' ? 'translateX(-100vw)' : 'translateX(100vw)';
    setTimeout(() => {
      swipeContainerRef.current.style.transition = 'none';
      swipeContainerRef.current.style.transform = 'translateX(0)';
    }, 300);
  };

  const handleAddGift = (userPk) => {
    const giftTitle = prompt('Neue Geschenkidee:');
    if (!giftTitle) return;
    fetch('/api/gift-lists/add', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ created_for: userPk, title: giftTitle })
    })
      .then(res => res.json())
      .then(data => {
        if (data.success) {
          setUsers(users => users.map(u =>
            u.pk === userPk ? { ...u, gifts: [...u.gifts, data.gift] } : u
          ));
        }
      });
  };

  // Render user switch bar with partial next/prev names
  const renderUserSwitchBar = () => {
    if (users.length === 0) return null;
    const prevUser = users[activeUserIdx - 1];
    const activeUser = users[activeUserIdx];
    const nextUser = users[activeUserIdx + 1];
    return (
      <div className="user-switch-bar">
        <div className="user-switch-bar-inner">
          <div className="user-switch-half user-switch-prev" style={{opacity: prevUser ? 1 : 0}}>
            {prevUser ? prevUser.username : ''}
          </div>
          <div className="user-switch-center">
            {activeUser ? activeUser.username : ''}
          </div>
          <div className="user-switch-half user-switch-next" style={{opacity: nextUser ? 1 : 0}}>
            {nextUser ? nextUser.username : ''}
          </div>
        </div>
      </div>
    );
  };

  const activeUser = users[activeUserIdx];

  return (
    <div className="container">
      <div
        className="swipe-sync-container"
        ref={swipeContainerRef}
      >
        {renderUserSwitchBar()}
        <div
          className="gift-lists"
          ref={listRef}
          onTouchStart={handleTouchStart}
          onTouchMove={handleTouchMove}
          onTouchEnd={handleTouchEnd}
          onMouseDown={handleMouseDown}
          onMouseMove={handleMouseMove}
          onMouseUp={handleMouseUp}
        >
          {activeUser && (
            <div className="mb-3 gift-list" data-user-pk={activeUser.pk}>
              <div className="add-idea-container">
                <button className="neue-idee-button" onClick={() => handleAddGift(activeUser.pk)}>
                  <span style={{fontWeight: 'bold', fontSize: '1.2em'}}>+</span> Neue Idee
                </button>
              </div>
              <ul className="gift-list-content list-group-flush" id={`gift-list-receiver-${activeUser.pk}`}>
                {activeUser.gifts && activeUser.gifts.length > 0 ? (
                  activeUser.gifts.map(gift => (
                    <li className="gift-list-item" key={gift.pk} data-gift-id={gift.pk}>
                      <div className="gift-list-box" style={{ display: 'flex', flexDirection: 'column', alignItems: 'stretch' }}>
                        <div style={{ display: 'flex', flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' }}>
                          <span className="gift-title">{gift.title}</span>
                        </div>
                        <div style={{ display: 'flex', flexDirection: 'row', justifyContent: 'flex-end', width: '100%' }}>
                          <span className="gift-creator">{gift.created_by_name ? gift.created_by_name.slice(0,5) : ''}</span>
                        </div>
                      </div>
                    </li>
                  ))
                ) : (
                  <li className="gift-list-item gift-list-item-empty">
                    Noch gibt es keine Wünsche für {activeUser.username}.
                  </li>
                )}
              </ul>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default GiftListsPage;
