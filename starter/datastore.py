import os
from google.api_core.client_options import ClientOptions
from google.cloud import discoveryengine_v1 as discoveryengine


# Definition of a tool that accesses a Vertex AI Search Datastore
#
# This is based on code provided by Google at
# https://cloud.google.com/generative-ai-app-builder/docs/samples/genappbuilder-search
#
# The object definitions aren't available to all IDEs because of Google's ProtoBuf
# implementation, so the IDE may generate a warning, but work fine. I've used
# dicts here instead, but indicated the Class that could be used instead.
# You can see the definitions at
# https://cloud.google.com/python/docs/reference/discoveryengine/latest/google.cloud.discoveryengine_v1.types
#
def search(
    project_id: str,
    location: str,
    engine_id: str,
    search_query: str,
) -> list[str]:
    # For more information, refer to:
    # https://cloud.google.com/generative-ai-app-builder/docs/locations#specify_a_multi-region_for_your_data_store
    client_options = (
        ClientOptions(api_endpoint=f"{location}-discoveryengine.googleapis.com")
        if location != "global"
        else None
    )

    # Create a client
    client = discoveryengine.SearchServiceClient(client_options=client_options)

    # The full resource name of the search app serving config
    serving_config = f"projects/{project_id}/locations/{location}/collections/default_collection/engines/{engine_id}/servingConfigs/default_config"

    # discoveryengine.SearchRequest - Using dict format for compatibility
    request = {
        "request": {
            "servingConfig": serving_config,
            "query": search_query,
            "contentSearchSpec": {
                "type": "DOCUMENTS",
                "spec": [
                    {"field": "title", "weight": 1.0},
                    {"field": "description", "weight": 2.0},
                ],
            },
            "pageLimit": 5,
            "topK": 3,
        }
    }

    page_result = client.search(request)

    # Completed: Format and return the results - Convert to list of strings
    results = []
    for result in page_result.results:
        if hasattr(result, "content"):
            content = (
                result.content.get("text", "")
                if isinstance(result.content, dict)
                else str(result.content)
            )
            results.append(content[:500])  # Limit length for readability

    return results


# Completed: Implement a tool that calls search() and returns processed results
def datastore_search_tool(search_query: str):
    """
    Search the Vertex AI Search Datastore for information about Betty's Bird Boutique.

    Args:
        query (str): The search query to look up in documents

    Returns:
        list[str]: List of document snippets relevant to the query
    """
    # Get configuration from environment variables with defaults
    project_id = os.environ.get("DATASTORE_PROJECT_ID", "")
    engine_id = os.environ.get("DATASTORE_ENGINE_ID", "")
    location = os.environ.get("DATASTORE_LOCATION", "global")

    # Call the search function
    try:
        results = search(project_id, location, engine_id, search_query)
        if not results:
            return "No results found."
        return results
    except Exception as e:
        return f"A problem occurred: {e}"
