import pytest

API_URL = '/film/'


@pytest.mark.asyncio
async def test_film_get_by_id(make_get_request, create_movie_index,
                              expected_json_response):
    some_id = "010feda9-8137-453b-b1c8-1038600d4399"
    response = await make_get_request(f"{API_URL}{some_id}", {})
    assert response.status == 200
    assert response.body == expected_json_response


@pytest.mark.asyncio
async def test_film_get_all(make_get_request, create_movie_index):
    response = await make_get_request(API_URL, {})
    assert response.status == 200
    assert len(response.body) == 3


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("page_size", "page_number"),
    (
        (1, 1), (1, 2), (2, 1))
    )
async def test_film_paging(make_get_request, create_movie_index,
                           page_size, page_number):
    response = await make_get_request(
        API_URL,
        {"page[number]": page_number, "page[size]": page_size}
    )
    assert response.status == 200
    assert len(response.body) == page_size


@pytest.mark.asyncio
async def test_film_paging_invalid_page(make_get_request):
    response = await make_get_request(API_URL, {'page[number]': -1})
    assert response.status == 422


@pytest.mark.asyncio
async def test_film_search(make_get_request, create_movie_index):
    response = await make_get_request(
        f"{API_URL}search/",
        {"query": "Rogers"}
    )
    assert response.status == 200
    assert len(response.body) == 1


@pytest.mark.asyncio
async def test_film_search_unknown(make_get_request, create_movie_index):
    response = await make_get_request(
        f"{API_URL}search/",
        {"query": "UnknownFilm"}
    )
    assert response.status == 200
    assert len(response.body) == 0


@pytest.mark.asyncio
async def test_film_filter_genre(make_get_request, create_movie_index):
    response = await make_get_request(
        API_URL,
        {"filter[genre]": "b7d7086c-4778-493f-909f-04629b2bba3c"}
    )
    assert response.status == 200
    assert len(response.body) == 2


@pytest.mark.asyncio
async def test_film_filter_unknown_genre(make_get_request, create_movie_index):
    response = await make_get_request(
        API_URL,
        {"filter[genre]": "deadbeaf"}
    )
    assert response.status == 200
    assert len(response.body) == 0
