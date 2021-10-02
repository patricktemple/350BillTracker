from flask import request
from functools import wraps

# TODO: Rewrite this to invert the auth check
def auth_required(view_fn):
  @wraps(view_fn)
  def check_auth_and_run(*args, **kwargs):
    auth = request.headers.get("Authorization")
    if not auth:
      # TODO: HTTP error types in flask?
      raise ValueError("Authorization required")
    if not auth.startswith("JWT "):
      raise ValueError("Expecting JWT auth type")
    
    # TODO: Validate the JWT itself

    return view_fn(*args, **kwargs)
  
  return check_auth_and_run