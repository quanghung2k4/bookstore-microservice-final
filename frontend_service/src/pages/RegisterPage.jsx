import { useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { api } from '../api';

const RegisterPage = () => {
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: '',
    first_name: '',
    role: 'customer'
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
    
    // Validation
    if (!formData.username || !formData.email || !formData.password) {
      setError('Vui lòng điền đầy đủ thông tin bắt buộc');
      return;
    }

    if (formData.password !== formData.confirmPassword) {
      setError('Mật khẩu xác nhận không khớp');
      return;
    }

    if (formData.password.length < 6) {
      setError('Mật khẩu phải có ít nhất 6 ký tự');
      return;
    }

    try {
      setLoading(true);
      setError('');
      
      const { confirmPassword, ...registerData } = formData;
      const response = await api.register(registerData);
      
      // Auto login after successful registration
      login(response, 'dummy-token');
      
      navigate(from, { replace: true });
    } catch (error) {
      setError(error.message || 'Đăng ký thất bại');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page">
      <div className="container">
        <div className="auth-form-container">
          <div className="auth-form">
            <h2>Đăng ký tài khoản</h2>
            
            {error && (
              <div className="error-message">
                {error}
              </div>
            )}

            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label htmlFor="username">Tên đăng nhập *</label>
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
                <label htmlFor="email">Email *</label>
                <input
                  type="email"
                  id="email"
                  name="email"
                  value={formData.email}
                  onChange={handleChange}
                  placeholder="Nhập địa chỉ email"
                  required
                />
              </div>

              <div className="form-group">
                <label htmlFor="first_name">Họ và tên</label>
                <input
                  type="text"
                  id="first_name"
                  name="first_name"
                  value={formData.first_name}
                  onChange={handleChange}
                  placeholder="Nhập họ và tên"
                />
              </div>

              <div className="form-group">
                <label htmlFor="password">Mật khẩu *</label>
                <input
                  type="password"
                  id="password"
                  name="password"
                  value={formData.password}
                  onChange={handleChange}
                  placeholder="Nhập mật khẩu (ít nhất 6 ký tự)"
                  required
                />
              </div>

              <div className="form-group">
                <label htmlFor="confirmPassword">Xác nhận mật khẩu *</label>
                <input
                  type="password"
                  id="confirmPassword"
                  name="confirmPassword"
                  value={formData.confirmPassword}
                  onChange={handleChange}
                  placeholder="Nhập lại mật khẩu"
                  required
                />
              </div>

              <button 
                type="submit" 
                className="submit-btn"
                disabled={loading}
              >
                {loading ? 'Đang đăng ký...' : 'Đăng ký'}
              </button>
            </form>

            <div className="auth-links">
              <p>
                Đã có tài khoản? 
                <Link to="/login" state={{ from: location.state?.from }}>
                  Đăng nhập ngay
                </Link>
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RegisterPage;