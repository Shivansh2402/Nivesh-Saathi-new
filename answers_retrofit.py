import requests
import json

from metahackathonfinance import settings


def get_matching_response(body):
    url = f"http://{settings.answers_base_url}/api/v2/get_matching_response"
    headers = {'Content-Type': 'application/json'}

    try:
        api_response = requests.request("POST", url, headers=headers, data=body)
        if api_response.status_code == 200:
            return api_response.json()
        else:
            print(f"Error: Received status code {api_response.status_code}")
            print(f"Response: {api_response.text}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None


# Example usage
if __name__ == "__main__":
    body_val = {
        "query": "shipping cost refund",
        "categories": [],
        "excludedCategories": [],
        "tags": [],
        "user_id": "e634ecb8-18b5-4ac5-87c5-4f4238022be0",
        "bot_ref": 67387,
        "bot_locale": [
            "en"
        ],
        "default_locale": "en",
        "api_ai_client_token": "9a1fc27dfae14928a3dd01e5c0cdc698",
        "small_talk_enabled": False,
        "spell_check_enabled": "OFF",
        "semantic_search_status": "ENABLED",
        "is_ecom_ner_enabled": True,
        "is_llm_enabled": False,
        "cid": 20659,
        "query_timestamp": 1729248152514,
        "custom_logic": None,
        "is_instance": None,
        "bot_category": None,
        "is_context_enabled": False,
        "entity_enabled": True
    }
    response = get_matching_response(body_val)
    if response:
        print("API Response:")
        print(json.dumps(response, indent=4))

