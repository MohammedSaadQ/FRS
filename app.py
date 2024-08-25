from flask import Flask, request, jsonify
import requests
import logging

# Initialize Flask app
app = Flask(__name__)

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Create a file handler with UTF-8 encoding
log_file = 'app.log'
file_handler = logging.FileHandler(log_file, encoding='utf-8')
file_handler.setLevel(logging.DEBUG)

# Create a console handler (optional)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)

# Create a formatter and set it for both handlers
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Add handlers to the logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)

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
                customer_data = response.json()
                logger.debug(f"Received customer data: {customer_data}")
            except ValueError:
                logger.error("Failed to parse the JSON response from the external API.")
                return jsonify({"error": "Failed to parse the JSON response from the external API."}), 500

            if isinstance(customer_data, list) and len(customer_data) > 0:
                logger.debug("Returning successful response with customer data.")
                return jsonify({"customer_data": customer_data}), 200
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
