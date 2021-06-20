import pytest


@pytest.mark.asyncio
async def test_search_person(make_get_request):
    response = await make_get_request("/person/search/", params={"query": "Lucas"})
    assert response.status == 200


@pytest.mark.asyncio
async def test_person_not_found(make_get_request):
    some_id = "this-is-not-even-an-uuid"
    response = await make_get_request(f"/person/{some_id}", params={})
    assert response.status == 404
