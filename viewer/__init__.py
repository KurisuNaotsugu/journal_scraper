from flask import Blueprint

# Generate Blueprint instances
viewer_bp  = Blueprint('viewer', __name__, template_folder='templates', static_folder='static')

# Blueprint modules import
from . import routes