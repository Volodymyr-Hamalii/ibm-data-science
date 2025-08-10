from fastapi import APIRouter, Query
from app.services.rag_service import recommend_hotels
from app.models.hotel import Hotel

router = APIRouter()

@router.get("/recommendations", response_model=list[Hotel])
async def hotel_recommendations(
        query: str = Query(..., example="Family-friendly hotel with pool"),
    ) -> list[Hotel]:
    return recommend_hotels(query)

@router.get("/debug/elasticsearch")
async def debug_elasticsearch():
    """Debug endpoint to check Elasticsearch status and index information."""
    from app.core.config import settings
    import requests
    
    try:
        # Check Elasticsearch health
        health_response = requests.get(f"{settings.ES_URL}/_cluster/health")
        health_status = "unknown"
        if health_response.status_code == 200:
            health_data = health_response.json()
            health_status = health_data.get("status", "unknown")
        
        # Check index info
        index_response = requests.get(f"{settings.ES_URL}/{settings.ES_INDEX}")
        index_info = {}
        if index_response.status_code == 200:
            index_data = index_response.json()
            index_info = {
                "exists": True,
                "document_count": index_data[settings.ES_INDEX]["total"]["docs"]["count"],
                "size": index_data[settings.ES_INDEX]["total"]["store"]["size_in_bytes"]
            }
        else:
            index_info = {
                "exists": False,
                "error": f"Status code: {index_response.status_code}"
            }
        
        # Get a sample document if index exists
        sample_doc = None
        if index_info.get("exists") and index_info.get("document_count", 0) > 0:
            try:
                sample_response = requests.get(f"{settings.ES_URL}/{settings.ES_INDEX}/_search?size=1")
                if sample_response.status_code == 200:
                    sample_data = sample_response.json()
                    if sample_data.get("hits", {}).get("hits"):
                        sample_doc = sample_data["hits"]["hits"][0]["_source"]
            except Exception as e:
                sample_doc = {"error": str(e)}
        
        return {
            "elasticsearch_url": settings.ES_URL,
            "index_name": settings.ES_INDEX,
            "health_status": health_status,
            "index_info": index_info,
            "sample_document": sample_doc
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "elasticsearch_url": settings.ES_URL,
            "index_name": settings.ES_INDEX
        }

@router.get("/debug/test-search")
async def test_search():
    """Test endpoint to see what the actual search returns."""
    from app.core.config import settings
    import requests
    
    try:
        # Try a simple search query
        search_query = {
            "query": {
                "match_all": {}
            },
            "size": 1
        }
        
        search_response = requests.post(
            f"{settings.ES_URL}/{settings.ES_INDEX}/_search",
            json=search_query
        )
        
        if search_response.status_code == 200:
            search_data = search_response.json()
            hits = search_data.get("hits", {}).get("hits", [])
            
            if hits:
                doc = hits[0]["_source"]
                return {
                    "found_documents": len(hits),
                    "total_hits": search_data["hits"]["total"]["value"],
                    "sample_document_keys": list(doc.keys()),
                    "sample_document": doc
                }
            else:
                return {
                    "found_documents": 0,
                    "total_hits": 0,
                    "message": "No documents found in index"
                }
        else:
            return {
                "error": f"Search failed with status {search_response.status_code}",
                "response": search_response.text
            }
            
    except Exception as e:
        return {
            "error": str(e)
        }
