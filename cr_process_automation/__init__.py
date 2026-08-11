import rootutils
from dotenv import load_dotenv

# This finds the root, sets PROJECT_ROOT env var, loads .env, and adds root to PYTHONPATH
root = rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True, dotenv=True)

os.environ["PROJECT_ROOT"] = str(root)

# Load variables from .env into the system environment
load_dotenv()

# print("loaded all dotenv and rootutils")
