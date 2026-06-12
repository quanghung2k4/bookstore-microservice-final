# API Examples

## Product Service Examples

### Get Products with Filters

```bash
# Get all products
curl "http://localhost:8000/gateway/products/products/"

# Filter by category
curl "http://localhost:8000/gateway/products/products/?category=electronics"

# Search products
curl "http://localhost:8000/gateway/products/products/?search=iphone"

# Filter by price range
curl "http://localhost:8000/gateway/products/products/?min_price=100&max_price=500"
```

### Product Stock Management

```bash
# Check stock for multiple items
curl -X POST "http://localhost:8000/gateway/products/products/check_stock/" \
  -H "Content-Type: application/json" \
  -d '{
    "items": [
      {"product_id": 1, "quantity": 2},
      {"product_id": 2, "quantity": 1}
    ]
  }'

# Reserve stock for checkout
curl -X POST "http://localhost:8000/gateway/products/products/1/reserve_stock/" \
  -H "Content-Type: application/json" \
  -d '{"quantity": 2}'
```

## User Service Examples

### Create User

```bash
curl -X POST "http://localhost:8000/gateway/users/users/" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "email": "john@example.com",
    "password": "secret123",
    "first_name": "John",
    "role": "customer"
  }'
```

### User Login

```bash
curl -X POST "http://localhost:8000/gateway/users/users/login/" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "password": "secret123"
  }'
```

## Cart Service Examples

### Create Cart

```bash
curl -X POST "http://localhost:8000/gateway/carts/carts/" \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1}'
```

### Add Item to Cart

```bash
curl -X POST "http://localhost:8000/gateway/carts/carts/1/items/" \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": 1,
    "quantity": 2
  }'
```

### Get Cart Summary

```bash
curl "http://localhost:8000/gateway/carts/carts/1/summary/"
```

### Update Cart Item Quantity

```bash
curl -X PATCH "http://localhost:8000/gateway/carts/cart-items/1/" \
  -H "Content-Type: application/json" \
  -d '{"quantity": 3}'
```

### Clear Cart

```bash
curl -X POST "http://localhost:8000/gateway/carts/carts/1/clear/"
```

## Order Service Examples

### Checkout Cart

```bash
curl -X POST "http://localhost:8000/gateway/orders/orders/checkout/" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1,
    "cart_id": 1
  }'
```

### Get Orders

```bash
curl "http://localhost:8000/gateway/orders/orders/"
```

## Payment Service Examples

### Get Payments

```bash
curl "http://localhost:8000/gateway/payments/payments/"
```

## AI Service Examples (History + Recommend)

Các endpoint AI được gọi thông qua API Gateway theo base URL:

- `http://localhost:8000/gateway/ai/...`

### Health check

```bash
curl "http://localhost:8000/gateway/ai/health/"
```

### Track event (lưu hành vi để dùng cho model)

Gửi từng event, AI service sẽ lưu vào SQLite (history) và vẫn record sang Neo4j (nếu Neo4j chạy).

```bash
# Click/view
curl -X POST "http://localhost:8000/gateway/ai/events/" \
  -H "Content-Type: application/json" \
  -d '{"user_id":"U1","product_id":"P0111","action":"click"}'

# Add to cart
curl -X POST "http://localhost:8000/gateway/ai/events/" \
  -H "Content-Type: application/json" \
  -d '{"user_id":"U1","product_id":"P0700","action":"add_to_cart"}'
```

PowerShell (Windows):

```powershell
$body = @{ user_id='U1'; product_id='P0111'; action='click' } | ConvertTo-Json
Invoke-RestMethod 'http://localhost:8000/gateway/ai/events/' -Method Post -ContentType 'application/json' -Body $body
```

### Get history (đúng format predictor cần)

```bash
curl "http://localhost:8000/gateway/ai/history/?user_id=U1&limit=5"
```

### Recommend (2 cách test)

1. Recommend dựa trên history đã lưu (chỉ cần user_id):

```bash
curl -X POST "http://localhost:8000/gateway/ai/recommend/" \
  -H "Content-Type: application/json" \
  -d '{"user_id":"U1","limit":5}'
```

2. Recommend bằng cách gửi trực tiếp `history` (không cần lưu trước):

```bash
curl -X POST "http://localhost:8000/gateway/ai/recommend/" \
  -H "Content-Type: application/json" \
  -d '{
    "history": [
      {"product_id": "P0111", "action": "click"},
      {"product_id": "P0700", "action": "add_to_cart"}
    ]
  }'
```

## Complete E-commerce Flow Example

### 1. Create a user

```bash
USER_RESPONSE=$(curl -s -X POST "http://localhost:8000/gateway/users/users/" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "customer1",
    "email": "customer1@example.com",
    "password": "secret123",
    "first_name": "Customer",
    "role": "customer"
  }')

USER_ID=$(echo $USER_RESPONSE | jq -r '.id')
echo "Created user with ID: $USER_ID"
```

### 2. Create a cart

```bash
CART_RESPONSE=$(curl -s -X POST "http://localhost:8000/gateway/carts/carts/" \
  -H "Content-Type: application/json" \
  -d "{\"user_id\": $USER_ID}")

CART_ID=$(echo $CART_RESPONSE | jq -r '.id')
echo "Created cart with ID: $CART_ID"
```

### 3. Add products to cart

```bash
# Add iPhone to cart
curl -X POST "http://localhost:8000/gateway/carts/carts/$CART_ID/items/" \
  -H "Content-Type: application/json" \
  -d '{"product_id": 1, "quantity": 1}'

# Add Samsung phone to cart
curl -X POST "http://localhost:8000/gateway/carts/carts/$CART_ID/items/" \
  -H "Content-Type: application/json" \
  -d '{"product_id": 2, "quantity": 1}'
```

### 4. View cart summary

```bash
curl "http://localhost:8000/gateway/carts/carts/$CART_ID/summary/"
```

### 5. Checkout

```bash
curl -X POST "http://localhost:8000/gateway/orders/orders/checkout/" \
  -H "Content-Type: application/json" \
  -d "{
    \"user_id\": $USER_ID,
    \"cart_id\": $CART_ID
  }"
```

### 6. View orders and payments

```bash
# View orders
curl "http://localhost:8000/gateway/orders/orders/"

# View payments
curl "http://localhost:8000/gateway/payments/payments/"
```

## Error Handling Examples

### Insufficient Stock

```bash
# Try to add more items than available stock
curl -X POST "http://localhost:8000/gateway/carts/carts/1/items/" \
  -H "Content-Type: application/json" \
  -d '{"product_id": 1, "quantity": 1000}'
```

### Invalid User/Cart

```bash
# Try checkout with invalid user
curl -X POST "http://localhost:8000/gateway/orders/orders/checkout/" \
  -H "Content-Type: application/json" \
  -d '{"user_id": 999, "cart_id": 1}'
```

### Empty Cart Checkout

```bash
# Try checkout empty cart
curl -X POST "http://localhost:8000/gateway/orders/orders/checkout/" \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1, "cart_id": 999}'
```
