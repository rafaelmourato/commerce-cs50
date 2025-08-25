from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django import forms
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import User, Listing

class ListingForm(forms.Form):
    categories = [ ("",""),
        ('Fash', 'Fashion'),
        ('Toys', 'Toys'),
        ('Elec', 'Electronics'),
        ( 'Home', 'Home'),
    ]
    Title = forms.CharField(max_length=64)
    Description = forms.CharField(widget=forms.Textarea)
    CurrentBid = forms.DecimalField(max_digits = 10, decimal_places=2)
    Image = forms.URLField(max_length=500, required=False)
    Category = forms.ChoiceField(choices=categories, required=False)

def index(request):
    return render(request, "auctions/index.html",{
        "listings": Listing.objects.all()
    })

@login_required
def create_listing(request):
    if request.method == "POST":
        form = ListingForm(request.POST)
        if form.is_valid():
            listing = Listing(
                Owner=request.user,
                Title=form.cleaned_data["Title"],
                Description=form.cleaned_data["Description"],
                CurrentBid=form.cleaned_data["InitialBid"],
                Image=form.cleaned_data["Image"],
                Category=form.cleaned_data["Category"]
            )
            listing.save()
            return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/createlisting.html",{
            "form": ListingForm()
        })

def categories(request):
    return render(request, "auctions/categories.html")

def listing(request, id):
    listing = Listing.objects.get(pk=id)
    if request.method == "POST":
        bid = request.POST.get("bid")
        if bid:
            bid2 = float(bid)
            if bid2 > listing.CurrentBid:
                listing.Owner = request.user
                listing.CurrentBid = bid
                listing.save()
                return render(request, "auctions/listing.html",{
                "listing": listing
            })
            else:
                return render(request, "auctions/listing.html",{
                "listing": listing,
                "error": "Your bid must be higher than the current bid"
            })
        else:
            return render(request, "auctions/listing.html",{
                "listing": listing,
                "error": "You must place a bid"
            })
    else:
        return render(request, "auctions/listing.html",{
            "listing": listing
        }) 

def watchlist(request):
    return render(request, "auctions/watchlist.html")

def bid(request):
    return None

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")

def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))

def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")
