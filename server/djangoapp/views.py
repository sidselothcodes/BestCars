# Uncomment the required imports before adding the code

from .populate import initiate
from django.contrib.auth.models import User
from django.contrib.auth import logout
from django.http import JsonResponse
from django.contrib.auth import login, authenticate
import logging
import json
from django.views.decorators.csrf import csrf_exempt
from .models import CarMake, CarModel
from .restapis import get_request, analyze_review_sentiments



# Get an instance of a logger
logger = logging.getLogger(__name__)


def get_cars(request):
    """Fetches car models and makes from the database."""
    count = CarMake.objects.filter().count()
    print(count)
    if count == 0:
        initiate()
    car_models = CarModel.objects.select_related("car_make")
    cars = [
        {"CarModel": car_model.name, "CarMake": car_model.car_make.name}
        for car_model in car_models
    ]
    return JsonResponse({"CarModels": cars})


# Create a `login_request` view to handle sign-in request
@csrf_exempt
def login_user(request):
    """Authenticates user login."""
    # Get username and password from request.POST dictionary
    user_data = json.loads(request.body)
    username = user_data["userName"]
    password = user_data["password"]

    # Try to check if provided credentials can be authenticated
    user = authenticate(username=username, password=password)

    if user is not None:
        # If user is valid, log them in
        login(request, user)
        return JsonResponse({"userName": username, 
                             "status": "Authenticated"})

    return JsonResponse({"userName": username})


# Create a `logout_request` view to handle sign-out request
def logout_request(request):
    """Handles user logout."""
    logout(request)
    return JsonResponse({"userName": ""})


# Create a `registration` view to handle sign-up request
@csrf_exempt
def registration(request):
    """Handles new user registration."""
    data = json.loads(request.body)
    username = data["userName"]
    password = data["password"]
    first_name = data["firstName"]
    last_name = data["lastName"]
    email = data["email"]

    # Check if user already exists
    try:
        User.objects.get(username=username)
        return JsonResponse(
            {"userName": username, 
             "error": "Already Registered"})
    except User.DoesNotExist:
        logger.debug(f"{username} is a new user")

    # Create and login new user
    user = User.objects.create_user(
        username=username,
        first_name=first_name,
        last_name=last_name,
        password=password,
        email=email,
    )
    login(request, user)
    return JsonResponse({"userName": username, 
                         "status": "Authenticated"})


def get_dealer_details(request, dealer_id):
    """Fetch dealer details using API."""
    if dealer_id:
        endpoint = f"/fetchDealer/{dealer_id}"
        dealership = get_request(endpoint)
        if dealership:
            return JsonResponse({"status": 200, "dealer": dealership})
        return JsonResponse({"status": 404, "message": "Dealer not found"})

    return JsonResponse({"status": 400, "message": "Bad Request"})


def get_dealer_reviews(request, dealer_id):
    """Fetch reviews of a specific dealer."""
    print(f"Fetching reviews for dealer ID: {dealer_id}")
    if dealer_id:
        endpoint = f"/fetchReviews/dealer/{dealer_id}"
        print(f"Endpoint: {endpoint}")
        reviews = get_request(endpoint)
        print(f"Reviews: {reviews}")

        if reviews:
            for review_detail in reviews:
                sentiment_response = analyze_review_sentiments(
                    review_detail["review"]
                )
                review_detail["sentiment"] = sentiment_response["sentiment"]

            return JsonResponse({"status": 200, "reviews": reviews})

        return JsonResponse(
            {"status": 500, 
             "message": "Failed to fetch reviews"})

    return JsonResponse({"status": 400, "message": "Bad Request"})


# Create a `add_review` view to submit a review
@csrf_exempt
def add_review(request):
    """Handles review submissions."""
    if request.user.is_authenticated:
        try:
            response = post_review(data)
            return JsonResponse(
                {"status": 200, "message": "Review posted successfully"}
            )
        except Exception as err:
            print(f"Error: {err}")
            return JsonResponse(
                {"status": 401, "message": "Error in posting review"}
            )

    return JsonResponse({"status": 403, "message": "Unauthorized"})


def get_dealerships(request, state="All"):
    """Fetch a list of dealerships."""
    endpoint = "/fetchDealers" if state == "All" else f"/fetchDealers/{state}"
    dealerships = get_request(endpoint)
    return JsonResponse({"status": 200, "dealers": dealerships})

