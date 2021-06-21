import pytest


@pytest.mark.asyncio
async def test_search_person(make_get_request, es_from_snapshot):
    response = await make_get_request("/person/search/", params={"query": "Lucas"})
    assert response.status == 200


@pytest.mark.asyncio
async def test_person_not_found(make_get_request, es_from_snapshot):
    some_id = "this-is-not-even-an-uuid"
    response = await make_get_request(f"/person/{some_id}")
    assert response.status == 404
    assert response.body == {"detail": "person not found"}


@pytest.mark.asyncio
async def test_person_by_id(make_get_request, es_from_snapshot):
    some_id = "239f6e94-b317-4f10-bb0c-ef86dfe33d8a"
    response = await make_get_request(f"/person/{some_id}")
    assert response.status == 200
    assert response.body == {'id': '239f6e94-b317-4f10-bb0c-ef86dfe33d8a',
                             'full_name': 'George Lucas',
                             'films': [{'id': '00a7ea86-a39d-4f6b-b790-325551aea635', 'role': 'writer'},
                                       {'id': '07725695-eca3-4584-97b4-a63b0f41f72e', 'role': 'writer'},
                                       {'id': '0b9b87af-910d-49cf-b327-874519ecb187', 'role': 'writer'},
                                       {'id': '16e85475-63d1-4707-bf8e-f86cd3c92502', 'role': 'writer'},
                                       {'id': '19f02d63-1a52-4da5-9cde-8533c03864b4', 'role': 'writer'},
                                       {'id': '23754811-0371-4113-bae0-92148a3a7205', 'role': 'writer'},
                                       {'id': '26489631-e1e2-44ca-a380-f7b5607f946a', 'role': 'writer'},
                                       {'id': '30757fe5-c5b2-49e4-ba21-305f3be45575', 'role': 'writer'},
                                       {'id': '322c645e-7ad0-49da-9412-3c5e71bab348', 'role': 'writer'},
                                       {'id': '38fde497-adea-4668-b1ec-6daf0ddd0eec', 'role': 'writer'},
                                       {'id': '23754811-0371-4113-bae0-92148a3a7205', 'role': 'director'},
                                       {'id': '26489631-e1e2-44ca-a380-f7b5607f946a', 'role': 'director'},
                                       {'id': '322c645e-7ad0-49da-9412-3c5e71bab348', 'role': 'director'},
                                       {'id': '3fdcd34b-7eb1-42ec-8480-abb660c165bc', 'role': 'director'},
                                       {'id': '6f48de57-fe7d-46d6-a09f-909d8fd54fa6', 'role': 'director'},
                                       {'id': '38dfc86f-330d-44fb-a824-a2386ec579e6', 'role': 'actor'},
                                       {'id': '47783b76-832d-4221-829b-aafd8b646d97', 'role': 'actor'},
                                       {'id': '5435a2d2-4ada-4756-ac98-3a9f1edc63d5', 'role': 'actor'},
                                       {'id': 'd749e4a3-678c-41ab-95e9-2960446f6616', 'role': 'actor'},
                                       {'id': 'd7d15cb7-dd8f-414d-acca-782c7c233171', 'role': 'actor'},
                                       {'id': 'e00117ef-913e-41f0-9d52-4ab40556a240', 'role': 'actor'}
                                       ]
                             }
