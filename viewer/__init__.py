from flask import Blueprint

# Generate Blueprint instances
view_bp  = Blueprint('view', __name__, template_folder='templates', static_folder='static')

# Blueprint modules import
from . import routes