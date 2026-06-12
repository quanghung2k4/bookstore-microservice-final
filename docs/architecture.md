# Architecture

## Service Boundaries

- `product_service`
  - Owns catalog data: products, categories, brands, product types, variants.
- `user_service`
  - Owns identities and business roles: `admin`, `staff`, `customer`.
- `cart_service`
  - Owns cart aggregate. Stores `product_id` and `quantity` only.
- `order_service`
  - Owns order history and checkout orchestration.
- `payment_service`
  - Owns payment lifecycle and simulated transaction reference.
- `api_gateway`
  - Thin proxy for north-south traffic.

## Layering

Each service uses:

- `domain`: framework-free entities and rules.
- `application`: use cases and orchestration.
- `infrastructure`: Django ORM, repositories, external HTTP clients.
- `presentation`: DRF serializers, views, URLs.

## Communication

- Gateway proxies client requests to downstream services.
- Cart validates users and products by calling `user_service` and `product_service`.
- Order reads cart data, fetches product prices, validates users, computes totals, then calls `payment_service`.
- Payment stores payment transactions and can confirm payment for an order.

## Role Model

- `admin`: manage users and global operations.
- `staff`: back-office catalog/order support.
- `customer`: shopping and checkout.

## AI Roadmap

`ai_service` is intentionally deferred. The current design leaves room for:

- product-view events
- cart events
- order events
- recommendation API

