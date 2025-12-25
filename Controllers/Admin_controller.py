from flask import Blueprint, render_template, session, redirect, url_for,request,flash
from Controllers.decorators import admin_required
from models.User_model import UserModel
from models.Report_model import ReportModel
from models.admin_dashboard_model import AdminDashboardModel

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin')
@admin_required
def dashboard():
    model = AdminDashboardModel()

    total_users = model.get_total_users()
    active_users = model.get_active_users()
    total_reports = model.get_total_reports()
    latest_reports = model.get_latest_reports()
    top_downloads = model.top_down_reports()
    top_views = model.top_view_reports()
    top_favorites = model.top_like_reports()

    return render_template('admin/dashboard.html',
        total_users=total_users,
        total_reports=total_reports,
        active_users=active_users,
        latest_reports=latest_reports,
        top_downloads=top_downloads,
        top_views=top_views,
        top_favorites=top_favorites
        )
@admin_bp.route('/admin/users')
@admin_required
def users():
    keyword = request.args.get('keyword', '')
    status = request.args.get('status', '')
    sort = request.args.get('sort', 'asc')

    users = UserModel.get_users(keyword, status, sort)

    return render_template(
        'admin/user.html',
        users=users,
        keyword=keyword,
        status=status,
        sort=sort
    )

@admin_bp.route('/admin/reports')
@admin_required
def reports():
    keyword = request.args.get('keyword', '')
    status = request.args.get('status', '')
    sort = request.args.get('sort', 'asc')

    reports = ReportModel.get_reports(keyword, status, sort)
    return render_template('admin/reports.html',
        reports=reports,
        keyword=keyword,
        status=status,
        sort=sort)

@admin_bp.route('/admin/create-user', methods=['GET', 'POST'])
@admin_required
def create_user():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        full_name = request.form['full_name']
        role = request.form['role']

        UserModel.create_user(username, password, full_name, role)

        flash('Tạo user thành công!', 'success')
        return redirect(url_for('admin.users'))

    return render_template('admin/user_add.html')

@admin_bp.route('/admin/create_report', methods=['GET', 'POST'])
@admin_required
def create_report():
    if request.method == 'POST':
        NameReport = request.form['name']
        FileUrl = request.form['file_url']
        FileDownload = request.form['file_download']
        param_names = request.form.getlist('param_name[]')
        param_values = request.form.getlist('param_value[]')
        base_url = "https://webconnect.trailsofindochina.com/ReportServer"
        params = []
        for k, v in zip(param_names, param_values):
            if k:
                params.append({
                    'name': k,
                    'value': v
                })
        file_download = (
            f"{base_url}?"
            f"{FileDownload}"
            f"&rs:Format=EXCEL"
        )

        ReportModel.create_report(NameReport, FileUrl, file_download,params)
        flash('Tạo report thành công!', 'success')
        return redirect(url_for('admin.reports'))

    return render_template('admin/report_add.html')

@admin_bp.route('/admin/users/edit/<int:id>', methods=['GET', 'POST'])
@admin_required
def edit_user(id):
    user = UserModel.get_by_id(id)
    if not user:
        flash('User không tồn tại !!!', 'error')
        return redirect(url_for('admin.users'))
    if request.method == 'POST':
        full_name = request.form.get('full_name')
        role = request.form.get('role')
        status = request.form.get('status')
        password = request.form.get('password')
        password_hash = None
        if password:
            password_hash = UserModel.hash_password(password)
        if password_hash is not None:
            UserModel.update_user(
                id=id,
                full_name=full_name,
                role=role,
                status=status,
                password=password_hash
            )
        else:
            UserModel.update_user(
                id=id,
                full_name=full_name,
                role=role,
                status=status
            )
        flash('Sửa user thành công!', 'success')
        return redirect(url_for('admin.users'))

    return render_template('admin/user_edit.html',user=user)

@admin_bp.route('/admin/reports/edit/<int:id>', methods=['GET', 'POST'])
@admin_required
def edit_report(id):
    report = ReportModel.get_by_id(id)
    if not report:
        flash('Report không tồn tại !!!', 'error')
        return redirect(url_for('admin.reports'))
    if request.method == 'POST':
        report_name = request.form.get('name')
        link = request.form.get('file_url')
        download = request.form.get('file_download')
        status = request.form.get('status')

        param_ids = request.form.getlist('param_id[]')
        param_names = request.form.getlist('param_name[]')
        param_values = request.form.getlist('param_value[]')

        params = []
        for pid, pname, pvalue in zip(param_ids, param_names, param_values):
            if pname.strip():
                params.append({
                    "id": pid,
                    "name": pname.strip(),
                    "value": pvalue.strip()
                })

        ReportModel.update_report(
                id=id,
                report_name=report_name,
                filepath=link,
                downloadLink=download,
                status=status,
                params = params
            )
        flash('Sửa report thành công!', 'success')
        return redirect(url_for('admin.reports'))

    return render_template('admin/report_edit.html',report=report)


@admin_bp.route('/admin/users/delete/<int:id>', methods=['POST', 'GET'])
@admin_required
def delete_user_route(id):
    if id == session.get('user_id'):
        flash('❌ Bạn không thể xoá chính mình', 'error')
        return redirect(url_for('admin.users'))

    if UserModel.delete_user(id):
        flash('✅ Xoá user thành công', 'success')
    else:
        flash('⚠️ User không tồn tại hoặc đã bị xoá', 'warning')
    return redirect(url_for('admin.users'))

@admin_bp.route('/admin/reports/delete/<int:id>', methods=['POST', 'GET'])
@admin_required
def delete_report_route(id):
    if ReportModel.delete_report(id):
        flash('✅ Xoá Report thành công', 'success')
    else:
        flash('⚠️ Report không tồn tại hoặc đã bị xoá', 'warning')
    return redirect(url_for('admin.reports'))