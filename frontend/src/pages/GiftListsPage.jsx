import React, { useEffect, useState, useRef } from 'react';
import './gift_lists.css';

const GiftListsPage = () => {
  const [users, setUsers] = useState([]);
  const [activeUserIdx, setActiveUserIdx] = useState(0);
  const [showPopup, setShowPopup] = useState(false);
  const [popupTitle, setPopupTitle] = useState('');
  const [popupLink, setPopupLink] = useState('');
  const [editGift, setEditGift] = useState(null);
  const [editTitle, setEditTitle] = useState('');
  const [editLink, setEditLink] = useState('');
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

  const getCurrentUserFromCookie = () => {
    const match = document.cookie.match(/(?:^|; )APP_USER=([^;]*)/);
    return match ? decodeURIComponent(match[1]) : null;
  };

  const [currentUser, setCurrentUser] = useState(null);

  useEffect(() => {
    setCurrentUser(getCurrentUserFromCookie());
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

  const openAddGiftPopup = () => {
    setPopupTitle('');
    setPopupLink('');
    setShowPopup(true);
  };

  const closeAddGiftPopup = () => {
    setShowPopup(false);
  };

  const handleAddGiftSubmit = (userPk, userName) => {
    if (!popupTitle.trim()) return;
    fetch('/api/gifts/add', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ created_for: userName, title: popupTitle, description: '', links: popupLink })
    })
      .then(res => res.json())
      .then(data => {
        if (data.pk) {
          setUsers(users => users.map(u =>
            u.pk === userPk ? { ...u, gifts: [data, ...u.gifts] } : u
          ));
        }
        closeAddGiftPopup();
      });
  };

  const openEditGiftPopup = (gift) => {
    setEditGift(gift);
    setEditTitle(gift.title);
    setEditLink(gift.link || '');
  };

  const closeEditGiftPopup = () => {
    setEditGift(null);
    setEditTitle('');
    setEditLink('');
  };

  const handleDeleteGiftSubmit = () => {
    if (!editGift) return;
    fetch(`/api/gifts/${editGift.pk}`, {
        method: 'DELETE'
        })
        .then(res => {
            if (res.ok) {
                setUsers(users => users.map(u =>
                    u.pk === activeUser.pk ? {
                        ...u,
                        gifts: u.gifts.filter(g => g.pk !== editGift.pk)
                    } : u
                ));
            }
            closeEditGiftPopup();
        });
  };

  const handleEditGiftSubmit = () => {
    if (!editGift || !editTitle.trim()) return;
    fetch(`/api/gifts/${editGift.pk}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ title: editTitle, link: editLink })
    })
      .then(res => res.json())
      .then(data => {
        if (data.pk) {
          setUsers(users => users.map(u =>
            u.pk === activeUser.pk ? {
              ...u,
              gifts: u.gifts.map(g => g.pk === data.pk ? { ...g, ...data } : g)
            } : u
          ));
        }
        closeEditGiftPopup();
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
    <div className="container"
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
                <button className="neue-idee-button" onClick={openAddGiftPopup}>
                  <span style={{fontWeight: 'bold', fontSize: '1.2em'}}>+</span> Neue Idee
                </button>
              </div>
              <ul className="gift-list-content list-group-flush" id={`gift-list-receiver-${activeUser.pk}`}>
                {activeUser.gifts && activeUser.gifts.length > 0 ? (
                  activeUser.gifts.map(gift => (
                    <li className="gift-list-item" key={gift.pk} data-gift-id={gift.pk}
                      onClick={() => {
                        if (currentUser && gift.created_by_name === currentUser) {
                          openEditGiftPopup(gift);
                        }
                      }}>
                      <div className="gift-list-box">
                        <div className="gift-main-row">
                          <img
                            src={gift.preview_image_path || "/static/previews/default_preview.png"}
                            alt={gift.title}
                            className="gift-preview-image"
                            onClick={e => e.stopPropagation()}
                            onError={e => {
                              if (e.target.dataset.fallback !== "true") {
                                e.target.src = "/static/previews/default_preview.png";
                                e.target.dataset.fallback = "true";
                              }
                            }}
                            style={{ maxWidth: '60px', maxHeight: '60px', objectFit: 'cover', borderRadius: '8px', marginRight: '10px' }}
                          />
                          {gift.link ? (
                            <a
                              href={gift.link}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="gift-title gift-title-link"
                              onClick={e => e.stopPropagation()}
                            >{gift.title}</a>
                          ) : (
                            <span className="gift-title">{gift.title}</span>
                          )}
                        </div>
                        <div className="gift-creator-row">
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
      {showPopup && (
        <div className="add-idea-popup" onClick={closeAddGiftPopup}>
          <div className="popup-content" onClick={e => e.stopPropagation()}>
            <h3>Neue Idee</h3>
            <div className="input-group">
              <label htmlFor="gift-title">Name</label>
              <input
                id="gift-title"
                type="text"
                value={popupTitle}
                onChange={e => setPopupTitle(e.target.value)}
                placeholder="Name des Geschenks"
                autoFocus
              />
            </div>
            <div className="input-group">
              <label htmlFor="gift-link">Link (optional)</label>
              <input
                id="gift-link"
                type="text"
                value={popupLink}
                onChange={e => setPopupLink(e.target.value)}
                placeholder="z.B. https://..."
              />
            </div>
            <div className="popup-buttons">
              <button className="abbrechen-button" onClick={closeAddGiftPopup}>Abbrechen</button>
              <button className="fertig-button" onClick={() => handleAddGiftSubmit(activeUser.pk, activeUser.username)}>Speichern</button>
            </div>
          </div>
        </div>
      )}
      {editGift && (
        <div className="add-idea-popup" onClick={closeEditGiftPopup}>
          <div className="popup-content" onClick={e => e.stopPropagation()}>
            <h3>Geschenk bearbeiten</h3>
            <div className="input-group">
              <label htmlFor="edit-gift-title">Name</label>
              <input
                id="edit-gift-title"
                type="text"
                value={editTitle}
                onChange={e => setEditTitle(e.target.value)}
                placeholder="Name des Geschenks"
                autoFocus
              />
            </div>
            <div className="input-group">
              <label htmlFor="edit-gift-link">Link (optional)</label>
              <input
                id="edit-gift-link"
                type="text"
                value={editLink}
                onChange={e => setEditLink(e.target.value)}
                placeholder="z.B. https://..."
              />
            </div>
            <div className="popup-buttons">
              <button className="abbrechen-button" onClick={closeEditGiftPopup}>Abbrechen</button>
              <button className="fertig-button" onClick={handleEditGiftSubmit}>Speichern</button>
            </div>
            <div className="popup-buttons">
              <button className="delete-button" onClick={handleDeleteGiftSubmit}>Löschen</button>
            </div>

          </div>
        </div>
      )}
      </div>
  );
};

export default GiftListsPage;
