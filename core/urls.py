from django.urls import path
from .views import HomeView, CheckoutView, ItemDetailView, add_to_cart
from .views import (remove_from_Cart, TestSite, about,
                    OrderSummaryView, remove_single_item_from_cart, PaymentView, AddCoupon, RequestRefundView, FirstComponentForm, imageFile, predict_image
                    )
app_name = 'core'
urlpatterns = [
    path("", HomeView.as_view(), name="home-view"),
    path("checkout/", CheckoutView.as_view(), name="checkout"),
    path("product/<slug>/", ItemDetailView.as_view(), name="product"),
    path("about/", about, name="about"),
    path("add-to-cart/<slug>/", add_to_cart, name="add-to-cart"),
    path("image-upload", imageFile, name="imageFile"),

    path("remove_from_Cart/<slug>/", remove_from_Cart, name="remove_from_Cart"),
    path("pt/", TestSite.as_view(), name="test_site"),
    path("order-summary/", OrderSummaryView.as_view(), name="order-summary"),
    path('remove-item-from-cart/<slug>/', remove_single_item_from_cart,
         name="remove-single-item-from-cart"),
    path("payment/<payment_option>/", PaymentView.as_view(), name="payment"),
    path("add-coupon/", AddCoupon.as_view(), name="add-coupon"),
    path("request-refund/", RequestRefundView.as_view(), name="reuest-refund"),
    path('appform/', FirstComponentForm.as_view(), name="appform "),
    path("predictions_for_image/", predict_image, name="predict_image"),


]
