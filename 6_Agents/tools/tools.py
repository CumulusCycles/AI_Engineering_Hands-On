"""
tools.py — Shared tool definitions for the Agents demo.

Each tool has two parts:
  1. A Python function that does the actual work (the "implementation").
  2. An OpenAI tool schema (a dict) that describes the tool to the model so it
     knows when and how to call it.

The model never runs Python directly — it emits a JSON tool_call, and our agent
loop is responsible for dispatching that call to the matching Python function.
"""

from pathlib import Path

# ---------------------------------------------------------------------------
# Data — load the company document once at import time so every tool that
# needs it can reference the same in-memory string without re-reading disk.
# ---------------------------------------------------------------------------
_DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "AI_Agent_Insure.md"
_COMPANY_DOC = _DATA_FILE.read_text(encoding="utf-8") if _DATA_FILE.exists() else ""

# ---------------------------------------------------------------------------
# Tool 1: get_product_info
# Returns a short description of a named insurance product by scanning the
# company document for the product name.  If the product isn't found we say so
# clearly — the model needs honest "no result" signals to reason correctly.
# ---------------------------------------------------------------------------
PRODUCTS = {
    "ai infrastructure & operations protection": (
        "Covers failures in AI compute infrastructure, cloud dependencies, and "
        "operational outages caused by model or pipeline failures."
    ),
    "agentic ai liability insurance": (
        "Covers third-party liability arising from decisions or actions taken by "
        "autonomous AI agents on behalf of the insured."
    ),
    "autonomous systems & robotics coverage": (
        "Covers physical damage, liability, and operational risk for robotics and "
        "autonomous vehicle deployments."
    ),
    "compliance & regulatory shield": (
        "Covers regulatory fines, legal defence costs, and compliance remediation "
        "arising from AI-related regulatory actions."
    ),
    "agentic workflow uptime insurance": (
        "Covers business interruption losses when agentic workflows go offline or "
        "produce degraded output."
    ),
    "intellectual property & output protection": (
        "Covers IP infringement claims and disputes arising from AI-generated "
        "content or model outputs."
    ),
    "model & data security insurance": (
        "Covers breaches, adversarial attacks, data poisoning, and model theft "
        "incidents."
    ),
    "ai incident response & crisis management": (
        "Covers the cost of technical triage, root cause analysis, PR response, "
        "and legal coordination following an AI incident."
    ),
    "synthetic data & dataset integrity coverage": (
        "Covers liability and losses arising from flawed synthetic datasets used "
        "in model training."
    ),
}


def get_product_info(product_name: str) -> str:
    """
    Look up a product by name and return its description.
    Normalises the input to lowercase so minor capitalisation differences don't
    cause a miss.
    """
    key = product_name.strip().lower()
    # Try an exact match first, then fall back to a substring search so the
    # model can pass a partial name (e.g. "robotics coverage") and still get a hit.
    if key in PRODUCTS:
        return PRODUCTS[key]
    for product_key, description in PRODUCTS.items():
        if key in product_key or product_key in key:
            return description
    return (
        f"No product named '{product_name}' found. "
        f"Available products: {', '.join(PRODUCTS.keys())}."
    )


# ---------------------------------------------------------------------------
# Tool 2: get_pricing_estimate
# Returns a rough annual premium estimate based on coverage type and company
# size.  In a real system this would call an underwriting API; here we use a
# simple lookup table so the demo stays self-contained and reproducible.
# ---------------------------------------------------------------------------
_BASE_PREMIUMS = {
    "startup":    {"low": 5_000,  "mid": 12_000, "high": 25_000},
    "mid-market": {"low": 20_000, "mid": 45_000, "high": 90_000},
    "enterprise": {"low": 75_000, "mid": 150_000, "high": 300_000},
}

_COVERAGE_MULTIPLIERS = {
    "agentic ai liability insurance":          1.4,
    "autonomous systems & robotics coverage":  1.6,
    "compliance & regulatory shield":          1.2,
    "model & data security insurance":         1.3,
    "ai incident response & crisis management": 1.1,
}


