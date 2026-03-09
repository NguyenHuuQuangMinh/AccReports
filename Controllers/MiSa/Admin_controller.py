from flask import Blueprint, render_template, session, redirect, url_for, request, flash, jsonify
from Controllers.decorators import admin_required
from models.Misa.User_model import UserModel
from models.Misa.Report_model import ReportModel
from models.Misa.admin_dashboard_model import AdminDashboardModel
from models.Misa.Role_model import RoleModel
from collections import defaultdict
from models.LandingPage.weblink_model import LinkModel as WeblinkModel

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin')
@admin_required
def dashboard():
    model = AdminDashboardModel()

    total_users = model.get_total_users()
    active_users = model.get_active_users()
    active_reports = model.get_active_reports()
    total_reports = model.get_total_reports()
    latest_reports = model.get_latest_reports()
    top_downloads = model.top_down_reports()
    top_views = model.top_view_reports()
    top_favorites = model.top_like_reports()
    top_api = model.top_api_reports()

    return render_template('Misa/admin/dashboard.html',
        total_users=total_users,
        total_reports=total_reports,
        active_users=active_users,
        active_reports=active_reports,
        latest_reports=latest_reports,
        top_downloads=top_downloads,
        top_views=top_views,
        top_favorites=top_favorites,
        top_api=top_api
        )
@admin_bp.route('/admin/users')
@admin_required
def users():
    keyword = request.args.get('keyword', '')
    status = request.args.get('status', '')
    sort = request.args.get('sort', 'asc')
    page = request.args.get('page', 1, type=int)  # trang hiện tại
    per_page = 5

    session['user_filter'] = {
        'keyword': keyword,
        'status': status,
        'sort': sort
    }

    bulk = session.get('bulk_mode')
    bulk_selected = session.get('bulk_selected', [])
    selected_count = len(bulk_selected)
    users, total_users = UserModel.get_users(keyword, status, sort, page, per_page)
    total_pages = (total_users + per_page - 1) // per_page

    return render_template(
        'Misa/admin/user.html',
        users=users,
        keyword=keyword,
        status=status,
        sort=sort,
        page=page,
        total_pages=total_pages,
        bulk=bulk,
        selected_count=selected_count
    )

@admin_bp.route('/admin/bulk-mode/multi', methods=['POST'])
@admin_required
def bulk_mode_multi():
    session['bulk_mode'] = 'multi'
    session['bulk_selected'] = []   # reset
    session.modified = True
    return jsonify(ok=True)

@admin_bp.route('/admin/bulk-mode/clear', methods=['POST'])
@admin_required
def bulk_mode_clear():
    session.pop('bulk_mode', None)
    session.pop('bulk_selected', None)
    session.modified = True
    return jsonify(ok=True)

@admin_bp.route('/admin/bulk-mode/all', methods=['POST'])
@admin_required
def bulk_mode_all():
    ids = UserModel.get_all_user_ids(
        exclude_user_id=session['user_id'],
        keyword=request.args.get('keyword', ''),
        status=request.args.get('status', '')
    )
    session['bulk_mode'] = 'all'
    session['bulk_selected'] = ids
    session.modified = True
    return jsonify(ok=True)

@admin_bp.route('/admin/bulk-select', methods=['POST'])
@admin_required
def bulk_select():
    data = request.json
    uid = int(data['user_id'])
    checked = data['checked']

    selected = session.get('bulk_selected', [])

    if checked and uid not in selected:
        selected.append(uid)
    if not checked and uid in selected:
        selected.remove(uid)
    if session['bulk_mode'] != 'multi':
        session['bulk_mode'] = 'multi'
    session['bulk_selected'] = selected
    session.modified = True

    return jsonify(ok=True, count=len(selected))

@admin_bp.route('/admin/roles')
@admin_required
def roles():
    keyword = request.args.get('keyword', '')
    status = request.args.get('status', '')
    sort = request.args.get('sort', 'asc')
    page = request.args.get('page', 1, type=int)  # trang hiện tại
    per_page = 5

    session['role_filter'] = {
        'keyword': keyword,
        'status': status,
        'sort': sort
    }

    bulk = session.get('bulk_mode_role')
    bulk_selected = session.get('bulk_selected_role', [])
    selected_count = len(bulk_selected)
    Model = RoleModel()
    roles, total_roles = Model.get_roles(keyword, status, sort, page, per_page)
    total_pages = (total_roles + per_page - 1) // per_page

    return render_template(
        'Misa/admin/role.html',
        roles=roles,
        keyword=keyword,
        status=status,
        sort=sort,
        page=page,
        total_pages=total_pages,
        bulk=bulk,
        selected_count=selected_count
    )

@admin_bp.route('/admin/bulk-mode-role/multi', methods=['POST'])
@admin_required
def bulk_mode_multi_role():
    session['bulk_mode_role'] = 'multi'
    session['bulk_selected_role'] = []   # reset
    session.modified = True
    return jsonify(ok=True)

