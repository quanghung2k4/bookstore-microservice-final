import { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { api } from '../api';
import { useCart } from '../context/CartContext';
import { useAuth } from '../context/AuthContext';
import { useTrackEvent } from '../utils/useTrackEvent';
import Loading from '../components/Loading';
import Recommendations from '../components/Recommendations';

const ProductDetailPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { addToCart } = useCart();
  const { user } = useAuth();
  const trackEvent = useTrackEvent();
  
  const [product, setProduct] = useState(null);
  const [loading, setLoading] = useState(true);
  const [addingToCart, setAddingToCart] = useState(false);
  const [quantity, setQuantity] = useState(1);
  const viewStart = useRef(Date.now());

  useEffect(() => {
    loadProduct();
  }, [id]);

  // Track view on mount, record duration on unmount
  useEffect(() => {
    if (!product) return;
    trackEvent('click', product.id);
    console.log("click:",product.id);
    const start = Date.now();
    return () => {
      const duration = Math.round((Date.now() - start) / 1000);
      trackEvent('click', product.id, { duration });
    };
  }, [product?.id]);

  const loadProduct = async () => {
    try {
      setLoading(true);
      const response = await api.getProduct(id);
      setProduct(response);
    } catch (error) {
      console.error('Failed to load product:', error);
      // If product not found, redirect to products page
      navigate('/products');
    } finally {
      setLoading(false);
    }
  };

  const handleAddToCart = async () => {
    if (!user) {
      alert('Vui lòng đăng nhập để thêm sản phẩm vào giỏ hàng');
      navigate('/login');
      return;
    }

    try {
      setAddingToCart(true);
      await addToCart(product.id, quantity);
      trackEvent('add_to_cart', product.id, { quantity });
      console.log("add_to_cart:",product.id);
      
      alert(`Đã thêm ${quantity} sản phẩm vào giỏ hàng!`);
    } catch (error) {
      console.error('Add to cart error:', error);
      alert('Không thể thêm sản phẩm vào giỏ hàng: ' + (error.message || 'Lỗi không xác định'));
    } finally {
      setAddingToCart(false);
    }
  };

  const handleQuantityChange = (e) => {
    const value = parseInt(e.target.value);
    if (value >= 1 && value <= product.stock) {
      setQuantity(value);
    }
  };

  if (loading) {
    return <Loading message="Đang tải thông tin sản phẩm..." />;
  }

  if (!product) {
    return (
      <div className="container">
        <div className="error-message">
          Không tìm thấy sản phẩm
        </div>
      </div>
    );
  }

  return (
    <div className="product-detail-page">
      <div className="container">
        <div className="product-detail">
          <div className="product-images">
            <div className="main-image">
              <img 
                src={product.image || `https://via.placeholder.com/500x400?text=${encodeURIComponent(product.name)}`}
                alt={product.name}
              />
            </div>
          </div>

          <div className="product-info">
            <div className="breadcrumb">
              <span onClick={() => navigate('/products')} className="breadcrumb-link">
                Sản phẩm
              </span>
              <span className="breadcrumb-separator"> / </span>
              <span>{product.category_detail?.name}</span>
              <span className="breadcrumb-separator"> / </span>
              <span>{product.name}</span>
            </div>

            <h1 className="product-title">{product.name}</h1>
            
            <div className="product-meta">
              <p className="product-sku">SKU: {product.sku}</p>
              <p className="product-category">
                Danh mục: {product.category_detail?.name}
              </p>
              {product.brand_detail && (
                <p className="product-brand">
                  Thương hiệu: {product.brand_detail.name}
                </p>
              )}
            </div>

            <div className="product-price">
              <span className="price">${product.price}</span>
            </div>

            <div className="product-stock">
              <span className={`stock-status ${product.stock > 0 ? 'in-stock' : 'out-of-stock'}`}>
                {product.stock > 0 ? `Còn ${product.stock} sản phẩm` : 'Hết hàng'}
              </span>
            </div>

            <div className="product-description">
              <h3>Mô tả sản phẩm</h3>
              <p>{product.description || 'Chưa có mô tả cho sản phẩm này.'}</p>
            </div>

            {product.attributes && Object.keys(product.attributes).length > 0 && (
              <div className="product-attributes">
                <h3>Thông số kỹ thuật</h3>
                <div className="attributes-list">
                  {Object.entries(product.attributes).map(([key, value]) => (
                    <div key={key} className="attribute-item">
                      <span className="attribute-name">{key}:</span>
                      <span className="attribute-value">{value}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {product.variants && product.variants.length > 0 && (
              <div className="product-variants">
                <h3>Phiên bản</h3>
                <div className="variants-list">
                  {product.variants.map(variant => (
                    <div key={variant.id} className="variant-item">
                      <span className="variant-name">{variant.name}</span>
                      {variant.extra_price > 0 && (
                        <span className="variant-price">+${variant.extra_price}</span>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}

            <div className="product-actions">
              {product.stock > 0 ? (
                <>
                  <div className="quantity-selector">
                    <label htmlFor="quantity">Số lượng:</label>
                    <input
                      type="number"
                      id="quantity"
                      min="1"
                      max={product.stock}
                      value={quantity}
                      onChange={handleQuantityChange}
                    />
                  </div>
                  
                  <button 
                    className="add-to-cart-btn primary"
                    onClick={handleAddToCart}
                    disabled={addingToCart}
                  >
                    {addingToCart ? 'Đang thêm...' : `Thêm ${quantity} vào giỏ hàng`}
                  </button>
                </>
              ) : (
                <button className="add-to-cart-btn disabled" disabled>
                  Hết hàng
                </button>
              )}
            </div>
          </div>
        </div>
      </div>
      <Recommendations title="Sản phẩm tương tự" strategy="content" limit={4} />
    </div>
  );
};

export default ProductDetailPage;