from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models.Misa.User_model import UserModel
from Controllers.extensions import limiter

auth_bp = Blueprint('auth', __name__)
@auth_bp.route('/')
def index():
    # CHƯA đăng nhập → login
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    # ĐÃ đăng nhập
    role = session.get('role')

    if role.strip().lower() == 'admin':
        return redirect(url_for('admin.dashboard'))
    else:
        return redirect(url_for('user.home'))

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        role = session.get('role')
        return redirect(
            url_for('admin.dashboard') if role.strip().lower() == 'admin'
            else url_for('user.home')
        )
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        remember = request.form.get('remember')
        user = UserModel.authenticate(username, password)
        if not username or not password:
            flash("❌ Vui lòng nhập đầy đủ tài khoản và mật khẩu", "error")
            return redirect(url_for('auth.login'))
        if user and int(user.status) == 0:
            flash("🚫 Tài khoản của bạn đã bị khóa!", 'error')
            return redirect(url_for('auth.login'))
        if user and int(user.roleStatus) == 0:
            flash("🚫 Quyền hạn của bạn đã bị khóa!", 'error')
            return redirect(url_for('auth.login'))
        if not user:
            flash('❌ Sai tên đăng nhập hoặc mật khẩu', 'error')
            return redirect(url_for('auth.login'))
        else:
            session.clear()
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role
            session['roleID'] = user.roleID
            if remember:
                session.permanent = True
            else:
                session.permanent = False
            UserModel.update_online(user.id, True)
            flash(f'✅ Đăng nhập thành công, mừng quay trở lại {user.username}', 'success')
            if user.role.strip().lower() == 'admin':
                return redirect(url_for('admin.dashboard'))
            else:
                return redirect(url_for('user.home'))
    return render_template('Misa/auth/login.html', error=error)

@auth_bp.route('/logout')
def logout():
    user_id = session.get('user_id')
    if user_id:
        UserModel.update_online(user_id, False)
    session.clear()
    return redirect(url_for('auth.login'))

@auth_bp.route('/change-password', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
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

    return render_template('Misa/auth/change_password.html')

@auth_bp.route('/set_offline', methods=['POST'])
def set_offline():
    user_id = session.get('user_id')
    if user_id:
        UserModel.update_online(user_id, False)
    return '', 204