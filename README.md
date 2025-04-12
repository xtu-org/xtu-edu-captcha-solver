# 湘潭大学 教务系统 验证码识别

## 安装

从 PyPI 安装：

```bash
pip install xtu-edu-captcha-solver
```

从 GitHub 安装：

```bash
pip install git+https://github.com/xtu-org/xtu-edu-captcha-solver.git@main#egg=xtu-edu-captcha-solver
```

## 示例

```python
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
```

## 开源协议

本仓库使用 [MIT](https://mit-license.org) 协议，注意事项：

本软件按“现状”提供，不提供任何形式的明示或暗示的保证，包括但不限于对适销性、特定用途的适用性和非侵权性的保证。
在任何情况下，作者或版权持有人均不对任何索赔、损害或其他责任承担责任，无论是在合同诉讼、侵权行为还是其他方面，由本软件引起、或与本软件或使用或其它方式处理本软件有关。

## 原作者

[原作者 GitHub仓库](https://github.com/WindrunnerMax/SWVerifyCode)

依照 MIT 协议，您在修改、使用、分发本软件时，应当保留原作者的版权声明。
