from typing import final
from django.conf import settings
from django.shortcuts import render, get_object_or_404, HttpResponse
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.views.generic import ListView, DetailView, View
from django.utils import timezone
from .models import Item, OrderItem, Order, Address, Payment, Coupon, Refund, FirstComponentModel
from .forms import CheckOutForm, CouponForm, RefundForm, ImageClassification
from .address_form import FirstComponent
from .casavara_diseases import predict_disease

import os
# Create your views here.
# payment method stripe
import random
import string
import stripe

stripe.api_key = "sk_test_51IZKY4SIPnDXbbiek1h2lL8rOQ3kcWRGsaO1AqHd5jAaqWxe8g2srMqKp4IokBDvFyVFHFN7t63QKq4L6mdP5r2t00EU2k66kr"
# stripe.api_key = "pk_test_51IZKY4SIPnDXbbie4IL9PU7Iu1wBhUPTwZWRHJkNsNta3HkcHxxydvk92AfHcJ6cCpluscLBch7OwJAVL3WruYvu00kdE49lbn"
# `source` is obtained with Stripe.js; see https://stripe.com/docs/payments/accept-a-payment-charges#web-create-token


def create_ref_code():
    return ''.join(random.choice(string.ascii_lowercase+string.digits, k=20))


class TestSite(ListView):
    model = Item
    template_name = "product_test.html"


