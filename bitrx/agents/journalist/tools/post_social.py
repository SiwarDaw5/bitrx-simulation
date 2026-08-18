import os
import httpx
from base.tool_base import ToolBase, ToolSchema, ToolResult


class PostSocialTool(ToolBase):

    @property
    def schema(self) -> ToolSchema:
        return ToolSchema(
            name="post_social",
            description=(
                "Post a short message to the social network as The Daily Catch. "
                "Use this AFTER publishing an article to drive traffic to it, "
                "or to share a breaking development before the full article is ready. "
                "Keep posts short, punchy, and impactful. "
                "Do NOT include any links or URLs in the content. "
                "Use hashtags only."            ),
            parameters={
                "type": "object",
                "properties": {
                    "content": {
                        "type": "string",
                        "description": "The post text — maximum 280 characters. No links or URLs. End with relevant hashtags like #HappyTuna #FoodSafety #Recall",                    },
                    "tags": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Hashtags to include.",
                    },
                },
                "required": ["content"],
            },
        )

    def _get_token(self, client: httpx.Client) -> str | None:
        """Login and get auth token."""
        try:
            r = client.post(
                f"{os.getenv('SOCIAL_URL', 'http://localhost:3005')}/api/auth/login",
                json={"name": "journalist"},
                timeout=5,
            )
            r.raise_for_status()
            return r.json()["data"]["token"]
        except Exception as e:
            print(f"[PostSocial] Login failed: {e}")
            return None

    def run(self, **kwargs) -> ToolResult:
        SOCIAL_URL = os.getenv("SOCIAL_URL", "http://localhost:3005")
        content = kwargs["content"]
        tags = kwargs.get("tags", [])

        if len(content) > 280:
            content = content[:277] + "..."

        try:
            with httpx.Client() as client:
                # Step 1 — login
                token = self._get_token(client)
                if not token:
                    return ToolResult(
                        value="[Social network — login failed, post not delivered]",
                        is_idempotent=False,
                    )

                # Step 2 — post
                r = client.post(
                    f"{SOCIAL_URL}/api/posts",
                    headers={"Authorization": f"Bearer {token}"},
                    json={
                        "content": content,
                    },
                    timeout=10,
                )
                r.raise_for_status()
                data = r.json()

                return ToolResult(
                    value=(
                        f"Post published to social network. "
                        f"Post ID: {data.get('id', 'unknown')} | "
                        f"Content: '{content[:80]}...'"
                    ),
                    is_idempotent=False,
                )

        except httpx.ConnectError:
            return ToolResult(
                value=f"[Social network offline — post not delivered]",
                is_idempotent=False,
            )
        except httpx.HTTPStatusError as e:
            return ToolResult(
                error=f"Social network error: {e.response.status_code} — {e.response.text}",
                is_idempotent=False,
            )
        except Exception as e:
            return ToolResult(
                error=f"Failed to post: {e}",
                is_idempotent=True,
            )