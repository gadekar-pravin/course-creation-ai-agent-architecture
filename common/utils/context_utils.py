from typing import Any, Optional
import logging
from a2a.server.agent_execution.context import RequestContext

logger = logging.getLogger(__name__)

def extract_user_id(context: RequestContext, default: str = "default_user") -> str:
    """
    Extracts the user ID from the RequestContext.

    This function attempts to retrieve the user ID from the `user` object in the
    `ServerCallContext`. If that is not available or does not contain an ID,
    it falls back to checking the `state` dictionary for a "user_id" key.

    This is a workaround for the lack of `raw_headers` in `ServerCallContext`
    where authentication details might otherwise be found.

    Args:
        context: The request context containing the call context.
        default: The default user ID to return if no user ID can be found.

    Returns:
        The extracted user ID or the default value.
    """
    user_id = default

    if context.call_context:
        # Check user object
        if hasattr(context.call_context, "user") and context.call_context.user:
            # If it's an authenticated user object, it might have an id
            if hasattr(context.call_context.user, "id") and context.call_context.user.id:
                return context.call_context.user.id

        # Fallback: check state for potential headers or info
        if context.call_context.state:
             return context.call_context.state.get("user_id", default)

    return user_id
