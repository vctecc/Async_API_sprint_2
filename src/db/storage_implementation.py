from elasticsearch import AsyncElasticsearch

es: AsyncElasticsearch = None


# Функция понадобится при внедрении зависимостей
async def get_storage() -> AsyncElasticsearch:
    return es
