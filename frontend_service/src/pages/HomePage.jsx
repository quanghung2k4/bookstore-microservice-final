import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../api';
import ProductCard from '../components/ProductCard';
import Recommendations from '../components/Recommendations';
import Loading from '../components/Loading';
import { useAuth } from '../context/AuthContext';

const HomePage = () => {
  const { user, loading: authLoading } = useAuth();
  const [featuredProducts, setFeaturedProducts] = useState([]);
  const [categories, setCategories] = useState([]);
  const [categoryImages, setCategoryImages] = useState({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (authLoading) return;
    loadData();
    // Reload when user changes so recommendations can reflect history.
  }, [authLoading, user?.id]);

  const loadData = async () => {
    try {
      setLoading(true);
      const [recsRes, categoriesRes] = await Promise.all([
        api.getRecommendations({ userId: user?.id, limit: 10, strategy: 'hybrid' }),
        api.getCategories(),
      ]);

      const recs = recsRes?.recommendations || [];
      const details = await Promise.allSettled(
        recs.slice(0, 8).map((r) => api.getProduct(r.product_id))
      );

      const featured = details
        .filter((r) => r.status === 'fulfilled')
        .map((r) => r.value);

      const cats = categoriesRes.results || categoriesRes || [];

      setFeaturedProducts(featured);
      setCategories(cats);

      const imageBySlug = {};
      for (const category of cats) {
        const match = featured.find((p) => {
          const detail = p?.category_detail;
          if (!detail) return false;
          return (
            (detail?.id != null && category?.id != null && String(detail.id) === String(category.id)) ||
            (detail?.slug && category?.slug && String(detail.slug) === String(category.slug)) ||
            (detail?.name && category?.name && String(detail.name) === String(category.name))
          );
        });

        if (match?.image && category?.slug) {
          imageBySlug[category.slug] = match.image;
        }
      }
      setCategoryImages(imageBySlug);
    } catch (error) {
      console.error('Failed to load data:', error);

      // Safety fallback: if AI service is down, show newest products
      try {
        const productsRes = await api.getProducts('?ordering=-created_at&page_size=8');
        const products = productsRes.results || [];
        setFeaturedProducts(products.slice(0, 8));
      } catch {
        setFeaturedProducts([]);
      }
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <Loading message="Đang tải trang chủ..." />;
  }

  return (
    <div className="home-page">
      {/* Hero Section */}
      <section className="hero">
        <div className="container">
          <div className="hero-inner">
            <div className="hero-content">
              <p className="hero-eyebrow">Premium essentials, everyday value</p>
              <h1>Mua sắm tối giản. Trải nghiệm tối đa.</h1>
              <p>Giao diện sạch, tìm kiếm thông minh, thanh toán nhanh — tối ưu cho cả mobile lẫn desktop.</p>
              <div className="hero-cta-row">
                <Link to="/products" className="cta-button">Shop Now</Link>
                <Link to="/products" className="cta-button secondary">Explore</Link>
              </div>
              <div className="hero-trust">
                <span className="trust-chip">🔒 Secure checkout</span>
                <span className="trust-chip">🚚 Fast delivery</span>
                <span className="trust-chip">↩️ Easy returns</span>
              </div>
            </div>  
          </div>
        </div>
      </section>
      {/* AI Recommendations */}
      <section className="recommendations-section">
        <div className="container">
          <Recommendations title="Gợi ý" strategy="hybrid" limit={8} />
        </div>
      </section>

      {/* Featured Products Section */}
      <section className="featured-products">
        <div className="container">
          <div className="section-header">
            <h2>Nổi bật</h2>
            <Link to="/products" className="view-all-link">
              Xem tất cả →
            </Link>
          </div>
          
          <div className="products-grid">
            {featuredProducts.map(product => (
              <ProductCard key={product.id} product={product} />
            ))}
          </div>
        </div>
      </section>

      

      {/* Categories Section */}
      <section className="categories-section">
        <div className="container">
          <div className="section-header">
            <h2>Danh mục</h2>
            <Link to="/products" className="view-all-link">Xem tất cả →</Link>
          </div>

          <div className="categories-grid" aria-label="Danh mục sản phẩm">
            {categories.map(category => {
              const image = categoryImages[category.slug];
              return (
                <Link
                  key={category.id}
                  to={`/products?category=${category.slug}`}
                  className="category-card"
                >
                  <div className="category-image">
                    {image ? (
                      <img src={image} alt={category.name} loading="lazy" />
                    ) : (
                      <div className="category-image-placeholder" aria-hidden="true">
                        {category.name?.charAt(0)?.toUpperCase() || '#'}
                      </div>
                    )}
                  </div>
                  <h3>{category.name}</h3>
                </Link>
              );
            })}
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="features">
        <div className="container">
          <div className="features-grid">
            <div className="feature">
              <div className="feature-icon">🚚</div>
              <h3>Giao hàng miễn phí</h3>
              <p>Miễn phí giao hàng cho đơn hàng trên $50</p>
            </div>
            <div className="feature">
              <div className="feature-icon">🔒</div>
              <h3>Thanh toán an toàn</h3>
              <p>Bảo mật thông tin thanh toán 100%</p>
            </div>
            <div className="feature">
              <div className="feature-icon">↩️</div>
              <h3>Đổi trả dễ dàng</h3>
              <p>Đổi trả trong vòng 30 ngày</p>
            </div>
            <div className="feature">
              <div className="feature-icon">📞</div>
              <h3>Hỗ trợ 24/7</h3>
              <p>Hỗ trợ khách hàng mọi lúc mọi nơi</p>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};

export default HomePage;