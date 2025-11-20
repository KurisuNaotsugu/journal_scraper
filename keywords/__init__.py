from flask import Blueprint

# Generate Blueprint instances
keywords_bp  = Blueprint('keywords', __name___, template_folder='templates')

# Blueprint modules import
from . import routes