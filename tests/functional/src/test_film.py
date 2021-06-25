import pytest

API_URL = '/film/'


@pytest.mark.asyncio
async def test_get_all(make_get_request, initialize_environment):
    response = await make_get_request(API_URL, {})
    assert response.status == 200


@pytest.mark.asyncio
async def test_get_by_id(make_get_request, initialize_environment):
    response = await make_get_request(API_URL + "010feda9-8137-453b-b1c8-1038600d4399", {})
    assert response.status == 200


@pytest.mark.asyncio
async def test_no_exist_film(make_get_request, initialize_environment):
    response = await make_get_request(API_URL + "ab2811a3-3295-4564-988d-1ebc2ee03ab7", {})
    assert response.status == 404
    assert response.body == {"detail": "film not found"}


@pytest.mark.asyncio
async def test_search(make_get_request, initialize_environment):
    response = await make_get_request(API_URL, {"query": "Star"})
    assert response.status == 200
    assert response.body == []


@pytest.mark.asyncio
async def test_search_not_found(make_get_request, initialize_environment):
    response = await make_get_request(API_URL, {"query": "NotFoundFilm"})
    assert response.status == 200
    assert response.body == []


@pytest.mark.asyncio
async def test_filter_genre(make_get_request):
    response = await make_get_request(
        API_URL,
        {"filter[genre]": "b7d7086c-4778-493f-909f-04629b2bba3c"}
    )
    assert response.status == 200
    assert len(response.body) == 2
