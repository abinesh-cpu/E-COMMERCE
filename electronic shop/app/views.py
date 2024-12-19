from django.shortcuts import render,redirect
from .models import *
from django.contrib.auth import login, authenticate,logout
from .forms import *
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.contrib import messages

def product_list(request):
    products = Product.objects.all()
    return render(request, 'products/product_list.html', {'products': products})

def product_detail(request, product_id):
    product = Product.objects.get(id=product_id)
    return render(request, 'products/product_detail.html', {'product': product})

def add_to_cart(request, product_id):
    product = Product.objects.get(id=product_id)
    order, created = Order.objects.get_or_create(user=request.user, status="Pending")
    order.total_amount += product.price
    order.save()
    return redirect('order_summary')

def order_summary(request):
    order = Order.objects.filter(user=request.user, status="Pending").first()
    return render(request, 'orders/order_summary.html', {'order': order})

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserRegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('product_list')
    return render(request, 'accounts/login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def checkout(request):
    # Get the user's cart (Order)
    user_cart = Order.objects.get(user=request.user, status='in_cart')  # Assuming you have 'in_cart' status
    if user_cart.items.count() == 0:
        # If there are no items in the cart, redirect to the product listing page
        messages.error(request, "Your cart is empty!")
        return redirect('product_list')  # Change this to the correct URL name for product listing
    
    # Create a form for checkout
    form = CheckoutForm()

    context = {
        'user_cart': user_cart,
        'form': form
    }
    return render(request, 'checkout.html', context)

# View for handling the checkout form submission
@login_required
def place_order(request):
    if request.method == "POST":
        # Get the cart associated with the user
        user_cart = Order.objects.get(user=request.user, status='in_cart')
        
        if user_cart.items.count() == 0:
            messages.error(request, "Your cart is empty!")
            return redirect('product_list')  # Redirect if cart is empty

        form = CheckoutForm(request.POST)
        if form.is_valid():
            # Process the form data and create the order
            address = form.cleaned_data['address']
            payment_method = form.cleaned_data['payment_method']

            # Update the order status to 'ordered'
            user_cart.status = 'ordered'
            user_cart.shipping_address = address
            user_cart.payment_method = payment_method
            user_cart.save()

            # Create OrderItems and link them to the order
            for item in user_cart.items.all():
                OrderItem.objects.create(
                    order=user_cart,
                    product=item.product,
                    quantity=item.quantity,
                    price=item.product.price
                )

            # Clear the cart
            user_cart.items.clear()

            messages.success(request, "Your order has been placed successfully!")
            return redirect('order_confirmation', order_id=user_cart.id)

    else:
        return HttpResponse("Invalid request", status=400)

# View for order confirmation page
@login_required
def order_confirmation(request, order_id):
    order = Order.objects.get(id=order_id, user=request.user)
    if not order:
        return HttpResponse("Order not found", status=404)
    
    context = {
        'order': order
    }
    return render(request, 'order_confirmation.html', context)