import pytest

API_URL = '/film/'


@pytest.mark.asyncio
async def test_film_get_by_id(make_get_request, initialize_environment,
                              expected_json_response):
    some_id = "0fdad8d4-6672-46a4-b5c6-529faa368ac7"
    response = await make_get_request(f"{API_URL}{some_id}", {})
    assert response.status == 200
    assert response.body == expected_json_response


@pytest.mark.asyncio
async def test_film_get_all(make_get_request, initialize_environment):
    response = await make_get_request(API_URL, {})
    assert response.status == 200
    assert len(response.body) == 10


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("page_size", "page_number"),
    (
        (1, 1), (1, 2), (50, 1))
    )
async def test_film_paging(make_get_request, initialize_environment,
                           page_size, page_number):
    response = await make_get_request(
        API_URL,
        {"page[number]": page_number, "page[size]": page_size}
    )
    assert response.status == 200
    assert len(response.body) == page_size


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("page_number", "page_size"),
    (
        (0, 1), (1, 0), (-1, 1), (1, -1),
    )
)
async def test_film_paging_invalid_page(make_get_request, initialize_environment,
                                        page_number, page_size):
    response = await make_get_request(
        f"{API_URL}search/",
        {"page[number]": page_number, "page[size]": page_size}
    )
    assert response.status == 422


@pytest.mark.asyncio
async def test_film_search(make_get_request, initialize_environment,
                           expected_json_response):
    response = await make_get_request(
        f"{API_URL}search/",
        {"query": "The Reality"}
    )
    assert response.status == 200
    assert len(response.body) == 10
    assert response.body == expected_json_response


@pytest.mark.asyncio
async def test_film_search_unknown(make_get_request, initialize_environment):
    response = await make_get_request(
        f"{API_URL}search/",
        {"query": "UnknownFilm"}
    )
    assert response.status == 200
    assert len(response.body) == 0


@pytest.mark.asyncio
async def test_film_filter_genre(make_get_request, initialize_environment):
    response = await make_get_request(
        API_URL,
        {"filter[genre]": "d55e7647-bf7a-4011-8f4c-04025adfa127"}
    )
    assert response.status == 200
    assert len(response.body) == 10


@pytest.mark.asyncio
async def test_film_filter_unknown_genre(make_get_request, initialize_environment):
    response = await make_get_request(
        API_URL,
        {"filter[genre]": "deadbeaf"}
    )
    assert response.status == 200
    assert len(response.body) == 0


@pytest.mark.asyncio
async def test_film_cache(make_get_request, initialize_environment, es_client):
    request = (f"{API_URL}", {"page[number]": 1, "page[size]": 1})
    cache_response = await make_get_request(*request)
    assert cache_response.status == 200
    await es_client.indices.delete(index="movies", ignore=[400, 404])

    response = await make_get_request(*request)
    assert response.status == 200
    assert response.body == cache_response.body
