from flask import Flask, request, jsonify
import requests
import logging

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
            "allergy": str(customer_data.get("allergy", "")),
            "budget": str(customer_data.get("budget", "")),
            "calories": str(customer_data.get("calories", "")),
            "customerid": str(customer_data.get("customerid", "")),
            "dislikes": str(customer_data.get("dislikes", "")),
            "location": str(customer_data.get("location", "")),
            "preferences": str(customer_data.get("preferences", ""))
        }
    else:
        logger.error("Data is not in the expected format.")
        return None

# Define the API endpoint
@app.route('/get_customer_data', methods=['POST'])
def get_customer_data():
    params = request.json
    customer_id = params.get("id")
    logger.debug(f"Received request with customer ID: {customer_id}")

    if customer_id is None:
        logger.error("No customer ID provided.")
        return jsonify({"error": "No customer ID provided."}), 400

    try:
        api_url = f"https://mysara210.pythonanywhere.com/get_customer?id={customer_id}"
        logger.debug(f"Making API request to: {api_url}")
        response = requests.get(api_url)

        if response.status_code == 200:
            try:
                customer_data = response.json()  # Assume this returns a dictionary
                logger.debug(f"Received customer data: {customer_data}")
            except ValueError:
                logger.error("Failed to parse the JSON response from the external API.")
                return jsonify({"error": "Failed to parse the JSON response from the external API."}), 500

            if isinstance(customer_data, dict):
                response_data = set_variables_from_data(customer_data)
                if response_data is None:
                    return jsonify({"error": "Failed to process customer data."}), 500
                
                # Return the dictionary as JSON
                return jsonify(response_data), 200
            else:
                logger.error("Unexpected data format received from the external API.")
                return jsonify({"error": "Unexpected data format received from the external API."}), 500
        else:
            logger.error(f"Failed to fetch customer data. Status code: {response.status_code}")
            return jsonify({"error": f"Failed to fetch customer data. Status code: {response.status_code}"}), response.status_code

    except Exception as e:
        logger.error(f"An error occurred during the API request: {str(e)}")
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

# Run the Flask app
if __name__ == '__main__':
    app.run(port=8080)
