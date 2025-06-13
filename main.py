# main.py (in project root) - Clean approach
import sys
import os

# Add the package to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'redis-notification-system'))

# Import the main function from __init__.py
from __init__ import main

if __name__ == "__main__":
    main()