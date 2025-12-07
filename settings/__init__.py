from flask import Blueprint

# Generate Blueprint instances
settings_bp  = Blueprint('settings', __name__, template_folder='templates', static_folder='static')

# Blueprint modules import
from . import routes