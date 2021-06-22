import pytest


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "route, body",
    (
            ("/person/wrong-id", {"detail": "person not found"}),
            ("/person/wrong-id/film", {"detail": "person not found"}),
            ("/film/wrong-id", {"detail": "film not found"}),
            ("/absolutely_wrong_route", {"detail": "Not Found"}),
    )
)
async def test_404_routes(make_get_request, es_from_snapshot, route, body):
    response = await make_get_request(route)
    assert response.status == 404
    assert response.body == body