@admin_bp.route('/admin/bulk-mode-role/clear', methods=['POST'])
@admin_required
def bulk_mode_clear_role():
    session.pop('bulk_mode_role', None)
    session.pop('bulk_selected_role', None)
    session.modified = True
    return jsonify(ok=True)

@admin_bp.route('/admin/bulk-mode-role/all', methods=['POST'])
@admin_required
def bulk_mode_all_role():
    model = RoleModel()
    ids = model.get_all_role_ids(
        exclude_role_id=1,
        keyword=request.args.get('keyword', ''),
        status=request.args.get('status', '')
    )
    session['bulk_mode_role'] = 'all'
    session['bulk_selected_role'] = ids
    session.modified = True
    return jsonify(ok=True)

@admin_bp.route('/admin/bulk-select-role', methods=['POST'])
@admin_required
def bulk_select_role():
    data = request.json
    rid = int(data['role_id'])
    checked = data['checked']

    selected = session.get('bulk_selected_role', [])

    if checked and rid not in selected:
        selected.append(rid)
    if not checked and rid in selected:
        selected.remove(rid)
    if session['bulk_mode_role'] != 'multi':
        session['bulk_mode_role'] = 'multi'
    session['bulk_selected_role'] = selected
    session.modified = True

    return jsonify(ok=True, count=len(selected))

@admin_bp.route('/admin/reports')
@admin_required
def reports():
    categories = ReportModel.get_all_category()
    keyword = request.args.get('keyword', '')
    status = request.args.get('status', '')
    sort = request.args.get('sort', 'asc')
    category = request.args.get('category_sort', '')
    page = request.args.get('page', 1, type=int)  # trang hiện tại
    per_page = 5

    session['report_filter'] = {
        'keyword': keyword,
        'status': status,
        'sort': sort,
        'category': category
    }

    bulk = session.get('bulk_mode_report')
    bulk_selected = session.get('bulk_selected_report', [])
    selected_count = len(bulk_selected)

    reports, total_reports = ReportModel.get_reports(keyword, status, sort, category, page, per_page)
    print(total_reports)
    total_pages = (total_reports + per_page - 1) // per_page
    print(total_pages)
    return render_template('Misa/admin/reports.html',
        reports=reports,
        keyword=keyword,
        status=status,
        sort=sort,
        cate = category,
        page=page,
        total_pages=total_pages,
        bulk=bulk,
        selected_count=selected_count,
        categories=categories
        )

@admin_bp.route('/admin/reports_category')
@admin_required
def reports_category():
    keyword = request.args.get('keyword', '')
    status = request.args.get('status', '')
    sort = request.args.get('sort', 'asc')
    page = request.args.get('page', 1, type=int)  # trang hiện tại
    per_page = 5
    session['report_category_filter'] = {
        'keyword': keyword,
        'status': status,
        'sort': sort
    }

    bulk = session.get('bulk_mode_report_cate')
    bulk_selected = session.get('bulk_selected_report_cate', [])
    selected_count = len(bulk_selected)

    reports_category, total_reports = ReportModel.get_reports_cate(keyword, status, sort, page, per_page)
    print(total_reports)
    total_pages = (total_reports + per_page - 1) // per_page
    print(total_pages)
    return render_template('Misa/admin/reports_cate.html',
        reports_cate=reports_category,
        keyword=keyword,
        status=status,
        sort=sort,
        page=page,
        total_pages=total_pages,
        bulk=bulk,
        selected_count=selected_count
        )

@admin_bp.route('/admin/bulk-mode-report/multi', methods=['POST'])
@admin_required
def bulk_mode_multi_reports():
    session['bulk_mode_report'] = 'multi'
    session['bulk_selected_report'] = []   # reset
    session.modified = True
    return jsonify(ok=True)

@admin_bp.route('/admin/bulk-mode-report/clear', methods=['POST'])
@admin_required
def bulk_mode_clear_reports():
    session.pop('bulk_mode_report', None)
    session.pop('bulk_selected_report', None)
    session.modified = True
    return jsonify(ok=True)

@admin_bp.route('/admin/bulk-mode-report/all', methods=['POST'])
@admin_required
def bulk_mode_all_reports():
    filters = session.get('report_filter', {})
    keyword = filters.get('keyword', '')
    status = filters.get('status', '')
    category = filters.get('category', '')
    ids = ReportModel.get_all_report_ids(
        keyword=keyword,
        status=status,
        category = category
    )
    session['bulk_mode_report'] = 'all'
    session['bulk_selected_report'] = ids
    session.modified = True
    return jsonify(ok=True)

@admin_bp.route('/admin/bulk-select-report', methods=['POST'])
@admin_required
def bulk_select_reports():
    data = request.json
    rid = int(data['report_id'])
    checked = data['checked']

    selected = session.get('bulk_selected_report', [])

    if checked and rid not in selected:
        selected.append(rid)
    if not checked and rid in selected:
        selected.remove(rid)
    if session['bulk_mode_report'] != 'multi':
        session['bulk_mode_report'] = 'multi'
    session['bulk_selected_report'] = selected
    session.modified = True

    return jsonify(ok=True, count=len(selected))

