from flask import Blueprint, render_template
from . import keywords_bp  # initで定義されたBlueprintインスタンスをインポート

@keywords_bp.route('/keywords')
def product_home():
    return "keywirds Page"