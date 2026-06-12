import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { api } from '../api';
import Loading from '../components/Loading';

const STATUS_COLOR = { pending: 'status-pending', confirmed: 'status-confirmed', shipped: 'status-shipped', delivered: 'status-delivered', cancelled: 'status-cancelled', paid: 'status-confirmed' };
const STATUS_TEXT = { pending: 'Chờ xử lý', confirmed: 'Đã xác nhận', shipped: 'Đang giao', delivered: 'Đã giao', cancelled: 'Đã hủy', paid: 'Đã thanh toán' };

const OrdersPage = () => {
  const { user } = useAuth();
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selected, setSelected] = useState(null);

  useEffect(() => { if (user) loadOrders(); }, [user]);

  const loadOrders = async () => {
    try {
      setLoading(true);
      const response = await api.getOrders();
      const all = response.results || response || [];
      setOrders(all.filter(o => o.user_id === user.id));
    } catch (error) {
      console.error('Failed to load orders:', error);
    } finally {
      setLoading(false);
    }
  };

  if (!user) return (
    <div className="container">
      <div className="auth-required">
        <h2>Vui lòng đăng nhập</h2>
        <Link to="/login" className="login-btn">Đăng nhập</Link>
      </div>
    </div>
  );

  if (loading) return <Loading message="Đang tải đơn hàng..." />;

  return (
    <div className="orders-page">
      <div className="container">
        <div className="page-header">
          <h1>Đơn hàng của bạn</h1>
        </div>

        {orders.length === 0 ? (
          <div className="empty-orders">
            <div className="empty-orders-icon">📦</div>
            <h2>Chưa có đơn hàng nào</h2>
            <p>Hãy bắt đầu mua sắm!</p>
            <Link to="/products" className="continue-shopping-btn">Mua sắm ngay</Link>
          </div>
        ) : (
          <div className="orders-list">
            {orders.map(order => (
              <div key={order.id} className="order-card">
                <div className="order-header">
                  <div className="order-info">
                    <h3 className="order-id">Đơn hàng #{order.id}</h3>
                    <p className="order-date">{new Date(order.created_at).toLocaleDateString('vi-VN', { year: 'numeric', month: 'long', day: 'numeric' })}</p>
                  </div>
                  <span className={`status-badge ${STATUS_COLOR[order.status] || 'status-pending'}`}>
                    {STATUS_TEXT[order.status] || order.status}
                  </span>
                </div>

                {/* Items preview */}
                <div className="order-items-preview">
                  {(order.items || []).slice(0, 3).map(item => (
                    <div key={item.id} className="order-item-preview">
                      <span className="item-name">{item.product_name}</span>
                      <span className="item-qty-price">×{item.quantity} — <strong>${parseFloat(item.unit_price).toFixed(2)}</strong></span>
                    </div>
                  ))}
                  {(order.items || []).length > 3 && (
                    <p className="more-items">+{order.items.length - 3} sản phẩm khác</p>
                  )}
                </div>

                <div className="order-footer">
                  <div className="order-total">
                    Tổng cộng: <strong>${parseFloat(order.total_price).toFixed(2)}</strong>
                  </div>
                  <button className="view-details-btn" onClick={() => setSelected(order)}>
                    Xem chi tiết
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Detail Modal */}
      {selected && (
        <div className="modal-overlay" onClick={() => setSelected(null)}>
          <div className="modal order-detail-modal" onClick={e => e.stopPropagation()}>
            <div className="order-detail-header">
              <div>
                <h3>Đơn hàng #{selected.id}</h3>
                <p className="order-date">{new Date(selected.created_at).toLocaleDateString('vi-VN', { year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit' })}</p>
              </div>
              <span className={`status-badge ${STATUS_COLOR[selected.status] || 'status-pending'}`}>
                {STATUS_TEXT[selected.status] || selected.status}
              </span>
            </div>

            <div className="order-detail-items">
              <h4>Sản phẩm đã đặt</h4>
              <table className="order-items-table">
                <thead>
                  <tr><th>Sản phẩm</th><th>Đơn giá</th><th>Số lượng</th><th>Thành tiền</th></tr>
                </thead>
                <tbody>
                  {(selected.items || []).map(item => (
                    <tr key={item.id}>
                      <td>{item.product_name}</td>
                      <td>${parseFloat(item.unit_price).toFixed(2)}</td>
                      <td>{item.quantity}</td>
                      <td><strong>${(item.quantity * parseFloat(item.unit_price)).toFixed(2)}</strong></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <div className="order-detail-summary">
              <div className="summary-row">
                <span>Tổng tiền hàng</span>
                <span>${parseFloat(selected.total_price).toFixed(2)}</span>
              </div>
              <div className="summary-row">
                <span>Phí vận chuyển</span>
                <span>Miễn phí</span>
              </div>
              <div className="summary-row total">
                <span>Tổng thanh toán</span>
                <span>${parseFloat(selected.total_price).toFixed(2)}</span>
              </div>
              {selected.payment_reference && (
                <div className="summary-row">
                  <span>Mã thanh toán</span>
                  <span className="payment-ref-text">{selected.payment_reference}</span>
                </div>
              )}
            </div>

            <div className="form-actions">
              <button className="btn-secondary" onClick={() => setSelected(null)}>Đóng</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default OrdersPage;
