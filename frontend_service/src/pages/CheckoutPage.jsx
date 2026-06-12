import { useEffect, useMemo, useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { api } from '../api';
import { useAuth } from '../context/AuthContext';
import { useTrackEvent } from '../utils/useTrackEvent';


const CITIES = ['Hà Nội', 'TP. Hồ Chí Minh', 'Đà Nẵng', 'Hải Phòng', 'Cần Thơ', 'Biên Hòa', 'Nha Trang', 'Huế', 'Buôn Ma Thuột', 'Quy Nhơn', 'Vũng Tàu', 'Đà Lạt', 'Khác'];

const CheckoutPage = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const trackEvent = useTrackEvent();

  const orderId = location.state?.orderId;

  const [paymentMethod, setPaymentMethod] = useState('cod');

  const paymentLabel = useMemo(() => {
    switch (paymentMethod) {
      case 'card': return 'Thẻ (Visa/Mastercard)';
      case 'bank': return 'Chuyển khoản ngân hàng';
      case 'wallet': return 'Ví điện tử';
      default: return 'COD (Thanh toán khi nhận hàng)';
    }
  }, [paymentMethod]);

  const [form, setForm] = useState({
    full_name: [user?.first_name, user?.last_name].filter(Boolean).join(' ') || '',
    phone: user?.phone || '',
    address: '',
    city: '',
    note: '',
  });
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!orderId) navigate('/cart');
  }, [orderId, navigate]);

  if (!orderId) return null;

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSaving(true);
    try {
      const note = [form.note, `Payment: ${paymentLabel}`].filter(Boolean).join('\n');
      await api.createShipping({
        ...form,
        note,
        order_id: orderId,
        user_id: user.id,
      });
      

      navigate('/orders', { state: { success: true } });
    } catch (err) {
      setError(err.message || 'Không thể lưu thông tin giao hàng');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="checkout-page">
      <div className="container">
        <div className="checkout-wrapper">
          <div className="checkout-header">
            <div className="checkout-step done">✓ Cart</div>
            <div className="checkout-step-line done" />
            <div className="checkout-step active">1. Info</div>
            <div className="checkout-step-line" />
            <div className="checkout-step active">2. Payment</div>
            <div className="checkout-step-line" />
            <div className="checkout-step">3. Done</div>
          </div>

          <div className="checkout-card">
            <h2>Checkout</h2>
            <p className="checkout-subtitle">Đơn hàng #{orderId} đã được tạo. Vui lòng điền thông tin và chọn phương thức thanh toán.</p>

            {error && <div className="error-message">{error}</div>}

            <form onSubmit={handleSubmit} className="checkout-form">
              <div className="form-row-2">
                <div className="form-group">
                  <label>Họ và tên *</label>
                  <input
                    required
                    value={form.full_name}
                    onChange={e => setForm({ ...form, full_name: e.target.value })}
                    placeholder="Nguyễn Văn A"
                  />
                </div>
                <div className="form-group">
                  <label>Số điện thoại *</label>
                  <input
                    required
                    value={form.phone}
                    onChange={e => setForm({ ...form, phone: e.target.value })}
                    placeholder="0912 345 678"
                  />
                </div>
              </div>

              <div className="form-group">
                <label>Địa chỉ *</label>
                <input
                  required
                  value={form.address}
                  onChange={e => setForm({ ...form, address: e.target.value })}
                  placeholder="Số nhà, tên đường, phường/xã, quận/huyện"
                />
              </div>

              <div className="form-group">
                <label>Tỉnh / Thành phố *</label>
                <select required value={form.city} onChange={e => setForm({ ...form, city: e.target.value })}>
                  <option value="">-- Chọn tỉnh/thành --</option>
                  {CITIES.map(c => <option key={c} value={c}>{c}</option>)}
                </select>
              </div>

              <div className="form-group">
                <label>Ghi chú</label>
                <textarea
                  rows={3}
                  value={form.note}
                  onChange={e => setForm({ ...form, note: e.target.value })}
                  placeholder="Ghi chú cho người giao hàng (không bắt buộc)"
                />
              </div>

              <div className="checkout-section-title">Thanh toán</div>
              <div className="payment-options" role="radiogroup" aria-label="Phương thức thanh toán">
                <label className={`payment-option ${paymentMethod === 'cod' ? 'active' : ''}`}>
                  <input
                    type="radio"
                    name="paymentMethod"
                    value="cod"
                    checked={paymentMethod === 'cod'}
                    onChange={() => setPaymentMethod('cod')}
                  />
                  <div>
                    <div className="payment-title">COD</div>
                    <div className="payment-desc">Thanh toán khi nhận hàng</div>
                  </div>
                </label>

                <label className={`payment-option ${paymentMethod === 'card' ? 'active' : ''}`}>
                  <input
                    type="radio"
                    name="paymentMethod"
                    value="card"
                    checked={paymentMethod === 'card'}
                    onChange={() => setPaymentMethod('card')}
                  />
                  <div>
                    <div className="payment-title">Card</div>
                    <div className="payment-desc">Visa / Mastercard</div>
                  </div>
                </label>

                <label className={`payment-option ${paymentMethod === 'bank' ? 'active' : ''}`}>
                  <input
                    type="radio"
                    name="paymentMethod"
                    value="bank"
                    checked={paymentMethod === 'bank'}
                    onChange={() => setPaymentMethod('bank')}
                  />
                  <div>
                    <div className="payment-title">Bank</div>
                    <div className="payment-desc">Chuyển khoản ngân hàng</div>
                  </div>
                </label>

                <label className={`payment-option ${paymentMethod === 'wallet' ? 'active' : ''}`}>
                  <input
                    type="radio"
                    name="paymentMethod"
                    value="wallet"
                    checked={paymentMethod === 'wallet'}
                    onChange={() => setPaymentMethod('wallet')}
                  />
                  <div>
                    <div className="payment-title">Wallet</div>
                    <div className="payment-desc">Ví điện tử</div>
                  </div>
                </label>
              </div>

              <div className="trust-row" aria-label="Trust signals">
                <span className="trust-chip">🔒 Secure payment</span>
                <span className="trust-chip">✅ Verified checkout</span>
                <span className="trust-chip">↩️ 30-day returns</span>
              </div>

              <div className="checkout-info-box">
                <span>🚚</span>
                <span>Giao hàng tiêu chuẩn — Miễn phí — Dự kiến 3-5 ngày làm việc</span>
              </div>

              <button type="submit" className="checkout-submit-btn" disabled={saving}>
                {saving ? 'Đang xử lý...' : 'Xác nhận đặt hàng'}
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CheckoutPage;