@admin_bp.route('/admin/bulk-mode-report-cate/multi', methods=['POST'])
@admin_required
def bulk_mode_multi_reports_cate():
    session['bulk_mode_report_cate'] = 'multi'
    session['bulk_selected_report_cate'] = []   # reset
    session.modified = True
    return jsonify(ok=True)

@admin_bp.route('/admin/bulk-mode-report-cate/clear', methods=['POST'])
@admin_required
def bulk_mode_clear_reports_cate():
    session.pop('bulk_mode_report_cate', None)
    session.pop('bulk_selected_report_cate', None)
    session.modified = True
    return jsonify(ok=True)

@admin_bp.route('/admin/bulk-mode-report-cate/all', methods=['POST'])
@admin_required
def bulk_mode_all_reports_cate():
    ids = ReportModel.get_all_report_cate_ids(
        keyword=request.args.get('keyword', ''),
        status=request.args.get('status', '')
    )
    session['bulk_mode_report_cate'] = 'all'
    session['bulk_selected_report_cate'] = ids
    session.modified = True
    return jsonify(ok=True)

@admin_bp.route('/admin/bulk-select-report-cate', methods=['POST'])
@admin_required
def bulk_select_reports_cate():
    data = request.json
    rid = int(data['report_cate_id'])
    checked = data['checked']

    selected = session.get('bulk_selected_report_cate', [])

    if checked and rid not in selected:
        selected.append(rid)
    if not checked and rid in selected:
        selected.remove(rid)
    if session['bulk_mode_report_cate'] != 'multi':
        session['bulk_mode_report_cate'] = 'multi'
    session['bulk_selected_report_cate'] = selected
    session.modified = True

    return jsonify(ok=True, count=len(selected))
@admin_bp.route('/admin/create-user', methods=['GET', 'POST'])
@admin_required
def create_user():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        full_name = request.form['full_name']
        role_id = request.form['role']

        success = UserModel.create_user(username, password, full_name, role_id)
        if not success:
            flash('❌ Username đã tồn tại!', 'error')
            return redirect(url_for('admin.create_user'))
        flash('Tạo user thành công!', 'success')
        return redirect(url_for('admin.users'))
    role_model = RoleModel()
    roles = role_model.get_all_roles()
    return render_template('Misa/admin/user_add.html', roles=roles)

@admin_bp.route('/admin/create-role', methods=['GET', 'POST'])
@admin_required
def create_role():
    if request.method == 'POST':
        rolename = request.form['name']
        role_model = RoleModel()
        role_model.create_role(rolename, 1)

        flash('Tạo role thành công!', 'success')
        return redirect(url_for('admin.roles'))
    return render_template('Misa/admin/role_add.html')

@admin_bp.route('/admin/create_report', methods=['GET', 'POST'])
@admin_required
def create_report():
    categories = ReportModel.get_all_category()
    if request.method == 'POST':
        NameReport = request.form['name']
        FileUrl = request.form['file_url']
        FileDownload = request.form['file_download']
        Descrip = request.form['description']
        CategoryId = request.form['category_id']
        param_names = request.form.getlist('param_name[]')
        param_values = request.form.getlist('param_value[]')
        param_labels = request.form.getlist('param_label[]')
        param_types = request.form.getlist('param_type[]')
        params = []
        for i in range(len(param_names)):
            k = param_names[i]
            v = param_values[i]
            l = param_labels[i]
            t = param_types[i]

            allow_null = request.form.get(f"allow_null[{i}]")
            allow_all = request.form.get(f"allow_all[{i}]")
            print(
                f'param_id:{i}, param_name:{k}, param_value:{v}, para_null:{allow_null}, para_all:{allow_all}')
            if k and t:
                params.append({
                    'name': k,
                    'value': v,
                    'label': l,
                    'type': t,
                    'null': 1 if allow_null else 0,
                    'all': 1 if allow_all else 0
                })
        ReportModel.create_report(NameReport, FileUrl, FileDownload,params,Descrip, CategoryId)
        flash('Tạo report thành công!', 'success')
        return redirect(url_for('admin.reports'))

    return render_template('Misa/admin/report_add.html', categories=categories)

@admin_bp.route('/admin/create_report_cate', methods=['GET', 'POST'])
@admin_required
def create_report_cate():
    if request.method == 'POST':
        NameReportCate = request.form['name']
        ReportModel.create_report_cate(NameReportCate)
        flash('Tạo tiêu đề Report thành công!', 'success')
        return redirect(url_for('admin.reports_category'))

    return render_template('Misa/admin/report_cate_add.html')

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
    role_model = RoleModel()
    roles = role_model.get_all_roles()
    return render_template('Misa/admin/user_edit.html',user=user, roles = roles)


@admin_bp.route('/admin/roles/edit/<int:id>', methods=['GET', 'POST'])
@admin_required
def edit_role(id):
    model = RoleModel()
    Role = model.get_role_by_id(id)
    if not Role:
        flash('Role không tồn tại !!!', 'error')
        return redirect(url_for('admin.roles'))
    if request.method == 'POST':
        Role_name = request.form.get('name')
        status = request.form.get('status')
        model.update_Role(
                id=id,
                name=Role_name,
                status=status
            )
        flash('Sửa Role thành công!', 'success')
        return redirect(url_for('admin.roles'))
    return render_template('Misa/admin/role_edit.html',role=Role)

