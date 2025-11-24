import os
import base64
from typing import Callable

# Default flag if not set in environment
flag = os.getenv("FLAG", "ctf{test}").encode()

encoders: list[Callable[[bytes], bytes]] = [
    base64.b64encode,
    lambda x: b''.join(f'{i:08b}'.encode() for i in x),
    base64.b32encode,
    base64.b85encode,
    lambda x: x.hex().encode(),
]

for encoder in encoders:
    flag = encoder(flag)

with open("output/flag.enc.txt", "wb") as f:
    f.write(flag)
