from django.contrib.auth import authenticate, login as auth_login, update_session_auth_hash, logout as auth_logout
from django.contrib.sites.shortcuts import get_current_site
from django.core.paginator import Paginator
# from django.http import HttpResponse, HttpResponseRedirect
from .forms import RegisterForm, LoginForm, UpdateProfileForm, ChangePasswordForm, ChangeEmailForm
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
# Password Reset Imports
from django.core.mail import send_mail, BadHeaderError, EmailMessage
from django.http import HttpResponse
from django.contrib.auth.forms import PasswordResetForm
from django.template.loader import render_to_string
from django.db.models.query_utils import Q
# from django.contrib.auth.tokens import default_token_generator
from django.contrib import messages
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from .tokens import account_activation_token, password_reset_token, update_email_token
from django.contrib.auth.models import User
from .models import Customer, Product, Category, Brand, DeliveryAddress


# Create your views here.
def paginator(request, objects):
    # Set the number of items per page
    per_page = 8

    # Create a Paginator object with the customers queryset and the per_page value
    page = Paginator(objects, per_page)

    # Get the current page number from the request's GET parameters
    page_number = request.GET.get('page')

    # Get the current page object from the Paginator object
    page_obj = page.get_page(page_number)
    return page_obj


# Display Homepage for all users. Display List of all products, categories, brands, etc.
def home(request):
    products = Product.objects.all().order_by('id')
    categories = Category.objects.all().order_by('id')
    brands = Brand.objects.all().order_by('id')
    page_object = paginator(request, products)
    context = {'products': page_object,
               'categories': categories,
               'brands': brands}
    return render(request, 'main/base/base.html', context)


def is_admin(user):
    return user.is_authenticated and user.is_active and user.is_superuser and user.is_staff


def is_customer(user):
    return user.is_authenticated and user.is_active


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST, request.FILES)
        if form.is_valid():
            if User.objects.filter(email=form.cleaned_data['email']).exists():
                form.add_error('email', 'Email is already exist. Please use another email.')
                return render(request, "registration/register/register.html", {"form": form})
            elif User.objects.filter(username=form.cleaned_data['username']).exists():
                form.add_error('username', 'Username is already exist')
                return render(request, "registration/register/register.html", {"form": form})
            else:
                user = form.save(commit=False)
                user.is_active = False
                user.save()
                customer = Customer.objects.create(user=user)
                customer.address = form.cleaned_data['address']
                customer.mobile = form.cleaned_data['mobile']
                customer.customer_image = form.cleaned_data['customer_image']
                customer.save()

                send_email_activate_account(request, user)
                return render(request, 'registration/register/account_activation_sent.html')
    else:
        form = RegisterForm()
    return render(request, 'registration/register/register.html', {'form': form})


def send_email_activate_account(request, user):
    current_site = get_current_site(request)
    mail_subject = 'Activate your account.'
    message = render_to_string('registration/register/account_activation_email.html', {
        'user': user,
        'domain': current_site.domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': account_activation_token.make_token(user),
        'protocol': 'http',
    })
    to_email = [user.email]
    form_email = 'LCL Shop <lclshop.dev@gmail.com>'
    email = EmailMessage(mail_subject, message, form_email, to_email)
    email.content_subtype = "html"
    email.send()


def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        auth_login(request, user)
        messages.success(request, 'Thank you for your email confirmation. Now you can login your account.')
        return redirect('/')
    else:
        return render(request, 'registration/register/account_activation_invalid.html')


def login(request, *args, **kwargs):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password'])
            if user is not None:
                # authenticate the user and log them in
                auth_login(request, user)
                # check if admin redirect to admin page else redirect to user page
                if user.is_superuser and user.is_staff and user.is_active:
                    messages.success(request, 'Welcome back administrator!')
                    return redirect("/dashboard/")
                else:
                    messages.success(request, 'Welcome back {}'.format(user.username))
                    return redirect("/")
            else:
                username = form.cleaned_data['username']
                user = User.objects.filter(username=username).first()
                if user is not None and user.is_active is False:
                    send_email_activate_account(request, user)
                    messages.warning(request, 'Your account is not active. Please check your email {} to '
                                              'activate your account.'.format(user.email))
                    return render(request, "registration/login.html", {"form": form})
                form.add_error('username', 'Username or password is incorrect')
                return render(request, "registration/login.html", {"form": form})
    else:
        form = LoginForm()
    return render(request, "registration/login.html", {"form": form})


def send_verify_new_email(request, user):
    current_site = get_current_site(request)
    mail_subject = 'Update your account.'
    message = render_to_string('registration/profile/verify_new_email.html', {
        'user': user,
        'domain': current_site.domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': update_email_token.make_token(user),
        'protocol': 'http',
    })
    to_email = [user.email]
    form_email = 'LCL Shop <lclshop.dev@gmail.com>'
    email = EmailMessage(mail_subject, message, form_email, to_email)
    email.content_subtype = "html"
    email.send()


