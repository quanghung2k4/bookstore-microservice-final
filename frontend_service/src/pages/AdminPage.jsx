import { useState, useEffect } from 'react';
import { api } from '../api';
import Loading from '../components/Loading';

const AdminPage = () => {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => { loadUsers(); }, []);

  const loadUsers = async () => {
    setLoading(true);
    try {
      const res = await api.getUsers();
      setUsers(res.results || res || []);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  const handleRoleChange = async (user, role) => {
    try {
      await api.updateUser(user.id, { role });
      setUsers(prev => prev.map(u => u.id === user.id ? { ...u, role } : u));
    } catch (e) {
      alert('Lỗi: ' + e.message);
    }
  };

  const handleToggleActive = async (user) => {
    try {
      await api.updateUser(user.id, { is_active: !user.is_active });
      setUsers(prev => prev.map(u => u.id === user.id ? { ...u, is_active: !u.is_active } : u));
    } catch (e) {
      alert('Lỗi: ' + e.message);
    }
  };

  const handleDeleteUser = async (id) => {
    if (!confirm('Xóa user này?')) return;
    try {
      await api.deleteUser(id);
      setUsers(prev => prev.filter(u => u.id !== id));
    } catch (e) {
      alert('Lỗi: ' + e.message);
    }
  };

  return (
    <div className="dash-section">
      <h2 className="dash-title">Quản lý người dùng</h2>

      {loading ? <Loading /> : (
        <div className="admin-section">
          {error && <div className="error-message">{error}</div>}
          <div className="section-toolbar">
            <span>{users.length} người dùng</span>
          </div>
          <div className="admin-table-wrap">
            <table className="admin-table">
              <thead>
                <tr><th>ID</th><th>Username</th><th>Email</th><th>Họ tên</th><th>Role</th><th>Trạng thái</th><th>Thao tác</th></tr>
              </thead>
              <tbody>
                {users.map(u => (
                  <tr key={u.id}>
                    <td>{u.id}</td>
                    <td>{u.username}</td>
                    <td>{u.email}</td>
                    <td>{[u.first_name, u.last_name].filter(Boolean).join(' ') || '—'}</td>
                    <td>
                      <select value={u.role} onChange={e => handleRoleChange(u, e.target.value)} className="role-select">
                        <option value="customer">Customer</option>
                        <option value="staff">Staff</option>
                        <option value="admin">Admin</option>
                      </select>
                    </td>
                    <td>
                      <span className={`badge ${u.is_active ? 'badge-green' : 'badge-red'}`}>
                        {u.is_active ? 'Hoạt động' : 'Bị khóa'}
                      </span>
                    </td>
                    <td className="table-actions">
                      <button className="btn-edit" onClick={() => handleToggleActive(u)}>
                        {u.is_active ? 'Khóa' : 'Mở khóa'}
                      </button>
                      <button className="btn-delete" onClick={() => handleDeleteUser(u.id)}>Xóa</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};

export default AdminPage;