@admin_bp.route('/admin/reports/edit/<int:id>', methods=['GET', 'POST'])
@admin_required
def edit_report(id):
    report = ReportModel.get_by_id(id)
    categories = ReportModel.get_all_category()
    if not report:
        flash('Report không tồn tại !!!', 'error')
        return redirect(url_for('admin.reports'))
    if request.method == 'POST':
        report_name = request.form.get('name')
        link = request.form.get('file_url')
        download = request.form.get('file_download')
        status = request.form.get('status')
        cate = request.form.get('category')
        description = request.form.get('description')
        param_ids = request.form.getlist('param_id[]') or ['']
        param_names = request.form.getlist('param_name[]') or ['']
        param_values = request.form.getlist('param_value[]') or ['']
        param_labels = request.form.getlist('param_label[]') or ['']
        param_types = request.form.getlist('param_type[]') or ['']
        params = []

        for i, (pid, pname, pvalue, plabel, ptype) in enumerate(zip(param_ids, param_names, param_values,param_labels,param_types)):
            pnull = request.form.get(f'allow_null[{i}]', 0)
            pall = request.form.get(f'allow_all[{i}]', 0)
            if pname.strip():
                params.append({
                    "id": pid,
                    "name": pname.strip(),
                    "value": pvalue.strip(),
                    "label": plabel.strip(),
                    "type": ptype.strip(),
                    "null": pnull,
                    "all": pall
                })

        ReportModel.update_report(
                id=id,
                report_name=report_name,
                filepath=link,
                downloadLink=download,
                status=status,
                params = params,
                description= description,
                category= cate
            )
        flash('Sửa report thành công!', 'success')
        return redirect(url_for('admin.reports'))

    return render_template('Misa/admin/report_edit.html',report=report, categories= categories)


@admin_bp.route('/admin/reports_cate/edit/<int:id>', methods=['GET', 'POST'])
@admin_required
def edit_report_cate(id):
    report_cate = ReportModel.get_cate_by_id(id)
    if not report_cate:
        flash('Tiêu đề report không tồn tại !!!', 'error')
        return redirect(url_for('admin.reports_category'))
    if request.method == 'POST':
        Name = request.form.get('name')
        status = request.form.get('status')
        ReportModel.update_report_cate(
                id=id,
                Cate_name=Name,
                status=status,
            )
        flash('Sửa tiêu đề report thành công!', 'success')
        return redirect(url_for('admin.reports_category'))

    return render_template('Misa/admin/report_cate_edit.html',report_cate=report_cate)

@admin_bp.route('/users/delete-multiple', methods=['POST'])
@admin_required
def delete_users():
    current_user = session.get('user_id')
    bulk = session.get('bulk_mode')
    bulk_selected = session.get('bulk_selected', [])
    filters = session.get('user_filter', {})
    keyword = filters.get('keyword', '')
    status = filters.get('status', '')
    if bulk == 'all':
        deleted_count = UserModel.delete_all_users(
            exclude_user_id=current_user,
            keyword=keyword,
            status=status
        )
        session.pop('bulk_mode', None)
        session.pop('bulk_selected', None)

        flash(f'🔥 Đã xoá {deleted_count} user.', 'success')
        return redirect(url_for('admin.users'))

    if not bulk_selected:
        flash('⚠️ Bạn chưa chọn user nào để xóa.', 'warning')
        return redirect(url_for('admin.users'))

    deleted_count = 0
    for uid in bulk_selected:
        uid_int = int(uid)
        if uid_int == current_user:
            flash('❌ Bạn không thể xoá chính mình', 'error')
            return redirect(url_for('admin.users'))
        if UserModel.delete_user(uid_int):
            deleted_count += 1
    session.pop('bulk_mode', None)
    session.pop('bulk_selected', None)

    flash(f'✅ Đã xóa {deleted_count} user thành công.', 'success')
    return redirect(url_for('admin.users'))

@admin_bp.route('/roles/delete-multiple', methods=['POST'])
@admin_required
def delete_roles():
    model = RoleModel()
    bulk = session.get('bulk_mode_role')
    bulk_selected = session.get('bulk_selected_role', [])
    filters = session.get('role_filter', {})
    keyword = filters.get('keyword', '')
    status = filters.get('status', '')
    if bulk == 'all':
        deleted_count = model.delete_all_roles(
            keyword=keyword,
            status=status
        )
        session.pop('bulk_mode_role', None)
        session.pop('bulk_selected_role', None)

        flash(f'🔥 Đã xoá {deleted_count} role.', 'success')
        return redirect(url_for('admin.roles'))

    if not bulk_selected:
        flash('⚠️ Bạn chưa chọn role nào để xóa.', 'warning')
        return redirect(url_for('admin.roles'))

    deleted_count = 0
    for rid in bulk_selected:
        rid_int = int(rid)
        if rid_int == 1:
            flash('❌ Bạn không thể xoá admin', 'error')
            return redirect(url_for('admin.roles'))
        if model.delete_role(rid_int):
            deleted_count += 1
    session.pop('bulk_mode_role', None)
    session.pop('bulk_selected_role', None)

    flash(f'✅ Đã xóa {deleted_count} role thành công.', 'success')
    return redirect(url_for('admin.roles'))

