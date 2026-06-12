import { useState, useEffect } from 'react';
import { api } from '../api';
import Loading from '../components/Loading';

const EMPTY_PRODUCT = { name: '', sku: '', description: '', price: '', stock: '', image: '', category: '', brand: '', product_type: '', is_active: true };

const StaffPage = ({ tab: initialTab }) => {
  const [tab, setTab] = useState(initialTab || 'products');
  const [products, setProducts] = useState([]);
  const [categories, setCategories] = useState([]);
  const [brands, setBrands] = useState([]);
  const [productTypes, setProductTypes] = useState([]);
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editProduct, setEditProduct] = useState(null);
  const [form, setForm] = useState(EMPTY_PRODUCT);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => { loadData(); }, [tab]);

  const fetchAllPages = async (path) => {
    const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/gateway';
    const token = localStorage.getItem('token');
    const headers = { 'Content-Type': 'application/json', ...(token && { Authorization: `Bearer ${token}` }) };
    let results = [];
    let page = 1;
    while (true) {
      const sep = path.includes('?') ? '&' : '?';
      const res = await fetch(`${API_BASE}${path}${sep}page=${page}&page_size=100`, { headers });
      const data = await res.json();
      results = results.concat(data.results || []);
      if (!data.next) break;
      page++;
    }
    return results;
  };

  const loadData = async () => {
    setLoading(true);
    try {
      if (tab === 'products') {
        const [allProducts, c, b, pt] = await Promise.all([
          fetchAllPages('/products/products/'),
          api.getCategories(),
          api.getBrands(),
          api.getProductTypes()
        ]);
        setProducts(allProducts);
        setCategories(c.results || c || []);
        setBrands(b.results || b || []);
        setProductTypes(pt.results || pt || []);
      } else {
        const o = await api.getOrders();
        setOrders(o.results || o || []);
      }
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  const openCreate = () => { setEditProduct(null); setForm(EMPTY_PRODUCT); setShowForm(true); setError(''); };
  const openEdit = (p) => { setEditProduct(p); setForm({ name: p.name, sku: p.sku, description: p.description || '', price: p.price, stock: p.stock, image: p.image || '', category: p.category, brand: p.brand || '', product_type: p.product_type || '', is_active: p.is_active }); setShowForm(true); setError(''); };

  const handleSave = async (e) => {
    e.preventDefault();
    setSaving(true);
    setError('');
    try {
      const payload = { ...form, price: parseFloat(form.price), stock: parseInt(form.stock), brand: form.brand || null, product_type: form.product_type || null };
      if (editProduct) await api.updateProduct(editProduct.id, payload);
      else await api.createProduct(payload);
      setShowForm(false);
      loadData();
    } catch (e) {
      setError(e.message);
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (id) => {
    if (!confirm('Xóa sản phẩm này?')) return;
    try {
      await api.deleteProduct(id);
      loadData();
    } catch (e) {
      alert('Lỗi: ' + e.message);
    }
  };

  return (
    <div className="dash-section">
      <h2 className="dash-title">{tab === 'products' ? 'Quản lý sản phẩm' : 'Quản lý đơn hàng'}</h2>

        {loading ? <Loading /> : (
          <>
            {tab === 'products' && (
              <div className="admin-section">
                <div className="section-toolbar">
                  <span>{products.length} sản phẩm</span>
                  <button className="btn-primary" onClick={openCreate}>+ Thêm sản phẩm</button>
                </div>

                {showForm && (
                  <div className="modal-overlay" onClick={() => setShowForm(false)}>
                    <div className="modal" onClick={e => e.stopPropagation()}>
                      <h3>{editProduct ? 'Sửa sản phẩm' : 'Thêm sản phẩm'}</h3>
                      {error && <div className="error-message">{error}</div>}
                      <form onSubmit={handleSave} className="admin-form">
                        <div className="form-row">
                          <div className="form-group">
                            <label>Tên sản phẩm *</label>
                            <input required value={form.name} onChange={e => setForm({...form, name: e.target.value})} />
                          </div>
                          <div className="form-group">
                            <label>SKU *</label>
                            <input required value={form.sku} onChange={e => setForm({...form, sku: e.target.value})} />
                          </div>
                        </div>
                        <div className="form-row">
                          <div className="form-group">
                            <label>Giá *</label>
                            <input required type="number" step="0.01" value={form.price} onChange={e => setForm({...form, price: e.target.value})} />
                          </div>
                          <div className="form-group">
                            <label>Tồn kho *</label>
                            <input required type="number" value={form.stock} onChange={e => setForm({...form, stock: e.target.value})} />
                          </div>
                        </div>
                        <div className="form-row">
                          <div className="form-group">
                            <label>Danh mục *</label>
                            <select required value={form.category} onChange={e => setForm({...form, category: e.target.value})}>
                              <option value="">-- Chọn danh mục --</option>
                              {categories.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
                            </select>
                          </div>
                          <div className="form-group">
                            <label>Thương hiệu</label>
                            <select value={form.brand} onChange={e => setForm({...form, brand: e.target.value})}>
                              <option value="">-- Không có --</option>
                              {brands.map(b => <option key={b.id} value={b.id}>{b.name}</option>)}
                            </select>
                          </div>
                        </div>
                        <div className="form-row">
                          <div className="form-group">
                            <label>Loại sản phẩm *</label>
                            <select required value={form.product_type} onChange={e => setForm({...form, product_type: e.target.value})}>
                              <option value="">-- Chọn loại --</option>
                              {productTypes.map(pt => <option key={pt.id} value={pt.id}>{pt.name}</option>)}
                            </select>
                          </div>
                        </div>
                        <div className="form-group">
                          <label>Mô tả</label>
                          <textarea rows={3} value={form.description} onChange={e => setForm({...form, description: e.target.value})} />
                        </div>
                        <div className="form-group">
                          <label>URL hình ảnh</label>
                          <input value={form.image} onChange={e => setForm({...form, image: e.target.value})} placeholder="https://..." />
                        </div>
                        <div className="form-group checkbox-group">
                          <label><input type="checkbox" checked={form.is_active} onChange={e => setForm({...form, is_active: e.target.checked})} /> Đang bán</label>
                        </div>
                        <div className="form-actions">
                          <button type="button" className="btn-secondary" onClick={() => setShowForm(false)}>Hủy</button>
                          <button type="submit" className="btn-primary" disabled={saving}>{saving ? 'Đang lưu...' : 'Lưu'}</button>
                        </div>
                      </form>
                    </div>
                  </div>
                )}

                <div className="admin-table-wrap">
                  <table className="admin-table">
                    <thead>
                      <tr><th>Ảnh</th><th>Tên</th><th>SKU</th><th>Danh mục</th><th>Giá</th><th>Tồn kho</th><th>Trạng thái</th><th>Thao tác</th></tr>
                    </thead>
                    <tbody>
                      {products.map(p => (
                        <tr key={p.id}>
                          <td><img src={p.image || 'https://placehold.co/48x48?text=SP'} alt={p.name} className="table-thumb" /></td>
                          <td>{p.name}</td>
                          <td>{p.sku}</td>
                          <td>{p.category_detail?.name}</td>
                          <td>${p.price}</td>
                          <td>{p.stock}</td>
                          <td><span className={`badge ${p.is_active ? 'badge-green' : 'badge-gray'}`}>{p.is_active ? 'Đang bán' : 'Ẩn'}</span></td>
                          <td className="table-actions">
                            <button className="btn-edit" onClick={() => openEdit(p)}>Sửa</button>
                            <button className="btn-delete" onClick={() => handleDelete(p.id)}>Xóa</button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            {tab === 'orders' && (
              <div className="admin-section">
                <div className="section-toolbar"><span>{orders.length} đơn hàng</span></div>
                <div className="admin-table-wrap">
                  <table className="admin-table">
                    <thead>
                      <tr><th>ID</th><th>User ID</th><th>Sản phẩm</th><th>Tổng tiền</th><th>Thanh toán</th><th>Trạng thái</th><th>Ngày tạo</th></tr>
                    </thead>
                    <tbody>
                      {orders.map(o => (
                        <tr key={o.id}>
                          <td>#{o.id}</td>
                          <td>{o.user_id}</td>
                          <td>
                            <div className="order-items-cell">
                              {(o.items || []).map(item => (
                                <div key={item.id} className="order-item-row">
                                  <span className="order-item-name">{item.product_name}</span>
                                  <span className="order-item-qty">×{item.quantity} — ${parseFloat(item.unit_price).toFixed(2)}</span>
                                </div>
                              ))}
                            </div>
                          </td>
                          <td><strong>${parseFloat(o.total_price || 0).toFixed(2)}</strong></td>
                          <td>
                            {o.payment_reference
                              ? <span className="payment-ref">{o.payment_reference}</span>
                              : <span className="text-muted">—</span>}
                          </td>
                          <td><span className={`badge badge-${statusColor(o.status)}`}>{statusLabel(o.status)}</span></td>
                          <td>{new Date(o.created_at).toLocaleDateString('vi-VN')}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </>
        )}
    </div>
  );
};

const statusColor = (s) => ({ pending: 'yellow', confirmed: 'blue', shipped: 'purple', delivered: 'green', cancelled: 'red', paid: 'green' }[s] || 'gray');
const statusLabel = (s) => ({ pending: 'Chờ xử lý', confirmed: 'Đã xác nhận', shipped: 'Đang giao', delivered: 'Đã giao', cancelled: 'Đã hủy', paid: 'Đã thanh toán' }[s] || s);

export default StaffPage;
