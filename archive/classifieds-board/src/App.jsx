import React, { useState, useEffect, useCallback } from 'react';

const ONE_WEEK_MS = 7 * 24 * 60 * 60 * 1000;
const MAX_VIEWS = 10;

function App() {
  const [user, setUser] = useState(null);
  const [posts, setPosts] = useState([]);
  const [authMode, setAuthMode] = useState('login');
  const [authForm, setAuthForm] = useState({ username: '', password: '' });
  const [newPostOpen, setNewPostOpen] = useState(false);
  const [newPost, setNewPost] = useState({ content: '', location: '' });
  const [userLocation, setUserLocation] = useState(null);
  const [selectedPost, setSelectedPost] = useState(null);

  // Load from localStorage
  useEffect(() => {
    const savedPosts = localStorage.getItem('classifieds-posts');
    const savedUser = localStorage.getItem('classifieds-user');
    
    if (savedPosts) setPosts(JSON.parse(savedPosts));
    if (savedUser) setUser(JSON.parse(savedUser));

    // Try to get user location
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (pos) => setUserLocation({ lat: pos.coords.latitude, lng: pos.coords.longitude }),
        () => console.log('Location access denied')
      );
    }
  }, []);

  // Save posts to localStorage
  useEffect(() => {
    localStorage.setItem('classifieds-posts', JSON.stringify(posts));
  }, [posts]);

  // Auto-clean expired posts every minute
  useEffect(() => {
    const interval = setInterval(() => {
      setPosts(prev => prev.filter(post => 
        Date.now() < post.expiresAt && post.views < MAX_VIEWS
      ));
    }, 60000);
    return () => clearInterval(interval);
  }, []);

  // Calculate distance between two coordinates (haversine formula)
  const calculateDistance = useCallback((lat1, lon1, lat2, lon2) => {
    const R = 3959; // miles
    const dLat = (lat2 - lat1) * Math.PI / 180;
    const dLon = (lon2 - lon1) * Math.PI / 180;
    const a = 
      Math.sin(dLat/2) * Math.sin(dLat/2) +
      Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) * 
      Math.sin(dLon/2) * Math.sin(dLon/2); 
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a)); 
    return R * c;
  }, []);

  // Sort posts by proximity if user location is available
  const sortedPosts = [...posts].sort((a, b) => {
    if (userLocation && a.location?.lat && b.location?.lat) {
      const distA = calculateDistance(userLocation.lat, userLocation.lng, a.location.lat, a.location.lng);
      const distB = calculateDistance(userLocation.lat, userLocation.lng, b.location.lat, b.location.lng);
      return distA - distB;
    }
    return new Date(b.createdAt) - new Date(a.createdAt);
  });

  const handleAuth = (e) => {
    e.preventDefault();
    if (authMode === 'register') {
      // Simple registration - no verification
      localStorage.setItem(`user-${authForm.username}`, JSON.stringify(authForm));
    }
    
    const savedUser = localStorage.getItem(`user-${authForm.username}`);
    if (savedUser) {
      const userData = JSON.parse(savedUser);
      if (userData.password === authForm.password) {
        setUser(userData);
        localStorage.setItem('classifieds-user', JSON.stringify(userData));
      }
    }
  };

  const handleLogout = () => {
    setUser(null);
    localStorage.removeItem('classifieds-user');
  };

  const handleCreatePost = (e) => {
    e.preventDefault();
    if (!user) return;

    const post = {
      id: Date.now().toString(),
      content: newPost.content,
      author: user.username,
      createdAt: new Date().toISOString(),
      expiresAt: Date.now() + ONE_WEEK_MS,
      views: 0,
      location: userLocation || null,
      locationName: newPost.location
    };

    setPosts(prev => [...prev, post]);
    setNewPostOpen(false);
    setNewPost({ content: '', location: '' });
  };

  const handleViewPost = (post) => {
    setSelectedPost(post);
    setPosts(prev => prev.map(p => 
      p.id === post.id ? { ...p, views: p.views + 1 } : p
    ));
  };

  const getTimeRemaining = (expiresAt) => {
    const remaining = expiresAt - Date.now();
    const hours = Math.floor(remaining / (1000 * 60 * 60));
    const days = Math.floor(hours / 24);
    if (days > 0) return `${days}d`;
    return `${hours}h`;
  };

  if (!user) {
    return (
      <div className="container">
        <div className="header-bar">CLASSIFIEDS BOARD v0.1</div>
        <div className="auth-box classic-border">
          <div className="header-bar">{authMode === 'login' ? 'LOGIN' : 'REGISTER'}</div>
          <form onSubmit={handleAuth} style={{ padding: '8px' }}>
            <div className="form-row">
              <label>USERNAME:</label>
              <input 
                type="text" 
                value={authForm.username}
                onChange={e => setAuthForm({ ...authForm, username: e.target.value })}
              />
            </div>
            <div className="form-row">
              <label>PASSWORD:</label>
              <input 
                type="password"
                value={authForm.password}
                onChange={e => setAuthForm({ ...authForm, password: e.target.value })}
              />
            </div>
            <div className="form-row">
              <button type="submit">{authMode === 'login' ? 'LOGIN' : 'REGISTER'}</button>
              <button 
                type="button"
                onClick={() => setAuthMode(authMode === 'login' ? 'register' : 'login')}
                style={{ marginLeft: '8px' }}
              >
                {authMode === 'login' ? 'CREATE ACCOUNT' : 'BACK TO LOGIN'}
              </button>
            </div>
            <p className="warning-text">NO EMAIL REQUIRED. NO VERIFICATION.</p>
          </form>
        </div>
      </div>
    );
  }

  return (
    <div className="container">
      <div className="header-bar">
        CLASSIFIEDS BOARD v0.1 | Logged in as: {user.username}
        <button onClick={handleLogout} style={{ float: 'right' }}>LOGOUT</button>
      </div>
      
      <div className="location-bar">
        {userLocation 
          ? `📍 YOUR LOCATION: ${userLocation.lat.toFixed(4)}, ${userLocation.lng.toFixed(4)}` 
          : '📍 LOCATION ACCESS NOT AVAILABLE - POSTS WILL NOT BE SORTED BY PROXIMITY'
        }
        <button onClick={() => setNewPostOpen(true)} style={{ float: 'right' }}>NEW POST</button>
      </div>

      {newPostOpen && (
        <div className="classic-border" style={{ margin: '8px', padding: '8px' }}>
          <div className="header-bar">CREATE NEW POST</div>
          <form onSubmit={handleCreatePost} style={{ padding: '8px' }}>
            <div className="form-row">
              <label>LOCATION (city/area):</label>
              <input 
                type="text"
                value={newPost.location}
                onChange={e => setNewPost({ ...newPost, location: e.target.value })}
                style={{ width: '100%' }}
              />
            </div>
            <div className="form-row">
              <label>SPECS ONLY. NO FLUFF. MAX 140 CHARS:</label>
              <textarea 
                value={newPost.content}
                onChange={e => setNewPost({ ...newPost, content: e.target.value.slice(0, 140) })}
                maxLength={140}
                rows={4}
                style={{ width: '100%' }}
              />
              <div style={{ fontSize: '10px', color: '#808080' }}>{newPost.content.length}/140</div>
            </div>
            <div className="warning-text">
              ⚠️ POST EXPIRES AFTER 7 DAYS OR 10 VIEWS, WHICHEVER COMES FIRST
            </div>
            <button type="submit">POST</button>
            <button type="button" onClick={() => setNewPostOpen(false)} style={{ marginLeft: '8px' }}>CANCEL</button>
          </form>
        </div>
      )}

      {selectedPost && (
        <div className="classic-border" style={{ margin: '8px', padding: '8px' }}>
          <div className="header-bar">VIEWING POST #{selectedPost.id}</div>
          <div style={{ padding: '8px' }}>
            <div className="post-spec" style={{ margin: '8px 0' }}>{selectedPost.content}</div>
            <div className="post-meta">
              <span className="location-indicator">📍 {selectedPost.locationName || 'UNKNOWN LOCATION'}</span> | 
              <span className="views-indicator"> 👁 {selectedPost.views}/{MAX_VIEWS} </span> | 
              <span className="expiry-indicator"> ⏳ {getTimeRemaining(selectedPost.expiresAt)} REMAINING</span>
            </div>
            <button onClick={() => setSelectedPost(null)}>CLOSE</button>
          </div>
        </div>
      )}

      <div className="classic-border" style={{ margin: '8px' }}>
        <div className="header-bar">POSTS - SORTED BY PROXIMITY ({sortedPosts.length} ACTIVE)</div>
        <div className="post-grid clearfix">
          {sortedPosts.map(post => {
            const isExpiring = post.views >= 7 || (post.expiresAt - Date.now()) < 24 * 60 * 60 * 1000;
            return (
              <div 
                key={post.id} 
                className={`post-box ${isExpiring ? 'post-box-expiring' : ''}`}
                onClick={() => handleViewPost(post)}
              >
                <div className="post-spec">{post.content}</div>
                <div className="post-meta">
                  <span className="location-indicator">{post.locationName?.substring(0, 12) || '?'}</span>
                  <br />
                  <span className="views-indicator">{post.views}/{MAX_VIEWS}</span> | 
                  <span className="expiry-indicator"> {getTimeRemaining(post.expiresAt)}</span>
                </div>
              </div>
            );
          })}
          {sortedPosts.length === 0 && (
            <div style={{ padding: '16px', textAlign: 'center', width: '100%' }}>
              NO POSTS YET. BE THE FIRST TO POST.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;