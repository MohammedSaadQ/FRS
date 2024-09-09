from flask import Flask, request, jsonify
import requests
import logging
import json
# Initialize Flask app
app = Flask(__name__)
# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
log_file = 'app.log'
file_handler = logging.FileHandler(log_file, encoding='utf-8')
file_handler.setLevel(logging.DEBUG)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)
logger.addHandler(file_handler)
logger.addHandler(console_handler)
# Function to set variables based on the retrieved customer data and return as a dictionary
def set_variables_from_data(customer_data):
    if isinstance(customer_data, dict):
        return {
            "Ingredients": str(customer_data.get("Ingredients", "")),
            "Phone_Num": str(customer_data.get("Phone_Num", "")),
            "allergy": str(customer_data.get("allergy", "")),
            "budget": str(customer_data.get("budget", "")),
            "calories": str(customer_data.get("calories", "")),
            "customer_id": str(customer_data.get("customer_id", "")),  # Updated key based on the response
            "dislikes": str(customer_data.get("dislikes", "")),
            "first_name": str(customer_data.get("first_name", "")),
            "last_name": str(customer_data.get("last_name", "")),
            "location": str(customer_data.get("location", "")),
            "preferences": str(customer_data.get("preferences", ""))
        }
    else:
        return None

# Define the API endpoint
@app.route('/get_customer_data', methods=['POST'])
def get_customer_data():
    params = request.json
    Num = params.get("PhNum")
    
    if Num is None:
        return jsonify({"error": "No customer Phone_Num provided."}), 400
    
    try:
        api_url = f"https://mysara210.pythonanywhere.com/get_customer?Phone_Num={Num}"
        response = requests.get(api_url)  # Adding a timeout for the request
        
        if response.status_code == 200:
            try:
                customer_data = response.json()  # This should return a list based on the example response
                
                # Check if it's a list and extract the first element
                if isinstance(customer_data, list) and len(customer_data) > 0:
                    customer_data = customer_data[0]  # Extract the first element from the list

            except ValueError:
                return jsonify({"error": "Failed to parse the JSON response from the external API."}), 500
            except Exception as e:  # Catch any other exception during JSON parsing
                return jsonify({"error": f"Unexpected error: {str(e)}"}), 500

            if isinstance(customer_data, dict):
                response_data = set_variables_from_data(customer_data)
                if response_data is None:
                    return jsonify({"error": "Failed to process customer data."}), 500
                
                # Return the dictionary as JSON
                return jsonify(response_data), 200
            else:
                return jsonify({"error": "Unexpected data format received from the external API."}), 500
        else:
            return jsonify({"error": f"Failed to fetch customer data. Status code: {response.status_code}"}), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

def get_ibm_token():
    API_KEY = "tAqvF4CdCAl9Ly4TrNECn-p1t_KyCHqbrYa_XXUQldul"
    token_response = requests.post(
        'https://iam.cloud.ibm.com/identity/token',
        data={"apikey": API_KEY, "grant_type": 'urn:ibm:params:oauth:grant-type:apikey'}
    )
    return token_response.json()["access_token"]
