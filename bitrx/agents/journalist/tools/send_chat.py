import os
import httpx
from base.tool_base import ToolBase, ToolSchema, ToolResult

# Known agent IDs in the BitriX world
AGENT_IDS = {
    "ceo": "CEO-1",
    "coo": "COO-1",
    "employee": "EMP-QA-17",
}


class SendChatTool(ToolBase):
    """
    Sends a message to an agent via the Internal Messaging System.
    Creates a direct channel with the target agent if one doesn't exist yet.
    Replaces send_email — the internal chat is the primary communication channel.
    """

    def __init__(self):
        self._channels: dict[str, str] = {}  # cache: agent_id -> channel_id

    @property
    def schema(self) -> ToolSchema:
        return ToolSchema(
            name="send_chat",
            description=(
                "Send a message to an agent via the internal messaging system. "
                "Use this to contact sources for interviews or official comments. "
                "A direct channel is created automatically if one doesn't exist. "
                "Available targets: ceo, coo, employee."
            ),
            parameters={
                "type": "object",
                "properties": {
                    "to": {
                        "type": "string",
                        "enum": ["ceo", "coo", "employee"],
                        "description": "Who to send the message to.",
                    },
                    "body": {
                        "type": "string",
                        "description": (
                            "The message body. Be professional and specific. "
                            "Identify yourself as a journalist from The Daily Catch. "
                            "Ask a clear question and request a response."
                        ),
                    },
                },
                "required": ["to", "body"],
            },
        )

    def run(self, **kwargs) -> ToolResult:
        CHAT_URL = os.getenv("INTERNAL_CHAT_URL", "http://localhost:8080")
        AGENT_ID = os.getenv("JOURNALIST_AGENT_ID", "JOURNALIST-1")

        to = kwargs["to"]
        body = kwargs["body"]
        target_id = AGENT_IDS.get(to)

        if not target_id:
            return ToolResult(error=f"Unknown target '{to}'. Available: {list(AGENT_IDS.keys())}")

        headers = {
            "Authorization": f"Bearer {AGENT_ID}",
            "Content-Type": "application/json",
        }

        try:
            with httpx.Client(timeout=10) as client:

                # Step 1 — get or create channel
                channel_id = self._channels.get(target_id)
                if not channel_id:
                    r = client.post(
                        f"{CHAT_URL}/api/channels",
                        headers=headers,
                        json={
                            "type": "direct",
                            "members": [target_id],
                            "name": f"journalist-{to}",
                        },
                    )
                    r.raise_for_status()
                    data = r.json()
                    if not data.get("success"):
                        return ToolResult(error=f"Failed to create channel: {data.get('error')}")
                    channel_id = data["data"]["channel"]
                    self._channels[target_id] = channel_id

                # Step 2 — send message
                r = client.post(
                    f"{CHAT_URL}/api/channels/{channel_id}/messages",
                    headers=headers,
                    json={"body": body},
                )
                r.raise_for_status()
                data = r.json()

                if not data.get("success"):
                    return ToolResult(
                        error=f"Failed to send message: {data.get('error')}",
                        is_idempotent=False,
                    )

                delivered_to = data["data"].get("delivered_to", [])
                return ToolResult(
                    value=(
                        f"Message sent to {to} ({target_id}) via internal chat. "
                        f"Channel: {channel_id} | "
                        f"Delivered to: {delivered_to} | "
                        f"Message ID: {data['data'].get('message_id')}"
                    ),
                    is_idempotent=False,
                )

        except httpx.ConnectError:
            return ToolResult(
                value=(
                    f"[Internal chat offline — message to {to} not delivered. "
                    f"Proceeding without response from this source.]"
                ),
                is_idempotent=False,
            )
        except httpx.HTTPStatusError as e:
            return ToolResult(
                error=f"Internal chat error: {e.response.status_code} — {e.response.text}",
                is_idempotent=False,
            )
        except Exception as e:
            return ToolResult(
                error=f"Failed to send chat message: {e}",
                is_idempotent=True,
            )