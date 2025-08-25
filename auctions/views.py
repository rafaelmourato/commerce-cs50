from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django import forms
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import User, Listing, Bid, Comment

categories = [ ("",""),
        ('Fash', 'Fashion'),
        ('Toys', 'Toys'),
        ('Elec', 'Electronics'),
        ( 'Home', 'Home'),
    ]

class ListingForm(forms.Form):
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
                CurrentBid=form.cleaned_data["CurrentBid"],
                Image=form.cleaned_data["Image"],
                Category=form.cleaned_data["Category"]
            )
            listing.save()
            return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/createlisting.html",{
            "form": ListingForm()
        })

def categoriesList(request):
    used_categories = Listing.objects.values_list("Category", flat=True).distinct()
    filtered_categories = [item for item in categories if item[0] in used_categories]
    return render(request, "auctions/categories.html",{
        "categories": filtered_categories
    })

def categoryList(request, category):
    listings = Listing.objects.filter(Category=category)
    value = next((label for key, label in categories if key == category), category)
    return render(request, "auctions/categories.html",{
        "listings": listings,
        "category": value
    })

def listing(request, id):
    listing = Listing.objects.get(pk=id)
    comments = Comment.objects.filter(OnListing=listing)
    error = None
    if request.method == "POST":
        if request.user.is_authenticated:
            bid = request.POST.get("bid")
            if bid:
                bid2 = float(bid)
                if bid2 > listing.CurrentBid:
                    newBid = Bid(Bidder=request.user, Value=bid2, Receiver=listing)
                    newBid.save()
                    listing.Winner = request.user
                    listing.CurrentBid = bid
                    listing.save()
                else:
                    error = "Your bid must be higher than the current bid"
            else:
                    error = "You must place a bid"
        else:
            error = "You must login to bid"
    return render(request, "auctions/listing.html",{
        "listing": listing,
        "comments": comments,
        "error": error
    })

def end_listing(request, id):
    listing = Listing.objects.get(pk=id)
    listing.Active = False
    listing.save()
    return HttpResponseRedirect(reverse("listing", args=[id]))

@login_required
def mybids(request):
    mybids = Bid.objects.filter(Bidder=request.user)
    
    return render(request, "auctions/mybids.html",{
        "mybids": mybids
    })

@login_required
def watchlist_toggle(request, id):
    user = request.user
    if request.method == "POST" and user.is_authenticated:
        listing = Listing.objects.get(pk=id)
        if listing not in user.Watchlist.all():
            user.Watchlist.add(listing)
            message = "Added to your watchlist"
        else:    
            user.Watchlist.remove(listing)
            message = "Deleted from your watchlist"
    else:
        message = "You must be logged in"
    return render(request, "auctions/listing.html",{
        "listing": listing,
        "message": message
    })

@login_required
def watchlist(request):
    user = request.user
    return render(request, "auctions/watchlist.html",{
    "watchlist": user.Watchlist.all()
    })

def commenting(request,id): 
    comment = request.POST.get("comment")
    listing = Listing.objects.get(pk=id)
    user = request.user
    new_comment = Comment(Comenting=user, OnListing=listing, Content=comment)
    new_comment.save()
    return HttpResponseRedirect(reverse("listing", args=[id]))

    

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

@login_required
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
