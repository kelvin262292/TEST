from django.shortcuts import render, get_object_or_404 # Import get_object_or_404
from .models import Product, Category # Import Product and Category models

def home_page(request):
    # Placeholder data for the template
    context = {
        'banner_title': "Welcome to the Awesome 3D Store!",
        'banner_subtitle': "Your one-stop shop for amazing 3D models. Discover models for all your creative needs.",
        'featured_products': [
            {
                'name': 'Futuristic Spaceship',
                'description': 'A high-detail model of a sci-fi spaceship.',
                'image_url': 'https://via.placeholder.com/240x240.png?text=Spaceship', # Placeholder image
            },
            {
                'name': 'Medieval Castle',
                'description': 'A detailed model of a medieval castle keep.',
                'image_url': 'https://via.placeholder.com/240x240.png?text=Castle', # Placeholder image
            },
            {
                'name': 'Cartoon Character',
                'description': 'A fun and expressive cartoon character model.',
                'image_url': 'https://via.placeholder.com/240x240.png?text=Character', # Placeholder image
            }
        ],
        'about_us_content': "We are dedicated to providing top-quality 3D assets for creators, game developers, and animators. Our library is constantly growing!"
    }
    return render(request, 'store/home.html', context)

def product_list_page(request):
    products = Product.objects.all()
    categories = Category.objects.all() # Fetch all categories
    context = {
        'products': products,
        'categories': categories,
    }
    return render(request, 'store/product_list.html', context)

