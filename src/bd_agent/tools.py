from langchain_core.tools import tool
from typing import List, Dict, Any, Optional
import requests
import os
import json
from datetime import datetime, timedelta


def _perplexity_query(query: str, system_prompt: str = "") -> dict:
    """
    Core Perplexity API call used by most tools.
    Uses sonar-pro for deep, cited research.
    """
    api_key = os.getenv("PERPLEXITY_API_KEY")

    if not api_key:
        return {
            "error": "PERPLEXITY_API_KEY not set",
            "message": "Get your API key at https://www.perplexity.ai/settings/api",
            "results": []
        }

    try:
        url = "https://api.perplexity.ai/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": query})

        payload = {
            "model": "sonar-pro",
            "messages": messages,
            "return_citations": True,
            "return_related_questions": False
        }

        response = requests.post(url, json=payload, headers=headers, timeout=60)
        response.raise_for_status()
        data = response.json()

        answer = data["choices"][0]["message"]["content"]
        citations = data.get("citations", [])

        return {
            "answer": answer,
            "citations": citations,
            "source": "perplexity_sonar_pro"
        }

    except Exception as e:
        return {"error": str(e), "results": []}


@tool
def deep_research(query: str) -> str:
    """
    Deep research using Perplexity sonar-pro. Returns cited, factual answers.

    This is the primary research tool. Use it for any question that needs
    accurate, up-to-date information with source citations.

    Args:
        query: Research question or topic

    Returns:
        JSON string with answer and citation URLs
    """
    result = _perplexity_query(
        query,
        system_prompt=(
            "You are a business development research assistant. "
            "Provide detailed, factual answers with specific data points. "
            "Include company names, funding amounts, employee counts, and dates when available."
        )
    )
    return json.dumps(result, indent=2)


@tool
def search_companies_by_criteria(
    industry: str,
    location: str = "",
    stage: str = "",
    min_employees: int = 0,
    max_employees: int = 10000
) -> str:
    """
    Search for companies matching specific ICP criteria using Perplexity.

    Args:
        industry: Industry or vertical (e.g., "fintech", "health tech")
        location: Geographic location (e.g., "NYC", "San Francisco", "US")
        stage: Funding stage (e.g., "seed", "series A", "series B")
        min_employees: Minimum employee count
        max_employees: Maximum employee count

    Returns:
        JSON string with companies and evidence URLs
    """
    query_parts = [f"List {industry} companies"]

    if stage:
        query_parts.append(f"that have raised {stage} funding")
    if location:
        query_parts.append(f"based in {location}")
    if min_employees > 0 or max_employees < 10000:
        query_parts.append(f"with {min_employees}-{max_employees} employees")

    query = " ".join(query_parts)
    query += ". For each company, include: name, website, funding stage, employee count, and what they do."

    result = _perplexity_query(query)
    result["search_criteria"] = {
        "industry": industry,
        "location": location,
        "stage": stage,
        "size_range": f"{min_employees}-{max_employees}"
    }
    return json.dumps(result, indent=2)


@tool
def find_hiring_signals(company_name: str, role_keywords: str = "SDR,sales,growth") -> str:
    """
    Find hiring signals for a company using Perplexity.

    Args:
        company_name: Name of the company
        role_keywords: Comma-separated role keywords to search for

    Returns:
        JSON string with hiring postings and URLs as evidence
    """
    query = (
        f"Is {company_name} currently hiring for {role_keywords} roles? "
        f"Check LinkedIn, job boards, and their careers page. "
        f"Include links to any open positions found."
    )

    result = _perplexity_query(query)
    result["company"] = company_name
    result["signal_type"] = "hiring"
    return json.dumps(result, indent=2)


@tool
def find_funding_signals(company_name: str, within_days: int = 365) -> str:
    """
    Find recent funding announcements for a company.

    Args:
        company_name: Name of the company
        within_days: Look for funding within this many days

    Returns:
        JSON string with funding news and evidence URLs
    """
    cutoff = (datetime.now() - timedelta(days=within_days)).strftime("%B %Y")

    query = (
        f"Has {company_name} raised any funding since {cutoff}? "
        f"Include: round type, amount raised, lead investors, valuation if known, and date."
    )

    result = _perplexity_query(query)
    result["company"] = company_name
    result["signal_type"] = "funding"
    return json.dumps(result, indent=2)


@tool
def find_company_contacts(company_name: str, title: str) -> str:
    """
    Find contacts at a company with specific titles.

    Args:
        company_name: Name of the company
        title: Job title to search for (e.g., "VP Sales", "Head of Growth")

    Returns:
        JSON string with contacts and profile URLs
    """
    query = (
        f"Who is the {title} at {company_name}? "
        f"Include their full name, exact title, and LinkedIn profile URL if available."
    )

    result = _perplexity_query(query)
    result["company"] = company_name
    result["target_title"] = title
    return json.dumps(result, indent=2)


