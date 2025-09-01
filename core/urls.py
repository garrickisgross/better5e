from django.urls import path
from . import views

app_name = "core"

urlpatterns =[
    path("", views.home, name="home"),
    path("dice-theme/<str:base_b64>/<path:res_path>", views.dice_theme_proxy, name="dice_theme_proxy"),
    path("api/dice-theme/test", views.dice_theme_test, name="dice_theme_test"),
    path("api/dice-theme/load", views.dice_theme_load, name="dice_theme_load"),
]
