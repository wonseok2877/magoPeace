import json
import bcrypt
import jwt
import datetime

from django.views           import View
from django.http            import JsonResponse
from django.db.utils        import DataError, IntegrityError
from django.db.models       import Avg
from django.db.models.query import Prefetch

from json.decoder           import JSONDecodeError

import my_settings
from users.models           import User
from restaurants.models     import Food, Image
from users.utils            import ConfirmUser

class SignInView(View):
    def post(self,request):
        try:
            data = json.loads(request.body)
            user = User.objects.get(email=data["email"])
            
            if not bcrypt.checkpw(data["password"].encode(), user.password.encode()):
                return JsonResponse({"message":"VALIDATION_ERROR"}, status=400)        

            exp           = datetime.datetime.now() + datetime.timedelta(hours=24)
            access_token  = jwt.encode(
                payload   = {"id" : user.id, "exp" : exp},
                key       = my_settings.SECRET_KEY,
                algorithm = my_settings.ALGORITHM
            )

            return JsonResponse({"message":"SUCCESS", "access_token":access_token}, status=200)

        except KeyError:
            return JsonResponse({"message":"KEY_ERROR"}, status=400)   
        
        except User.DoesNotExist:
            return JsonResponse({"message":"USER_NOT_EXIST"}, status=404)       

        except DataError:
            return JsonResponse({"message": "DATA_ERROR"}, status=400) 

class SignupView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            
            if not User.validate(data):
                return JsonResponse({"message":"VALIDATION_ERROR"}, status=401)        

            bcrypt_password = bcrypt.hashpw(data["password"].encode("utf-8"), bcrypt.gensalt()).decode()

            User.objects.create(
                nickname     = data["nickname"],
                email        = data["email"],
                password     = bcrypt_password,
                phone_number = data["phone_number"],
            )

            return JsonResponse({"message":"SUCCESS"}, status=201)

        except JSONDecodeError:
            return JsonResponse({"message":"JSON_DECODE_ERROR"}, status=400)        
        
        except KeyError:
            return JsonResponse({"message":"KEY_ERROR"}, status=400)        
        
        except DataError:
            return JsonResponse({"message": "DATA_ERROR"}, status=400)

        except IntegrityError:
            return JsonResponse({"message": "INTEGRITY_ERROR"}, status=400)


class UserDetailView(View):
    @ConfirmUser
    def get(self, request):
        restaurants = request.user.wishlist_restaurants.select_related("sub_category").prefetch_related(
            Prefetch(
                    lookup="foods",
                    queryset=Food.objects.prefetch_related(
                        Prefetch(
                            lookup="images",
                            queryset=Image.objects.all(),
                            to_attr="all_images"
                    )),
                    to_attr="all_foods"
            )
        ).annotate(average_rating=Avg("reviews__rating"))
        result = {
            "nickname"       : request.user.nickname,
            "email"          : request.user.email,
            "profileUrl"     : request.user.profile_url,
            "wishList"       : [{
                "id"             : restaurant.id,
                "name"           : restaurant.name,
                "address"        : restaurant.address,
                "subCategory"    : restaurant.sub_category.name,
                "averageRating"  : restaurant.average_rating,
                "foodImage"      : restaurant.all_foods[0].all_images[0].image_url
            } for restaurant in restaurants],
        }
        
        return JsonResponse({"message":"SUCCESS","result":result}, status=200)