import re
from collections.abc import Callable

from app.core.exceptions import AnalysisError

# Explicit aliases, not special-case analysis paths. Qualified listings are preserved.
ALIASES = {
    "apple": "AAPL",
    "microsoft": "MSFT",
    "alphabet": "GOOGL",
    "amazon": "AMZN",
    "reliance": "RELIANCE.NS",
    "reliance industries": "RELIANCE.NS",
    "hdfc bank": "HDFCBANK.NS",
    "hdfcbank": "HDFCBANK.NS",
    "infosys": "INFY.NS",
    "tata consultancy services": "TCS.NS",
}
SYMBOL = re.compile(r"[A-Z^][A-Z0-9.^&=-]{0,24}\Z")


def resolve(query: str, search: Callable[[str], list[dict]] | None = None) -> str:
    query = " ".join(query.split())
    if not query or len(query) > 80 or not re.fullmatch(r"[\w .^&=\-]+", query):
        raise AnalysisError(
            "Enter a valid company name or exchange-qualified ticker.", "invalid_ticker"
        )
    if query.lower() in ALIASES:
        return ALIASES[query.lower()]
    if SYMBOL.fullmatch(query.upper()) and " " not in query:
        return query.upper()
    matches = search(query) if search else []
    symbols = sorted(
        {
            m["symbol"]
            for m in matches
            if m.get("quoteType") == "EQUITY" and SYMBOL.fullmatch(m.get("symbol", ""))
        }
    )
    if len(symbols) == 1:
        return symbols[0]
    if symbols:
        raise AnalysisError(
            "Ambiguous company name. Enter a ticker: " + ", ".join(symbols[:6]), "ambiguous_ticker"
        )
    raise AnalysisError(
        "Company not resolved. Try an exact ticker such as MSFT or INFY.NS.", "invalid_ticker"
    )


def default_benchmark(symbol: str) -> str | None:
    if symbol.endswith((".NS", ".BO")):
        return "^NSEI"
    if "." not in symbol and not symbol.startswith("^"):
        return "^GSPC"
    return None