@admin_bp.route('/users/delete-multiple-report', methods=['POST'])
@admin_required
def delete_reports():
    bulk = session.get('bulk_mode_report')
    bulk_selected = session.get('bulk_selected_report', [])
    filters = session.get('report_filter', {})
    keyword = filters.get('keyword', '')
    status = filters.get('status', '')
    category = filters.get('category', '')

    print(f"{keyword} - - - -{status} - - -{category}")
    if bulk == 'all':
        deleted_count = ReportModel.delete_all_reports(
            keyword=keyword,
            status=status,
            category=category
        )
        session.pop('bulk_mode_report', None)
        session.pop('bulk_selected_report', None)

        flash(f'🔥 Đã xoá {deleted_count} report.', 'success')
        return redirect(url_for('admin.reports'))

    if not bulk_selected:
        flash('⚠️ Bạn chưa chọn report nào để xóa.', 'warning')
        return redirect(url_for('admin.reports'))

    deleted_count = 0
    for rid in bulk_selected:
        rid_int = int(rid)
        if ReportModel.delete_report(rid_int):
            deleted_count += 1
    session.pop('bulk_mode_report', None)
    session.pop('bulk_selected_report', None)

    flash(f'✅ Đã xóa {deleted_count} report thành công.', 'success')
    return redirect(url_for('admin.reports'))

@admin_bp.route('/users/delete-multiple-report-cate', methods=['POST'])
@admin_required
def delete_reports_cate():
    bulk = session.get('bulk_mode_report_cate')
    bulk_selected = session.get('bulk_selected_report_cate', [])
    filters = session.get('report_category_filter', {})
    keyword = filters.get('keyword', '')
    status = filters.get('status', '')

    print(f"{keyword}:{status}")
    if bulk == 'all':
        deleted_count = ReportModel.delete_all_reports_cate(
            keyword=keyword,
            status=status
        )
        session.pop('bulk_mode_report_cate', None)
        session.pop('bulk_selected_report_cate', None)

        flash(f'🔥 Đã xoá {deleted_count} tiêu đề report.', 'success')
        return redirect(url_for('admin.reports_category'))

    if not bulk_selected:
        flash('⚠️ Bạn chưa chọn tiêu đề report nào để xóa.', 'warning')
        return redirect(url_for('admin.reports_category'))

    deleted_count = 0
    for rid in bulk_selected:
        rid_int = int(rid)
        if ReportModel.delete_report_cate(rid_int):
            deleted_count += 1
    session.pop('bulk_mode_report_cate', None)
    session.pop('bulk_selected_report_cate', None)

    flash(f'✅ Đã xóa {deleted_count} tiêu đề report thành công.', 'success')
    return redirect(url_for('admin.reports_category'))

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

@admin_bp.route('/admin/roles/delete/<int:id>', methods=['POST', 'GET'])
@admin_required
def delete_role_route(id):
    if id == 1:
        flash('❌ Bạn không thể xoá role admin', 'error')
        return redirect(url_for('admin.roles'))
    model = RoleModel()
    if model.delete_role(id):
        flash('✅ Xoá Role thành công', 'success')
    else:
        flash('⚠️ Role không tồn tại hoặc đã bị xoá', 'warning')
    return redirect(url_for('admin.roles'))

@admin_bp.route('/admin/reports/delete/<int:id>', methods=['POST', 'GET'])
@admin_required
def delete_report_route(id):
    if ReportModel.delete_report(id):
        flash('✅ Xoá Report thành công', 'success')
    else:
        flash('⚠️ Report không tồn tại hoặc đã bị xoá', 'warning')
    return redirect(url_for('admin.reports'))

@admin_bp.route('/admin/reports_cate/delete/<int:id>', methods=['POST', 'GET'])
@admin_required
def delete_report_route_cate(id):
    if ReportModel.delete_report_cate(id):
        flash('✅ Xoá tiêu đề thành công', 'success')
    else:
        flash('⚠️ Tiêu đề report không tồn tại hoặc đã bị xoá', 'warning')
    return redirect(url_for('admin.reports_category'))

@admin_bp.route('/admin/roles/permissions/<int:id>/<string:name>', methods=['POST', 'GET'])
@admin_required
def role_permissions(id, name):
    id_role = id
    name_role = name
    model = RoleModel()
    assigned_reports,available_reports = model.role_permission(id_role)
    return render_template('Misa/admin/role_permission.html',
                           id_role=id_role,
                           name_role=name_role,
                           assigned_reports = assigned_reports,
                           available_reports = available_reports
                           )

