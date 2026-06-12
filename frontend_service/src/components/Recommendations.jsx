import { useEffect, useState } from 'react';
import { api } from '../api';
import { useAuth } from '../context/AuthContext';
import ProductCard from './ProductCard';

export default function Recommendations({ strategy = 'hybrid', title = 'Gợi ý cho bạn', limit = 8 }) {
  const { user } = useAuth();
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!user?.id) {
      setProducts([]);
      setLoading(false);
      return;
    }

    setLoading(true);
    api.postRecommendations({ 
    userId: user.id,
    strategy: strategy, // Truyền thêm strategy để API map đúng logic
    limit: limit        // Truyền thêm limit để LSTM biết cần tạo bao nhiêu gợi ý
  })
      .then(async (data) => {
        const recs = data.recommendations || [];
        // Fetch full product details for each recommendation
        const details = await Promise.allSettled(
          recs.slice(0, limit).map(r => api.getProduct(r.product_id))
        );
        setProducts(details.filter(r => r.status === 'fulfilled').map(r => r.value));
      })
      .catch(() => setProducts([]))
      .finally(() => setLoading(false));
  }, [user?.id, strategy, limit]);

  if (loading) return <div className="recommendations-loading">Đang tải gợi ý...</div>;
  if (!products.length) return null;

  return (
    <section className="recommendations" aria-label={title}>
      <h2 className="recommendations-title">{title}</h2>
      <div className="products-grid">
        {products.map(p => <ProductCard key={p.id} product={p} />)}
      </div>
    </section>
  );
}
