from django.db import models
from django.contrib.auth.models import User
from django.db.models import Sum


# Create your models here.
class Customer(models.Model):
    REQUIRED_FIELDS = ('user',)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer', unique=True)
    mobile = models.CharField(max_length=20, null=True)
    address = models.CharField(max_length=40, null=True)
    customer_image = models.ImageField(upload_to='customer_image/', null=True, blank=True,
                                       default='customer_image/default.jpg')

    @property
    def get_name(self):
        return self.user.first_name + " " + self.user.last_name

    @property
    def get_id(self):
        return self.user.id

    @property
    def cart_items_count(self):
        return self.cartitem_set.count() or 0

    @property
    def wishlist_items_count(self):
        return self.wishlist_set.count() or 0

    def __str__(self):
        return self.user.first_name

    class Meta:
        db_table = "Customer"


class Category(models.Model):
    slug = models.SlugField(max_length=50, unique=True, null=True, blank=True)
    name = models.CharField(max_length=40)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "Category"


class Brand(models.Model):
    slug = models.SlugField(max_length=50, unique=True, null=True, blank=True)
    name = models.CharField(max_length=40)
    description = models.TextField(null=True, blank=True)
    logo = models.ImageField(upload_to='brand_logo/', null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "Brand"


class Product(models.Model):
    slug = models.SlugField(max_length=50, unique=True, null=True, blank=True)
    name = models.CharField(max_length=40)
    category = models.ForeignKey('Category', on_delete=models.CASCADE, null=True)
    brand = models.ForeignKey('Brand', on_delete=models.CASCADE, null=True)
    price_original = models.DecimalField(max_digits=10, decimal_places=1, null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=1, null=True, blank=True)
    old_price = models.DecimalField(max_digits=10, decimal_places=1, null=True, blank=True)
    stock = models.PositiveIntegerField()
    description = models.TextField(null=True, blank=True)
    product_image = models.ImageField(upload_to='product_image/', null=True, blank=True)
    sold = models.PositiveIntegerField(default=0)
    created_date = models.DateTimeField(auto_now_add=True, null=True)
    updated_date = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "Product"


class Coupon(models.Model):
    code = models.CharField(max_length=20)
    discount = models.DecimalField(max_digits=10, decimal_places=1, null=True, blank=True)
    amount = models.PositiveIntegerField(default=1)
    valid_from = models.DateTimeField(blank=True, null=True)
    valid_to = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField(default=True, null=True, blank=True)

    def __str__(self):
        return self.code

    class Meta:
        db_table = "Coupon"


class CartItem(models.Model):
    customer = models.ForeignKey('Customer', on_delete=models.CASCADE, null=True)
    product = models.ForeignKey('Product', on_delete=models.CASCADE, null=True)
    quantity = models.PositiveIntegerField(null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=1, null=True, blank=True)
    sub_total = models.DecimalField(max_digits=10, decimal_places=1, null=True, blank=True)
    discount = models.DecimalField(max_digits=10, decimal_places=1, null=True, blank=True, default=0)
    date_added = models.DateTimeField(auto_now_add=True, null=True)
    coupon = models.ForeignKey('Coupon', on_delete=models.CASCADE, null=True, blank=True, default=None)
    coupon_applied = models.BooleanField(default=False, null=True, blank=True)

    @property
    def get_total_amount_without_coupon(self):
        total = self.product.price * self.quantity
        return total

    @property
    def get_discount(self):
        return self.coupon.discount * self.quantity

    @property
    def get_total_amount_with_coupon(self):
        total = self.product.price * self.quantity
        if self.coupon_applied and self.coupon is not None:
            return total - self.discount
        else:
            return total

    def update_subtotal_total(self):
        self.sub_total = self.quantity * self.price
        if self.coupon:
            self.total = self.sub_total - self.coupon.discount
            self.coupon_applied = True
        else:
            self.total = self.sub_total
            self.coupon_applied = False
        self.save()

    def __str__(self):
        return self.product.name

    class Meta:
        db_table = "CartItem"


class Orders(models.Model):
    STATUS = (
        ('Pending', 'Pending'),
        ('Order Confirmed', 'Order Confirmed'),
        ('Out for Delivery', 'Out for Delivery'),
        ('Delivered', 'Delivered'),
    )
    customer = models.ForeignKey('Customer', on_delete=models.CASCADE, null=True)
    product = models.ForeignKey('Product', on_delete=models.CASCADE, null=True)
    order_date = models.DateTimeField(auto_now_add=True, null=True)
    status = models.CharField(max_length=50, null=True, choices=STATUS)
    payment_method = models.ForeignKey('Payment', on_delete=models.CASCADE, null=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=1, null=True, blank=True)
    delivery_address = models.ForeignKey('DeliveryAddress', on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.product.name

    class Meta:
        db_table = "Orders"


class OrderDetails(models.Model):
    order = models.ForeignKey('Orders', on_delete=models.CASCADE, null=True)
    product = models.ForeignKey('Product', on_delete=models.CASCADE, null=True)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=1, null=True, blank=True)
    sub_total = models.DecimalField(max_digits=10, decimal_places=1, null=True, blank=True)
    discount = models.DecimalField(max_digits=10, decimal_places=1, null=True, blank=True, default=0)
    coupon = models.ForeignKey('Coupon', on_delete=models.CASCADE, null=True, blank=True, default=None)
    coupon_applied = models.BooleanField(default=False, null=True, blank=True)

    def __str__(self):
        return self.product.name

    class Meta:
        db_table = "OrderDetails"


class DeliveryAddress(models.Model):
    customer = models.ForeignKey('Customer', on_delete=models.CASCADE, null=True)
    first_name = models.CharField(max_length=40, null=True)
    last_name = models.CharField(max_length=40, null=True)
    mobile = models.CharField(max_length=20, null=True)
    email = models.CharField(max_length=50, null=True)
    address = models.CharField(max_length=500, null=True)
    city = models.CharField(max_length=40, null=True)
    state = models.CharField(max_length=40, null=True)
    country = models.CharField(max_length=40, null=True)
    zip_code = models.CharField(max_length=20, null=True)
    date_added = models.DateTimeField(auto_now_add=True, null=True)
    is_default = models.BooleanField(default=False)

    def __str__(self):
        return self.address

    class Meta:
        db_table = "DeliveryAddress"


class Payment(models.Model):
    METHOD_CHOICES = (
        ('Cash on Delivery', 'Cash on Delivery'),
        ('Online Payment', 'Online Payment'),
        ('Bank Transfer', 'Bank Transfer'),
        ('Visa', 'Visa'),
        ('Paypal', 'Paypal'),
        ('Master Card', 'Master Card'),
        ('Credit Card', 'Credit Card'),
        ('Debit Card', 'Debit Card')
    )
    PAYMENT_STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Paid', 'Paid')
    )
    customer = models.ForeignKey('Customer', on_delete=models.CASCADE, null=True)
    order = models.ForeignKey('Orders', on_delete=models.CASCADE, null=True)
    payment_method = models.CharField(max_length=50, null=True, choices=METHOD_CHOICES)
    payment_status = models.CharField(max_length=50, null=True, choices=PAYMENT_STATUS_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    transaction_id = models.CharField(max_length=100, null=True)
    payment_date = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return self.order.__str__()

    class Meta:
        db_table = "Payment"


class Review(models.Model):
    customer = models.ForeignKey('Customer', on_delete=models.CASCADE, null=True)
    product = models.ForeignKey('Product', on_delete=models.CASCADE, null=True)
    rate = models.PositiveIntegerField()
    message_review = models.CharField(max_length=500)
    date_added = models.DateTimeField(auto_now_add=True, null=True)
    date_updated = models.DateTimeField(auto_now=True, null=True)
    review_status = models.BooleanField(default=False)

    def __str__(self):
        return self.product.name

    class Meta:
        db_table = "Review"


class Wishlist(models.Model):
    customer = models.ForeignKey('Customer', on_delete=models.CASCADE, null=True)
    product = models.ForeignKey('Product', on_delete=models.CASCADE, null=True)
    date_added = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return self.product.name

    class Meta:
        db_table = "Wishlist"


class Feedback(models.Model):
    name = models.CharField(max_length=40)
    email = models.CharField(max_length=50, null=True)
    mobile = models.CharField(max_length=20, null=True)
    subject = models.CharField(max_length=100, null=True)
    message = models.CharField(null=True, max_length=2000)
    date_sent = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "Feedback"
