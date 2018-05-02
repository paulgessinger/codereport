from jinja2 import Environment, PackageLoader, select_autoescape
from .html import HtmlFormatter, get_style
from datetime import datetime


env = Environment(
    loader=PackageLoader('codereport', 'templates'),
)

env.globals["pygments_style"] = get_style()
env.globals["report_created"] = datetime.now().strftime("%H:%M:%S %d.%m.%Y")

file_tpl = env.get_template("file.html")
index_tpl = env.get_template("index.html")
line_tpl = env.get_template("line.html")
