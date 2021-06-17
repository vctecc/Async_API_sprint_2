import pytest


@pytest.mark.asyncio
async def test_search_person(make_get_request):
    response = await make_get_request('/person/search/', params={'query': 'Lucas'})
    assert response.status in (200, 404)
