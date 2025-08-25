from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("createlisting", views.create_listing, name="createlisting"),
    path("endlisting/<int:id>", views.end_listing, name="endlisting"),
    path("categories", views.categoriesList, name="categories"),
    path("categories/<str:category>", views.categoryList, name="category"),
    path("listing/<int:id>", views.listing, name="listing"),
    path("watchlist/>", views.watchlist, name="watchlist"),
    path("watchlisttoggle/<int:id>", views.watchlist_toggle, name="watchlistToggle")

]
