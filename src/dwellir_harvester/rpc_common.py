"""Common RPC utilities for interacting with blockchain nodes."""
from typing import Any, Dict, List, Optional, Tuple

def jsonrpc_call(url: str, method: str, params: Optional[List[Any]] = None, **kwargs) -> Tuple[Any, Optional[str]]:
    """Make a JSON-RPC call to a node.
    
    Args:
        url: The URL of the JSON-RPC endpoint
        method: The JSON-RPC method to call
        params: Optional list of parameters for the method
        **kwargs: Additional arguments to pass to requests.post()
        
    Returns:
        A tuple of (result, error) where only one will be non-None
    """
    try:
        import requests
        payload = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params or [],
            "id": 1
        }
        
        # Add any additional request parameters
        request_kwargs = {"json": payload, "timeout": 10}
        if 'headers' not in request_kwargs:
            request_kwargs['headers'] = {'Content-Type': 'application/json'}
        request_kwargs.update(kwargs)
        
        response = requests.post(url, **request_kwargs)
        response.raise_for_status()
        result = response.json()
        
        # Handle JSON-RPC error response
        if 'error' in result and result['error'] is not None:
            return None, str(result['error'])
            
        return result.get('result'), None
        
    except Exception as e:
        return None, str(e)
