import { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { api } from '../api';
import ProductCard from '../components/ProductCard';
import Loading from '../components/Loading';
import { getWishlist } from '../utils/wishlist';
import { useTrackEvent } from '../utils/useTrackEvent';


function getParam(searchParams, key) {
  const v = searchParams.get(key);
  return v == null ? '' : v;
}

const ProductsPage = () => {
  const [products, setProducts] = useState([]);
  const [visibleProducts, setVisibleProducts] = useState([]);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchParams, setSearchParams] = useSearchParams();
  const trackEvent = useTrackEvent();
  

  const [filters, setFilters] = useState({
    search: getParam(searchParams, 'search'),
    category: getParam(searchParams, 'category'),
    minPrice: getParam(searchParams, 'minPrice'),
    maxPrice: getParam(searchParams, 'maxPrice'),
    ordering: getParam(searchParams, 'ordering'),
    minRating: getParam(searchParams, 'minRating'),
    wishlist: getParam(searchParams, 'wishlist')
  });

  useEffect(() => {
    loadCategories();
  }, []);

  useEffect(() => {
    // Keep UI state in sync with URL (supports deep links from header search)
    setFilters({
      search: getParam(searchParams, 'search'),
      category: getParam(searchParams, 'category'),
      minPrice: getParam(searchParams, 'minPrice'),
      maxPrice: getParam(searchParams, 'maxPrice'),
      ordering: getParam(searchParams, 'ordering'),
      minRating: getParam(searchParams, 'minRating'),
      wishlist: getParam(searchParams, 'wishlist')
    });
    loadProducts();
  }, [searchParams]);

  useEffect(() => {
    // Apply client-side filters (wishlist, rating) after API fetch
    let next = [...products];

    if (filters.wishlist === '1') {
      const wished = new Set(getWishlist());
      next = next.filter(p => wished.has(Number(p.id)));
    }

    const minR = Number(filters.minRating);
    if (Number.isFinite(minR) && minR > 0) {
      next = next.filter(p => {
        const r = Number(p?.average_rating ?? p?.avg_rating ?? p?.rating ?? p?.rating_avg ?? 0);
        return Number.isFinite(r) ? r >= minR : false;
      });
    }

    setVisibleProducts(next);
  }, [products, filters.wishlist, filters.minRating]);

  const loadCategories = async () => {
    try {
      const response = await api.getCategories();
      setCategories(response.results || response || []);
    } catch (error) {
      console.error('Failed to load categories:', error);
    }
  };

  const loadProducts = async () => {
    try {
      setLoading(true);
      
      const params = new URLSearchParams();
      params.set('page_size', '100');
      // Build query directly from URL params for correctness
      const search = getParam(searchParams, 'search');
      const category = getParam(searchParams, 'category');
      const minPrice = getParam(searchParams, 'minPrice');
      const maxPrice = getParam(searchParams, 'maxPrice');
      const ordering = getParam(searchParams, 'ordering');
      if (search) params.set('search', search);
      if (category) params.set('category', category);
      if (minPrice) params.set('min_price', minPrice);
      if (maxPrice) params.set('max_price', maxPrice);
      if (ordering) params.set('ordering', ordering);

      const queryString = params.toString();
      const response = await api.getProducts(`?${queryString}`);

      if(response.results.length >0){
        trackEvent("search",response.results[0].id);
        console.log("search:",response.results[0].id);
      } else console.log("null");
      
      
      setProducts(response.results || []);
    } catch (error) {
      console.error('Failed to load products:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleFilterChange = (key, value) => {
    const current = {
      search: getParam(searchParams, 'search'),
      category: getParam(searchParams, 'category'),
      minPrice: getParam(searchParams, 'minPrice'),
      maxPrice: getParam(searchParams, 'maxPrice'),
      ordering: getParam(searchParams, 'ordering'),
      minRating: getParam(searchParams, 'minRating'),
      wishlist: getParam(searchParams, 'wishlist')
    };

    const next = { ...current, [key]: value };
    setFilters(next);

    const newParams = new URLSearchParams();
    Object.entries(next).forEach(([k, v]) => {
      if (v) newParams.set(k, v);
    });
    setSearchParams(newParams);
  };

  const clearFilters = () => {
    setFilters({
      search: '',
      category: '',
      minPrice: '',
      maxPrice: '',
      ordering: '',
      minRating: '',
      wishlist: ''
    });
    setSearchParams({});
  };

  return (
    <div className="products-page">
      <div className="container">
        <div className="page-header">
          <h1>{filters.wishlist === '1' ? 'Wishlist' : 'Sản phẩm'}</h1>
          <p>{filters.wishlist === '1' ? 'Các sản phẩm bạn đã lưu' : 'Khám phá bộ sưu tập sản phẩm đa dạng của chúng tôi'}</p>
        </div>

        <div className="products-layout">
          {/* Sidebar filters */}
          <aside className="filters-sidebar" aria-label="Bộ lọc">
            <details className="filters-mobile" open>
              <summary className="filters-mobile-summary">Bộ lọc & sắp xếp</summary>

              <div className="filters-block">
                <div className="filter-group">
                  <label className="filter-label">Tìm kiếm</label>
                  <input
                    type="text"
                    placeholder="Tên sản phẩm…"
                    value={filters.search}
                    onChange={(e) => handleFilterChange('search', e.target.value)}
                    className="search-input"
                  />
                </div>

                <div className="filter-group">
                  <label className="filter-label">Danh mục</label>
                  <select
                    value={filters.category}
                    onChange={(e) => handleFilterChange('category', e.target.value)}
                    className="filter-select"
                  >
                    <option value="">Tất cả</option>
                    {categories.map(category => (
                      <option key={category.id} value={category.slug}>
                        {category.name}
                      </option>
                    ))}
                  </select>
                </div>

                <div className="filter-row">
                  <div className="filter-group">
                    <label className="filter-label">Giá từ</label>
                    <input
                      type="number"
                      placeholder="Min"
                      value={filters.minPrice}
                      onChange={(e) => handleFilterChange('minPrice', e.target.value)}
                      className="price-input"
                    />
                  </div>
                  <div className="filter-group">
                    <label className="filter-label">Giá đến</label>
                    <input
                      type="number"
                      placeholder="Max"
                      value={filters.maxPrice}
                      onChange={(e) => handleFilterChange('maxPrice', e.target.value)}
                      className="price-input"
                    />
                  </div>
                </div>

                <div className="filter-group">
                  <label className="filter-label">Đánh giá</label>
                  <select
                    value={filters.minRating}
                    onChange={(e) => handleFilterChange('minRating', e.target.value)}
                    className="filter-select"
                  >
                    <option value="">Tất cả</option>
                    <option value="4">Từ 4★ trở lên</option>
                    <option value="3">Từ 3★ trở lên</option>
                    <option value="2">Từ 2★ trở lên</option>
                  </select>
                </div>

                <div className="filter-group">
                  <label className="filter-label">Sắp xếp</label>
                  <select
                    value={filters.ordering}
                    onChange={(e) => handleFilterChange('ordering', e.target.value)}
                    className="filter-select"
                  >
                    <option value="">Mặc định</option>
                    <option value="price">Giá tăng dần</option>
                    <option value="-price">Giá giảm dần</option>
                    <option value="name">Tên A-Z</option>
                    <option value="-name">Tên Z-A</option>
                    <option value="-created_at">Mới nhất</option>
                  </select>
                </div>

                <div className="filter-actions">
                  <button onClick={clearFilters} className="clear-filters-btn">
                    Xóa bộ lọc
                  </button>
                  <button
                    onClick={() => handleFilterChange('wishlist', filters.wishlist === '1' ? '' : '1')}
                    className="clear-filters-btn"
                  >
                    {filters.wishlist === '1' ? 'Xem tất cả' : 'Chỉ Wishlist'}
                  </button>
                </div>
              </div>
            </details>
          </aside>

          <div className="products-content">
            {loading ? (
              <Loading message="Đang tải sản phẩm..." />
            ) : (
              <div className="products-section">
                <div className="products-header">
                  <p>{visibleProducts.length} sản phẩm</p>
                </div>

                {visibleProducts.length > 0 ? (
                  <div className="products-grid">
                    {visibleProducts.map((product) => (
                      <ProductCard key={product.id} product={product} />
                    ))}
                  </div>
                ) : (
                  <div className="no-products">
                    <p>Không tìm thấy sản phẩm nào phù hợp với bộ lọc của bạn.</p>
                    <button onClick={clearFilters} className="clear-filters-btn">
                      Xóa bộ lọc
                    </button>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProductsPage;