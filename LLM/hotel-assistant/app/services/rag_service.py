from langchain_openai import OpenAIEmbeddings
from langchain_elasticsearch import ElasticsearchStore
from app.core.config import settings
from app.models.hotel import Hotel, Location
import requests

embeddings = OpenAIEmbeddings(api_key=settings.OPENAI_API_KEY)  # type: ignore

# es_store = ElasticsearchStore(
#     index_name=settings.ES_INDEX,
#     es_url=settings.ES_URL,
#     es_user=settings.ES_USER,
#     es_password=settings.ES_PASS,
#     embedding=embeddings,
# )

es_store = ElasticsearchStore.from_documents(
    documents=[],  # empty or preloaded LangChain documents
    embedding=embeddings,
    index_name=settings.ES_INDEX,
    es_url=settings.ES_URL,
    # es_user=settings.ES_USER,
    # es_password=settings.ES_PASS,
    # strategy="script_score"  # Use script_score to avoid KNN incompatibility
)


def check_elasticsearch_status():
    """Check if Elasticsearch is running and the index exists with documents."""
    try:
        # Check if Elasticsearch is running
        health_response = requests.get(f"{settings.ES_URL}/_cluster/health")
        if health_response.status_code == 200:
            health_data = health_response.json()
            print(f"✅ Elasticsearch is running. Status: {health_data.get('status')}")
        else:
            print(f"❌ Elasticsearch health check failed: {health_response.status_code}")
            return False
        
        # Check if the index exists
        index_response = requests.get(f"{settings.ES_URL}/{settings.ES_INDEX}")
        if index_response.status_code == 200:
            index_data = index_response.json()
            
            # Try different possible response structures
            doc_count = 0
            if settings.ES_INDEX in index_data:
                index_info = index_data[settings.ES_INDEX]
                
                # Check for different possible structures
                if 'total' in index_info:
                    if 'docs' in index_info['total']:
                        doc_count = index_info['total']['docs']['count']
                    else:
                        doc_count = index_info['total'].get('count', 0)
                elif 'docs' in index_info:
                    doc_count = index_info['docs'].get('count', 0)
                else:
                    # Try to get count from stats
                    stats_response = requests.get(f"{settings.ES_URL}/{settings.ES_INDEX}/_stats")
                    if stats_response.status_code == 200:
                        stats_data = stats_response.json()
                        doc_count = stats_data.get('indices', {}).get(settings.ES_INDEX, {}).get('total', {}).get('docs', {}).get('count', 0)
            
            print(f"✅ Index '{settings.ES_INDEX}' exists with {doc_count} documents")
            return doc_count > 0
        else:
            print(f"❌ Index '{settings.ES_INDEX}' not found: {index_response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error checking Elasticsearch status: {e}")
        return False


def recommend_hotels(query: str, top_k: int = 5) -> list[Hotel]:
    # Check Elasticsearch status first
    if not check_elasticsearch_status():
        print("❌ Elasticsearch is not available or index is empty")
        return []
    
    try:
        # First, let's try the LangChain search to see what it returns
        results = es_store.similarity_search(query, k=top_k)
        
        if len(results) == 0:
            print("❌ No results found from LangChain search")
            return []
        
        # If LangChain results are empty, try direct Elasticsearch query
        if not results[0].metadata and len(results[0].page_content) == 0:
            return recommend_hotels_direct(query, top_k)
        
    except Exception as e:
        print(f"❌ Error during LangChain search: {e}")
        return recommend_hotels_direct(query, top_k)
    
    hotels = []
    
    for r in results:
        # Extract data from the nested structure
        basics = r.metadata.get("basics", {})
        amenities = r.metadata.get("amenities", {})
        all_locations = r.metadata.get("allLocations", [])
        
        # Handle location data
        location = None
        if all_locations and len(all_locations) > 0:
            # Assuming the first location in the array
            loc_data = all_locations[0].get("locations", {})
            if loc_data:
                location = Location(
                    lon=loc_data.get("lon", 0.0),
                    lat=loc_data.get("lat", 0.0)
                )
        
        # Handle highlights and local_tips (they might be strings that need splitting)
        highlights = basics.get("highlights", "")
        if isinstance(highlights, str):
            highlights = [h.strip() for h in highlights.split(",") if h.strip()]
        elif not isinstance(highlights, list):
            highlights = []
            
        local_tips = basics.get("local_tips", "")
        if isinstance(local_tips, str):
            local_tips = [tip.strip() for tip in local_tips.split(",") if tip.strip()]
        elif not isinstance(local_tips, list):
            local_tips = []
        
        hotel = Hotel(
            id=basics.get("id", ""),
            title=basics.get("title", basics.get("name", "")),  # Fallback to name if title not available
            description=r.page_content,  # This should contain the embedding_text
            amenities=amenities,
            location=location or Location(lon=0.0, lat=0.0),  # Default location if not found
            highlights=highlights,
            local_tips=local_tips,
            url=basics.get("url", "")
        )
        
        hotels.append(hotel)
    
    return hotels


def recommend_hotels_direct(query: str, top_k: int = 5) -> list[Hotel]:
    """Direct Elasticsearch query as fallback when LangChain doesn't work."""
    
    try:
        # Create a simple text search query
        search_query = {
            "query": {
                "multi_match": {
                    "query": query,
                    "fields": ["basics.name^2", "basics.title^2", "basics.short_description", "embedding_text"],
                    "type": "best_fields"
                }
            },
            "size": top_k
        }
        
        search_response = requests.post(
            f"{settings.ES_URL}/{settings.ES_INDEX}/_search",
            json=search_query
        )
        
        if search_response.status_code != 200:
            print(f"❌ Direct search failed: {search_response.status_code}")
            return []
        
        search_data = search_response.json()
        hits = search_data.get("hits", {}).get("hits", [])
        
        hotels = []
        for hit in hits:
            doc = hit["_source"]
            
            # Extract data from the document
            basics = doc.get("basics", {})
            amenities = {
                key: value for key, value in doc.get("amenities", {}).items()
                if value
            }
            all_locations = doc.get("allLocations", [])
            
            # Handle location data
            location = None
            if all_locations and len(all_locations) > 0:
                loc_data = all_locations[0].get("locations", {})
                if loc_data:
                    location = Location(
                        lon=loc_data.get("lon", 0.0),
                        lat=loc_data.get("lat", 0.0)
                    )
            
            # Handle highlights and local_tips
            highlights = basics.get("highlights", "")
            if isinstance(highlights, str):
                highlights = [h.strip() for h in highlights.split(",") if h.strip()]
            elif not isinstance(highlights, list):
                highlights = []
                
            local_tips = basics.get("local_tips", "")
            if isinstance(local_tips, str):
                local_tips = [tip.strip() for tip in local_tips.split(",") if tip.strip()]
            elif not isinstance(local_tips, list):
                local_tips = []
            
            hotel = Hotel(
                id=basics.get("id", ""),
                title=basics.get("title", basics.get("name", "")),
                description=doc.get("embedding_text", ""),
                amenities=amenities,
                location=location or Location(lon=0.0, lat=0.0),
                highlights=highlights,
                local_tips=local_tips,
                url=basics.get("url", "")
            )
            
            hotels.append(hotel)
        
        return hotels
        
    except Exception as e:
        print(f"❌ Error in direct search: {e}")
        return []
