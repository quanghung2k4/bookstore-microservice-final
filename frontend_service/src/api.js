const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/gateway";

async function request(path, options = {}) {
  const token = localStorage.getItem("token");

  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...(token && { Authorization: `Bearer ${token}` }),
      ...(options.headers || {}),
    },
    ...options,
  });

  const text = await response.text();
  const data = text ? JSON.parse(text) : null;

  if (!response.ok) {
    throw new Error(
      data?.detail || data?.message || JSON.stringify(data) || "Request failed",
    );
  }

  return data;
}

export const api = {
  // Auth
  login(credentials) {
    return request("/users/users/login/", {
      method: "POST",
      body: JSON.stringify(credentials),
    });
  },

  register(userData) {
    return request("/users/users/", {
      method: "POST",
      body: JSON.stringify(userData),
    });
  },

  // Products
  getProducts(params = "") {
    return request(`/products/products/${params}`);
  },

  getProduct(id) {
    return request(`/products/products/${id}/`);
  },

  getCategories() {
    return request("/products/categories/?page_size=100");
  },

  getBrands() {
    return request("/products/brands/?page_size=100");
  },

  getProductTypes() {
    return request("/products/product-types/?page_size=100");
  },

  // Cart
  createCart(userId) {
    return request("/carts/carts/", {
      method: "POST",
      body: JSON.stringify({ user_id: userId }),
    });
  },

  getCart(cartId) {
    return request(`/carts/carts/${cartId}/summary/`);
  },

  addToCart(cartId, productId, quantity = 1) {
    return request(`/carts/carts/${cartId}/items/`, {
      method: "POST",
      body: JSON.stringify({ product_id: productId, quantity }),
    });
  },

  updateCartItem(itemId, quantity) {
    return request(`/carts/cart-items/${itemId}/`, {
      method: "PATCH",
      body: JSON.stringify({ quantity }),
    });
  },

  removeCartItem(itemId) {
    return request(`/carts/cart-items/${itemId}/`, {
      method: "DELETE",
    });
  },

  clearCart(cartId) {
    return request(`/carts/carts/${cartId}/clear/`, {
      method: "POST",
    });
  },

  // Orders
  checkout(userId, cartId) {
    return request("/orders/orders/checkout/", {
      method: "POST",
      body: JSON.stringify({ user_id: userId, cart_id: cartId }),
    });
  },

  getOrders() {
    return request("/orders/orders/");
  },

  // Admin - Products
  createProduct(data) {
    return request("/products/products/", {
      method: "POST",
      body: JSON.stringify(data),
    });
  },

  updateProduct(id, data) {
    return request(`/products/products/${id}/`, {
      method: "PUT",
      body: JSON.stringify(data),
    });
  },

  deleteProduct(id) {
    return request(`/products/products/${id}/`, { method: "DELETE" });
  },

  createCategory(data) {
    return request("/products/categories/", {
      method: "POST",
      body: JSON.stringify(data),
    });
  },

  // Admin - Users
  getUsers() {
    return request("/users/users/");
  },

  updateUser(id, data) {
    return request(`/users/users/${id}/`, {
      method: "PATCH",
      body: JSON.stringify(data),
    });
  },

  deleteUser(id) {
    return request(`/users/users/${id}/`, { method: "DELETE" });
  },

  // Shipping
  createShipping(data) {
    return request("/shipping/shipping/", {
      method: "POST",
      body: JSON.stringify(data),
    });
  },

  getShipping(params = "") {
    return request(`/shipping/shipping/${params}`);
  },

  // Payments
  getPayments() {
    return request("/payments/payments/");
  },

  // AI Service
  trackEvent(data) {
    return request("/ai/events/", {
      method: "POST",
      body: JSON.stringify(data),
    });
  },

  getRecommendations(userId, strategy = "hybrid", limit = 10) {
    return request(
      `/ai/recommendations/?user_id=${userId}&strategy=${strategy}&limit=${limit}`,
    );
  },

  postRecommendations({
    userId,
    events = [],
    strategy = "hybrid",
    limit = 10,
  } = {}) {
    return request("/ai/recommendations/", {
      method: "POST",
      body: JSON.stringify({
        user_id: userId,
        events,
        strategy,
        limit,
      }),
    });
  },

  aiSearch(query, userId) {
    const params = userId
      ? `?q=${encodeURIComponent(query)}&user_id=${userId}`
      : `?q=${encodeURIComponent(query)}`;
    return request(`/ai/search/${params}`);
  },

  chat(message, userId, history = []) {
    return request("/ai/chat/", {
      method: "POST",
      body: JSON.stringify({ message, user_id: userId, history }),
    });
  },
};
