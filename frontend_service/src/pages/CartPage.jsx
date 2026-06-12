import { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useCart } from '../context/CartContext';
import { useAuth } from '../context/AuthContext';
import { api } from '../api';
import Loading from '../components/Loading';
import { useTrackEvent } from '../utils/useTrackEvent';


const CartPage = () => {
  const { cart, updateQuantity, removeItem, clearCart, checkout, getCartTotal, loading } = useCart();
  const { user } = useAuth();
  const navigate = useNavigate();
  const [checkoutLoading, setCheckoutLoading] = useState(false);
  const [productDetails, setProductDetails] = useState({});
  const trackEvent = useTrackEvent();
  
  console.log(user);
  
  useEffect(() => {
    const items = cart?.items || [];
    const missingIds = items
      .map(item => item.product_id)
      .filter(id => !productDetails[id]);

    if (missingIds.length === 0) return;

    missingIds.forEach(async (id) => {
      try {
        const product = await api.getProduct(id);
        setProductDetails(prev => ({ ...prev, [id]: product }));
      } catch (e) {
        setProductDetails(prev => ({ ...prev, [id]: null }));
      }
    });
  }, [cart]);

  const handleQuantityChange = async (itemId, newQuantity) => {
    if (newQuantity < 1) return;
    
    try {
      await updateQuantity(itemId, newQuantity);
    } catch (error) {
      alert('Không thể cập nhật số lượng');
    }
  };

  const handleRemoveItem = async (itemId,pId) => {
    if (confirm('Bạn có chắc muốn xóa sản phẩm này khỏi giỏ hàng?')) {
      try {
        await removeItem(itemId);
        trackEvent('remove_from_cart', pId);
        console.log("remove_from_cart:",pId);
      } catch (error) {
        alert('Không thể xóa sản phẩm');
      }
    }
  };

  const handleClearCart = async () => {
    if (confirm('Bạn có chắc muốn xóa toàn bộ giỏ hàng?')) {
      try {
        await clearCart();
      } catch (error) {
        alert('Không thể xóa giỏ hàng');
      }
    }
  };

  const handleCheckout = async () => {
    if (!user) {
      navigate('/login');
      return;
    }

    try {
      setCheckoutLoading(true);
      const order = await checkout();
      console.log("product:",productDetails);
      for(var x in productDetails){
        console.log("purchase",x);
        
        trackEvent('purchase', x);
      }

      
      navigate('/checkout', { state: { orderId: order.id } });
    } catch (error) {
      alert('Đặt hàng thất bại: ' + error.message);
    } finally {
      setCheckoutLoading(false);
    }
  };

  if (!user) {
    return (
      <div className="container">
        <div className="auth-required">
          <h2>Vui lòng đăng nhập</h2>
          <p>Bạn cần đăng nhập để xem giỏ hàng</p>
          <Link to="/login" className="login-btn">
            Đăng nhập
          </Link>
        </div>
      </div>
    );
  }

  if (loading) {
    return <Loading message="Đang tải giỏ hàng..." />;
  }

  const cartItems = cart?.items || [];
  const total = getCartTotal();

  return (
    <div className="cart-page">
      <div className="container">
        <div className="page-header">
          <h1>Giỏ hàng của bạn</h1>
        </div>

        {cartItems.length === 0 ? (
          <div className="empty-cart">
            <div className="empty-cart-icon">🛒</div>
            <h2>Giỏ hàng trống</h2>
            <p>Bạn chưa có sản phẩm nào trong giỏ hàng</p>
            <Link to="/products" className="continue-shopping-btn">
              Tiếp tục mua sắm
            </Link>
          </div>
        ) : (
          <div className="cart-content">
            <div className="cart-items">
              <div className="cart-header">
                <span>Sản phẩm</span>
                <span>Giá</span>
                <span>Số lượng</span>
                <span>Tổng</span>
                <span></span>
              </div>

              {cartItems.map(item => {
                console.log(item);
                
                const product = productDetails[item.product_id];
                const imageUrl = product?.image || `https://placehold.co/80x80?text=${encodeURIComponent(product?.name || 'SP')}`;
                const productName = product?.name || `Sản phẩm #${item.product_id}`;
                return (
                <div key={item.id} className="cart-item">
                  <div className="item-info">
                    <img 
                      src={imageUrl}
                      alt={productName}
                      className="item-image"
                    />
                    <div className="item-details">
                      <h3>{productName}</h3>
                      {product?.category_detail?.name && (
                        <p className="item-category">{product.category_detail.name}</p>
                      )}
                    </div>
                  </div>

                  <div className="item-price">
                    ${parseFloat(item.price || 0).toFixed(2)}
                  </div>

                  <div className="item-quantity">
                    <button 
                      onClick={() => handleQuantityChange(item.id, item.quantity - 1)}
                      className="quantity-btn"
                      disabled={item.quantity <= 1}
                    >
                      -
                    </button>
                    <span className="quantity">{item.quantity}</span>
                    <button 
                      onClick={() => handleQuantityChange(item.id, item.quantity + 1)}
                      className="quantity-btn"
                    >
                      +
                    </button>
                  </div>

                  <div className="item-total">
                    ${(item.quantity * parseFloat(item.price || 0)).toFixed(2)}
                  </div>

                  <div className="item-actions">
                    <button 
                      onClick={() => handleRemoveItem(item.id,item.product_id)}
                      className="remove-btn"
                    >
                      🗑️
                    </button>
                  </div>
                </div>
                );
              })}

              <div className="cart-actions">
                <button onClick={handleClearCart} className="clear-cart-btn">
                  Xóa toàn bộ giỏ hàng
                </button>
                <Link to="/products" className="continue-shopping-link">
                  Tiếp tục mua sắm
                </Link>
              </div>
            </div>

            <div className="cart-summary">
              <h3>Tóm tắt đơn hàng</h3>
              
              <div className="summary-row">
                <span>Tạm tính:</span>
                <span>${total.toFixed(2)}</span>
              </div>
              
              <div className="summary-row">
                <span>Phí vận chuyển:</span>
                <span>Miễn phí</span>
              </div>
              
              <div className="summary-row total">
                <span>Tổng cộng:</span>
                <span>${total.toFixed(2)}</span>
              </div>

              <button 
                onClick={handleCheckout}
                className="checkout-btn"
                disabled={checkoutLoading || cartItems.length === 0}
              >
                {checkoutLoading ? 'Đang xử lý...' : 'Đặt hàng'}
              </button>

              <div className="payment-info">
                <p>💳 Thanh toán khi nhận hàng</p>
                <p>🚚 Giao hàng miễn phí</p>
                <p>↩️ Đổi trả trong 30 ngày</p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default CartPage;