def get_pricing_estimate(coverage_type: str, company_size: str) -> str:
    """
    Return a rough annual premium range for a given coverage type and company
    size (startup / mid-market / enterprise).
    """
    size_key = company_size.strip().lower()
    if size_key not in _BASE_PREMIUMS:
        return (
            f"Unknown company size '{company_size}'. "
            "Please use: startup, mid-market, or enterprise."
        )

    base = _BASE_PREMIUMS[size_key]
    multiplier = _COVERAGE_MULTIPLIERS.get(coverage_type.strip().lower(), 1.0)

    low  = int(base["low"]  * multiplier)
    mid  = int(base["mid"]  * multiplier)
    high = int(base["high"] * multiplier)

    return (
        f"Estimated annual premium for '{coverage_type}' "
        f"({company_size}): ${low:,} – ${high:,} "
        f"(midpoint ~${mid:,}). "
        "Final pricing subject to full underwriting assessment."
    )


# ---------------------------------------------------------------------------
# Tool 3: check_eligibility
# Returns whether a given industry is in AI Agent Insure's target market.
# The model can use this before quoting to avoid recommending products to
# industries the company doesn't serve.
# ---------------------------------------------------------------------------
_ELIGIBLE_INDUSTRIES = {
    "ai startups",
    "llm application providers",
    "enterprises deploying autonomous agents",
    "robotics developers",
    "autonomous vehicle developers",
    "synthetic data organizations",
    "model training organizations",
    "healthcare",
    "finance",
    "legal",
    "regulated industries",
}


def check_eligibility(industry: str) -> str:
    """
    Check whether an industry falls within AI Agent Insure's target market.
    Returns a plain-English eligibility verdict the model can include in its
    response.
    """
    key = industry.strip().lower()
    # Check for a substring match so "healthcare company" matches "healthcare".
    for eligible in _ELIGIBLE_INDUSTRIES:
        if eligible in key or key in eligible:
            return (
                f"'{industry}' is within AI Agent Insure's target market. "
                "Coverage options are available."
            )
    return (
        f"'{industry}' is not currently listed as a target market segment. "
        "AI Agent Insure focuses on AI-native companies and regulated industries "
        "adopting AI. A custom underwriting review may still be possible."
    )


# ---------------------------------------------------------------------------
# OpenAI tool schemas
# These dicts are passed directly to the `tools=` parameter of
# client.chat.completions.create().  The model reads the name, description,
# and parameters to decide when and how to call each tool.
# ---------------------------------------------------------------------------
TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "get_product_info",
            "description": (
                "Look up details about a specific AI Agent Insure insurance product. "
                "Use this when the user asks what a product covers or how it works."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "product_name": {
                        "type": "string",
                        "description": (
                            "The name of the insurance product to look up, "
                            "e.g. 'Agentic AI Liability Insurance'."
                        ),
                    }
                },
                "required": ["product_name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_pricing_estimate",
            "description": (
                "Return a rough annual premium estimate for a coverage type and "
                "company size. Use this when the user asks about cost or pricing."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "coverage_type": {
                        "type": "string",
                        "description": "The name of the insurance product to price.",
                    },
                    "company_size": {
                        "type": "string",
                        "enum": ["startup", "mid-market", "enterprise"],
                        "description": "The size of the company seeking coverage.",
                    },
                },
                "required": ["coverage_type", "company_size"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "check_eligibility",
            "description": (
                "Check whether a given industry or company type is within "
                "AI Agent Insure's target market. Use this before recommending "
                "products to confirm the company qualifies."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "industry": {
                        "type": "string",
                        "description": (
                            "The industry or company type to check, "
                            "e.g. 'healthcare', 'robotics startup'."
                        ),
                    }
                },
                "required": ["industry"],
            },
        },
    },
]

# ---------------------------------------------------------------------------
# Dispatch helper
# Maps a tool name string (as the model emits it) to the corresponding Python
# function.  The agent loop calls this instead of a long if/elif chain.
# ---------------------------------------------------------------------------
TOOL_FUNCTIONS = {
    "get_product_info":      get_product_info,
    "get_pricing_estimate":  get_pricing_estimate,
    "check_eligibility":     check_eligibility,
}
