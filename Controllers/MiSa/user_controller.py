from flask import Blueprint, render_template, flash, redirect, url_for,Response,request,session,jsonify, request, g
from Controllers.decorators import login_required, require_api_key
from Controllers.extensions import limiter
from models.Misa.Report_model import ReportModel
from models.Misa.Favourite_model import FavoriteModel
from models.Misa.User_model import UserModel
from models.Misa.APIKey_model import APIKeyModel
from requests_ntlm import HttpNtlmAuth
from collections import defaultdict
from requests.exceptions import ConnectTimeout, RequestException
import requests
import os

user_bp = Blueprint('user', __name__)

@user_bp.route('/home')
@login_required
def home():
    role_id = session.get('roleID')
    categories = ReportModel.get_category_roles(role_id)
    keyword = request.args.get('keyword', '')
    sort = request.args.get('sort', 'asc')
    category = request.args.get('category_sort', '')
    page = request.args.get('page', 1, type=int)
    per_page = 6
    reports, total_reports = ReportModel.get_reports(keyword,1, sort,category, page, per_page)
    total_report = len(reports)
    total_pages = (total_reports + per_page - 1) // per_page
    print(f'Total reports: {total_pages}, total pages: {total_pages}')
    favorites = FavoriteModel.get_user_favorites(session['user_id'])
    return render_template('Misa/user/home.html',
                           reports=reports,
                           total_reports=total_report,
                           keyword=keyword,
                           sort=sort,
                           cate = category,
                           favorites=favorites,
                           page=page,
                           total_pages=total_pages,
                           categories=categories
                           )

@user_bp.route('/download/prepare/<int:report_id>')
@login_required
def prepare_download(report_id):
    report = ReportModel.get_by_id(report_id)
    if not report:
        return jsonify({
            "error": True,
            "message": "Report không tồn tại"
        }), 404

    if not report["DownloadLink"]:
        return jsonify({
            "error": True,
            "message": "Report chưa được gán link download"
        }), 400

    # Tìm param rỗng
    empty_params = [
        {
            "name": p["name"],
            "label": p["label"],
            "datatype": p["datatype"],
            "allow_null":p["allow_null"],
            "allow_all":p["allow_all"]
        }
        for p in report["Params"]
        if UserModel.is_empty(p["value"])
    ]

    if empty_params:
        return jsonify({
            "need_params": True,
            "report_id": report_id,
            "params": empty_params
        })

    return jsonify({
        "need_params": False,
        "download_url": url_for('user.download_report', report_id=report_id)
    })

@user_bp.route('/download/confirm/<int:report_id>', methods=['POST'])
@login_required
def confirm_download(report_id):
    user_id = session['user_id']
    report = ReportModel.get_by_id(report_id)

    if not report:
        flash('Report không tồn tại', 'error')
        return redirect(url_for('user.home'))

    override_params = {}

    for p in report["Params"]:
        name = p["name"]
        value = request.form.get(f"param_{name}")
        is_null = request.form.get(f"null_{name}")
        is_all = request.form.get(f"all_{name}")

        override_params[name] = {
            "value": value,
            "null": 1 if is_null == "1" else 0,
            "all": 1 if is_all == "1" else 0
        }
    # Build link với param user nhập
    download_url = ReportModel.build_download_link(report, override_params)
    UserModel.log_history(user_id, report_id, 'download')

    auth = HttpNtlmAuth(
        os.getenv('SSRS_USER'),
        os.getenv('SSRS_PASSWORD')
    )

    try:
        r = requests.get(download_url, auth=auth, stream=True, timeout=15)

        # Nếu server trả về lỗi (404, 500...)
        if r.status_code != 200:
            flash("Server báo lỗi khi xuất báo cáo", "error")
            return redirect(url_for('user.home'))

        return Response(
            r.iter_content(8192),
            headers={
                "Content-Disposition": f'attachment; filename="{report["ReportName"]}.xls"',
                "Content-Type": r.headers.get("Content-Type", "application/octet-stream")
            }
        )

    except ConnectTimeout:
        flash("Không kết nối được tới server báo cáo (timeout).", "error")
        return redirect(url_for('user.home'))

    except RequestException as e:
        flash("Lỗi server khi tải báo cáo.", "error")
        return redirect(url_for('user.home'))

