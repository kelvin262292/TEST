from django.contrib import admin
from .models import User, Product, Category, Order, OrderItem, Address
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

# Unregister the default User admin if User is our custom model from store.User
# This is not strictly necessary if store.User is ALREADY the AUTH_USER_MODEL
# and Django's default User is not separately registered.
# However, if you had a User model registered by Django's auth app and then
# also registered your store.User, you might need this.
# Given our setup, store.User IS AUTH_USER_MODEL, so we customize its registration.

@admin.register(User)
class CustomUserAdmin(BaseUserAdmin):
    list_display = ('email', 'username', 'first_name', 'last_name', 'is_staff', 'is_active', 'date_joined')
    search_fields = ('email', 'username', 'first_name', 'last_name')
    ordering = ('email',)
    # Add other customizations from BaseUserAdmin if needed, or add new ones.
    # fieldsets, add_fieldsets, etc., can be inherited or overridden.

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ['product'] # Use raw_id_fields for product ForeignKey for better performance with many products
    readonly_fields = ('price_at_purchase',) # Price shouldn't change after order
    # For V1, quantity can be editable by admin for adjustments before shipping.
    # If orders are strictly non-editable after placement, set more fields to readonly_fields:
    # readonly_fields = ('product', 'quantity', 'price_at_purchase')
    extra = 0 # Don't show extra empty forms by default

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'order_date', 'total_amount', 'payment_method', 'shipping_method')
    list_filter = ('status', 'order_date', 'payment_method', 'shipping_method')
    search_fields = ('id', 'user__email', 'shipping_address__full_name') # Search by order ID, user email, or shipping name
    list_editable = ('status', 'payment_method', 'shipping_method') # Allow direct editing of these fields in the list view
    
    readonly_fields = ('user', 'order_date', 'total_amount', 'shipping_address', 'billing_address')
    # To make Address fields more readable in admin, consider custom methods or string representations in Address model
    
    inlines = [OrderItemInline]
    
    fieldsets = (
        (None, {
            'fields': ('user', 'order_date', 'status')
        }),
        ('Amount Information', {
            'fields': ('total_amount',)
        }),
        ('Shipping Information', {
            'fields': ('shipping_address', 'shipping_method')
        }),
        ('Payment Information', {
            'fields': ('billing_address', 'payment_method') # Assuming billing_address could be different
        }),
    )
    # Actions
    actions = ['mark_as_shipped', 'mark_as_delivered']

    def mark_as_shipped(self, request, queryset):
        queryset.update(status='Shipped')
        self.message_user(request, "Selected orders have been marked as Shipped.")
    mark_as_shipped.short_description = "Mark selected orders as Shipped"

    def mark_as_delivered(self, request, queryset):
        queryset.update(status='Delivered')
        self.message_user(request, "Selected orders have been marked as Delivered.")
    mark_as_delivered.short_description = "Mark selected orders as Delivered"


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'stock_quantity', 'created_at')
    list_filter = ('category', 'created_at')
    search_fields = ('name', 'description')
    list_editable = ('price', 'stock_quantity')
    prepopulated_fields = {'slug': ('name',)}
    # For better UI with many categories:
    # autocomplete_fields = ['category'] 

@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('user', 'full_name', 'street_address', 'city', 'country', 'is_default_shipping', 'is_default_billing')
    list_filter = ('city', 'country', 'is_default_shipping', 'is_default_billing')
    search_fields = ('user__email', 'full_name', 'street_address', 'city', 'postal_code', 'country')
    # For better UI with many users:
    # autocomplete_fields = ['user']
    ordering = ('user', '-is_default_shipping')
