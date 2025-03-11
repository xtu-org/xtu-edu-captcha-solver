from xtu.edu.captcha import captcha
from pathlib import Path
import asyncio
import httpx
import os

PATH = Path(os.getcwd()) / "data"


async def task():
    PATH.mkdir(exist_ok=True)
    async with httpx.AsyncClient() as client:
        resp = await client.get("https://jwxt.xtu.edu.cn/jsxsd/verifycode.servlet")
        code = captcha(resp.content)

        with open(PATH / f"{code}.png", "wb") as f:
            f.write(resp.content)


async def main():
    await asyncio.gather(*[task() for _ in range(10)])


if __name__ == "__main__":
    asyncio.run(main())
