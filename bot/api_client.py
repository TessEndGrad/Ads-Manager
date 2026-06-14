import aiohttp
from typing import Optional

class AdsAPIClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")

    async def _request(self, method: str, path: str, token: Optional[str] = None, **kwargs):
        headers = {}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        async with aiohttp.ClientSession() as session:
            async with session.request(
                method,
                f"{self.base_url}/{path.lstrip('/')}",
                headers=headers,
                **kwargs
            ) as resp:
                if resp.content_type == "application/json":
                    return resp.status, await resp.json()
                return resp.status, {}

    async def login(self, email: str, password: str):
        status, data = await self._request(
            "POST", "/auth/login",
            json={"email": email, "password": password}
        )
        if status == 200:
            return data.get("access_token")
        return None

    async def get_me(self, token: str):
        status, data = await self._request("GET", "/users/me", token=token)
        return data if status == 200 else None

    async def get_posts(self, token: str, page: int = 1, page_size: int = 10):
        status, data = await self._request(
            "GET", f"/posts/?page={page}&page_size={page_size}", token=token
        )
        return data if status == 200 else None

    async def get_post(self, token: str, post_id: int):
        status, data = await self._request("GET", f"/posts/{post_id}", token=token)
        return data if status == 200 else None

    async def create_post(self, token: str, title: str, content: str):
        status, data = await self._request(
            "POST", "/posts/",
            token=token,
            json={"title": title, "content": content, "tag_ids": []}
        )
        return data if status == 201 else None

    async def submit_post(self, token: str, post_id: int):
        status, data = await self._request(
            "POST", f"/posts/{post_id}/submit", token=token
        )
        return data if status == 200 else None

    async def approve_post(self, token: str, post_id: int):
        status, data = await self._request(
            "POST", f"/posts/{post_id}/approve", token=token
        )
        return data if status == 200 else None

    async def reject_post(self, token: str, post_id: int):
        status, data = await self._request(
            "POST", f"/posts/{post_id}/reject", token=token
        )
        return data if status == 200 else None

    async def get_posts_on_moderation(self, token: str):
        status, data = await self._request(
            "GET", "/posts/?status_id=2&page_size=20", token=token
        )
        return data if status == 200 else None