@admin_bp.route('/admin/roles/permissions-cate/<int:id>/<string:name>', methods=['POST', 'GET'])
@admin_required
def role_permissions_cate(id, name):
    id_role = id
    name_role = name
    model = RoleModel()
    assigned_reports,available_reports = model.cate_permission(id_role)
    return render_template('Misa/admin/role_permission_cate.html',
                           id_role=id_role,
                           name_role=name_role,
                           assigned_reports = assigned_reports,
                           available_reports = available_reports
                           )

@admin_bp.route('/admin/roles/save_permissions', methods=['POST'])
@admin_required
def save_role_permissions():
    id_role = request.form.get('role_id')
    assigned_list = request.form.getlist('assigned[]')
    mode = RoleModel()
    update_permission = mode.update_permission(id_role, assigned_list)
    if update_permission:
        flash('✅ Cập nhật quyền thành công', 'success')
    else:
        flash('⚠️ Role không tồn tại hoặc đã bị xóa', 'warning')
    return redirect(url_for('admin.roles'))

@admin_bp.route('/admin/roles/save_permissions_cate', methods=['POST'])
@admin_required
def save_role_permissions_cate():
    id_role = request.form.get('role_id')
    assigned_list = request.form.getlist('assigned[]')
    mode = RoleModel()
    update_permission = mode.update_permission_cate(id_role, assigned_list)
    if update_permission:
        flash('✅ Cập nhật quyền thành công', 'success')
    else:
        flash('⚠️ Role không tồn tại hoặc đã bị xóa', 'warning')
    return redirect(url_for('admin.roles'))

@admin_bp.route('/admin/history')
@admin_required
def history_admin():
    from_date = request.args.get('from_date')
    to_date = request.args.get('to_date')
    keyword = request.args.get('keyword', '').strip()
    action_choice = request.args.get('action', '').strip()
    model = AdminDashboardModel()
    histories, total_dow, total_view, total_api = model.download_history_admin(from_date,to_date,keyword,action_choice)
    action = model.get_action()
    histories_by_date = defaultdict(list)

    for r in histories:
        date_key = r.CreatedAt.strftime('%d/%m/%Y')
        histories_by_date[date_key].append(r)
    return render_template('Misa/admin/history.html',
                                            histories_by_date=histories_by_date,
                                            from_date=from_date,
                                            to_date=to_date,
                                            keyword=keyword,
                                            action=action,
                                            total_download=total_dow,
                                            total_view=total_view,
                                            total_api=total_api
                                            )

@admin_bp.route('/admin/history-detail')
@admin_required
def history_detail():
    action = request.args.get('action')
    from_date = request.args.get('from_date')
    to_date = request.args.get('to_date')
    keyword = request.args.get('keyword')
    action_choice = request.args.get('action_choice', '')
    if action_choice == 'download-detail':
        action_choice = 'download'
    model = AdminDashboardModel()
    data = model.get_action_summary_detail(action_choice,action, from_date, to_date, keyword)

    return render_template('Misa/admin/history_detail_modal.html',
                           action=action,
                           data=data)

@admin_bp.route('/admin/brands')
@admin_required
def brands():
    keyword = request.args.get('keyword', '')
    status = request.args.get('status', '')
    sort = request.args.get('sort', 'asc')
    page = request.args.get('page', 1, type=int)  # trang hiện tại
    per_page = 5

    session['brands_filter'] = {
        'keyword': keyword,
        'status': status,
        'sort': sort
    }

    bulk = session.get('bulk_mode_brand')
    bulk_selected = session.get('bulk_selected_brand', [])
    selected_count = len(bulk_selected)
    model = WeblinkModel()
    brands_detail, total_brands = model.get_brands(keyword, status, sort, page, per_page)
    total_pages = (total_brands + per_page - 1) // per_page

    return render_template(
        'Misa/admin/brands.html',
        brands=brands_detail,
        keyword=keyword,
        status=status,
        sort=sort,
        page=page,
        total_pages=total_pages,
        bulk=bulk,
        selected_count=selected_count
    )

@admin_bp.route('/admin/bulk-mode-brands/multi', methods=['POST'])
@admin_required
def bulk_mode_multi_brands():
    session['bulk_mode_brand'] = 'multi'
    session['bulk_selected_brand'] = []   # reset
    session.modified = True
    return jsonify(ok=True)

@admin_bp.route('/admin/bulk-mode-brands/clear', methods=['POST'])
@admin_required
def bulk_mode_clear_brands():
    session.pop('bulk_mode_brand', None)
    session.pop('bulk_selected_brand', None)
    session.modified = True
    return jsonify(ok=True)

@admin_bp.route('/admin/bulk-mode-brands/all', methods=['POST'])
@admin_required
def bulk_mode_all_brands():
    model = WeblinkModel()
    ids = model.get_all_brand_ids(
        keyword=request.args.get('keyword', ''),
        status=request.args.get('status', '')
    )
    session['bulk_mode_brand'] = 'all'
    session['bulk_selected_brand'] = ids
    session.modified = True
    return jsonify(ok=True)

