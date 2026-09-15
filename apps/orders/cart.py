from decimal import Decimal
from apps.products.models import Product

class Cart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get('cart')
        if not cart:
            cart = self.session['cart'] = {}
        self.cart = cart

    def add(self, product, quantity_kg=1.0):
        product_id = str(product.id)
        qty = float(quantity_kg)
        if product_id not in self.cart:
            self.cart[product_id] = {
                'quantity': qty,
                'price': float(product.consumer_price_per_kg),
                'farmer_price': float(product.farmer_base_price_per_kg),
                'retail_price': float(product.traditional_market_price_per_kg),
            }
        else:
            self.cart[product_id]['quantity'] += qty

        self.save()

    def set_quantity(self, product, quantity_kg):
        product_id = str(product.id)
        qty = float(quantity_kg)
        if qty > 0:
            if product_id in self.cart:
                self.cart[product_id]['quantity'] = qty
            else:
                self.cart[product_id] = {
                    'quantity': qty,
                    'price': float(product.consumer_price_per_kg),
                    'farmer_price': float(product.farmer_base_price_per_kg),
                    'retail_price': float(product.traditional_market_price_per_kg),
                }
        else:
            self.remove(product)
        self.save()

    def remove(self, product):
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def clear(self):
        del self.session['cart']
        self.save()

    def save(self):
        self.session.modified = True

    def __iter__(self):
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids).select_related('farmer__user')
        cart_copy = self.cart.copy()

        for product in products:
            cart_copy[str(product.id)]['product'] = product

        for item in cart_copy.values():
            if 'product' in item:
                item['total_price'] = round(item['price'] * item['quantity'], 2)
                item['farmer_subtotal'] = round(item['farmer_price'] * item['quantity'], 2)
                item['traditional_subtotal'] = round(item['retail_price'] * item['quantity'], 2)
                item['savings'] = round(item['traditional_subtotal'] - item['total_price'], 2)
                yield item

    def __len__(self):
        return len(self.cart)

    @property
    def total_items_count(self):
        return len(self.cart)

    @property
    def total_weight_kg(self):
        return sum([item['quantity'] for item in self.cart.values()])

    def get_subtotal(self):
        return round(sum([item['price'] * item['quantity'] for item in self.cart.values()]), 2)

    def get_delivery_fee(self):
        subtotal = self.get_subtotal()
        if subtotal == 0 or subtotal >= 400:
            return 0.0
        return 40.0

    def get_total(self):
        return round(self.get_subtotal() + self.get_delivery_fee(), 2)

    def get_farmer_total(self):
        return round(sum([item['farmer_price'] * item['quantity'] for item in self.cart.values()]), 2)

    def get_total_savings(self):
        traditional_total = sum([item['retail_price'] * item['quantity'] for item in self.cart.values()])
        savings = traditional_total - self.get_subtotal()
        return round(max(0.0, savings), 2)


def cart_context(request):
    """Context processor so cart is globally available in templates."""
    return {'cart': Cart(request)}
