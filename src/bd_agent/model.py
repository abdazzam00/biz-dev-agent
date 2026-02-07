import os
from pydantic import BaseModel
from typing import Type, List, Optional, Any
from langchain_core.tools import BaseTool
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic

from bd_agent.prompts import DEFAULT_SYSTEM_PROMPT

# Default model - Claude is great for research tasks
DEFAULT_MODEL = "claude-3-5-sonnet-20241022"


def get_chat_model(
    model_name: str = DEFAULT_MODEL,
    temperature: float = 0,
    streaming: bool = False
) -> BaseChatModel:
    """Factory function to get the appropriate chat model"""
    
    if model_name.startswith("claude-"):
        # Anthropic models
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment variables")
        
        return ChatAnthropic(
            model=model_name,
            api_key=api_key,
            temperature=temperature,
            streaming=streaming
        )
    else:
        # OpenAI models
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        
        return ChatOpenAI(
            model=model_name,
            api_key=api_key,
            temperature=temperature,
            streaming=streaming
        )


def call_llm(
    prompt: str,
    system_prompt: str = DEFAULT_SYSTEM_PROMPT,
    model_name: str = DEFAULT_MODEL,
    response_format: Optional[Type[BaseModel]] = None,
    tools: Optional[List[BaseTool]] = None,
) -> Any:
    """
    Call the LLM with the given prompt
    
    Args:
        prompt: User prompt
        system_prompt: System prompt
        model_name: Model to use
        response_format: Optional Pydantic model for structured output
        tools: Optional list of tools
        
    Returns:
        LLM response
    """
    llm = get_chat_model(model_name=model_name)
    
    if response_format:
        llm = llm.with_structured_output(response_format)
    
    if tools:
        llm = llm.bind_tools(tools)
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": prompt}
    ]
    
    response = llm.invoke(messages)
    
    return response
