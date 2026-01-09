import logging
import httpx
from typing import AsyncGenerator, Any, Optional

from google.adk.agents import BaseAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event
from google.genai import types as genai_types

logger = logging.getLogger(__name__)

from pydantic import PrivateAttr

class SimpleRemoteAgent(BaseAgent):
    """A simple remote agent that communicates via HTTP POST requests.

    This agent forwards user messages to a remote service via HTTP POST and yields
    the response as an event.

    Attributes:
        base_url (str): The base URL of the remote agent.
        _client (httpx.AsyncClient): The HTTP client for making requests.
    """
    
    base_url: str
    _client: httpx.AsyncClient = PrivateAttr()

    def __init__(
        self,
        name: str,
        base_url: str,
        description: str = "",
        model: str = "", # Not used, but kept for compatibility
        **kwargs
    ):
        """Initialize the SimpleRemoteAgent.

        Args:
            name (str): The name of the agent.
            base_url (str): The base URL of the remote service.
            description (str, optional): A description of the agent. Defaults to "".
            model (str, optional): The model name (unused, kept for compatibility). Defaults to "".
            **kwargs: Additional arguments passed to the BaseAgent constructor.
        """
        super().__init__(name=name, description=description, base_url=base_url, **kwargs)
        self.base_url = base_url.rstrip("/")
        self._client = httpx.AsyncClient(timeout=60.0)

    @property
    def client(self):
        """Returns the HTTP client instance.

        Returns:
            httpx.AsyncClient: The async HTTP client.
        """
        return self._client

    async def _run_async_impl(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        """Sends the user message to the remote agent and yields the response.

        Extracts the last user message from the context events, sends it to the
        remote agent's chat endpoint, and yields the response as an Event.

        Args:
            ctx (InvocationContext): The context of the current invocation.

        Yields:
            Event: The event containing the response from the remote agent or an error message.
        """
        
        # Extract the last user message text
        user_message = ""
        for event in reversed(ctx.session.events):
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if part.text:
                        user_message = part.text
                        break
            if user_message:
                break
        
        if not user_message:
            logger.warning(f"[{self.name}] No user message found to send.")
            return

        payload = {
            "message": user_message,
            "user_id": ctx.session.user_id,
            "session_id": ctx.session.id,
        }

        try:
            logger.info(f"[{self.name}] Sending request to {self.base_url}/api/chat")
            response = await self.client.post(f"{self.base_url}/api/chat", json=payload)
            response.raise_for_status()
            
            data = response.json()
            response_text = data.get("response", "")

            if response_text:
                yield Event(
                    author=self.name,
                    content=genai_types.Content(
                        role="model",
                        parts=[genai_types.Part.from_text(text=response_text)]
                    )
                )
            else:
                 logger.warning(f"[{self.name}] Received empty response from remote agent.")

        except Exception as e:
            logger.error(f"[{self.name}] Error communicating with remote agent: {e}")
            yield Event(
                author=self.name,
                content=genai_types.Content(
                    role="model",
                    parts=[genai_types.Part.from_text(text=f"Error: Could not contact {self.name}. {e}")]
                )
            )

    async def close(self):
        await self.client.aclose()
