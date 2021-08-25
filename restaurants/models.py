from django.db import models

from mangoPeace.common import TimeStampModel

class Menu(models.Model):
    name = models.CharField(max_length=45, unique=True)

    class Meta():
        db_table = "menus"

    def __str__(self):
        return self.name

class Category(models.Model):
    menu = models.ForeignKey(Menu, on_delete=models.PROTECT, related_name="categories")
    name = models.CharField(max_length=45, unique=True)

    class Meta():
        db_table = "categories"

    def __str__(self):
        return self.name

class SubCategory(models.Model):
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="sub_category")
    name     = models.CharField(max_length=45, unique=True)

    class Meta():
        db_table = "sub_categories"

    def __str__(self):
        return self.name

class Restaurant(TimeStampModel):
    sub_category = models.ForeignKey(SubCategory, on_delete=models.PROTECT, related_name="restaurant")
    name         = models.CharField(max_length=45)
    address      = models.CharField(max_length=200, unique=True)
    phone_number = models.CharField(max_length=20, unique=True)
    coordinate   = models.JSONField()
    open_time    = models.CharField(max_length=100)

    class Meta():
        db_table = "restaurants"

    def __str__(self):
        return self.name

class Food(TimeStampModel):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name="foods")
    name       = models.CharField(max_length=45)
    price      = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta():
        db_table = "foods"

    def __str__(self):
        return self.name

class Image(models.Model):
    food      = models.ForeignKey(Food, on_delete=models.CASCADE, related_name="images")
    image_url = models.URLField(max_length=2000)

    class Meta():
        db_table = "food_images"

    def __str__(self):
        return f"({self.pk}) at {self.food.name}"