# Recommendation function
@app.route('/recommendation', methods=['POST'])
def recommendation():
    params = request.json
    customer_id = params.get("id")
    loc = str(params.get("location"))
    pref = str(params.get("prefernces"))
    customer_id =str(customer_id)
    print(customer_id)
    print(params.get("id"))
    print(pref)
    # Get the IBM Cloud OAuth token
    mltoken = get_ibm_token()
    
    # Construct the question
    question = f"recommend 3 dishes for customer with ID = {customer_id} that share the same location as the customer ({loc}) and do not recommend dishes that share ingredients with the customer's dislikes and allergies. recommend dishes that share ingredients with the customer's preferences. recommend dishes whose calories do not exceed the customer's calorie limit. recommend dishes whose price is less than or equal to the customer's budget. Please note customer {customer_id} prefers {pref}. make well-rounded suggestions. only respond with the Recommendation number, dish name and restaurant name and calories for the dish and the budget for the dish."
    
    # Prepare the messages payload
    messages = [{"role": "user", "content": question}]
    
    # Prepare the header
    header = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + mltoken}
    
    # Prepare the payload
    payload_scoring = {
        "input_data": [
            {
                "fields": ["Search", "access_token"],
                "values": [messages, [mltoken]]
            }
        ]
    }
    
    # Make the request to the Watson ML model deployment
    response_scoring = requests.post(
        'https://us-south.ml.cloud.ibm.com/ml/v4/deployments/af66b1fa-ad2b-489d-b127-f33556fce10b/predictions?version=2021-05-01',
        json=payload_scoring,
        headers=header
    )
    
    # Parse the response
    response_json = response_scoring.json()
    if "predictions" in response_json and len(response_json["predictions"]) > 0:
        prediction = response_json["predictions"][0]

    # Check if "values" contain valid data
    if "values" in prediction and len(prediction["values"]) > 1:
        recommendations_text = prediction["values"][1]
        recommendations_list = recommendations_text.split("\n\n")  # Split by double new lines

        # Format each recommendation as a separate response
        responses = []
        for item in recommendations_list:
            # Clean up the item by stripping leading/trailing spaces and newlines
            response = {"text": item.strip()}
            responses.append(response)

        # Initialize the list for cleaned recommendations
        cleaned_recommendations = []

        # Iterate over the responses and extract the recommendation details
        for item in responses:
            # Split the single string in 'text' into individual lines by using "\n"
            details = item['text'].split("\n")

            if len(details) >= 4 :
                    # Extract the recommendation details from the updated format
                    dish_number = details[0].split('Recommendation ')[1].strip()  # Strip any extra spaces
                    dish_number = dish_number[0]
                    dish_name = details[1].split(": ")[1].strip()
                    restaurant_name = details[2].split(": ")[1].strip()
                    calories = int(details[3].split(": ")[1].strip())
                    price = int(details[4].split(": ")[1].strip())  # Assuming budget refers to price
                   
                    # Store the cleaned recommendation
                    recommendation = {
                        "Recommendation": dish_number,
                        "DishName": dish_name,
                        "RestaurantName": restaurant_name,
                        "Calories": calories,
                        "Price": price
                    }
                    # Append the cleaned recommendation to the list
                    cleaned_recommendations.append(recommendation)
                
        return jsonify({"Recommendations": cleaned_recommendations}),200

        # Return the response as JSON
        #return jsonify(answer), 200
 
        
# Matching function
@app.route('/matching', methods=['POST'])
def matching():
    try:
        # Extract parameters from the request
        data = request.json
        restaurant = data.get("restaurant", "")
        meal = data.get("meal", "")
        # Get the IBM Cloud OAuth token
        mltoken = get_ibm_token()
        # Construct the prompt
        prompt = f"only based the document please Find the dish that matches '{meal}' from '{restaurant}' and don't mind any typos  ."
        # Prepare the messages payload
        messages1 = [{"role": "user", "content": prompt}]
        # Prepare the header
        header = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + mltoken}
        # Prepare the payload
        payload_scoring = {
            "input_data": [
                {
                    "fields": ["Search", "access_token"],
                    "values": [messages1, [mltoken]]
                }
            ]
        }
        # Make the request to the Watson ML model deployment
        response_scoring = requests.post(
        'https://us-south.ml.cloud.ibm.com/ml/v4/deployments/af66b1fa-ad2b-489d-b127-f33556fce10b/predictions?version=2021-05-01',
        json=payload_scoring,
        headers=header
    )
        # Parse the response
        answer = response_scoring.json()["predictions"][0]["values"][1]
        # Return the response as JSON
        answer = {"matchResult": answer}
        return jsonify(answer), 200
    except Exception as e:
        logger.error(f"An error occurred in the matching function: {str(e)}")
        return jsonify({"error": str(e)}), 500
# Run the Flask app
if __name__ == '__main__':
    app.run(port=8080)
