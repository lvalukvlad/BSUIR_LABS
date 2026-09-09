from flask import Blueprint, render_template, session
from app.controllers.admin_controller import AdminController

admin_bp = Blueprint('admin', __name__)
admin_controller = AdminController()

@admin_bp.route('/admin/report')
def report():
    if session.get('role') != 'admin':
        return "Access denied", 403
    stats = admin_controller.get_statistics()
    return render_template('report.html', stats=stats, user=session)