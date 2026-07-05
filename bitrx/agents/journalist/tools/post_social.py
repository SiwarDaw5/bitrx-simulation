import os
import httpx
from base.tool_base import ToolBase, ToolSchema, ToolResult

# Black box — social network owned by another team
SOCIAL_URL = os.getenv("SOCIAL_URL", "http://social-network:8005")


class PostSocialTool(ToolBase):
    """
    Posts a short teaser or update to the social network on behalf
    of The Daily Catch journalist account.

    The social network is owned by another team — treated as a black box.
    The Journalist uses this to:
    - Share a headline teaser after publishing an article
    - Break a developing story before the full article is ready
    - Grow audience reach and maximize article impact
    - React to breaking events in real time with short updates

    Note: posts are short (tweet-style) — the full article lives on the news website.
    """

    @property
    def schema(self) -> ToolSchema:
        return ToolSchema(
            name="post_social",
            description=(
                "Post a short message to the social network as The Daily Catch. "
                "Use this AFTER publishing an article to drive traffic to it, "
                "or to share a breaking development before the full article is ready. "
                "Keep posts short, punchy, and impactful. "
                "Include the article URL if one has been published."
            ),
            parameters={
                "type": "object",
                "properties": {
                    "content": {
                        "type": "string",
                        "description": (
                            "The post text — maximum 280 characters. "
                            "Should be attention-grabbing and newsworthy. "
                            "e.g. 'BREAKING: HappyTuna shuts down Production Line A "
                            "amid salmonella fears. Full story: [link] #FoodSafety #Recall'"
                        ),
                    },
                    "article_id": {
                        "type": "string",
                        "description": (
                            "Optional. The ID of the published article to link to. "
                            "Get this from the publish_article tool response."
                        ),
                    },
                    "tags": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Hashtags to include e.g. ['FoodSafety', 'Recall', 'HappyTuna'].",
                    },
                },
                "required": ["content"],
            },
        )

    def run(self, **kwargs) -> ToolResult:
        content = kwargs["content"]
        article_id = kwargs.get("article_id", "")
        tags = kwargs.get("tags", [])

        # Enforce character limit
        if len(content) > 280:
            content = content[:277] + "..."

        try:
            r = httpx.post(
                f"{SOCIAL_URL}/posts",
                json={
                    "content": content,
                    "author": "thedailycatch",
                    "author_role": "journalist",
                    "article_id": article_id,
                    "tags": tags,
                },
                timeout=10,
            )
            r.raise_for_status()
            data = r.json()

            return ToolResult(
                value=(
                    f"Post published to social network. "
                    f"Post ID: {data.get('id', 'unknown')} | "
                    f"Likes: 0 | "
                    f"Content: '{content[:80]}...'"
                ),
                is_idempotent=False,  # posting has a real side effect
            )

        except httpx.ConnectError:
            # Social network not yet available (other team hasn't built it)
            return ToolResult(
                value=(
                    f"[Social network offline — post queued but not delivered. "
                    f"Content: '{content[:80]}']"
                ),
                is_idempotent=False,
            )
        except httpx.HTTPStatusError as e:
            return ToolResult(
                error=f"Social network error: {e.response.status_code} — {e.response.text}",
                is_idempotent=False,
            )
        except Exception as e:
            return ToolResult(
                error=f"Failed to post to social network: {e}",
                is_idempotent=True,
            )
