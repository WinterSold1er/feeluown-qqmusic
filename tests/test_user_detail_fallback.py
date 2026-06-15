"""Tests for API.user_detail endpoint fallback.

These tests verify the new RPC-first / legacy-fallback behaviour
without making any real network calls. We mock the API.rpc and the
HTTP layer to assert:

- When the modern RPC returns ``code == 0`` with ``data``, we use it.
- When the modern RPC raises CodeShouldBe0, we fall back to the
  legacy ``fcg_get_profile_homepage.fcg`` endpoint.
- When both endpoints fail, the legacy CodeShouldBe0 propagates.
"""
from unittest.mock import MagicMock, patch

import pytest

from fuo_qqmusic.api import API, CodeShouldBe0


@pytest.fixture
def api_with_cookies():
    a = API()
    a.set_cookies(
        {
            "qqmusic_key": "X",
            "wxuin": "12345",
            "qm_keyst": "Y",
            "uin": "67890",
        }
    )
    return a


def test_user_detail_uses_modern_rpc_when_it_returns_data(api_with_cookies):
    api = api_with_cookies
    rpc_data = {
        "creator": {"nick": "alice", "headurl": "http://x"},
        "mymusic": [{"id": "fav-1"}],
    }
    api.rpc = MagicMock(
        return_value={"req_0": {"code": 0, "data": rpc_data}}
    )

    result = api.user_detail("12345")

    assert api.rpc.called
    # Payload must include authst, g_tk, uin etc.
    payload = api.rpc.call_args.args[0]
    assert payload["comm"]["authst"] == "Y"
    assert payload["comm"]["uin"] == "12345"
    assert payload["req_0"]["method"] == "GetHomepageHeader"
    assert payload["req_0"]["param"]["uin"] == "12345"

    # Normalized shape: creator.uin and fav_pid are set.
    assert result["creator"]["uin"] == "12345"
    assert result["creator"]["fav_pid"] == "fav-1"


def test_user_detail_falls_back_to_legacy_on_rpc_failure(api_with_cookies):
    api = api_with_cookies
    # Modern RPC raises CodeShouldBe0 — simulates expired cookies.
    api.rpc = MagicMock(side_effect=CodeShouldBe0({"code": 500003}))

    # Mock the legacy requests.get call.
    fake_resp = MagicMock()
    fake_resp.json.return_value = {"code": 0, "data": {"creator": {}, "mymusic": []}}
    with patch("fuo_qqmusic.api.requests.get", return_value=fake_resp) as mock_get:
        result = api.user_detail("12345")

    assert mock_get.called
    # Legacy URL is invoked.
    assert "fcg_get_profile_homepage.fcg" in mock_get.call_args.args[0]
    # Note: the legacy path does NOT normalize creator.{uin,fav_pid};
    # that's the job of provider.user_get(). See provider.py:325.


def test_user_detail_raises_when_both_endpoints_fail(api_with_cookies):
    api = api_with_cookies
    api.rpc = MagicMock(side_effect=CodeShouldBe0({"code": 500003}))

    fake_resp = MagicMock()
    fake_resp.json.return_value = {"code": 1000, "subcode": 1000, "msg": "", "data": {}}
    with patch("fuo_qqmusic.api.requests.get", return_value=fake_resp):
        with pytest.raises(CodeShouldBe0) as exc_info:
            api.user_detail("12345")
    assert exc_info.value._code == 1000
