import base64
import os
from pathlib import Path
from typing import Any
import jinja2

flag = os.getenv("FLAG")
assert flag, "FLAG is not set"

CLICKS_TO_GET_FLAG = int(os.getenv("CLICKS_TO_GET_FLAG", "10"))

def render_template(template_name: str, **kwargs: dict[str, Any]) -> str:
    template_path = Path('./static') / template_name
    template: jinja2.Template = jinja2.Template(template_path.read_text())
    return template.render(kwargs)


def eval_js(js: str) -> str:
    return f'eval(atob("{base64.b64encode(js.encode()).decode()}"))'


flag = base64.b64encode(flag.encode()).decode()[::-1]

js = render_template('flag_decoder.js', flag=flag)
js = eval_js(js)


clicks_count_checker = render_template('clicks_count_checker.js', clicks_to_get_flag=CLICKS_TO_GET_FLAG, flag_getter=js)
clicks_count_checker = eval_js(clicks_count_checker)

task = render_template('index.html', flag_getter=js, clicks_count_checker=clicks_count_checker, clicks_to_get_flag=CLICKS_TO_GET_FLAG)

with open('output/index.html', 'w') as f:
    f.write(task)
