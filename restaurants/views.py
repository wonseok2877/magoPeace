import json

from django.http        import JsonResponse
from django.views       import View
from django.db.utils    import DataError
from django.db.models   import Avg
from django.utils       import timezone

from restaurants.models import Restaurant, Food, SubCategory
from users.utils        import ConfirmUser, LooseConfirmUser
from users.models       import Review

class PopularRestaurantView(View):
    def get(self, request):
        try:
            dict_sort={
                "average_rating" : "-filtering"
            }
            filtering = request.GET.get("filtering", None)
            restaurants = Restaurant.objects.annotate(filtering=Avg("review__rating")).order_by(dict_sort[filtering])
            
            restaurant_list = []
            
            for restaurant in restaurants: 
                restaurant_list.append({
                    "sub_category"      : restaurant.sub_category.name,
                    "category"          : restaurant.sub_category.category.name,
                    "restaurant_name"   : restaurant.name,
                    "address"           : restaurant.address,
                    "rating"            : round(restaurant.filtering, 1),
                    "image"             : restaurant.foods.all()[0].images.all()[0].image_url,
                    "restaurant_id"     : restaurant.id
                })

            return JsonResponse({"message":"SUCCESS", "result":restaurant_list[:5]}, status=200)

        except Restaurant.DoesNotExist:
            return JsonResponse({"message":"RESTAURANT_NOT_EXIST"}, status=404)

class RestaurantDetailView(View):
    @LooseConfirmUser
    def get(self, request, restaurant_id):
        try:
            # ? : 왜 rating에 4가 곱해져서 나오지???? django shell에서는 멀쩡하게 나오는데.
            restaurant         = Restaurant.objects.filter(id=restaurant_id).annotate(
                rating_total   = Count("review"),
                rating_one     = Count("review", filter=Q(review__rating=1)),
                rating_two     = Count("review", filter=Q(review__rating=2)),
                rating_three   = Count("review", filter=Q(review__rating=3)),
                rating_four    = Count("review", filter=Q(review__rating=4)),
                rating_five    = Count("review", filter=Q(review__rating=5)),
                average_price  = Avg("foods__price"),
                average_rating = Avg("review__rating")
                )[0]
            is_wished          = request.user.wishlist_restaurants.filter(id=restaurant_id).exists() if request.user else False
            result             = {
                "id"             : restaurant.id,
                "sub_category"   : restaurant.sub_category.name,
                "name"           : restaurant.name,
                "address"        : restaurant.address,
                "phone_number"   : restaurant.phone_number,
                "coordinate"     : restaurant.coordinate,
                "open_time"      : restaurant.open_time,
                "updated_at"     : restaurant.updated_at,
                "is_wished"      : is_wished,
                "review_count"   : {
                    "total"        : restaurant.rating_total,
                    "rating_one"   : restaurant.rating_one,
                    "rating_two"   : restaurant.rating_two,
                    "rating_three" : restaurant.rating_three,
                    "rating_four"  : restaurant.rating_four,
                    "rating_five"  : restaurant.rating_five,
                    },
                "average_rating" : restaurant.average_rating,
                "average_price"  : restaurant.average_price,
            }

            return JsonResponse({"message":"SUCCESS", "result":result}, status=200)

        except Restaurant.DoesNotExist:
            return JsonResponse({"message":"RESTAURANT_NOT_EXIST"}, status=404)
        # ? : DoesNotExist가 에러 메세지로는 더 낫지 않나.
        except IndexError:
            return JsonResponse({"message":"RESTAURANT_NOT_EXIST"}, status=404)     

