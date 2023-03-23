import requests
import json
from .models import CarDealer
from requests.auth import HTTPBasicAuth


# Create a `get_request` to make HTTP GET requests
# e.g., response = requests.get(url, params=params, headers={'Content-Type': 'application/json'},
#                                     auth=HTTPBasicAuth('apikey', api_key))

def get_request(url, **kwargs):
    print(kwargs)
    print("GET from {} ".format(url))
    try:
        # Call get method of requests library with URL and parameters
        response = requests.get(url, headers={'Content-Type': 'application/json'},
                                    params=kwargs)
    except:
        # If any error occurs
        print("Network exception occurred")
    status_code = response.status_code
    print("With status {} ".format(status_code))
    json_data = json.loads(response.text)
    return json_data

# Create a `post_request` to make HTTP POST requests
# e.g., response = requests.post(url, params=kwargs, json=payload)


# Create a get_dealers_from_cf method to get dealers from a cloud function
# def get_dealers_from_cf(url, **kwargs):
# - Call get_request() with specified arguments
# - Parse JSON results into a CarDealer object list

def get_dealers_from_cf(url, **kwargs):
    results = []
    state = kwargs.get("state")
    if state:
        json_result = get_request(url, state=state)
    else:
        json_result = get_request(url)

    if json_result:
        dealers = json_result
        for dealer in dealers:
            dealer_doc = dealer["doc"]
            dealer_obj = CarDealer(address=dealer_doc["address"], 
            city=dealer_doc["city"],
            id=dealer_doc["id"], 
            lat=dealer_doc["lat"], 
            long=dealer_doc["long"], 
            full_name=dealer_doc["full_name"],
            st=dealer_doc["st"], 
            zip=dealer_doc["zip"], 
            short_name=dealer_doc["short_name"])
            results.append(dealer_obj)

    return results

def get_dealer_by_id_from_cf(url, id):
    json_result = get_request(url, id=id)
    print('json_result from line 54',json_result)
    if json_result:
        dealers = json_result
        dealer_doc = dealers[0]
        dealer_obj = CarDealer(address=dealer_doc["address"], city=dealer_doc["city"],
                                id=dealer_doc["id"], 
                                lat=dealer_doc["lat"], 
                                long=dealer_doc["long"], 
                                full_name=dealer_doc["full_name"],
                                short_name=dealer_doc["short_name"], 
                                st=dealer_doc["st"], 
                                zip=dealer_doc["zip"])
    return dealer_obj

def get_dealer_reviews_from_cf(url, **kwargs):
    results = []
    id = kwargs.get("id")
    if id:
        json_result = get_request(url, id=id)
    else:
        json_result = get_request(url)
    if json_result:
        reviews = json_result["data"]["docs"]
        for review in reviews:
            if review["purchase"]:
                review_obj = DealerReview(
                    dealership=review["dealership"],
                    name=review["name"],
                    purchase=review["purchase"],
                    review=review["review"],
                    purchase_date=review["purchase_date"],
                    car_make=review["car_make"],
                    car_model=review["car_model"],
                    car_year=review["car_year"],
                    sentiment=analyze_review_sentiments(review["review"]),
                    id=review['id']
                )
            else:
                review_obj = DealerReview(
                    dealership=review["dealership"],
                    name=review["name"],
                    purchase=review["purchase"],
                    review=review["review"],
                    purchase_date=None,
                    car_make=None,
                    car_model=None,
                    car_year=None,
                    sentiment=analyze_review_sentiments(review["review"]),
                    id=review['id']
                )
            results.append(review_obj)
    return results
 
def analyze_review_sentiments(text):
    url = "https://api.us-east.natural-language-understanding.watson.cloud.ibm.com/instances/4dbc0d27-777d-4dc2-974e-b945af37db61"
    api_key = "shmuyWvm6d_piet7ooNO5euiYemxIjjz9dHgWzdS0ad_"
    authenticator = IAMAuthenticator(api_key)
    natural_language_understanding = NaturalLanguageUnderstandingV1(version='2021-08-01',authenticator=authenticator)
    natural_language_understanding.set_service_url(url)
    response = natural_language_understanding.analyze( text=text+"hello hello hello",features=Features(sentiment=SentimentOptions(targets=[text+"hello hello hello"]))).get_result()
    label=json.dumps(response, indent=2)
    label = response['sentiment']['document']['label']
    print(label)
    
    return(label) 