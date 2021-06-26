import pytest

API_URL = "/genre/"


@pytest.mark.asyncio
async def test_genres(make_get_request, initialize_environment, expected_json_response):
    response = await make_get_request(f"{API_URL}")
    assert response.status == 200
    assert response.body == expected_json_response


@pytest.mark.asyncio
async def test_genre_by_id(make_get_request, initialize_environment, expected_json_response):
    some_id = "04f28f12-ff34-4f91-93d1-777b27d1b0e1"
    response = await make_get_request(f"{API_URL}{some_id}")
    assert response.status == 200
    assert response.body == expected_json_response


@pytest.mark.asyncio
async def test_genres_search(make_get_request, initialize_environment, expected_json_response):
    response = await make_get_request(f"{API_URL}search/",
                                      params={
                                          "query": "Comedy",
                                        }
                                      )
    assert response.status == 200
    assert response.body == expected_json_response


@pytest.mark.asyncio
@pytest.mark.parametrize(
    (
            "page_number", "page_size", "expected_count"
    ),
    (
            (1, 10000, 26),
            (1, 10, 10),
            (3, 10, 6),
            (4, 10, 0),
            (1, 2, 2),
    )
)
async def test_search_genre_pagination(make_get_request,
                                       initialize_environment,
                                       page_number,
                                       page_size,
                                       expected_count):
    response = await make_get_request(f"{API_URL}search/",
                                      params={
                                          "page": page_number,
                                          "size": page_size}
                                      )
    assert response.status == 200
    assert len(response.body) == expected_count


@pytest.mark.asyncio
@pytest.mark.parametrize(
    (
            "page_number", "page_size"
    ),
    (
            (0, 1),
            (1, 0),
            (-1, 1),
            (1, -1),
            (-1, -1),
            ("str", 1),
            (1, "str"),
            (1.1, 1),
            (1, 1.1)
    )
)
async def test_search_person_pagination_invalid_input(make_get_request,
                                                      initialize_environment,
                                                      page_number,
                                                      page_size):
    response = await make_get_request(f"{API_URL}search/",
                                      params={
                                          "page": page_number,
                                          "size": page_size}
                                      )
    assert response.status == 422


@pytest.mark.asyncio
async def test_genres_cache(make_get_request, initialize_environment, es_client, expected_json_response):
    # Запрашиваем данные. Они должны поместиться в кэш.
    response = await make_get_request(f"{API_URL}")
    assert response.status == 200
    assert response.body == expected_json_response

    # Удаляем индекс.
    await es_client.indices.delete(index="genre", ignore=[400, 404])

    # Запрашиваем данные ещё раз — они должны вернуться из кэша.
    response = await make_get_request(f"{API_URL}")
    assert response.status == 200
    assert response.body == expected_json_response
