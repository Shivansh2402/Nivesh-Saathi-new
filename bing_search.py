from langchain_community.tools.bing_search import BingSearchResults
from langchain_community.utilities import BingSearchAPIWrapper
from langchain.prompts import PromptTemplate
import json

from metahackathonfinance import settings


def search_query_on_bing(user_query):
    bing_search = BingSearchResults(api_wrapper=BingSearchAPIWrapper(bing_subscription_key=settings.bing_api_key,
                                                                     bing_search_url='https://api.bing.microsoft.com/v7.0/search',
                                                                     k=10, search_kwargs={}))

    prompt = PromptTemplate(
        input_variables=["query"],
        template="Give response for the following: {query}. Provide the response in bullet points and not greater than 40 words."
    )

    response = bing_search(prompt.format(query=user_query))
    return json.loads(response.replace("'", '"'))


if __name__ == "__main__":
    r = search_query_on_bing("when should i start investing")
    print(r)
