import os
import sys

# Add project directory to sys.path
project_home = os.path.dirname(os.path.abspath(__file__))
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Add virtualenv site-packages to sys.path (cPanel Python App)
# Update this path based on your cPanel Python app's virtualenv location
VIRTUALENV = os.path.join(project_home, 'venv')
python_version = f'python{sys.version_info.major}.{sys.version_info.minor}'
site_packages = os.path.join(VIRTUALENV, 'lib', python_version, 'site-packages')
if os.path.exists(site_packages):
    sys.path.insert(0, site_packages)

# Load .env file if python-decouple is available
env_file = os.path.join(project_home, '.env')
if os.path.exists(env_file):
    try:
        from decouple import Config, RepositoryEnv
        env_config = Config(RepositoryEnv(env_file))
    except ImportError:
        pass

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

# Import Django WSGI application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
