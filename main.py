import requests
import logging

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

def main(params):
    customer_id = params.get("id")
    logger.debug(f"Received request with customer ID: {customer_id}")

    if customer_id is None:
        logger.error("No customer ID provided.")
        return {
            "headers": {"Content-Type": "application/json"},
            "statusCode": 400,
            "body": {"error": "No customer ID provided."}
        }

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
                return {
                    "headers": {"Content-Type": "application/json"},
                    "statusCode": 500,
                    "body": {"error": "Failed to parse the JSON response from the external API."}
                }

            if isinstance(customer_data, list) and len(customer_data) > 0:
                logger.debug("Returning successful response with customer data.")
                return {
                    "headers": {"Content-Type": "application/json"},
                    "statusCode": 200,
                    "body": {"customer_data": customer_data}
                }
            else:
                logger.error("Unexpected data format received from the external API.")
                return {
                    "headers": {"Content-Type": "application/json"},
                    "statusCode": 500,
                    "body": {"error": "Unexpected data format received from the external API."}
                }
        else:
            logger.error(f"Failed to fetch customer data. Status code: {response.status_code}")
            return {
                "headers": {"Content-Type": "application/json"},
                "statusCode": response.status_code,
                "body": {"error": f"Failed to fetch customer data. Status code: {response.status_code}"}
            }
    except Exception as e:
        logger.error(f"An error occurred during the API request: {str(e)}")
        return {
            "headers": {"Content-Type": "application/json"},
            "statusCode": 500,
            "body": {"error": f"An error occurred: {str(e)}"}
        }