@admin_bp.route('/admin/bulk-select-brands', methods=['POST'])
@admin_required
def bulk_select_brands():
    data = request.json
    checked = data['checked']
    bid = int(data['brand_id'])
    selected = session.get('bulk_selected_brand', [])

    if checked and bid not in selected:
        selected.append(bid)
    if not checked and bid in selected:
        selected.remove(bid)
    if session['bulk_mode_brand'] != 'multi':
        session['bulk_mode_brand'] = 'multi'
    session['bulk_selected_brand'] = selected
    session.modified = True

    return jsonify(ok=True, count=len(selected))

@admin_bp.route('/admin/create-brand', methods=['GET', 'POST'])
@admin_required
def create_brand():
    if request.method == 'POST':
        logo_path_db = ""
        name = request.form["name"]
        color = request.form["color"]
        logo_file = request.files["logo"]
        model = WeblinkModel()
        if logo_file:
            logo_path_db = model.create_folder_save_pic(name,logo_file)

        model.add_brands(name, logo_path_db, color)

        flash('Tạo hãng thành công!', 'success')
        return redirect(url_for('admin.brands'))
    return render_template('Misa/admin/brand_add.html')

@admin_bp.route('/brands/delete-multiple', methods=['POST'])
@admin_required
def delete_brands():
    model = WeblinkModel()
    bulk = session.get('bulk_mode_brand')
    bulk_selected = session.get('bulk_selected_brand', [])
    filters = session.get('brands_filter', {})
    keyword = filters.get('keyword', '')
    status = filters.get('status', '')

    if bulk == 'all':
        deleted_count = model.delete_all_brands(
            keyword=keyword,
            status=status
        )
        session.pop('bulk_mode_brand', None)
        session.pop('bulk_selected_brand', None)

        flash(f'🔥 Đã xoá {deleted_count} role.', 'success')
        return redirect(url_for('admin.brands'))

    if not bulk_selected:
        flash('⚠️ Bạn chưa chọn hãng nào để xóa.', 'warning')
        return redirect(url_for('admin.brands'))

    deleted_count = 0
    for rid in bulk_selected:
        rid_int = int(rid)
        if model.delete_brand(rid_int):
            deleted_count += 1
    session.pop('bulk_mode_brand', None)
    session.pop('bulk_selected_brand', None)

    flash(f'✅ Đã xóa {deleted_count} Hãng thành công.', 'success')
    return redirect(url_for('admin.brands'))

@admin_bp.route('/admin/brands/delete/<int:id>', methods=['POST', 'GET'])
@admin_required
def delete_brand(id):
    model = WeblinkModel()
    if model.delete_brand(id):
        flash('✅ Xoá Hãng thành công', 'success')
    else:
        flash('⚠️ Hãng không tồn tại hoặc đã bị xoá', 'warning')
    return redirect(url_for('admin.brands'))

@admin_bp.route('/admin/brands/edit/<int:id>', methods=['GET', 'POST'])
@admin_required
def edit_brand(id):
    model = WeblinkModel()
    brand = model.get_brand_by_id(id)
    if not brand:
        flash('Hãng không tồn tại !!!', 'error')
        return redirect(url_for('admin.brands'))
    if request.method == 'POST':
        name = request.form.get("name")
        color = request.form.get("color")
        logo_file = request.files.get("logo")
        status = request.form.get("status")

        logo_path_db = brand[2]
        if logo_file and logo_file.filename:
            logo_path_db = model.create_folder_save_pic(name, logo_file)

        model.update_brand(
            id=id,
            name=name,
            color=color,
            logo=logo_path_db,
            status = status
        )

        flash('Sửa Hãng thành công!', 'success')
        return redirect(url_for('admin.brands'))
    return render_template('Misa/admin/brands_edit.html',brand=brand)


@admin_bp.route('/admin/links')
@admin_required
def links():
    models = WeblinkModel()
    all_brand = models.get_all_brand()
    keyword = request.args.get('keyword', '')
    status = request.args.get('status', '')
    sort = request.args.get('sort', 'asc')
    brand = request.args.get('brand', '')
    page = request.args.get('page', 1, type=int)  # trang hiện tại
    per_page = 5

    session['links_filter'] = {
        'keyword': keyword,
        'status': status,
        'sort': sort,
        'brand': brand
    }

    bulk = session.get('bulk_mode_link')
    bulk_selected = session.get('bulk_selected_link', [])
    selected_count = len(bulk_selected)
    model = WeblinkModel()
    links_detail, total_brands = model.get_links(brand,keyword, status, sort, page, per_page)
    total_pages = (total_brands + per_page - 1) // per_page

    return render_template(
        'Misa/admin/links.html',
        all_brand=all_brand,
        brand_select=brand,
        links=links_detail,
        keyword=keyword,
        status=status,
        sort=sort,
        page=page,
        total_pages=total_pages,
        bulk=bulk,
        selected_count=selected_count
    )

@admin_bp.route('/admin/bulk-mode-links/multi', methods=['POST'])
@admin_required
def bulk_mode_multi_links():
    session['bulk_mode_link'] = 'multi'
    session['bulk_selected_link'] = []   # reset
    session.modified = True
    return jsonify(ok=True)