@user_bp.route("/api/report/download/<int:report_id>")
@require_api_key
@limiter.limit("30 per minute")
def api_download(report_id):
    api_user_id = g.api_user_id

    # log lịch sử bằng user của API
    UserModel.log_history(api_user_id, report_id, "API")

    # lấy params từ query
    params = {k: v for k, v in request.args.items() if k != "apikey"}

    report = ReportModel.get_by_id(report_id)

    download_url = ReportModel.build_download_link(report, params, "XML")

    auth = HttpNtlmAuth(os.getenv('SSRS_USER'), os.getenv('SSRS_PASSWORD'))

    r = requests.get(download_url, auth=auth, stream=True)
    return Response(
        r.iter_content(8192),
        headers={
            "Content-Disposition": f'attachment; filename="{report['ReportName']}.xml"',
            "Content-Type": r.headers.get("Content-Type", "application/octet-stream")
        }
    )


@user_bp.route('/download/<int:report_id>')
@login_required
def download_report(report_id):
    user_id = session['user_id']
    report = ReportModel.get_by_id(report_id)
    if not report:
        flash('Report không tồn tại !!!', 'error')
        return redirect(url_for('user.home'))
    UserModel.log_history(user_id,report_id,'download')

    file_path = ReportModel.build_download_link(report)   # ví dụ: \\SERVER\Reports\a.pdf
    print(f"File: {file_path}")
    auth = HttpNtlmAuth(
        os.getenv('SSRS_USER'),  # DOMAIN\\user
        os.getenv('SSRS_PASSWORD')
    )

    try:
        r = requests.get(file_path, auth=auth, stream=True, timeout=15)

        if r.status_code != 200:
            flash("Server báo lỗi khi xuất báo cáo", "error")
            return redirect(url_for('user.home'))

        return Response(
            r.iter_content(8192),
            headers={
                "Content-Disposition": f'attachment; filename="{report["ReportName"]}.xls"',
                "Content-Type": r.headers.get("Content-Type", "application/octet-stream")
            }
        )

    except ConnectTimeout:
        flash("Không kết nối được tới server báo cáo (timeout).", "error")
        return redirect(url_for('user.home'))

    except RequestException as e:
        flash("Lỗi server khi tải báo cáo.", "error")
        return redirect(url_for('user.home'))

@user_bp.route('/report/<int:report_id>/view')
@login_required
def view_report(report_id):
    # Lấy thông tin report từ database
    user_id = session['user_id']
    report = ReportModel.get_by_id(report_id)
    if not report:
        flash('Report không tồn tại !!!', 'error')
        return redirect(url_for('user.home'))

    file_url = report["FilePath"]

    if not file_url:
        flash('Link Report không tồn tại !!!', 'error')
        return redirect(url_for('user.home'))
    UserModel.log_history(user_id, report_id, 'view')
    # Trả file về client
    return redirect(file_url)

@user_bp.route('/favorite/<int:report_id>', methods=['POST'])
@login_required
def toggle_favorite(report_id):
    user_id = session['user_id']
    liked = FavoriteModel.toggle(user_id, report_id)

    return jsonify({'liked': liked})

@user_bp.route('/favorites')
@login_required
def favorites():
    user_id = session['user_id']

    categories = ReportModel.get_all_category()
    # Lấy danh sách report đã favorite
    favorite_ids = FavoriteModel.get_user_favorites(user_id)
    keyword = request.args.get('keyword', '')
    sort = request.args.get('sort', 'asc')
    category = request.args.get('category_sort', '')
    reports = ReportModel.get_reports_by_ids(favorite_ids,keyword,sort,category)
    total_report = len(reports)
    return render_template('Misa/user/favorites.html',
                           reports=reports,
                           total_reports=total_report,
                           keyword=keyword,
                           sort=sort,
                           categories= categories,
                           cate=category)

