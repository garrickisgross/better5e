import sys, os
# Insert the project root (one level up from tests/) at the front of sys.path
sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
)