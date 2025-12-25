from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models.User_model import UserModel

auth_bp = Blueprint('auth', __name__)
@auth_bp.route('/')
def index():
    # CHƯA đăng nhập → login
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    # ĐÃ đăng nhập
    role = session.get('role')

    if role == 'admin':
        return redirect(url_for('admin.dashboard'))
    else:
        return redirect(url_for('user.home'))

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        role = session.get('role')
        return redirect(
            url_for('admin.dashboard') if role == 'admin'
            else url_for('user.home')
        )
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = UserModel.authenticate(username, password)
        if user and user.onl:
            flash("❗Tài khoản đang đăng nhập trên thiết bị khác!", 'error')
            return redirect(url_for('auth.login'))
        if not user:
            flash('❌ Sai tên đăng nhập hoặc mật khẩu', 'error')
            return redirect(url_for('auth.login'))
        else:
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role
            UserModel.update_online(user.id, True)
            flash(f'✅ Đăng nhập thành công, mừng quay trở lại {user.username}', 'success')
            if user.role == 'admin':
                return redirect(url_for('admin.dashboard'))
            else:
                return redirect(url_for('user.home'))
    return render_template('auth/login.html', error=error)

@auth_bp.route('/logout')
def logout():
    user_id = session.get('user_id')
    if user_id:
        UserModel.update_online(user_id, False)
    session.clear()
    return redirect(url_for('auth.login'))

@auth_bp.route('/change-password', methods=['GET', 'POST'])
def change_password():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        old_password = request.form.get('old_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')

        user = UserModel.get_by_id(session['user_id'])

        # 1️⃣ Mật khẩu cũ đúng không?
        if user.passwordHash != UserModel.hash_password(old_password):
            flash('❌ Mật khẩu cũ không đúng', 'error')
            return redirect(url_for('auth.change_password'))

        # 2️⃣ Mật khẩu mới trùng mật khẩu cũ?
        if user.passwordHash == UserModel.hash_password(new_password):
            flash('❌ Mật khẩu mới không được trùng mật khẩu cũ', 'error')
            return redirect(url_for('auth.change_password'))

        # 3️⃣ Nhập lại mật khẩu có trùng không?
        if new_password != confirm_password:
            flash('❌ Mật khẩu nhập lại không khớp', 'error')
            return redirect(url_for('auth.change_password'))

        # 4️⃣ Update password
        new_hash = UserModel.hash_password(new_password)
        UserModel.update_password(user.Id, new_hash)

        flash('✅ Đổi mật khẩu thành công', 'success')
        if user.Role == 'admin':
            return redirect(url_for('admin.dashboard'))
        else:
            return redirect(url_for('user.home'))

    return render_template('auth/change_password.html')

@auth_bp.route('/set_offline', methods=['POST'])
def set_offline():
    user_id = session.get('user_id')
    if user_id:
        UserModel.update_online(user_id, False)
    return '', 204