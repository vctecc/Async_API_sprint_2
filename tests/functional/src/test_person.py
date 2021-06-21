import pytest


@pytest.mark.asyncio
async def test_search_person(make_get_request, es_from_snapshot):
    response = await make_get_request("/person/search/", params={"query": "Lucas"})
    assert response.status == 200


@pytest.mark.asyncio
async def test_person_not_found(make_get_request, es_from_snapshot):
    some_id = "this-is-not-even-an-uuid"
    response = await make_get_request(f"/person/{some_id}", params={})
    assert response.status == 404


@pytest.mark.asyncio
async def test_person_by_id(make_get_request, es_from_snapshot):
    some_id = "239f6e94-b317-4f10-bb0c-ef86dfe33d8a"
    response = await make_get_request(f"/person/{some_id}", params={})
    print(response.body)
    assert response.status == 200
