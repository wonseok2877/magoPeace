import re

from django.db.models.deletion       import CASCADE
from django.db.models.fields         import CharField, IntegerField, TextField, URLField
from django.db.models.fields.related import ForeignKey, ManyToManyField

from restaurants.models              import Restaurant
from mangoPeace.common               import TimeStampModel


class User(TimeStampModel):
    nickname             = CharField(max_length=15, unique=True)
    email                = CharField(max_length=200, unique=True)
    password             = CharField(max_length=200)
    phone_number         = CharField(max_length=20, unique=True, null=True)
    profile_url          = URLField(null=True)
    wishlist_restaurants = ManyToManyField(Restaurant, through="Wishlist", related_name="wishlist_user")
    reviewed_restaurants = ManyToManyField(Restaurant, through="Review", related_name="reviewed_user")

    @classmethod
    def validate(cls, data):
        NICKNAME_REGEX     = r'^[a-zA-Z가-힇0-9]{1,8}$'
        EMAIL_REGEX        = r'^[a-zA-Z0-9]+@[a-zA-Z0-9.]+\.[a-zA-Z0-9]+$'
        PASSWORD_REGEX     = r'^(?=.*[a-z])(?=.+[A-Z])(?=.+\d)(?=.+[!@#$%^&*()-=_+])[a-zA-Z0-9`~!@#$%^&*()_+-=,./<>?]{6,25}$'
        PHONE_NUMBER_REGEX = r'^01[1|2|5|7|8|9|0][0-9]{3,4}[0-9]{4}$'
        
        if not re.match(EMAIL_REGEX, data["email"]) or not re.match(NICKNAME_REGEX, data["nickname"])\
            or not re.match(PASSWORD_REGEX, data["password"]) or not re.match(PHONE_NUMBER_REGEX, data["phone_number"]):
            return
        
        return True

    class Meta():
        db_table = "users"

    def __str__(self):
        return self.nickname

class Wishlist(TimeStampModel):
    user       = ForeignKey(User, on_delete=CASCADE)
    restaurant = ForeignKey(Restaurant, on_delete=CASCADE)

    class Meta():
        db_table        = "wishlists"
        unique_together = ['user', 'restaurant']

class Review(TimeStampModel):
    user       = ForeignKey(User, on_delete=CASCADE, related_name="reviews")
    restaurant = ForeignKey(Restaurant, on_delete=CASCADE, related_name="reviews")
    content    = TextField()
    rating     = IntegerField()

    class Meta():
        db_table = "reviews"

    def __str__(self):
        return f"{self.content[:10]}..."