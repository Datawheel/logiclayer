A simple framework to quickly compose and use multiple functionalities as endpoints.  
LogicLayer is built upon FastAPI to provide a simple way to group functionalities into reusable modules.

<p>
<a href="https://github.com/Datawheel/logiclayer/releases"><img src="https://flat.badgen.net/github/release/Datawheel/logiclayer" /></a>
<a href="https://github.com/Datawheel/logiclayer/blob/master/LICENSE"><img src="https://flat.badgen.net/github/license/Datawheel/logiclayer" /></a>
<a href="https://github.com/Datawheel/logiclayer/"><img src="https://flat.badgen.net/github/checks/Datawheel/logiclayer" /></a>
<a href="https://github.com/Datawheel/logiclayer/issues"><img src="https://flat.badgen.net/github/issues/Datawheel/logiclayer" /></a>
</p>

## Getting started

To generate a new instance of LogicLayer, create a python file and execute this snippet:

```python
# example.py

import requests
from logiclayer import LogicLayer
from logiclayer.echo import EchoModule # Example module

echo = EchoModule()

def is_online() -> bool:
    res = requests.get("http://clients3.google.com/generate_204")
    return (res.status_code == 204) and (res.headers.get("Content-Length") == "0")

layer = LogicLayer()
layer.add_check(is_online)
layer.add_module(echo, prefix="/echo")
```

The `layer` object is an ASGI-compatible application, that can be used with uvicorn/gunicorn to run a server, the same way as you would with a FastAPI instance.

```bash
$ pip install uvicorn[standard]
$ uvicorn example:layer
```

Note the `example:layer` is the reference to the `layer` variable in the `example` module, which [points to the ASGI app instance](https://www.uvicorn.org/#usage).

---
&copy; 2022 [Datawheel, LLC.](https://www.datawheel.us/)  
This project is licensed under [MIT](./LICENSE).
