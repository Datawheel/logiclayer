<a href="https://github.com/Datawheel/logiclayer"><img src="https://flat.badgen.net/github/release/Datawheel/logiclayer" /></a>
<a href="https://github.com/Datawheel/logiclayer/blob/master/LICENSE"><img src="https://flat.badgen.net/github/license/Datawheel/logiclayer" /></a>
<a href="https://github.com/Datawheel/logiclayer/issues"><img src="https://flat.badgen.net/github/issues/Datawheel/logiclayer" /></a>


> A simple framework to quickly compose and use multiple functionalities as endpoints.

LogicLayer is built upon FastAPI to provide a simple way to group functionalities into reusable modules.

## Usage

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

> Note: The `example:layer` parameter refers to `full.module.path:asgi_object`, and will change according to how you set the file.

## License

&copy; 2022 Datawheel, LLC.  
This project is licensed under [MIT](./LICENSE).
