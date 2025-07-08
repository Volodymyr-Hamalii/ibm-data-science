from langchain_openai import OpenAIEmbeddings
from langchain_elasticsearch import ElasticsearchStore
from app.core.config import settings
from app.models.hotel import Hotel

embeddings = OpenAIEmbeddings(api_key=settings.OPENAI_API_KEY)  # type: ignore

es_store = ElasticsearchStore(
    index_name=settings.ES_INDEX,
    es_url=settings.ES_URL,
    es_user=settings.ES_USER,
    es_password=settings.ES_PASS,
    embedding=embeddings,
)

def recommend_hotels(query: str, top_k: int = 5) -> list[Hotel]:
    results = es_store.similarity_search(query, k=top_k)
    return [
        Hotel(
            id=r.metadata["id"],
            title=r.metadata["title"],
            description=r.page_content,
            amenities=r.metadata["amenities"],
            location=r.metadata["location"],
            highlights=r.metadata["highlights"],
            local_tips=r.metadata["local_tips"],
            url=r.metadata["url"],
        )
        for r in results
    ]
