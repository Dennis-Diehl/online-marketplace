function updateCartBadge(count) {
    const badge = document.getElementById('cart-badge');
    if (badge) badge.textContent = count;
}

async function addToCart(productId) {
    try {
        const res = await fetch(`/api/cart/${productId}`, { method: 'POST' });
        const data = await res.json();
        if (data.success) {
            updateCartBadge(data.cart_count);
        } else {
            alert(data.error || 'Could not add to cart.');
        }
    } catch (e) {
        alert('Network error.');
    }
}

async function removeFromCart(productId, btn) {
    try {
        const res = await fetch(`/api/cart/${productId}`, { method: 'DELETE' });
        const data = await res.json();
        if (data.success) {
            updateCartBadge(data.cart_count);
            const item = document.getElementById(`cart-item-${productId}`);
            if (item) item.remove();
        } else {
            alert(data.error || 'Could not remove from cart.');
        }
    } catch (e) {
        alert('Network error.');
    }
}

async function toggleWishlist(btn) {
    const productId = btn.dataset.productId;
    const inWishlist = btn.dataset.inWishlist === 'true';
    const method = inWishlist ? 'DELETE' : 'POST';
    try {
        const res = await fetch(`/api/wishlist/${productId}`, { method });
        const data = await res.json();
        if (data.success) {
            btn.dataset.inWishlist = data.in_wishlist ? 'true' : 'false';
            if (data.in_wishlist) {
                btn.textContent = 'Remove from Wishlist';
                btn.classList.remove('btn-outline-secondary');
                btn.classList.add('btn-outline-danger');
            } else {
                btn.textContent = 'Add to Wishlist';
                btn.classList.remove('btn-outline-danger');
                btn.classList.add('btn-outline-secondary');
            }
        } else {
            alert(data.error || 'Could not update wishlist.');
        }
    } catch (e) {
        alert('Network error.');
    }
}