@tool
def verify_email(email: str) -> str:
    """
    Verify if an email address is valid and deliverable.
    For MVP, does format validation. In production, integrate Hunter.io or similar.

    Args:
        email: Email address to verify

    Returns:
        JSON string with verification status
    """
    import re

    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

    if not email or not re.match(email_pattern, email):
        return json.dumps({
            'email': email,
            'status': 'invalid',
            'deliverable': False,
            'reason': 'Invalid email format'
        })

    disposable_domains = ['tempmail.com', 'throwaway.email', '10minutemail.com']
    domain = email.split('@')[1].lower()

    if domain in disposable_domains:
        return json.dumps({
            'email': email,
            'status': 'disposable',
            'deliverable': False,
            'reason': 'Disposable email domain'
        })

    return json.dumps({
        'email': email,
        'status': 'unverified',
        'deliverable': 'unknown',
        'reason': 'Format valid. Integrate Hunter.io/NeverBounce for production verification.'
    })


@tool
def enrich_company(domain: str) -> str:
    """
    Get company information from domain using Perplexity.

    Args:
        domain: Company domain (e.g., "stripe.com")

    Returns:
        JSON string with company info and evidence URLs
    """
    query = (
        f"Tell me about the company at {domain}. "
        f"Include: what they do, industry, founding year, headquarters, "
        f"employee count, funding raised, key executives, and recent news."
    )

    result = _perplexity_query(query)
    result["domain"] = domain
    return json.dumps(result, indent=2)


@tool
def search_news(company_name: str, topic: str = "", within_days: int = 90) -> str:
    """
    Search for recent news about a company.

    Args:
        company_name: Name of the company
        topic: Optional specific topic (e.g., "product launch", "partnership")
        within_days: Search news within this many days

    Returns:
        JSON string with news articles and URLs
    """
    cutoff = (datetime.now() - timedelta(days=within_days)).strftime("%B %Y")
    topic_str = f" related to {topic}" if topic else ""

    query = (
        f"What are the latest news and updates about {company_name}{topic_str} "
        f"since {cutoff}? Include product launches, partnerships, expansions, and announcements."
    )

    result = _perplexity_query(query)
    result["company"] = company_name
    result["signal_type"] = "news"
    return json.dumps(result, indent=2)


@tool
def find_competitors(company_name: str, industry: str = "") -> str:
    """
    Find and analyze competitors for a company.

    Args:
        company_name: Your company or a target company
        industry: Industry context for better results

    Returns:
        JSON string with competitor analysis and citations
    """
    industry_str = f" in the {industry} space" if industry else ""

    query = (
        f"Who are the main competitors of {company_name}{industry_str}? "
        f"For each competitor, include: name, website, what they do differently, "
        f"recent funding, and any recent product moves or announcements."
    )

    result = _perplexity_query(query)
    result["company"] = company_name
    return json.dumps(result, indent=2)


@tool
def find_product_insights(industry: str, topic: str = "trends") -> str:
    """
    Find product and market insights for an industry.

    Args:
        industry: Industry to research
        topic: Specific topic (e.g., "trends", "pain points", "emerging tech")

    Returns:
        JSON string with insights and citations
    """
    query = (
        f"What are the latest {topic} in the {industry} industry? "
        f"Include specific examples, data points, and emerging opportunities. "
        f"Focus on what's changed in the last 6 months."
    )

    result = _perplexity_query(query)
    result["industry"] = industry
    result["topic"] = topic
    return json.dumps(result, indent=2)


@tool
def find_partnership_opportunities(
    company_name: str,
    industry: str = "",
    partnership_type: str = "integration"
) -> str:
    """
    Scout potential partnership opportunities.

    Args:
        company_name: Your company name
        industry: Industry context
        partnership_type: Type of partnership (integration, reseller, co-marketing)

    Returns:
        JSON string with partnership opportunities and citations
    """
    query = (
        f"What companies would be good {partnership_type} partners for {company_name} "
        f"{'in ' + industry if industry else ''}? "
        f"Look for companies with complementary products, shared customer base, "
        f"or recent partnership announcements in the space."
    )

    result = _perplexity_query(query)
    result["company"] = company_name
    result["partnership_type"] = partnership_type
    return json.dumps(result, indent=2)


# All available tools
TOOLS = [
    deep_research,
    search_companies_by_criteria,
    find_hiring_signals,
    find_funding_signals,
    find_company_contacts,
    verify_email,
    enrich_company,
    search_news,
    find_competitors,
    find_product_insights,
    find_partnership_opportunities,
]


def get_tool_by_name(name: str):
    """Get a tool by its name"""
    for t in TOOLS:
        if t.name == name:
            return t
    raise ValueError(f"Tool {name} not found. Available: {[t.name for t in TOOLS]}")
