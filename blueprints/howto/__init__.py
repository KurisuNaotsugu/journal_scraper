from flask import Blueprint

# Generate Blueprint instances
howto_bp  = Blueprint('howto', __name__, template_folder='templates', static_folder='static')

# Blueprint modules import
from . import routes