def imageFile(request):
    if request.method == 'POST':
        form = ImageClassification(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return render(request, 'uploadImage.html', {'form': form, 'image_status': True})
    else:
        form = ImageClassification()
    return render(request, 'uploadImage.html', {
        'form': form, 'image_status': False
    })


def predict_image(request):
    directory = "media_root/documents"
    files = os.listdir(directory)
    img_path = files[-1]
    final_path = os.path.join(directory, img_path)
    ans = predict_disease(final_path)
    return render(request, 'imagePredictions.html', {'source': img_path, 'content': ans})


class FirstComponentForm(View):

    def get(self, *args, **kwargs):
        try:
            tags = FirstComponentModel()
            form = FirstComponent()
            context = {
                'form': form,
                'buity_tag': False
            }
            form_model = FirstComponentModel.objects.filter(builty_type="M")
            ts = FirstComponentModel.objects
            print("hi", form_model, ts, form_model.exists())
            if form_model.exists():
                context.update({'builty_tag': True})
            return render(self.request, 'appForms.html', context)
        except ObjectDoesNotExist:
            return redirect('core:appform')

    def post(self, *args, **kwargs):
        form = FirstComponent(self.request.POST or None)
        try:
            if form.is_valid():
                builty_type = form.cleaned_data.get("builty_type")
                manual_number = form.cleaned_data.get('manual_number')
                form.save()
                print(builty_type, manual_number)
                return render(self.request, 'appForms.html', {'form': form})

            else:
                messages.info(
                    self.request, "This Form is not valid,manual number must be 8 digits long")
                return render(self.request, 'appForms.html', {'form': form})

        except ObjectDoesNotExist:
            return redirect('core:appform')


def is_valid_form(values):
    valid = True
    for field in values:
        if field == "":
            valid = False
    return valid


class CheckoutView(View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(
                user=self.request.user, ordered=False)

            # order.save()
            form = CheckOutForm()
            context = {
                'form': form,
                'couponform': CouponForm(),
                'order': order,
                'DISPLAY_COUPON_FORM': True
            }
            shipping_address_qs = Address.objects.filter(user=self.request.user,
                                                         address_type="S",
                                                         default=True)
            if shipping_address_qs.exists():
                context.update(
                    {'default_shipping_address': shipping_address_qs[0]})
            billing_address_qs = Address.objects.filter(
                user=self.request.user,
                address_type="S",
                default=True)
            if billing_address_qs.exists():
                context.update(
                    {'default_billing_address': billing_address_qs[0]})

            return render(self.request, 'checkout-page.html', context)

        except ObjectDoesNotExist:
            return redirect('core:checkout')

    def post(self, *args, **kwargs):
        form = CheckOutForm(self.request.POST or None)
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            if form.is_valid():

                use_default_shipping = form.cleaned_data.get(
                    'use_default_shipping')
                if use_default_shipping:
                    print('use_default_shipping')
                    address_qs = Address.objects.filter(user=self.request.user,
                                                        address_type="S",
                                                        default=True)
                    if address_qs.exists():
                        shipping_address = address_qs[0]
                    else:
                        messages.info(
                            self.request, "You not have default address")
                        return redirect("core:checkout")
                else:
                    print("user is new and new address required")
                    use_default_billing = form.cleaned_data.get(
                        'use_default_billing')
                    shipping_address = form.cleaned_data.get(
                        'shipping_address')
                    shipping_address2 = form.cleaned_data.get(
                        'shipping_address2')
                    shipping_country = form.cleaned_data.get(
                        'shipping_country')
                    shipping_zip = form.cleaned_data.get('shipping_zip')
                    if is_valid_form([shipping_address, shipping_zip, shipping_country]):

                        shipping_address = Address(
                            user=self.request.user,
                            street_address=shipping_address,
                            apartment_address=shipping_address2,
                            country=shipping_country,
                            zip=shipping_zip,
                            address_type="S"

                        )
                        shipping_address.save()
                        order.shipping_address = shipping_address
                        order.save()

                        set_default_shipping = form.cleaned_data.get(
                            'set_default_shipping')
                        if set_default_shipping:
                            shipping_address.default = True
                            shipping_address.save()

                    else:
                        messages.info(self.request, "please fill address"
                                      )
                use_default_billing = form.cleaned_data.get(
                    'use_default_billing')
                same_billing_address = form.cleaned_data.get(
                    'same_billing_address')
                if same_billing_address:
                    billing_address = shipping_address
                    billing_address.pk = None
                    billing_address.save()
                    billing_address.address_type = "B"
                    billing_address.save()
                    order.billing_address = billing_address
                    order.save()

                elif use_default_billing:
                    print('use_default_billing')
                    address_qs = Address.objects.filter(user=self.request.user,
                                                        address_type="B",
                                                        default=True)
                    if address_qs.exists():
                        billing_address = address_qs[0]
                    else:
                        messages.info(
                            self.request, "You not have default address")
                        return redirect("core:checkout")
                else:
                    print("user is new and new address required")
                    billing_address = form.cleaned_data.get('billing_address')
                    billing_address2 = form.cleaned_data.get(
                        'billing_address2')
                    billing_country = form.cleaned_data.get('billing_country')
                    billing_zip = form.cleaned_data.get('billing_zip')
                    if is_valid_form([billing_address, billing_zip, billing_country]):

                        billing_address = Address(
                            user=self.request.user,
                            street_address=billing_address,
                            apartment_address=billing_address2,
                            country=billing_country,
                            zip=billing_zip,
                            address_type="B"

                        )
                        # billing_country.save()
                        order.billing_country = billing_country
                        order.save()

                        set_default_billing = form.cleaned_data.get(
                            'set_default_billing')
                        if set_default_billing:
                            billing_address.default = True
                            billing_address.save()
                    else:
                        messages.info(
                            self.request, "Please fill form correctly and complete, if you have any issue file it on git hub repo of code")

                payment_option = form.cleaned_data.get('payment_option')
                if payment_option == "S":
                    return redirect('core:payment', payment_option="stripe")
                elif payment_option == "P":

                    return redirect('core:payment', payment_option="paypal")
                else:
                    messages.warning(
                        self.request, "Failed checkout, invalid payment option")
                    return redirect('core:checkout')

        except ObjectDoesNotExist:
            messages.warning(self.request, "You do not have an active order")
            return redirect("core:order-summary")


class PaymentView(View):
    def get(self, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, ordered=False)
        if order.billing_address:
            context = {
                'order': order,
                'DISPLAY_COUPON_FORM': False
            }
            return render(self.request, "payment.html", context)
        else:
            messages.warning(
                self.request, "You do not have billing address")
            return redirect("core:order-summary")

    def post(self, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, ordered=False)
        token = self.request.POST.get('stripeToken')
        amount = int(order.get_total()*100)

        try:
            # Use Stripe's library to make requests...
            # charge = stripe.Charge.create(
            # amount=amount,
            # currency="usd",
            # source='tok_in',
            # description="it is test data "
            # )
            customer = stripe.Customer.create(
                name=self.request.user,
                address={order.shipping_address},
                # amount=amount,
                # currency="usd",
                source='tok_in',
                description="it is test data"
            )
            payment = Payment()
            payment.stripe_charge_id = customer['id']
            payment.user = self.request.user
            payment.amount = order.get_total()
            payment.save()
            # assign payment to order

            order_item = order.items.all()
            order_item.update(ordered=True)
            for item in order_item:
                item.save()

            order.ordered = True
            order.payment = payment
            order.ref_code = create_ref_code()
            order.save()

            order.ordered = True

            # Payment
            messages.success(self.request, "successfull payment "+str(token))
            return redirect("/")

        except stripe.error.CardError as e:
            # Since it's a decline, stripe.error.CardError will be caught
            body = e.json_body
            err = body.get('error', {})
            messages.error(self.request, f"{err.get('message')}")
            return redirect("/")

        except stripe.error.RateLimitError as e:
            # Too many requests made to the API too quickly
            messages.error(self.request, "rate limit error")
            return redirect("/")

        except stripe.error.InvalidRequestError as e:
            # Invalid parameters were supplied to Stripe's API
            messages.error(
                self.request, "invalid request error "+str(e)+str(token))
            return redirect("/")
        except stripe.error.AuthenticationError as e:
            # Authentication with Stripe's API failed
            # (maybe you changed API keys recently)
            messages.error(self.request, "authentication error")
            return redirect("/")

        except stripe.error.APIConnectionError as e:
            # Network communication with Stripe failed
            messages.error(self.request, "api connection error")
            return redirect("/")

        except stripe.error.StripeError as e:
            # Display a very generic error to the user, and maybe send
            # yourself an email
            messages.error(self.request, "stripe error "+str(e))
            return redirect("/")

        except Exception as e:
            # Something else happened, completely unrelated to Stripe

            messages.error(self.request, "Serious error  "+str(e))
            return redirect("/")
        return redirect("/")


def about(request):
    return render(request, "about.html", {})


class HomeView(ListView):
    model = Item
    paginate_by = 10
    template_name = "home-page.html"


class OrderSummaryView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            context = {
                'object': order
            }
            return render(self.request, 'order_summary.html', context)
        except ObjectDoesNotExist:
            messages.warning(self.request, "You do not have an active order")
            return redirect("/")


class ItemDetailView(DetailView):
    model = Item
    template_name = "product-page.html"


@login_required
def add_to_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_item, created = OrderItem.objects.get_or_create(
        item=item, user=request.user, ordered=False)
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter(item__slug=item.slug).exists():
            order_item.quantity += 1
            order_item.save()
            messages.info(request, "Successfully Added to your cart")
            return redirect("core:order-summary")
        else:
            messages.info(request, "Successfully added to your cart")
            order.items.add(order_item)
            return redirect("core:order-summary")
    else:
        ordered_date = timezone.localtime(timezone.now())
        order = Order.objects.create(
            user=request.user, ordered_date=ordered_date)
        order.items.add(order_item)
        return redirect("core:product", slug=slug)
    return redirect("core:product", slug=slug)


@login_required
def remove_from_Cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item, user=request.user, ordered=False
            )[0]
            order.items.remove(order_item)
            messages.info(request, "successfully removed to your cart")
            return redirect("core:product", slug=slug)
        else:
            messages.info(request, "not exist in your cart")
            return redirect("core:product", slug=slug)

    else:
        messages.info(request, "you  do not have active orders")
        return redirect("core:product", slug=slug)
    return redirect("core:product", slug=slug)


@login_required
def remove_single_item_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False
    )
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
            else:
                order.items.remove(order_item)
            messages.info(request, "This item quantity was updated.")
            return redirect("core:order-summary")
        else:
            messages.info(request, "This item was not in your cart")
            return redirect("core:product")
    else:
        messages.info(request, "You do not have an active order")
        return redirect("core:product")


