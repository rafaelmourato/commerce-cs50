from django.contrib.auth.models import AbstractUser
from django.db import models

#user:  Listing(n:1), Watchlist(n:n), ListingsWon(1:n)
class User(AbstractUser): #abstract has username, firs, last, password.
    Watchlist = models.ManyToManyField('Listing', blank=True, related_name="interested_users")


# Listing: id, Title, Description, StartitngBid, Image(none/url), category(none:list) Active(t,f), user(1:n)(fkon.deletecascade), bid(n:1), WinningBid(1:n), Coments(n:1)
class Listing(models.Model):
    categories = [
        ('Fash', 'Fashion'),
        ('Toys', 'Toys'),
        ('Elec', 'Electronics'),
        ( 'Home', 'Home'),
    ]
    Owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="owner")
    Winner = models.ForeignKey(User, on_delete=models.PROTECT, related_name="winner", null=True, blank=True)
    Title = models.CharField(max_length=64)
    Description = models.TextField(blank=True)
    CurrentBid = models.DecimalField(max_digits = 10, decimal_places=2)
    Image = models.URLField(max_length=500, blank=True, null=True)
    Category = models.CharField(choices=categories, null=True, blank=True, default= None, max_length=100)
    Active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.Title}:"


#comments: user(fkon.deletecascade), listing, content
class Comment(models.Model):
    Comenting = models.ForeignKey(User, on_delete=models.CASCADE, related_name="commenting")
    OnListing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="listingComment")
    Content = models.TextField()

#Bids: User(fkon.deletecascade), Listing, Value
class Bid(models.Model):
    Bidder = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bidding")
    Receiver = models.ForeignKey(Listing, on_delete=models.PROTECT, related_name="listingBid")
    Value = models.DecimalField(max_digits = 10, decimal_places=2)
    

# harvard - cs50commerce