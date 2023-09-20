from decimal import Decimal
from django.conf import settings
from .models import Product

class Cart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart

    def add(self, product, quantity=1, override_quantity=False, selected_image_url=None):
        product_id = str(product.id)
        image_key = selected_image_url or product.productImage.url  # Use selected image URL if provided
        cart_item_key = f"{product_id}_{image_key}"  # Create a unique key based on product and image

        if cart_item_key not in self.cart:
            self.cart[cart_item_key] = {
                "code": product.productCode,
                "name": product.productName,
                "image": image_key,
                "quantity": 0,
                "price": str(product.productPrice),
            }

        if override_quantity:
            self.cart[cart_item_key]['quantity'] = quantity
        else:
            self.cart[cart_item_key]['quantity'] += quantity
        self.save()

    def save(self):
        self.session.modified = True

    def remove(self, product):
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
        self.save()

    def __iter__(self):
        product_ids = [cart_item_key.split('_')[0] for cart_item_key in self.cart.keys()]
        products = Product.objects.filter(id__in=product_ids)
        cart = self.cart.copy()

        for product in products:
            for image_url in set(cart_item_key.split('_')[1] for cart_item_key in self.cart.keys() if cart_item_key.startswith(str(product.id))):
                cart_item_key = f"{str(product.id)}_{image_url}"
                item = cart[cart_item_key]
                item["product"] = product
                item["image"] = item["image"]
                item["code"] = item["code"]
                item["name"] = item["name"]
                item["price"] = Decimal(item["price"])
                item["total_price"] = item["price"] * item["quantity"]
                yield item

    def __len__(self):
        return sum(item['quantity'] for item in self.cart.values())

    def get_total_price(self):
        return sum(Decimal(item['price']) * item['quantity'] for item in self.cart.values())

    def get_total_items(self):
        return sum(item['quantity'] for item in self.cart.values())

    def clear(self):
        del self.session[settings.CART_SESSION_ID]
        self.save()