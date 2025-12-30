from flask import Blueprint

# Generate Blueprint instances
ktracker_bp  = Blueprint('ktracker', __name__, template_folder='templates', static_folder='static')

# Blueprint modules import
from . import routes