import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const AdminLayout = ({ children }) => {
  const { user, logout } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();

  const handleLogout = () => { logout(); navigate('/login'); };

  const staffLinks = [
    { to: '/staff', label: 'Sản phẩm', icon: '📦' },
    { to: '/staff/orders', label: 'Đơn hàng', icon: '🧾' },
  ];

  const adminLinks = [
    { to: '/admin', label: 'Người dùng', icon: '👥' },
    { to: '/admin/products', label: 'Sản phẩm', icon: '📦' },
    { to: '/admin/orders', label: 'Đơn hàng', icon: '🧾' },
  ];

  const links = user?.role === 'admin' ? adminLinks : staffLinks;
  const title = user?.role === 'admin' ? 'Admin Panel' : 'Staff Panel';

  return (
    <div className="dashboard-layout">
      <aside className="dashboard-sidebar">
        <div className="sidebar-brand">
          <span className="brand-icon">{user?.role === 'admin' ? '⚙️' : '🛠️'}</span>
          <span className="brand-name">{title}</span>
        </div>

        <nav className="sidebar-nav">
          {links.map(link => (
            <Link
              key={link.to}
              to={link.to}
              className={`sidebar-link ${location.pathname === link.to ? 'active' : ''}`}
            >
              <span className="sidebar-icon">{link.icon}</span>
              <span>{link.label}</span>
            </Link>
          ))}
        </nav>

        <div className="sidebar-footer">
          <div className="sidebar-user">
            <div className="sidebar-avatar">{(user?.username || 'U')[0].toUpperCase()}</div>
            <div className="sidebar-user-info">
              <span className="sidebar-username">{user?.username}</span>
              <span className="sidebar-role">{user?.role}</span>
            </div>
          </div>
          <button className="sidebar-logout" onClick={handleLogout}>Đăng xuất</button>
        </div>
      </aside>

      <main className="dashboard-main">
        <div className="dashboard-content">
          {children}
        </div>
      </main>
    </div>
  );
};

export default AdminLayout;
