from flask import Blueprint

# Generate Blueprint instances
main_bp  = Blueprint('main', __name__, template_folder='templates')

# Blueprint modules import
from . import routes