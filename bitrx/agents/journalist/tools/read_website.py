import os
import httpx
from base.tool_base import ToolBase, ToolSchema, ToolResult

# Black box — company website owned by another team
COMPANY_WEBSITE_URL = os.getenv("COMPANY_WEBSITE_URL", "http://company-website:8004")


class ReadWebsiteTool(ToolBase):
    """
    Reads publicly available content from the HappyTuna company website.
    The company website is owned by another team — treated as a black box.

    The Journalist uses this to:
    - Check for official press releases or statements
    - Find product batch numbers during a recall
    - Read the company's public response to the crisis
    - Verify claims made by company representatives
    - Investigate what the company is saying publicly vs what sources say privately
    """

    @property
    def schema(self) -> ToolSchema:
        return ToolSchema(
            name="read_website",
            description=(
                "Read content from the HappyTuna company website. "
                "Use this to check for official press releases, recall notices, "
                "batch numbers, executive statements, or any public company information. "
                "This is a key fact-checking tool — always check the company website "
                "before publishing claims about what the company said or did."
            ),
            parameters={
                "type": "object",
                "properties": {
                    "section": {
                        "type": "string",
                        "enum": [
                            "home",
                            "press_releases",
                            "recalls",
                            "statements",
                            "about",
                            "products",
                            "contact",
                        ],
                        "description": (
                            "Which section of the website to read. "
                            "'press_releases' — official company announcements. "
                            "'recalls' — active product recall notices with batch numbers. "
                            "'statements' — CEO and executive public statements. "
                            "'home' — latest news and updates on the front page."
                        ),
                    },
                    "search": {
                        "type": "string",
                        "description": (
                            "Optional keyword to search within the section. "
                            "e.g. 'Line A', 'salmonella', 'batch number'."
                        ),
                    },
                },
                "required": ["section"],
            },
        )

    def run(self, **kwargs) -> ToolResult:
        section = kwargs["section"]
        search = kwargs.get("search", "")

        try:
            params = {"search": search} if search else {}
            r = httpx.get(
                f"{COMPANY_WEBSITE_URL}/{section}",
                params=params,
                timeout=10,
            )
            r.raise_for_status()
            data = r.json()

            content = data.get("content") or data.get("text") or str(data)
            if not content:
                return ToolResult(
                    value=f"The '{section}' section of the HappyTuna website is empty or has no public content."
                )

            return ToolResult(
                value=(
                    f"HappyTuna website — {section.replace('_', ' ').title()}:\n\n"
                    f"{content[:1500]}"
                    f"{'...[truncated]' if len(content) > 1500 else ''}"
                )
            )

        except httpx.ConnectError:
            # Company website not yet available (other team hasn't built it)
            # Return a realistic "no public statement" response
            return ToolResult(
                value=(
                    f"HappyTuna website — {section.replace('_', ' ').title()}:\n\n"
                    f"[Company website is currently unreachable. "
                    f"No public statement or content available in this section. "
                    f"The company may not have published anything yet.]"
                )
            )
        except httpx.HTTPStatusError as e:
            return ToolResult(
                error=f"Company website error: {e.response.status_code} — {e.response.text}"
            )
        except Exception as e:
            return ToolResult(
                error=f"Failed to read company website: {e}"
            )