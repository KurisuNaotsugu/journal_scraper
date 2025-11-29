from flask import Blueprint

# Generate Blueprint instances
manualsearch_bp  = Blueprint('manual_search', __name__, template_folder='templates', static_folder='static')

# Blueprint modules import
from . import routes