from langchain_core.tools import tool
from typing import List, Dict, Any, Optional
import requests
import os
import json
from datetime import datetime, timedelta


@tool
def web_search(query: str, num_results: int = 10) -> str:
    """
    Search the web for information. Returns results with URLs for evidence.
    
    CRITICAL: This is the foundation tool. Every piece of data must trace back to a URL.
    
    Use for:
    - Finding companies matching ICP criteria
    - Discovering signals (hiring, funding, product launches)
    - Researching competitors
    - Finding contact information
    
    Args:
        query: Search query
        num_results: Number of results to return (default 10)
        
    Returns:
        JSON string with search results including title, snippet, and URL
    """
    serper_api_key = os.getenv("SERPER_API_KEY")
    
    if not serper_api_key:
        return json.dumps({
            "error": "SERPER_API_KEY not found",
            "message": "Get a free key at https://serper.dev and add to .env",
            "results": []
        })
    
    url = "https://google.serper.dev/search"
    headers = {
        'X-API-KEY': serper_api_key,
        'Content-Type': 'application/json'
    }
    payload = {
        'q': query,
        'num': num_results
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        results = []
        if 'organic' in data:
            for item in data['organic']:
                results.append({
                    'title': item.get('title', ''),
                    'snippet': item.get('snippet', ''),
                    'url': item.get('link', ''),
                    'date': item.get('date', '')
                })
        
        return json.dumps({
            'query': query,
            'num_results': len(results),
            'results': results
        }, indent=2)
        
    except Exception as e:
        return json.dumps({
            'error': str(e),
            'results': []
        })


@tool
def search_companies_by_criteria(
    industry: str,
    location: str = "",
    stage: str = "",
    min_employees: int = 0,
    max_employees: int = 10000
) -> str:
    """
    Search for companies matching specific ICP criteria.
    
    Args:
        industry: Industry or vertical (e.g., "fintech", "health tech")
        location: Geographic location (e.g., "NYC", "San Francisco", "US")
        stage: Funding stage (e.g., "seed", "series A", "series B")
        min_employees: Minimum employee count
        max_employees: Maximum employee count
        
    Returns:
        JSON string with companies and evidence URLs
    """
    # Build search query
    query_parts = [industry]
    
    if stage:
        query_parts.append(f"{stage} funding")
    
    if location:
        query_parts.append(location)
    
    query_parts.append(f"{min_employees}-{max_employees} employees")
    query_parts.append("companies")
    
    query = " ".join(query_parts)
    
    return web_search(query=query, num_results=15)


@tool
def find_hiring_signals(company_name: str, role_keywords: str = "SDR,sales,growth") -> str:
    """
    Find hiring signals for a company.
    
    Args:
        company_name: Name of the company
        role_keywords: Comma-separated role keywords to search for
        
    Returns:
        JSON string with hiring postings and URLs as evidence
    """
    query = f"{company_name} hiring {role_keywords} site:linkedin.com OR site:greenhouse.io OR site:lever.co"
    
    return web_search(query=query, num_results=10)


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
    # Calculate date range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=within_days)
    
    query = f"{company_name} funding OR investment OR raised after:{start_date.strftime('%Y-%m-%d')}"
    
    return web_search(query=query, num_results=10)


@tool
def find_company_contacts(company_name: str, title: str) -> str:
    """
    Find contacts at a company with specific titles.
    
    IMPORTANT: Results must include LinkedIn URLs or other profile URLs as evidence.
    
    Args:
        company_name: Name of the company
        title: Job title to search for (e.g., "VP Sales", "Head of Growth")
        
    Returns:
        JSON string with contacts and profile URLs
    """
    query = f"{title} at {company_name} site:linkedin.com/in"
    
    return web_search(query=query, num_results=10)


@tool
def verify_email(email: str) -> str:
    """
    Verify if an email address is valid and deliverable.
    
    NOTE: In production, integrate with Hunter.io, NeverBounce, or ZeroBounce.
    For MVP, this does basic format validation only.
    
    Args:
        email: Email address to verify
        
    Returns:
        JSON string with verification status
    """
    import re
    
    # Basic email format validation
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if not email or not re.match(email_pattern, email):
        return json.dumps({
            'email': email,
            'status': 'invalid',
            'deliverable': False,
            'reason': 'Invalid email format'
        })
    
    # Check for common disposable domains
    disposable_domains = ['tempmail.com', 'throwaway.email', '10minutemail.com']
    domain = email.split('@')[1].lower()
    
    if domain in disposable_domains:
        return json.dumps({
            'email': email,
            'status': 'disposable',
            'deliverable': False,
            'reason': 'Disposable email domain'
        })
    
    # For MVP, return unverified but valid format
    return json.dumps({
        'email': email,
        'status': 'unverified',
        'deliverable': 'unknown',
        'reason': 'Email verification requires API integration (Hunter.io, NeverBounce, etc.)',
        'note': 'Format is valid. Integrate email verification API for production use.'
    })


@tool
def enrich_company(domain: str) -> str:
    """
    Get company information from domain.
    
    NOTE: In production, integrate with Clearbit, Apollo, or similar.
    For MVP, uses web search.
    
    Args:
        domain: Company domain (e.g., "stripe.com")
        
    Returns:
        JSON string with company info and evidence URLs
    """
    query = f"site:{domain} OR {domain} company information employees funding"
    
    result = web_search(query=query, num_results=5)
    
    try:
        data = json.loads(result)
        
        return json.dumps({
            'domain': domain,
            'source': 'web_search',
            'note': 'For production, integrate Clearbit/Apollo for structured data',
            'search_results': data.get('results', [])
        }, indent=2)
        
    except:
        return result


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
    end_date = datetime.now()
    start_date = end_date - timedelta(days=within_days)
    
    query = f"{company_name} {topic} after:{start_date.strftime('%Y-%m-%d')}".strip()
    
    return web_search(query=query, num_results=10)


@tool
def perplexity_search(query: str) -> str:
    """
    Use Perplexity AI for research (if API key is available).
    
    Perplexity is excellent for getting cited, factual answers with sources.
    
    Args:
        query: Research question
        
    Returns:
        JSON string with answer and citations
    """
    api_key = os.getenv("PERPLEXITY_API_KEY")
    
    if not api_key:
        return json.dumps({
            'error': 'PERPLEXITY_API_KEY not set',
            'fallback': 'Using regular web search instead',
            'note': 'Get Perplexity API key at https://www.perplexity.ai/settings/api'
        })
    
    try:
        url = "https://api.perplexity.ai/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "llama-3.1-sonar-small-128k-online",
            "messages": [
                {"role": "user", "content": query}
            ]
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        answer = data['choices'][0]['message']['content']
        citations = data.get('citations', [])
        
        return json.dumps({
            'query': query,
            'answer': answer,
            'citations': citations,
            'source': 'perplexity'
        }, indent=2)
        
    except Exception as e:
        # Fallback to web search
        return web_search(query=query)


# List of all available tools
TOOLS = [
    web_search,
    search_companies_by_criteria,
    find_hiring_signals,
    find_funding_signals,
    find_company_contacts,
    verify_email,
    enrich_company,
    search_news,
    perplexity_search,
]


def get_tool_by_name(name: str):
    """Get a tool by its name"""
    for tool in TOOLS:
        if tool.name == name:
            return tool
    raise ValueError(f"Tool {name} not found")
