"""Rendering logic for jira tickets."""

from dataclasses import dataclass

from jinja2 import Environment, PackageLoader, StrictUndefined, select_autoescape


@dataclass
class Model:
    """Data used to operate the jinja templates."""

    asset_name: str


JINJA_ENV = Environment(
    autoescape=select_autoescape(
        enabled_extensions=("html", "htm", "xml", "jinja2"),
        default_for_string=True,
    ),
    undefined=StrictUndefined,
    trim_blocks=True,
    lstrip_blocks=True,
    loader=PackageLoader(__name__, "templates"),
)

SUMMARY_TEMPLATE = JINJA_ENV.get_template("issue-summary.jinja2")
DESCRIPTION_TEMPLATE = JINJA_ENV.get_template("issue-description.jinja2")


def render_issue_summary(model: Model) -> str:
    """Render the issue summary."""
    return SUMMARY_TEMPLATE.render(model=model)


def render_issue_description(model: Model) -> str:
    """Render the issue summary."""
    return DESCRIPTION_TEMPLATE.render(model=model)
