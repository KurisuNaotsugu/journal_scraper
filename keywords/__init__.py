from flask import Blueprint

# Generate Blueprint instances
keywords_bp  = Blueprint('keywords', __name__, template_folder='templates')

# Blueprint modules import
from . import routes