def activate_new_email(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and update_email_token.check_token(user, token):
        user.is_active = True
        user.save()
        auth_login(request, user)
        messages.success(request, 'Your email has been updated. Now you can login your account.')
        return redirect('/auth/profile/')
    else:
        return render(request, 'registration/profile/verify_new_email_invalid.html')


@user_passes_test(is_customer, login_url='/auth/login/')
@login_required(login_url='/auth/login/')
def change_email(request):
    if request.method == 'POST':
        form = ChangeEmailForm(request.POST, instance=request.user)
        if form.is_valid():
            user = authenticate(username=request.user.username, password=form.cleaned_data['current_password'])
            if user is not None:
                # check if new email is already exist
                new_email = form.cleaned_data['new_email']
                if new_email == request.user.email:
                    form.add_error('new_email', 'New email is same as current email.')
                    return render(request, "registration/profile/change_email.html", {"form": form})
                elif User.objects.filter(email=new_email).exists():
                    form.add_error('new_email', 'Email is already exist. Please enter another email.')
                    return render(request, "registration/profile/change_email.html", {"form": form})
                else:
                    user.email = form.cleaned_data['new_email']
                    user.is_active = False
                    user.save()
                    send_verify_new_email(request, user)
                    return render(request, 'registration/profile/verify_new_email_sent.html')
            else:
                form.add_error('current_password', 'Password is incorrect')
                return render(request, "registration/profile/change_email.html", {"form": form})
    else:
        form = ChangeEmailForm(instance=request.user)
    return render(request, "registration/profile/change_email.html", {"form": form})


@user_passes_test(is_customer, login_url='/auth/login/')
@login_required(login_url='/auth/login/')
def update_profile(request):
    user = request.user
    # get customer-management object
    customer = Customer.objects.filter(user=user).first()
    if request.method == 'POST':
        form = UpdateProfileForm(request.POST, request.FILES, instance=user,
                                 initial={'address': customer.address, 'mobile': customer.mobile,
                                          'customer_image': customer.customer_image})

        if form.is_valid():
            form.save()
            customer.mobile = form.cleaned_data['mobile']
            customer.address = form.cleaned_data['address']
            customer.customer_image = form.cleaned_data['customer_image']

            customer.save()
            messages.success(request, 'Your profile has been updated.')
            return redirect('/auth/profile/')
    else:
        form = UpdateProfileForm(instance=user, initial={'address': customer.address,
                                                         'mobile': customer.mobile,
                                                         'customer_image': customer.customer_image})
    return render(request, 'registration/profile/update_profile.html', {'form': form})


@user_passes_test(is_customer, login_url='/auth/login/')
@login_required(login_url='/auth/login/')
def change_password(request):
    if request.method == 'POST':
        form = ChangePasswordForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = authenticate(username=request.user.username, password=form.cleaned_data['old_password'])
            if user is not None:
                user.set_password(form.cleaned_data['new_password1'])
                user.save()
                update_session_auth_hash(request, user)
                messages.success(request, 'Your password has been updated.')
                return redirect('/auth/change_password/')
            else:
                form.add_error('old_password', 'Wrong password. Please try again.')
    else:
        form = ChangePasswordForm(user=request.user)
    return render(request, 'registration/profile/change_password.html', {'form': form})


def logout(request):
    auth_logout(request)
    messages.success(request, "You have logged out. See you again!")
    return redirect('/')


def password_reset_request(request):
    if request.method == "POST":
        password_reset_form = PasswordResetForm(request.POST)
        if password_reset_form.is_valid():
            data = password_reset_form.cleaned_data['email']
            associated_users = User.objects.filter(Q(email=data))
            if associated_users.exists():
                for user in associated_users:
                    subject = "Password Reset Requested"
                    email_template_name = "registration/password/password_reset_email.html"
                    site = get_current_site(request)
                    c = {
                        "email": user.email,
                        'domain': site,
                        'site_name': 'Website',
                        "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                        "user": user,
                        'token': password_reset_token.make_token(user),
                        'protocol': 'http',
                    }
                    email = render_to_string(email_template_name, c)
                    form_email = 'LCL Shop <lclshop.dev@gmail.com>'
                    # sender_email = settings.EMAIL_HOST_USER
                    try:
                        send_mail(subject, email, form_email, [user.email], fail_silently=False, html_message=email)
                    except BadHeaderError:
                        return HttpResponse('Invalid header found.')

                return redirect("/auth/password_reset/done/")
            else:
                password_reset_form.add_error('email', 'The email address entered does not exist. Please try again')
                return render(request=request, template_name="registration/password/password_reset.html",
                              context={"password_reset_form": password_reset_form})
    else:
        password_reset_form = PasswordResetForm()
    return render(request=request, template_name="registration/password/password_reset.html",
                  context={"password_reset_form": password_reset_form})

