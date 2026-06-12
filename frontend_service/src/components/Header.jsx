import { Link, useNavigate } from 'react-router-dom';
import { useEffect, useMemo, useRef, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useCart } from '../context/CartContext';
import { api } from '../api';
import { getWishlistCount } from '../utils/wishlist';
import { useTrackEvent } from '../utils/useTrackEvent';

const Header = () => {
  const { user, logout } = useAuth();
  const { getCartItemCount } = useCart();
  const navigate = useNavigate();
  const trackEvent = useTrackEvent();

  const [query, setQuery] = useState('');
  const [suggestions, setSuggestions] = useState([]);
  const [searchOpen, setSearchOpen] = useState(false);
  const [searchLoading, setSearchLoading] = useState(false);
  const [wishlistCount, setWishlistCount] = useState(() => getWishlistCount());
  const [accountOpen, setAccountOpen] = useState(false);
  const rootRef = useRef(null);
  const debounceRef = useRef(null);

  const initials = useMemo(() => {
    const v = (user?.first_name || user?.username || 'U').trim();
    return (v[0] || 'U').toUpperCase();
  }, [user?.first_name, user?.username]);

  const handleLogout = () => {
    logout();
    setAccountOpen(false);
    navigate('/');
  };

  useEffect(() => {
    const onWishChanged = () => setWishlistCount(getWishlistCount());
    window.addEventListener('wishlist:changed', onWishChanged);
    window.addEventListener('storage', onWishChanged);
    return () => {
      window.removeEventListener('wishlist:changed', onWishChanged);
      window.removeEventListener('storage', onWishChanged);
    };
  }, []);

  useEffect(() => {
    const onDocClick = (e) => {
      if (!rootRef.current) return;
      if (!rootRef.current.contains(e.target)) {
        setSearchOpen(false);
        setAccountOpen(false);
      }
    };
    document.addEventListener('mousedown', onDocClick);
    return () => document.removeEventListener('mousedown', onDocClick);
  }, []);

  useEffect(() => {
    if (debounceRef.current) window.clearTimeout(debounceRef.current);
    const q = query.trim();
    if (q.length < 2) {
      setSuggestions([]);
      setSearchLoading(false);
      return;
    }

    debounceRef.current = window.setTimeout(async () => {
      try {
        setSearchLoading(true);
        const res = await api.aiSearch(q, user?.id);
      
        setSuggestions(res?.results || []);
      } catch (err) {
        console.error('Search error:', err);
        setSuggestions([]);
      } finally {
        setSearchLoading(false);
      }
    }, 220);

    return () => {
      if (debounceRef.current) window.clearTimeout(debounceRef.current);
    };
  }, [query, user?.id]);

  const handleSubmitSearch = (e) => {
    e.preventDefault();
    const q = query.trim();
    if (!q) return;

    setSearchOpen(false);
    navigate(`/products?search=${encodeURIComponent(q)}`);
  };

  const goToProduct = (productId) => {
    const q = query.trim();
    if (q) {
  
    }
    setSearchOpen(false);
    setQuery('');
    setSuggestions([]);
    navigate(`/products/${productId}`);
  };

  return (
    <header className="header" ref={rootRef}>
      <div className="container header-row">
        <Link to="/" className="logo" aria-label="Trang chủ">
          <span className="logo-text">SupperShop</span>
        </Link>

        <div className="header-search" role="search">
          <form onSubmit={handleSubmitSearch} className="header-search-form">
            <input
              value={query}
              onChange={(e) => {
                setQuery(e.target.value);
                setSearchOpen(true);
              }}
              onFocus={() => setSearchOpen(true)}
              className="header-search-input"
              placeholder="Tìm kiếm thông minh…"
              aria-label="Tìm kiếm"
            />
            <button type="submit" className="header-search-btn" aria-label="Tìm kiếm">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" aria-hidden="true">
                <path d="M10.5 18a7.5 7.5 0 1 1 0-15 7.5 7.5 0 0 1 0 15Z" stroke="currentColor" strokeWidth="2" />
                <path d="M16.2 16.2 21 21" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
              </svg>
            </button>
          </form>

          {searchOpen && (query.trim().length > 0) && (
            <div className="search-dropdown" role="listbox">
              <div className="search-dropdown-header">
                <span>{searchLoading ? 'Đang gợi ý…' : 'Gợi ý'}</span>
                <span className="search-dropdown-hint">Enter để tìm</span>
              </div>

              {suggestions.length > 0 ? (
                <div className="search-dropdown-list">
                  {suggestions.slice(0, 6).map((s) => (
                    <button
                      key={s.product_id}
                      type="button"
                      className="search-suggestion"
                      onClick={() => goToProduct(s.product_id)}
                    >
                      <span className="search-suggestion-title">{s.name}</span>
                      <span className="search-suggestion-meta">#{s.product_id}</span>
                    </button>
                  ))}
                </div>
              ) : (
                <button
                  type="button"
                  className="search-suggestion empty"
                  onClick={() => {
                    const q = query.trim();
                    if (!q) return;
                    setSearchOpen(false);
                    navigate(`/products?search=${encodeURIComponent(q)}`);
                  }}
                >
                  <span className="search-suggestion-title">Tìm “{query.trim()}” trong tất cả sản phẩm</span>
                </button>
              )}
            </div>
          )}
        </div>

        <div className="header-actions" aria-label="Tài khoản và tiện ích">
          <button
            type="button"
            className="icon-btn"
            aria-label={user ? 'Tài khoản' : 'Đăng nhập'}
            onClick={() => {
              if (!user) {
                navigate('/login');
                return;
              }
              setAccountOpen(v => !v);
              setSearchOpen(false);
            }}
          >
            {user ? (
              <span className="avatar-pill" aria-hidden="true">{initials}</span>
            ) : (
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" aria-hidden="true">
                <path d="M12 12a4 4 0 1 0-4-4 4 4 0 0 0 4 4Z" stroke="currentColor" strokeWidth="2" />
                <path d="M20 21a8 8 0 0 0-16 0" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
              </svg>
            )}
          </button>

          {accountOpen && user && (
            <div className="account-dropdown" role="menu">
              <div className="account-dropdown-title">{user.first_name || user.username}</div>
              <Link to="/orders" className="account-dropdown-item" onClick={() => setAccountOpen(false)}>Đơn hàng</Link>
              <button type="button" className="account-dropdown-item danger" onClick={handleLogout}>Đăng xuất</button>
            </div>
          )}

          <Link to="/products?wishlist=1" className="icon-btn" aria-label="Wishlist">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" aria-hidden="true">
              <path d="M12 21s-7-4.6-9.2-9.2C1.4 8.7 3.3 6 6.3 6c1.7 0 3 .9 3.7 1.9.7-1 2-1.9 3.7-1.9 3 0 4.9 2.7 3.5 5.8C19 16.4 12 21 12 21Z" stroke="currentColor" strokeWidth="2" strokeLinejoin="round" />
            </svg>
            {wishlistCount > 0 && <span className="icon-badge">{wishlistCount}</span>}
          </Link>

          <Link to="/cart" className="icon-btn" aria-label="Giỏ hàng">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" aria-hidden="true">
              <path d="M6 6h15l-2 9H7L6 6Z" stroke="currentColor" strokeWidth="2" strokeLinejoin="round" />
              <path d="M6 6 5 3H2" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
              <path d="M9 21a1 1 0 1 0 0-2 1 1 0 0 0 0 2Zm9 0a1 1 0 1 0 0-2 1 1 0 0 0 0 2Z" fill="currentColor" />
            </svg>
            {getCartItemCount() > 0 && <span className="icon-badge">{getCartItemCount()}</span>}
          </Link>
        </div>
      </div>
    </header>
  );
};

export default Header;
