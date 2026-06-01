from __future__ import annotations

from middleware.src.config import ROLE_FORMAT_MAP
from middleware.src.formatting.csv_formatter import CsvFormatter
from middleware.src.formatting.formatter import Formatter
from middleware.src.formatting.html_formatter import HtmlFormatter
from middleware.src.formatting.json_formatter import JsonFormatter
from middleware.src.formatting.markdown_formatter import MarkdownFormatter
from shared.log_schema import UserRole


def formatter_for_role(role: UserRole) -> Formatter:
    target = ROLE_FORMAT_MAP.get(role.value, "json")
    if target == "markdown":
        return MarkdownFormatter()
    if target == "csv":
        return CsvFormatter()
    if target == "html":
        return HtmlFormatter()
    return JsonFormatter()