@admin_bp.route('/admin/bulk-mode-links/clear', methods=['POST'])
@admin_required
def bulk_mode_clear_links():
    session.pop('bulk_mode_link', None)
    session.pop('bulk_selected_link', None)
    session.modified = True
    return jsonify(ok=True)

@admin_bp.route('/admin/bulk-mode-links/all', methods=['POST'])
@admin_required
def bulk_mode_all_links():
    model = WeblinkModel()
    ids = model.get_all_link_ids(
        brand=request.args.get('brand', ''),
        keyword=request.args.get('keyword', ''),
        status=request.args.get('status', '')
    )
    session['bulk_mode_link'] = 'all'
    session['bulk_selected_link'] = ids
    session.modified = True
    return jsonify(ok=True)

@admin_bp.route('/admin/bulk-select-links', methods=['POST'])
@admin_required
def bulk_select_links():
    data = request.json
    checked = data['checked']
    bid = int(data['link_id'])
    selected = session.get('bulk_selected_link', [])

    if checked and bid not in selected:
        selected.append(bid)
    if not checked and bid in selected:
        selected.remove(bid)
    if session['bulk_mode_link'] != 'multi':
        session['bulk_mode_link'] = 'multi'
    session['bulk_selected_link'] = selected
    session.modified = True

    return jsonify(ok=True, count=len(selected))

@admin_bp.route('/admin/create-link', methods=['GET', 'POST'])
@admin_required
def create_link():
    models = WeblinkModel()
    brand_list = models.get_all_brand()
    if request.method == 'POST':
        modal = request.form.get('modal') == '1'
        if modal:
            names = request.form.getlist('names[]')
            urls = request.form.getlist('urls[]')
            brand_id = request.form.get('brand_id')
            if not brand_id:
                return jsonify({
                    'success': False,
                    'message': 'Hãng không tồn tại hoặc đã bị xoá'})
            brand_id = int(brand_id)
            for name, url in zip(names, urls):
                if name.strip() and url.strip():
                    models.add_links(name, url, brand_id)
            return jsonify({'success': True,
                            'message': 'Tạo Link thành công!'})
        else:
            name = request.form["name"]
            url = request.form["Url"]
            brand = request.form["brand"]
            if not brand:
                flash("Vui lòng chọn hãng", "error")
                return redirect(url_for('admin.create_link'))
            models.add_links(name, url, brand)
            flash('Tạo link thành công!', 'success')
            return redirect(url_for('admin.links'))
    return render_template('Misa/admin/link_add.html', brand_list=brand_list)

@admin_bp.route('/links/delete-multiple', methods=['POST'])
@admin_required
def delete_links():
    model = WeblinkModel()
    bulk = session.get('bulk_mode_link')
    bulk_selected = session.get('bulk_selected_link', [])
    filters = session.get('links_filter', {})
    keyword = filters.get('keyword', '')
    status = filters.get('status', '')
    brand = filters.get('brand', '')
    if bulk == 'all':
        deleted_count = model.delete_all_links(
            keyword=keyword,
            status=status,
            brand=brand
        )
        session.pop('bulk_mode_link', None)
        session.pop('bulk_selected_link', None)

        flash(f'🔥 Đã xoá {deleted_count} link.', 'success')
        return redirect(url_for('admin.links'))

    if not bulk_selected:
        flash('⚠️ Bạn chưa chọn link nào để xóa.', 'warning')
        return redirect(url_for('admin.links'))

    deleted_count = 0
    for rid in bulk_selected:
        rid_int = int(rid)
        if model.delete_link(rid_int):
            deleted_count += 1
    session.pop('bulk_mode_link', None)
    session.pop('bulk_selected_link', None)

    flash(f'✅ Đã xóa {deleted_count} Link thành công.', 'success')
    return redirect(url_for('admin.links'))

@admin_bp.route('/admin/links/delete/<int:id>', methods=['POST', 'GET'])
@admin_required
def delete_link(id):
    model = WeblinkModel()
    if model.delete_link(id):
        flash('✅ Xoá Link thành công', 'success')
    else:
        flash('⚠️ Link không tồn tại hoặc đã bị xoá', 'warning')
    return redirect(url_for('admin.links'))

@admin_bp.route('/admin/links/edit/<int:id_link>/<int:id_brand>', methods=['GET', 'POST'])
@admin_required
def edit_link(id_link, id_brand):
    model = WeblinkModel()
    link = model.get_link_by_id(id_link, id_brand)
    all_brand = model.get_all_brand()
    if not link:
        flash('Link không tồn tại !!!', 'error')
        return redirect(url_for('admin.links'))
    if request.method == 'POST':
        name = request.form.get("name")
        url = request.form.get("Url")
        brand = request.form.get("brand")
        status = request.form.get("status")
        print(f"name: {name} - url: {url} - brand: {brand} - status: {status}")
        model.update_link(
            id=id_link,
            name=name,
            url=url,
            status = status,
            brand=brand
        )

        flash('Sửa Link thành công!', 'success')
        return redirect(url_for('admin.links'))
    return render_template('Misa/admin/links_edit.html',link=link, all_brand=all_brand)