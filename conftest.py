import os
import sys

# Ensure the project root is importable so tests can `import insights`,
# `from models.prophet_model import ...`, etc. — mirroring how the app runs
# from the repository root under `streamlit run app.py`.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
