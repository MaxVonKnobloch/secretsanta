import React, { useEffect, useState } from 'react';
import './gift_lists.css';

const GiftListsPage = () => {
  const [users, setUsers] = useState([]); // [{pk, username, gifts: [{pk, title, created_by_name}]}]
  const [activeUserPk, setActiveUserPk] = useState(null);

  useEffect(() => {
    fetch('/api/gift-lists')
      .then(res => res.json())
      .then(data => {
        console.log('Gift lists API response:', data); // Debug output
        if (Array.isArray(data)) {
          setUsers(data);
          if (data.length > 0) setActiveUserPk(data[0].pk);
        } else {
          setUsers([]);
        }
      })
      .catch((err) => {
        console.error('Error fetching gift lists:', err);
        setUsers([]);
      });
  }, []);

  const handleTabClick = (pk) => {
    setActiveUserPk(pk);
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

  return (
    <div className="container">
      <div className="person-tabs-scroll mb-4">
        <div className="person-tabs-inner">
          {(Array.isArray(users) ? users : []).map((user, idx) => (
            <button
              key={user.pk}
              className={`person-tab${idx === 0 ? ' gold-tab' : ''}${activeUserPk === user.pk ? ' active' : ''}`}
              onClick={() => handleTabClick(user.pk)}
            >
              {user.username}
            </button>
          ))}
        </div>
      </div>
      <div className="gift-lists">
        {(Array.isArray(users) ? users : []).map(user => (
          <div
            key={user.pk}
            className="mb-3 gift-list"
            data-user-pk={user.pk}
            style={{ display: activeUserPk === user.pk ? 'block' : 'none' }}
          >
            <div className="add-idea-container">
              <button className="neue-idee-button" onClick={() => handleAddGift(user.pk)}>
                <span style={{fontWeight: 'bold', fontSize: '1.2em'}}>+</span> Neue Idee
              </button>
            </div>
            <ul className="gift-list-content list-group-flush" id={`gift-list-receiver-${user.pk}`}>
              {user.gifts && user.gifts.length > 0 ? (
                user.gifts.map(gift => (
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
                  Noch gibt es keine Wünsche für {user.username}.
                </li>
              )}
            </ul>
          </div>
        ))}
      </div>
    </div>
  );
};

export default GiftListsPage;
