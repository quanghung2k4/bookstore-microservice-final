const KEY = "wishlist_product_ids";

function safeParse(value, fallback) {
  try {
    return JSON.parse(value);
  } catch {
    return fallback;
  }
}

export function getWishlist() {
  const raw = localStorage.getItem(KEY);
  const list = safeParse(raw, []);
  if (!Array.isArray(list)) return [];
  return list.map((v) => Number(v)).filter((v) => Number.isFinite(v));
}

export function isWishlisted(productId) {
  const id = Number(productId);
  if (!Number.isFinite(id)) return false;
  return getWishlist().includes(id);
}

export function getWishlistCount() {
  return getWishlist().length;
}

export function toggleWishlist(productId) {
  const id = Number(productId);
  if (!Number.isFinite(id)) return getWishlist();

  const current = getWishlist();
  const next = current.includes(id)
    ? current.filter((x) => x !== id)
    : [...current, id];

  localStorage.setItem(KEY, JSON.stringify(next));
  window.dispatchEvent(new Event("wishlist:changed"));
  return next;
}