def product_detail_page(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    # Placeholder for reviews if you were to implement them
    # reviews = product.reviews.all() 
    context = {
        'product': product,
        # 'reviews': reviews, # Uncomment if you have a review model and relationship
    }
    return render(request, 'store/product_detail.html', context)

from django.shortcuts import redirect
from django.views.decorators.http import require_POST
from .cart import Cart

@require_POST
def add_to_cart(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    # For simplicity, quantity is handled as 1, or from a form if you add one
    quantity = int(request.POST.get('quantity', 1)) 
    cart.add(product_id=product.id, quantity=quantity)
    return redirect('view_cart_page') # Or redirect to product detail page: 'product_detail_page', product_id=product_id

def view_cart_page(request):
    cart = Cart(request)
    return render(request, 'store/cart_detail.html', {'cart': cart})

@require_POST # Or handle GET if you use links for removal, but POST is safer
def remove_from_cart(request, product_id):
    cart = Cart(request)
    cart.remove(product_id)
    return redirect('view_cart_page')

@require_POST
def update_cart(request, product_id):
    cart = Cart(request)
    quantity = int(request.POST.get('quantity'))
    if quantity > 0:
        cart.update(product_id, quantity)
    else: # If quantity is 0 or less, remove the item
        cart.remove(product_id)
    return redirect('view_cart_page')

from django.contrib.auth.decorators import login_required
from .forms import ShippingAddressForm
from django.contrib import messages
from django.utils import timezone # Import timezone
from .models import Product, Category, Address, Order, OrderItem # Added Address, Order, OrderItem
from django.conf import settings # Added settings
from django.core.mail import send_mail # Added send_mail

@login_required
def checkout_page(request):
    cart = Cart(request)
    if not cart: # Check if cart has items by its length or specific content
        messages.error(request, "Your cart is empty. Please add items to your cart before proceeding to checkout.")
        return redirect('view_cart_page')

    if request.method == 'POST':
        form = ShippingAddressForm(request.POST)
        if form.is_valid():
            # Store shipping address in session for now
            # In a real application, you might save this to the user's profile or an Order object
            address_data = form.cleaned_data
            # Simulate saving the address and getting an ID or just use the data
            # For now, we'll just pass it via session.
            address_data = form.cleaned_data
            
            # Create or update Address object
            # For V1, we'll create a new one or find an identical one for simplicity.
            # A more robust solution would allow users to select from saved addresses.
            address, created = Address.objects.get_or_create(
                user=request.user,
                full_name=address_data['full_name'],
                phone_number=address_data['phone_number'],
                street_address=address_data['street_address'],
                city=address_data['city'],
                state_or_province=address_data['state_or_province'],
                postal_code=address_data['postal_code'],
                country=address_data['country'],
                defaults={'is_default_shipping': False} # Or True if it's the first one etc.
            )

            # Create Order object
            order = Order.objects.create(
                user=request.user,
                shipping_address=address,
                billing_address=address, # Same as shipping for V1
                total_amount=cart.get_total_price(),
                status='Pending', # Default, or 'Processing'
                # payment_method and shipping_method will use defaults from model for now
            )

            # Create OrderItem objects
            for item in cart:
                product = item['product']
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=item['quantity'],
                    price_at_purchase=item['price']
                )
                # Basic Inventory Management
                product.stock_quantity -= item['quantity']
                product.save()
            
            # Clear the cart
            cart.clear()

            # Remove shipping_address_data from session
            if 'shipping_address_data' in request.session:
                del request.session['shipping_address_data']
            if 'cart_order_id' in request.session: # also clear this if it was used previously
                del request.session['cart_order_id']

            # Send basic email confirmation
            try:
                send_mail(
                    f'Your Order #{order.id} has been placed!',
                    f"Thank you for your order!\n\nOrder ID: {order.id}\nTotal Amount: ${order.total_amount}\n\nWe will process it shortly.",
                    settings.DEFAULT_FROM_EMAIL,
                    [request.user.email],
                    fail_silently=False, # Set to True in production if minor email errors are okay
                )
                messages.success(request, f"Your order #{order.id} has been placed successfully! A confirmation email has been sent.")
            except Exception as e:
                # Log the error e
                messages.warning(request, f"Your order #{order.id} has been placed, but we couldn't send a confirmation email. Error: {e}")


            return redirect('order_success_page', order_id=order.id)
    else:
        # Check if user has a default shipping address to pre-fill the form
        default_address = Address.objects.filter(user=request.user, is_default_shipping=True).first()
        if default_address:
            initial_data = {
                'full_name': default_address.full_name or f"{request.user.first_name} {request.user.last_name}",
                'phone_number': default_address.phone_number,
                'street_address': default_address.street_address,
                'city': default_address.city,
                'state_or_province': default_address.state_or_province,
                'postal_code': default_address.postal_code,
                'country': default_address.country,
            }
            form = ShippingAddressForm(initial=initial_data)
        else:
            # Pre-fill name from user profile if no default address
            initial_data = {'full_name': f"{request.user.first_name} {request.user.last_name}"}
            if request.user.email: # Assuming email might be used as a contact, though phone is better
                # Or you might have a phone field on the User model itself
                pass 
            form = ShippingAddressForm(initial=initial_data)


    context = {
        'form': form,
        'cart': cart,
    }
    return render(request, 'store/checkout.html', context)

@login_required
def order_success_page(request, order_id): # order_id is now a parameter
    order = get_object_or_404(Order, id=order_id, user=request.user) # Fetch the actual order

    # Cart and session data ('shipping_address_data', 'cart_order_id') 
    # should have been cleared by the checkout_page view after order creation.

    context = {
        'order': order, # Pass the real Order object to the template
    }
    return render(request, 'store/order_success.html', context)

from .forms import UserProfileForm # Import UserProfileForm

@login_required
def user_profile_page(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('user_profile_page')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserProfileForm(instance=request.user)
    
    context = {
        'form': form,
        'page_title': 'User Profile' # Added for template customization
    }
    return render(request, 'store/user_profile.html', context)

@login_required
def order_history_page(request):
    orders = Order.objects.filter(user=request.user).order_by('-order_date')
    context = {
        'orders': orders,
        'page_title': 'Order History'
    }
    return render(request, 'store/order_history.html', context)

@login_required
def address_book_page(request):
    addresses = Address.objects.filter(user=request.user).order_by('-is_default_shipping') # Show default first
    
    if request.method == 'POST':
        form = ShippingAddressForm(request.POST)
        if form.is_valid():
            new_address = form.save(commit=False)
            new_address.user = request.user
            # Check if user wants to set this new address as default
            # For simplicity, we'll add a checkbox to the form later if needed.
            # For now, new addresses are not set as default unless it's the only one.
            if not addresses.exists(): # If this is the first address, make it default
                new_address.is_default_shipping = True
            new_address.save()
            messages.success(request, 'New address added successfully!')
            return redirect('address_book_page')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ShippingAddressForm() # Empty form for adding new address

    context = {
        'addresses': addresses,
        'form': form,
        'page_title': 'Address Book'
    }
    return render(request, 'store/address_book.html', context)

@login_required
@require_POST # Ensure this is a POST request for safety
def set_default_address(request, address_id):
    address = get_object_or_404(Address, id=address_id, user=request.user)
    # Set all other addresses to not default
    Address.objects.filter(user=request.user).update(is_default_shipping=False)
    # Set the selected address as default
    address.is_default_shipping = True
    address.save()
    messages.success(request, f'Address "{address.street_address}, {address.city}" set as default shipping address.')
    return redirect('address_book_page')

@login_required
@require_POST # Ensure this is a POST request for safety
def delete_address(request, address_id):
    address = get_object_or_404(Address, id=address_id, user=request.user)
    # Prevent deleting the default address if it's the only address (optional, good practice)
    # For now, allow deletion. If it was default, user might need to set a new default.
    address_info = f"{address.street_address}, {address.city}" # Get info before deleting
    address.delete()
    messages.success(request, f'Address "{address_info}" deleted successfully.')
    return redirect('address_book_page')
