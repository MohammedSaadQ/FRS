import requests

def main(params):
    # Extract the 'id' value from the parameters
    customer_id = params.get("id")

    if customer_id is not None:
        try:
            # Make a request to the external API using the 'id' value
            api_url = f"https://mysara210.pythonanywhere.com/get_customer?id={customer_id}"
            response = requests.get(api_url)
            
            # Check if the request was successful
            if response.status_code == 200:
                try:
                    customer_data = response.json()  # Attempt to parse JSON data
                except ValueError:
                    return {
                        "headers": {
                            "Content-Type": "application/json",
                        },
                        "statusCode": 500,
                        "body": {
                            "error": "Failed to parse the JSON response from the external API."
                        }
                    }
                
                # Check if the JSON data is in the expected format
                if isinstance(customer_data, list) and len(customer_data) > 0:
                    return {
                        "headers": {
                            "Content-Type": "application/json",
                        },
                        "statusCode": 200,
                        "body": {
                            "customer_data": customer_data
                        }
                    }
                else:
                    return {
                        "headers": {
                            "Content-Type": "application/json",
                        },
                        "statusCode": 500,
                        "body": {
                            "error": "Unexpected data format received from the external API."
                        }
                    }
            else:
                # Handle the case where the API request fails
                return {
                    "headers": {
                        "Content-Type": "application/json",
                    },
                    "statusCode": response.status_code,
                    "body": {
                        "error": f"Failed to retrieve data for id {customer_id}. API response code: {response.status_code}"
                    }
                }
        except Exception as e:
            # Handle any other exceptions that occur
            return {
                "headers": {
                    "Content-Type": "application/json",
                },
                "statusCode": 500,
                "body": {
                    "error": f"An error occurred: {str(e)}"
                }
            }
    else:
        # If 'id' is not provided, return an error
        return {
            "headers": {
                "Content-Type": "application/json",
            },
            "statusCode": 400,
            "body": {
                "error": "No 'id' parameter provided. Please provide a valid customer ID."
            }
        }
