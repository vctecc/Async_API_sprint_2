import pytest

from functional.settings import TestSettings

settings = TestSettings()


@pytest.mark.asyncio
async def test_search_person(make_get_request, es_from_snapshot, expected_json_response):
    response = await make_get_request("/person/search/", params={"query": "Lucas"})
    assert response.status == 200
    assert response.body == expected_json_response


@pytest.mark.asyncio
async def test_person_not_found(make_get_request, es_from_snapshot):
    some_id = "this-is-not-even-an-uuid"
    response = await make_get_request(f"/person/{some_id}")
    assert response.status == 404
    assert response.body == {"detail": "person not found"}


@pytest.mark.asyncio
async def test_person_by_id(make_get_request, es_from_snapshot, expected_json_response):
    some_id = "239f6e94-b317-4f10-bb0c-ef86dfe33d8a"
    response = await make_get_request(f"/person/{some_id}")
    assert response.status == 200
    assert response.body == expected_json_response


@pytest.mark.asyncio
async def test_person_films_by_id(make_get_request, es_from_snapshot, expected_json_response):
    some_id = "239f6e94-b317-4f10-bb0c-ef86dfe33d8a"
    response = await make_get_request(f"/person/{some_id}/film")
    print(response.body)
    assert response.status == 200
    assert response.body == expected_json_response
