import { useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { api } from '../api';

const LoginPage = () => {
  const [formData, setFormData] = useState({
    username: '',
    password: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const from = location.state?.from?.pathname || '/';

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
    setError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!formData.username || !formData.password) {
      setError('Vui lòng điền đầy đủ thông tin');
      return;
    }

    try {
      setLoading(true);
      setError('');
      
      const response = await api.login(formData);
      const userData = response.user || response;
      login(userData, response.token || 'dummy-token');

      // Redirect theo role
      if (userData.role === 'admin') navigate('/admin', { replace: true });
      else if (userData.role === 'staff') navigate('/staff', { replace: true });
      else navigate(from, { replace: true });
    } catch (error) {
      setError(error.message || 'Đăng nhập thất bại');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page">
      <div className="container">
        <div className="auth-form-container">
          <div className="auth-form">
            <h2>Đăng nhập</h2>
            <p className="auth-subtitle">Chào mừng trở lại!</p>
            
            {error && (
              <div className="error-message">
                {error}
              </div>
            )}

            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label htmlFor="username">Tên đăng nhập</label>
                <input
                  type="text"
                  id="username"
                  name="username"
                  value={formData.username}
                  onChange={handleChange}
                  placeholder="Nhập tên đăng nhập"
                  required
                />
              </div>

              <div className="form-group">
                <label htmlFor="password">Mật khẩu</label>
                <input
                  type="password"
                  id="password"
                  name="password"
                  value={formData.password}
                  onChange={handleChange}
                  placeholder="Nhập mật khẩu"
                  required
                />
              </div>

              <button 
                type="submit" 
                className="submit-btn"
                disabled={loading}
              >
                {loading ? 'Đang đăng nhập...' : 'Đăng nhập'}
              </button>
            </form>

            <div className="auth-links">
              <p>
                Chưa có tài khoản? 
                <Link to="/register" state={{ from: location.state?.from }}>
                  Đăng ký ngay
                </Link>
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;