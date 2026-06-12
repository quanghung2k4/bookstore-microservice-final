import { createContext, useContext, useState, useEffect } from 'react';
import { api } from '../api';
import { useAuth } from './AuthContext';

const CartContext = createContext();

export const useCart = () => {
  const context = useContext(CartContext);
  if (!context) {
    throw new Error('useCart must be used within a CartProvider');
  }
  return context;
};

export const CartProvider = ({ children }) => {
  const [cart, setCart] = useState(null);
  const [cartId, setCartId] = useState(null);
  const [loading, setLoading] = useState(false);
  const { user } = useAuth();

  useEffect(() => {
    const savedCartId = localStorage.getItem('cartId');
    if (savedCartId) {
      setCartId(savedCartId);
      loadCart(savedCartId);
    }
  }, []);

  useEffect(() => {
    if (user && !cartId) {
      createCart();
    }
  }, [user]);

  const createCart = async () => {
    if (!user) return null;
    
    try {
      setLoading(true);
      console.log('Creating cart for user:', user.id, user);
      const newCart = await api.createCart(user.id);
      console.log('Cart created:', newCart);
      setCart(newCart);
      setCartId(newCart.id);
      localStorage.setItem('cartId', newCart.id.toString());
      return newCart.id;
    } catch (error) {
      console.error('Failed to create cart:', error.message, error);
      return null;
    } finally {
      setLoading(false);
    }
  };

  const loadCart = async (id = cartId) => {
    if (!id) return;
    
    try {
      setLoading(true);
      const cartData = await api.getCart(id);
      setCart(cartData);
    } catch (error) {
      console.error('Failed to load cart:', error);
      // Cart not found — clear stale cartId and create a new one
      localStorage.removeItem('cartId');
      setCartId(null);
      setCart(null);
      if (user) {
        createCart();
      }
    } finally {
      setLoading(false);
    }
  };

  const addToCart = async (productId, quantity = 1) => {
    let activeCartId = cartId;
    if (!activeCartId) {
      activeCartId = await createCart();
      if (!activeCartId) throw new Error('Could not create cart');
    }
    
    try {
      await api.addToCart(activeCartId, productId, quantity);
      await loadCart(activeCartId);
      return true;
    } catch (error) {
      // If cart not found (404), create a new cart and retry once
      if (error.message?.includes('404') || error.message?.includes('Not found')) {
        localStorage.removeItem('cartId');
        setCartId(null);
        const newCartId = await createCart();
        if (!newCartId) throw new Error('Could not create cart');
        await api.addToCart(newCartId, productId, quantity);
        await loadCart(newCartId);
        return true;
      }
      console.error('Failed to add to cart:', error);
      throw error;
    }
  };

  const updateQuantity = async (itemId, quantity) => {
    try {
      await api.updateCartItem(itemId, quantity);
      await loadCart();
    } catch (error) {
      console.error('Failed to update quantity:', error);
      throw error;
    }
  };

  const removeItem = async (itemId) => {
    try {
      await api.removeCartItem(itemId);
      await loadCart();
    } catch (error) {
      console.error('Failed to remove item:', error);
      throw error;
    }
  };

  const clearCart = async () => {
    if (!cartId) return;
    
    try {
      await api.clearCart(cartId);
      await loadCart();
    } catch (error) {
      console.error('Failed to clear cart:', error);
      throw error;
    }
  };

  const checkout = async () => {
    if (!user || !cartId) return;
    
    try {
      const order = await api.checkout(user.id, cartId);
      await loadCart(); // Reload cart (should be empty after checkout)
      return order;
    } catch (error) {
      console.error('Checkout failed:', error);
      throw error;
    }
  };

  const getCartTotal = () => {
    if (!cart?.items) return 0;
    return cart.items.reduce((total, item) => {
      return total + (item.quantity * parseFloat(item.price || 0));
    }, 0);
  };

  const getCartItemCount = () => {
    if (!cart?.items) return 0;
    return cart.items.reduce((total, item) => total + item.quantity, 0);
  };

  const value = {
    cart,
    cartId,
    loading,
    addToCart,
    updateQuantity,
    removeItem,
    clearCart,
    checkout,
    loadCart,
    getCartTotal,
    getCartItemCount,
  };

  return (
    <CartContext.Provider value={value}>
      {children}
    </CartContext.Provider>
  );
};