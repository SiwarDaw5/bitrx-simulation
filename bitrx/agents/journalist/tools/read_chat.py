import os
import httpx
from base.tool_base import ToolBase, ToolSchema, ToolResult


class ReadChatTool(ToolBase):
    """
    Reads messages from a channel in the Internal Messaging System.
    Used after send_chat to check if the target agent has replied.
    Tracks the last read cursor per channel to only fetch new messages.
    """

    def __init__(self):
        self._cursors: dict[str, int] = {}  # channel_id -> last seq cursor

    @property
    def schema(self) -> ToolSchema:
        return ToolSchema(
            name="read_chat",
            description=(
                "Read new messages from an internal chat channel. "
                "Use this after send_chat to check if the target agent has replied. "
                "Returns only new messages since the last read. "
                "Available targets: ceo, coo, regulator, employee."
            ),
            parameters={
                "type": "object",
                "properties": {
                    "channel_id": {
                        "type": "string",
                        "description": (
                            "The channel ID to read from. "
                            "Get this from the send_chat tool response."
                        ),
                    },
                    "since": {
                        "type": "integer",
                        "description": (
                            "Read messages from this sequence number onwards. "
                            "Use 0 to read all messages. "
                            "Use the next_cursor from the previous read to get only new messages."
                        ),
                    },
                },
                "required": ["channel_id"],
            },
        )

    def run(self, **kwargs) -> ToolResult:
        CHAT_URL = os.getenv("INTERNAL_CHAT_URL", "http://localhost:8080")
        AGENT_ID = os.getenv("JOURNALIST_AGENT_ID", "JOURNALIST-1")

        channel_id = kwargs["channel_id"]
        since = int(kwargs.get("since", self._cursors.get(channel_id, 0)))

        headers = {"Authorization": f"Bearer {AGENT_ID}"}

        try:
            r = httpx.get(
                f"{CHAT_URL}/api/channels/{channel_id}/messages",
                headers=headers,
                params={"since": since},
                timeout=10,
            )
            r.raise_for_status()
            data = r.json()

            if not data.get("success"):
                return ToolResult(error=f"Failed to read channel: {data.get('error')}")

            messages = data["data"].get("messages", [])
            next_cursor = data["data"].get("next_cursor", since)

            # Update cursor for next read
            self._cursors[channel_id] = next_cursor

            # Filter out own messages — only show replies from others
            replies = [m for m in messages if m.get("sender") != AGENT_ID]

            if not replies:
                return ToolResult(
                    value=(
                        f"No new replies in channel {channel_id} since seq={since}. "
                        f"The source has not responded yet. next_cursor={next_cursor}"
                    )
                )

            lines = [f"Found {len(replies)} reply/replies in channel {channel_id}:\n"]
            for m in replies:
                lines.append(
                    f"From: {m.get('sender')} | seq={m.get('seq')} | {m.get('sent_at', '')[:19]}\n"
                    f"{m.get('body', '')}\n"
                )

            return ToolResult(
                value="\n".join(lines) + f"\nnext_cursor={next_cursor}"
            )

        except httpx.ConnectError:
            return ToolResult(
                value="[Internal chat offline — cannot read messages.]"
            )
        except httpx.HTTPStatusError as e:
            return ToolResult(
                error=f"Internal chat error: {e.response.status_code} — {e.response.text}"
            )
        except Exception as e:
            return ToolResult(
                error=f"Failed to read chat: {e}",
                is_idempotent=True,
            )