from flask import Blueprint, render_template
from . import main_bp  

@main_bp.route('/main')
def main_page():

    return "main Page"