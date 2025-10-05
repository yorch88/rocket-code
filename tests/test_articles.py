def test_crud_flow(client):
    headers = {"x-api-key":"47da9ef4-0a22-4625-89f3-ef7025a64192"}
    r = client.post("/articles", headers=headers, json={"title":"Big","body":"Fish","tags":["t"],"author":"Wallace"})
    assert r.status_code == 201, r.text
    aid = r.json()["id"]
    r = client.get(f"/articles/{aid}", headers=headers); assert r.status_code == 200
    r = client.put(f"/articles/{aid}", headers=headers, json={"title":"Big New"}); assert r.status_code == 200
    r = client.get("/articles", headers=headers); assert r.status_code == 200
    r = client.get("/articles/search", headers=headers, params={"q":"Big"}); assert r.status_code == 200
    r = client.delete(f"/articles/{aid}", headers=headers); assert r.status_code == 204