@user_bp.route('/history')
@login_required
def history():
    user_id = session['user_id']
    from_date = request.args.get('from_date')
    to_date = request.args.get('to_date')
    keyword = request.args.get('keyword', '').strip()
    histories = UserModel.download_history(user_id,from_date,to_date,keyword)
    histories_by_date = defaultdict(list)

    for r in histories:
        date_key = r.CreatedAt.strftime('%d/%m/%Y')
        histories_by_date[date_key].append(r)
    return render_template('Misa/user/history.html',
                                            histories_by_date=histories_by_date,
                                            from_date=from_date,
                                            to_date=to_date,
                                            keyword=keyword
                                            )
@user_bp.route("/api_keys")
@login_required
def list_api_keys():
    keyword = request.args.get('keyword', '')
    user_id = session['user_id']
    model = APIKeyModel()
    keys = model.list_API(keyword,user_id)
    return render_template('Misa/user/apikey.html',keys=keys)

@user_bp.route("/api_keys/json")
@login_required
def list_api_keys_json():
    user_id = session['user_id']
    model = APIKeyModel()
    keys = model.list_API('', user_id)

    # chỉ trả dữ liệu cần cho popup
    result = [
        {
            "Id": k.Id,
            "AppName": k.AppName
        } for k in keys
    ]

    return jsonify(result)


@user_bp.route("/api_keys/create", methods=['GET', 'POST'])
@login_required
def create_api_key():
    if request.method == 'POST':
        app_name = request.form['app_name']
        user_id = session['user_id']
        model = APIKeyModel()
        model.create(user_id,app_name)
        flash("Tạo API key thành công", "success")
        return redirect(url_for('user.list_api_keys'))
    return render_template('Misa/user/api_add.html')

@user_bp.route('/api_keys/delete/<int:id>', methods=['POST', 'GET'])
@login_required
def delete_API_route(id):
    model = APIKeyModel()
    if model.delete_API(id):
        flash('✅ Xoá API thành công', 'success')
    else:
        flash('⚠️ API không tồn tại hoặc đã bị xoá', 'warning')
    return redirect(url_for('user.list_api_keys'))

@user_bp.route('/api_keys_report/delete/<int:id>', methods=['POST', 'GET'])
@login_required
def delete_API_report_route(id):
    model = APIKeyModel()
    if model.delete_API_report(id):
        flash('✅ Xoá API report thành công', 'success')
    else:
        flash('⚠️ API report không tồn tại hoặc đã bị xoá', 'warning')
    return redirect(url_for('user.list_api_report'))

@user_bp.route("/flash/copy-success", methods=['POST'])
def flash_copy_success():
    flash("Đã copy API key!", "success")
    return "", 204

@user_bp.route("/user/create-api-link/<int:report_id>")
@login_required
def create_api_link(report_id):
    user_id = session['user_id']

    model = APIKeyModel()
    result = model.create_api_report(report_id=report_id, user_id=user_id)

    if result == "EXISTS":
        flash("⚠️ API report đã được tạo!!!", "warning")
        return redirect(url_for("user.list_api_report"))

    if result is False:
        flash("❌ API key không tồn tại!!!", "danger")
        return redirect(url_for("user.list_api_report"))

    flash("Tạo API report thành công", 'success')
    return redirect(url_for("user.list_api_report"))

@user_bp.route("/api_keys_report")
@login_required
def list_api_report():
    keyword = request.args.get('keyword', '')
    user_id = session['user_id']
    model = APIKeyModel()
    keys = model.list_API_report(keyword,user_id)
    return render_template('Misa/user/apikey_report.html',keys=keys)



