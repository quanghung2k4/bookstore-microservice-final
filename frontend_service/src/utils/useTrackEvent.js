import { useCallback } from 'react';
import { api } from '../api';
import { useAuth } from '../context/AuthContext';

/**
 * Returns a trackEvent(action, productId, extra) function.
 * Silently fires-and-forgets — never blocks UI.
 */
export function useTrackEvent() {
  const { user } = useAuth();

  return useCallback((action, productId, extra = {}) => {
    if (!user?.id) return;
    api.trackEvent({
      user_id: user.id,
      product_id: productId,
      action,
      ...extra,
    }).catch(() => {}); // silent
  }, [user?.id]);
}
