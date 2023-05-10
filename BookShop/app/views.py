
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, get_object_or_404, HttpResponseRedirect, redirect
from django.urls import reverse
from .models import User, Cart, CartItem, Book, Order, Discount, PaymentMethod, OrderItem, DeliveryMethod, OrderDelivery, OrderPayment, Contact

# The other functions remain unchanged

def add_to_cart(request, book_id):
    book = get_object_or_404(Book, pk=book_id)
    quantity = int(request.POST.get('quantity', 1))

    session_key = request.session.session_key
    if not session_key:
        request.session.create()
        session_key = request.session.session_key

    try:
        cart = Cart.objects.get(session_key=session_key)
    except Cart.DoesNotExist:
        cart = Cart.objects.create(session_key=session_key)

    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        book=book,
        defaults={'price': book.price}  # Установите значение поля `price` для создаваемого объекта
    )

    if not created:
        cart_item.quantity += quantity
        cart_item.save()

    return redirect('cart')

def cart(request):
    session_key = request.session.session_key
    if not session_key:
        request.session.create()
        session_key = request.session.session_key

    cart, created = Cart.objects.get_or_create(session_key=session_key)
    cart_items = CartItem.objects.filter(cart=cart)

    context = {'cart_items': cart_items}
    return render(request, 'app/cart.html', context)
def home(request):
    return render(request, 'app/base.html')
def book_list(request):
    books = Book.objects.all()
    context = {'books': books}
    return render(request, 'app/book_list.html', context)

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'app/registration/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            return render(request, 'app/registration/login.html', {'error_message': 'Invalid username or password.'})
    return render(request, 'app/registration/login.html')
def index(request):
    books = Book.objects.all()
    context = {'books': books}
    return render(request, 'app/index.html', context)

def book_detail(request, book_id):
    book = get_object_or_404(Book, pk=book_id)
    context = {'book': book}
    return render(request, 'app/book_detail.html', context)


def remove_from_cart(request, book_id):
    book = get_object_or_404(Book, pk=book_id)
    order = Order.objects.get(user=request.user, status='Pending')
    order_item = OrderItem.objects.get(order=order, book=book)
    if order_item.quantity > 1:
        order_item.quantity -= 1
        order_item.save()
    else:
        order_item.delete()
    return HttpResponseRedirect(reverse('cart'))

def checkout(request):
    order = Order.objects.filter(user=request.user, status='Pending').first()
    order_items = OrderItem.objects.filter(order=order) if order else []
    delivery_methods = DeliveryMethod.objects.all()
    payment_methods = PaymentMethod.objects.all()
    context = {'order_items': order_items, 'delivery_methods': delivery_methods, 'payment_methods': payment_methods}
    return render(request, 'app/checkout.html', context)

def place_order(request):
    order = Order.objects.filter(user=request.user, status='Pending').first()
    order_items = OrderItem.objects.filter(order=order)
    delivery_method = DeliveryMethod.objects.get(pk=request.POST.get('delivery_method'))
    delivery_cost = delivery_method.price
    delivery_address = request.POST.get('delivery_address')
    payment_method = PaymentMethod.objects.get(pk=request.POST.get('payment_method'))
    payment_amount = sum([item.price * item.quantity for item in order_items]) + delivery_cost
    order_delivery = OrderDelivery.objects.create(order=order, delivery_method=delivery_method, delivery_cost=delivery_cost, delivery_address=delivery_address)
    order_payment = OrderPayment.objects.create(order=order, payment_method=payment_method, payment_amount=payment_amount)
    order.status = 'Processing'
    order.save()
    return HttpResponseRedirect(reverse('order_confirmation'))

def order_confirmation(request):
    order = Order.objects.filter(user=request.user, status='Processing').first()
    order_items = OrderItem.objects.filter(order=order)
    order_delivery = OrderDelivery.objects.filter(order=order).first()
    order_payment = OrderPayment.objects.filter(order=order).first()
    context = {'order_items': order_items, 'order_delivery': order_delivery, 'order_payment': order_payment}
    return render(request, 'app/order_confirmation.html', context)
def search(request):
    query = request.GET.get('query')
    if query:
        books = Book.objects.filter(title__icontains=query)
    else:
        books = []
    context = {'books': books}
    return render(request, 'app/search_results.html', context)


def apply_discount(request):
    code = request.POST.get('code')
    try:
        discount = Discount.objects.get(code=code)
        request.session['discount'] = discount.id
    except Discount.DoesNotExist:
        pass
    return HttpResponseRedirect(reverse('cart'))

def remove_discount(request):
    if 'discount' in request.session:
        del request.session['discount']
    return HttpResponseRedirect(reverse('cart'))

def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        contact = Contact.objects.create(name=name, email=email, subject=subject, message=message)
        return HttpResponseRedirect(reverse('contact_thankyou'))
    else:
        return render(request, 'app/contact.html')

def contact_thankyou(request):
    return render(request, 'app/contact_thankyou.html')