def get_coupon(request, code):
    try:
        coupon = Coupon.objects.get(code=code)
        return coupon
    except ObjectDoesNotExist:
        messages.info(request, "this coupon not exist")
        return redirect('core:checkout')


class AddCoupon(View):
    def post(self, *args, **kwargs):

        # if request.method == "POST":
        form = CouponForm(self.request.POST or None)
        if form.is_valid():
            try:
                code = form.cleaned_data.get('code')
                order = Order.objects.get(
                    user=self.request.user, ordered=False)
                order.coupon = get_coupon(self.request, code)
                order.save()
                messages.info(self.request, "this coupon exist and success")

                return redirect('core:checkout')

            except ObjectDoesNotExist:
                messages.info(self.request, "you do not have active orders")
                return redirect('core:checkout')
            except ValueError:
                messages.info(self.request, "you do not have active orders")
                return redirect('core:checkout')


class RequestRefundView(View):
    def get(self, *args, **kwargs):
        form = RefundForm()
        context = {
            'form': form
        }
        return render(self.request, "request-refund.html", context)

    def post(self, *args, **kwargs):
        form = RefundForm(self.request.POST)
        if form.is_valid():
            ref_code = form.cleaned_data.get('ref_code')
            message = form.changed_data.get('message')
            email = form.changed_data.get('email')

            try:
                order = Order.objects.get(ref_code=ref_code)
                order.refund_requested = True
                order.save()
                refund = Refund()
                refund.order = order
                refund.reason = message
                refund.email = email
                refund.save()
                messages.info(self.request, "succeess")
                return redirect("core:request-refund")
            except ObjectDoesNotExist:
                messages.info(self.request, "this product not exist")
                return redirect("core:request-refund")
