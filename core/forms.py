from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Q
from decimal import Decimal


from .models import Product, Category, Order, OrderItem
from .cart import Cart

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


# ... existing RegisterForm ...

from django import forms
from .models import Order

class CheckoutForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['total_amount']  # we'll set this automatically
        widgets = {
            'total_amount': forms.HiddenInput(),
        }

    # Optional: add more fields if you want shipping info
    shipping_address = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3}),
        required=True,
        label="Shipping Address"
    )
    notes = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 2}),
        required=False,
        label="Order Notes"
    )


class CheckoutForm(forms.ModelForm):
    shipping_address = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), required=True)
    notes = forms.CharField(widget=forms.Textarea(attrs={'rows': 2}), required=False)

    class Meta:
        model = Order
        fields = []  # No model fields needed anymore since we handle manually
        widgets = {}


from django import forms
from .models import Product

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'category', 'description', 'price', 'stock_quantity', 'image', 'is_available']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
        }