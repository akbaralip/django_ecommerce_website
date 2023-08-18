from django import template
from cart.models import Cart  # Import your Cart model

register = template.Library()

@register.simple_tag(takes_context=True)
def get_cart_item_count(context):
    request = context['request']
    if request.user.is_authenticated:
        cart = Cart.objects.get_or_create(user=request.user)[0]
    else:
        cart_id = request.session.get('cart_id')
        if cart_id:
            cart = Cart.objects.get(id=cart_id)
        else:
            cart = Cart.objects.create(user=None)
            request.session['cart_id'] = cart.id

    item_count = cart.cartitems_set.count()
    return item_count