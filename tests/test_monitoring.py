from http import HTTPStatus


def test_metrics_endpoint_exposes_prometheus_metrics(client):

    response = client.get('/metrics')

    assert response.status_code == HTTPStatus.OK
    assert response.headers['content-type'].startswith('text/plain')
    assert 'python_gc_objects_collected_total' in response.text
