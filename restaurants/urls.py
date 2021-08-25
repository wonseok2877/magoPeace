from django.urls import path

from restaurants.views import (
    RestaurantDetailView,
    SubCategoriesView,
    WishListView,
    RestaurantFoodsView,
    RestaurantReviewsView,
    RestaurantReviewView,
    RestaurantsView,
)

urlpatterns = [
    path("", RestaurantsView.as_view()),
    path("/subCategory", SubCategoriesView.as_view()),
    path("/<int:restaurant_id>", RestaurantDetailView.as_view()),  
    path("/<int:restaurant_id>/foods", RestaurantFoodsView.as_view()),
    path("/<int:restaurant_id>/wishlist", WishListView.as_view()),
    path("/<int:restaurant_id>/reviews", RestaurantReviewsView.as_view()),
    path("/<int:restaurant_id>/review/<int:review_id>", RestaurantReviewView.as_view()),  
]