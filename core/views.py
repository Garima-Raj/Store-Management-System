from django.shortcuts import render, get_object_or_404
from .models import Product
from django.views.decorators.http import require_POST
from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import RegisterForm
from django.contrib.auth.decorators import login_required
from .cart import Cart
from django.contrib.admin.views.decorators import staff_member_required
from .forms import ProductForm


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # auto-login after register
            return redirect('home')
    else:
        form = RegisterForm()
    return render(request, 'core/registration/register.html', {'form': form})

from django.db.models import Q
from .models import Product, Category

def home(request):
    query = request.GET.get('q', '').strip()          # search term
    category_id = request.GET.get('category', '')     # selected category

    products = Product.objects.filter(is_available=True).order_by('name')

    # Apply category filter if selected
    if category_id:
        try:
            category = Category.objects.get(id=category_id)
            products = products.filter(category=category)
        except Category.DoesNotExist:
            pass  # ignore invalid category

    # Apply search if query exists
    if query:
        products = products.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )

    # Get all categories for dropdown
    categories = Category.objects.all()

    return render(request, 'core/home.html', {
        'products': products,
        'categories': categories,
        'selected_category': category_id,
        'query': query,  # to keep search term in input
    })

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk, is_available=True)
    return render(request, 'core/product_detail.html', {'product': product})

@login_required
@require_POST
def cart_add(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)

    quantity = int(request.POST.get('quantity', 1))

    # Check available stock
    current_in_cart = cart.cart.get(str(product.id), {}).get('quantity', 0)
    requested_total = current_in_cart + quantity

    if requested_total > product.stock_quantity:
        messages.error(request, f"Only {product.stock_quantity} of '{product.name}' available. You already have {current_in_cart} in cart.")
        return redirect('product_detail', pk=product.id)

    cart.add(product=product, quantity=quantity, override_quantity=False)
    messages.success(request, f"{quantity} × {product.name} added to cart.")
    return redirect('cart_detail')

@login_required
def cart_detail(request):
    cart = Cart(request)
    return render(request, 'core/cart_detail.html', {'cart': cart})

@login_required
@require_POST
def cart_remove(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    return redirect('cart_detail')


from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import RegisterForm, CheckoutForm, ProductForm
from .models import Order, OrderItem
from decimal import Decimal

@login_required
def checkout(request):
    cart = Cart(request)
    
    if not cart:
        messages.warning(request, "Your cart is empty.")
        return redirect('cart_detail')

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            # Double-check stock before creating order
            for item in cart:
                product = item['product']
                if item['quantity'] > product.stock_quantity:
                    messages.error(request, f"Insufficient stock for '{product.name}'. Only {product.stock_quantity} left.")
                    return redirect('cart_detail')

            # Create the order
            order = Order.objects.create(
                user=request.user,
                total_amount=Decimal(cart.get_total_price()),
                status='pending',
                shipping_address=form.cleaned_data['shipping_address'],
                notes=form.cleaned_data.get('notes', ''),
            )

            # Create order items and reduce stock
            for item in cart:
                product = item['product']
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=item['quantity'],
                    price_at_purchase=item['price'],
                )
                product.stock_quantity -= item['quantity']
                if product.stock_quantity <= 0:
                    product.is_available = False
                product.save()

            cart.clear()
            messages.success(request, f"Order #{order.id} placed successfully!")
            return redirect('order_confirmation', order_id=order.id)
    else:
        # This is the important part that was missing or wrong
        form = CheckoutForm()

    # Always render with form (now form is guaranteed to exist)
    return render(request, 'core/checkout.html', {
        'cart': cart,
        'form': form,
        'total': cart.get_total_price(),
    })

@login_required
def order_confirmation(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'core/order_confirmation.html', {'order': order})

@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'core/order_history.html', {
        'orders': orders
    })

@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    items = order.items.all()
    return render(request, 'core/order_detail.html', {
        'order': order,
        'items': items
    })



@staff_member_required
def product_list_staff(request):
    products = Product.objects.all().order_by('name')
    return render(request, 'core/product_list_staff.html', {'products': products})


@staff_member_required
def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Product added successfully!")
            return redirect('product_list_staff')
    else:
        form = ProductForm()
    return render(request, 'core/product_form.html', {'form': form, 'title': 'Add New Product'})


@staff_member_required
def product_update(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, "Product updated!")
            return redirect('product_list_staff')
    else:
        form = ProductForm(instance=product)
    return render(request, 'core/product_form.html', {'form': form, 'title': f'Edit {product.name}'})


@staff_member_required
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    
    if request.method == 'POST':
        try:
            product.delete()
            messages.success(request, f"Product '{product.name}' deleted successfully!")
            return redirect('product_list_staff')
        except ProtectedError as e:
            messages.error(request, f"Cannot delete '{product.name}' because it is part of existing orders. Please remove related orders first or archive the product.")
            return redirect('product_list_staff')
    
    return render(request, 'core/product_confirm_delete.html', {'product': product})

from django.contrib.admin.views.decorators import staff_member_required
from .models import Order

@staff_member_required
def order_list_staff(request):
    status_filter = request.GET.get('status', '')
    orders = Order.objects.all().order_by('-created_at')

    if status_filter:
        orders = orders.filter(status=status_filter)

    statuses = dict(Order.STATUS_CHOICES)  # for dropdown

    return render(request, 'core/order_list_staff.html', {
        'orders': orders,
        'statuses': statuses,
        'selected_status': status_filter,
    })

@staff_member_required
@require_POST
def order_update_status(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    new_status = request.POST.get('status')

    if new_status in dict(Order.STATUS_CHOICES):
        order.status = new_status
        order.save()
        messages.success(request, f"Order #{order.id} status updated to {new_status.capitalize()}.")
    else:
        messages.error(request, "Invalid status selected.")

    return redirect('order_list_staff')


@login_required
def profile(request):
    return render(request, 'core/profile.html', {'user': request.user})