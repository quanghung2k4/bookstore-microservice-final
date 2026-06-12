import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { CartProvider } from './context/CartContext';
import Header from './components/Header';
import ProtectedRoute from './components/ProtectedRoute';
import AdminLayout from './components/AdminLayout';
import Chatbot from './components/Chatbot';
import HomePage from './pages/HomePage';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import ProductsPage from './pages/ProductsPage';
import ProductDetailPage from './pages/ProductDetailPage';
import CartPage from './pages/CartPage';
import OrdersPage from './pages/OrdersPage';
import StaffPage from './pages/StaffPage';
import AdminPage from './pages/AdminPage';
import CheckoutPage from './pages/CheckoutPage';
import './styles.css';

const CustomerLayout = ({ children }) => (
  <>
    <Header />
    <main>{children}</main>
  </>
);

function App() {
  return (
    <AuthProvider>
      <CartProvider>
        <Router>
          <div className="App">
            <Routes>
              <Route path="/" element={<CustomerLayout><HomePage /></CustomerLayout>} />
              <Route path="/login" element={<CustomerLayout><LoginPage /></CustomerLayout>} />
              <Route path="/register" element={<CustomerLayout><RegisterPage /></CustomerLayout>} />
              <Route path="/products" element={<CustomerLayout><ProductsPage /></CustomerLayout>} />
              <Route path="/products/:id" element={<CustomerLayout><ProductDetailPage /></CustomerLayout>} />
              <Route path="/cart" element={<CustomerLayout><CartPage /></CustomerLayout>} />
              <Route path="/orders" element={<CustomerLayout><OrdersPage /></CustomerLayout>} />
              <Route path="/checkout" element={<CustomerLayout><CheckoutPage /></CustomerLayout>} />

              <Route path="/staff" element={
                <ProtectedRoute roles={['admin', 'staff']}>
                  <AdminLayout><StaffPage tab="products" /></AdminLayout>
                </ProtectedRoute>
              } />
              <Route path="/staff/orders" element={
                <ProtectedRoute roles={['admin', 'staff']}>
                  <AdminLayout><StaffPage tab="orders" /></AdminLayout>
                </ProtectedRoute>
              } />

              <Route path="/admin" element={
                <ProtectedRoute roles={['admin']}>
                  <AdminLayout><AdminPage tab="users" /></AdminLayout>
                </ProtectedRoute>
              } />
              <Route path="/admin/products" element={
                <ProtectedRoute roles={['admin']}>
                  <AdminLayout><StaffPage tab="products" /></AdminLayout>
                </ProtectedRoute>
              } />
              <Route path="/admin/orders" element={
                <ProtectedRoute roles={['admin']}>
                  <AdminLayout><StaffPage tab="orders" /></AdminLayout>
                </ProtectedRoute>
              } />
            </Routes>
            <Chatbot />
          </div>
        </Router>
      </CartProvider>
    </AuthProvider>
  );
}

export default App;
