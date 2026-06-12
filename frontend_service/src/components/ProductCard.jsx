import { Link } from 'react-router-dom';
import { useCart } from '../context/CartContext';
import { useAuth } from '../context/AuthContext';
import { useState } from 'react';
import { isWishlisted, toggleWishlist } from '../utils/wishlist';
import { useTrackEvent } from '../utils/useTrackEvent';

function getRating(product) {
  const candidates = [
    product?.average_rating,
    product?.avg_rating,
    product?.rating,
    product?.rating_avg,
  ];
  for (const c of candidates) {
    const n = Number(c);
    if (Number.isFinite(n) && n > 0) return Math.max(0, Math.min(5, n));
  }
  return null;
}

function Stars({ value }) {
  const rounded = Math.round(value * 10) / 10;
  const full = Math.floor(rounded);
  const hasHalf = rounded - full >= 0.5;
  const empty = 5 - full - (hasHalf ? 1 : 0);
  const items = [
    ...Array.from({ length: full }, () => 'full'),
    ...(hasHalf ? ['half'] : []),
    ...Array.from({ length: empty }, () => 'empty'),
  ];

  return (
    <span className="rating" aria-label={`Đánh giá ${rounded}/5`}>
      {items.map((t, i) => (
        <span key={i} className={`star ${t}`} aria-hidden="true">★</span>
      ))}
      <span className="rating-number">{rounded}</span>
    </span>
  );
}

const ProductCard = ({ product }) => {
  const { addToCart } = useCart();
  const { user } = useAuth();
  const [loading, setLoading] = useState(false);
  const trackEvent = useTrackEvent();

  const rating = getRating(product);
  const wished = isWishlisted(product.id);

  const handleAddToCart = async (e) => {
    e.preventDefault();
    e.stopPropagation();
    
    if (!user) {
      alert('Vui lòng đăng nhập để thêm sản phẩm vào giỏ hàng');
      return;
    }

    try {
      setLoading(true);
      await addToCart(product.id);
      trackEvent('add_to_cart', product.id, { quantity: 1 });
      console.log("add_to_cart:", product.id);
      alert('Đã thêm sản phẩm vào giỏ hàng!');
    } catch (error) {
      console.error('Add to cart error:', error);
      alert('Không thể thêm sản phẩm vào giỏ hàng: ' + (error.message || 'Lỗi không xác định'));
    } finally {
      setLoading(false);
    }
  };

  const handleToggleWishlist = (e) => {
    e.preventDefault();
    e.stopPropagation();
    toggleWishlist(product.id);
  };

  return (
    <div className="product-card">
      <Link to={`/products/${product.id}`} className="product-link" aria-label={product.name}>
        <div className="product-image">
          <img
            src={product.image || `https://via.placeholder.com/600x450?text=${encodeURIComponent(product.name)}`}
            alt={product.name}
            loading="lazy"
          />

          <button
            type="button"
            className={`product-fav-btn ${wished ? 'active' : ''}`}
            onClick={handleToggleWishlist}
            aria-label={wished ? 'Bỏ khỏi wishlist' : 'Thêm vào wishlist'}
          >
            <span aria-hidden="true">♥</span>
          </button>

          <div className="product-actions-overlay" aria-hidden="true">
            <div className="product-actions-overlay-inner">
              <span className="quick-pill">Xem nhanh</span>
              <span className="quick-pill">Thêm nhanh</span>
            </div>
          </div>

          {product.stock === 0 && (
            <div className="out-of-stock-overlay">Hết hàng</div>
          )}
        </div>

        <div className="product-info">
          <div className="product-topline">
            <h3 className="product-name">{product.name}</h3>
            {rating ? <Stars value={rating} /> : <span className="rating placeholder">&nbsp;</span>}
          </div>
          <p className="product-category">{product.category_detail?.name || '—'}</p>
          <div className="product-bottomline">
            <p className="product-price">${product.price}</p>
            <p className="product-stock">Còn: {product.stock}</p>
          </div>
        </div>
      </Link>
      
      <button 
        className="add-to-cart-btn"
        onClick={handleAddToCart}
        disabled={loading || product.stock === 0}
      >
        {loading ? 'Đang thêm...' : product.stock === 0 ? 'Hết hàng' : 'Thêm vào giỏ'}
      </button>
    </div>
  );
};

export default ProductCard;