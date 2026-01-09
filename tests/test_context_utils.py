import pytest
from unittest.mock import MagicMock
from a2a.server.agent_execution.context import RequestContext, ServerCallContext
from common.utils.context_utils import extract_user_id

class MockUser:
    def __init__(self, user_id=None):
        self.id = user_id

class MockCallContext:
    def __init__(self, user=None, state=None):
        self.user = user
        self.state = state or {}

class MockRequestContext:
    def __init__(self, call_context=None):
        self.call_context = call_context

def test_extract_user_id_from_user_object():
    user = MockUser(user_id="test_user_1")
    call_context = MockCallContext(user=user)
    context = MockRequestContext(call_context=call_context)

    assert extract_user_id(context) == "test_user_1"

def test_extract_user_id_from_state():
    call_context = MockCallContext(state={"user_id": "test_user_2"})
    context = MockRequestContext(call_context=call_context)

    assert extract_user_id(context) == "test_user_2"

def test_extract_user_id_user_object_priority():
    user = MockUser(user_id="user_priority")
    call_context = MockCallContext(user=user, state={"user_id": "state_user"})
    context = MockRequestContext(call_context=call_context)

    assert extract_user_id(context) == "user_priority"

def test_extract_user_id_default():
    context = MockRequestContext(call_context=MockCallContext())
    assert extract_user_id(context) == "default_user"

def test_extract_user_id_no_call_context():
    context = MockRequestContext(call_context=None)
    assert extract_user_id(context) == "default_user"

def test_extract_user_id_custom_default():
    context = MockRequestContext(call_context=None)
    assert extract_user_id(context, default="custom_default") == "custom_default"
