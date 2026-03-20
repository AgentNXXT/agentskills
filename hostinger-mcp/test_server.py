import pytest
from unittest.mock import patch, MagicMock
import server


def _mock_response(data=None, status_code=200):
    mock = MagicMock()
    mock.status_code = status_code
    mock.json.return_value = data or {}
    mock.raise_for_status.return_value = None
    return mock


# ─── Billing ─────────────────────────────────────────────────────────────────

@patch("server.httpx.get")
def test_billing_get_catalog(mock_get):
    mock_get.return_value = _mock_response([{"name": ".COM", "price": 1099}])
    result = server.billing_get_catalog(category="DOMAIN")
    assert isinstance(result, list)
    mock_get.assert_called_once()


@patch("server.httpx.get")
def test_billing_get_payment_methods(mock_get):
    mock_get.return_value = _mock_response([{"id": 1, "type": "credit_card"}])
    result = server.billing_get_payment_methods()
    assert isinstance(result, list)


@patch("server.httpx.get")
def test_billing_get_subscriptions(mock_get):
    mock_get.return_value = _mock_response([{"id": "sub_1", "status": "active"}])
    result = server.billing_get_subscriptions()
    assert isinstance(result, list)


# ─── DNS ─────────────────────────────────────────────────────────────────────

@patch("server.httpx.get")
def test_dns_get_records(mock_get):
    mock_get.return_value = _mock_response({"zone": [{"name": "@", "type": "A"}]})
    result = server.dns_get_records("example.com")
    assert "zone" in result


@patch("server.httpx.put")
def test_dns_update_records(mock_put):
    mock_put.return_value = _mock_response({"success": True})
    result = server.dns_update_records("example.com", [{"name": "@", "type": "A", "records": [{"content": "1.2.3.4"}]}])
    assert result["success"] is True


@patch("server.httpx.get")
def test_dns_get_snapshots(mock_get):
    mock_get.return_value = _mock_response([{"id": 1}])
    result = server.dns_get_snapshots("example.com")
    assert isinstance(result, list)


# ─── Domains ─────────────────────────────────────────────────────────────────

@patch("server.httpx.post")
def test_domains_check_availability(mock_post):
    mock_post.return_value = _mock_response({"results": [{"tld": "com", "available": True}]})
    result = server.domains_check_availability("mysite", ["com", "net"])
    assert "results" in result


@patch("server.httpx.get")
def test_domains_get_list(mock_get):
    mock_get.return_value = _mock_response([{"domain": "example.com"}])
    result = server.domains_get_list()
    assert isinstance(result, list)


@patch("server.httpx.get")
def test_domains_get_details(mock_get):
    mock_get.return_value = _mock_response({"domain": "example.com", "status": "active"})
    result = server.domains_get_details("example.com")
    assert result["domain"] == "example.com"


# ─── Hosting ─────────────────────────────────────────────────────────────────

@patch("server.httpx.get")
def test_hosting_list_websites(mock_get):
    mock_get.return_value = _mock_response({"data": [{"domain": "mysite.com"}]})
    result = server.hosting_list_websites()
    assert "data" in result


@patch("server.httpx.post")
def test_hosting_generate_free_subdomain(mock_post):
    mock_post.return_value = _mock_response({"subdomain": "abc123.hostingersite.com"})
    result = server.hosting_generate_free_subdomain()
    assert "subdomain" in result


# ─── VPS ─────────────────────────────────────────────────────────────────────

@patch("server.httpx.get")
def test_vps_list(mock_get):
    mock_get.return_value = _mock_response([{"id": 1, "hostname": "vps1"}])
    result = server.vps_list()
    assert isinstance(result, list)


@patch("server.httpx.get")
def test_vps_get_details(mock_get):
    mock_get.return_value = _mock_response({"id": 1, "status": "running"})
    result = server.vps_get_details(1)
    assert result["status"] == "running"


@patch("server.httpx.post")
def test_vps_start(mock_post):
    mock_post.return_value = _mock_response({"action": "start"})
    result = server.vps_start(1)
    assert result["action"] == "start"


@patch("server.httpx.post")
def test_vps_stop(mock_post):
    mock_post.return_value = _mock_response({"action": "stop"})
    result = server.vps_stop(1)
    assert result["action"] == "stop"


@patch("server.httpx.get")
def test_vps_get_firewalls(mock_get):
    mock_get.return_value = _mock_response([{"id": 1, "name": "default"}])
    result = server.vps_get_firewalls()
    assert isinstance(result, list)


@patch("server.httpx.get")
def test_vps_docker_list_projects(mock_get):
    mock_get.return_value = _mock_response([{"name": "myapp", "status": "running"}])
    result = server.vps_docker_list_projects(1)
    assert isinstance(result, list)


@patch("server.httpx.get")
def test_vps_get_templates(mock_get):
    mock_get.return_value = _mock_response([{"id": 1, "name": "Ubuntu 22.04"}])
    result = server.vps_get_templates()
    assert isinstance(result, list)


# ─── Reach (Email Marketing) ────────────────────────────────────────────────

@patch("server.httpx.get")
def test_reach_list_contacts(mock_get):
    mock_get.return_value = _mock_response({"data": [{"email": "test@example.com"}]})
    result = server.reach_list_contacts()
    assert "data" in result


@patch("server.httpx.post")
def test_reach_create_contact(mock_post):
    mock_post.return_value = _mock_response({"uuid": "abc-123", "email": "test@example.com"})
    result = server.reach_create_contact("test@example.com", name="Test")
    assert result["email"] == "test@example.com"


@patch("server.httpx.get")
def test_reach_list_profiles(mock_get):
    mock_get.return_value = _mock_response([{"uuid": "prof-1"}])
    result = server.reach_list_profiles()
    assert isinstance(result, list)