class RestaurantReviewView(View):
    @ConfirmUser
    def post(self, request, restaurant_id):
        try:
            data       = json.loads(request.body)
            restaurant = Restaurant.objects.get(id=restaurant_id)
            content    = data["content"]
            rating     = data["rating"]

            Review.objects.create(
                user       = request.user,
                restaurant = restaurant,
                content    = content,
                rating     = rating
            )

            return JsonResponse({"message":"SUCCESS"}, status=201)

        except KeyError:
            return JsonResponse({"message":"KEY_ERROR"}, status=400)
        
        except DataError:
            return JsonResponse({"message":"DATA_ERROR"}, status=400)

        except Restaurant.DoesNotExist:
            return JsonResponse({"message":"RESTAURANT_NOT_EXIST"}, status=404)     

    def get(self, request, restaurant_id):
        offset        = int(request.GET.get("offset", 0))
        limit         = int(request.GET.get("limit", 10))
        rating_min    = request.GET.get("rating-min", 1)
        rating_max    = request.GET.get("rating-max", 5)
        reviews       = Review.objects.filter(restaurant_id=restaurant_id, rating__gte = rating_min, rating__lte = rating_max).order_by("-created_at")[offset : offset + limit]
        review_list   = [{
            "user":{
                "id"            : review.user.id,
                "nickname"      : review.user.nickname,
                "profile_image" : review.user.profile_url,
                "review_count"  : review.user.reviewed_restaurants.count()
                },
                "id"         : review.id,
                "content"    : review.content,
                "rating"     : review.rating,
                "created_at" : review.created_at,
            } for review in reviews]

        return JsonResponse({"message":"success", "result":review_list}, status=200)

class RestaurantFoodsView(View):
    def get(self, request, restaurant_id):
        try:
            foods      = Food.objects.filter(restaurant_id=restaurant_id)
            foods_list = [{
                "id"     : food.id, 
                "name"   : food.name, 
                "price"  : food.price, 
                "images" : [image.image_url for image in food.images.all()]
            } for food in foods]

            return JsonResponse({"message":"success", "result":foods_list}, status=200)

        except Restaurant.DoesNotExist:
            return JsonResponse({"message":"RESTAURANT_NOT_EXISTS"}, status=404)
            
class WishListView(View):
    @ConfirmUser
    def post(self, request, restaurant_id):
        try:
            restaurant = Restaurant.objects.get(id=restaurant_id)

            if request.user.wishlist_restaurants.filter(id=restaurant_id).exists():
                return JsonResponse({"message":"WISHLIST_ALREADY_EXISTS"}, status=400)

            request.user.wishlist_restaurants.add(restaurant)
            
            return JsonResponse({"message":"SUCCESS"}, status=201)

        except Restaurant.DoesNotExist:
            return JsonResponse({"message":"RESTAURANT_NOT_EXISTS"}, status=404)   
        
    @ConfirmUser
    def delete(self, request, restaurant_id):
        try:
            restaurant = Restaurant.objects.get(id=restaurant_id)

            if not request.user.wishlist_restaurants.filter(id=restaurant_id).exists():
                return JsonResponse({"message":"WISHLIST_NOT_EXISTS"}, status=404)
           
            request.user.wishlist_restaurants.remove(restaurant)

            return JsonResponse({"message":"SUCCESS"}, status=204)

        except Restaurant.DoesNotExist:
            return JsonResponse({"message":"RESTAURANT_NOT_EXISTS"}, status=404)

class ReviewView(View):
    @ConfirmUser
    def patch(self, request, restaurant_id, review_id):
        try:
            data    = json.loads(request.body)
            content = data["content"]
            rating  = data["rating"]

            if not Review.objects.filter(id=review_id, user_id=request.user.id).exists():
                return JsonResponse({"message":"REVIEW_NOT_EXISTS"}, status=404)

            Review.objects.filter(id=review_id, user_id=request.user.id).update(content=content, rating=rating, updated_at=timezone.now())
            
            return JsonResponse({"message":"success"}, status=204)
            
        except KeyError:
            return JsonResponse({"message":"KEY_ERROR"}, status=400)

        except DataError:
            return JsonResponse({"message":"DATA_ERROR"}, status=400)
    def delete(self, request, restaurant_id, review_id):
        try:
            review = Review.objects.get(id=review_id, user_id=request.user.id)
            review.delete()

            return JsonResponse({"message":"success"}, status=204)

        except DataError:
            return JsonResponse({"message":"DATA_ERROR"}, status=400)

        except Review.DoesNotExist:
            return JsonResponse({"message":"REVIEW_NOT_EXISTS"}, status=404)
            
class SubCategoryListView(View):
    def get(self, request):
        try:
            subcategorys = SubCategory.objects.all()
                    
            subcategory_list = []
            for subcategory in subcategorys:                            
                subcategory_list.append({
                    "sub_category" : subcategory.id,
                    "image" : subcategory.restaurants.first().foods.first().images.first().image_url
                })

            return JsonResponse({"message":"success", "result":subcategory_list}, status=200)

        except SubCategory.DoesNotExist:
            return JsonResponse({"message":"sub_category_NOT_EXIST"}, status=404)
