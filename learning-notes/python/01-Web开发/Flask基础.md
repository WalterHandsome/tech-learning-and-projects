# Flask基础
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. Flask概述

Flask是一个轻量级的Python Web框架，具有以下特点：
- **轻量级**：核心功能简单，扩展性强
- **灵活性**：可以根据需求选择组件
- **易学易用**：API简洁，文档完善
- **适合小型项目**：快速开发原型和小型应用

## 2. 安装和配置

### 2.1 安装Flask

```bash
pip install flask
```

### 2.2 最小应用

```python
from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return 'Hello, World!'

if __name__ == '__main__':
    app.run(debug=True)
```

## 3. 路由

### 3.1 基本路由

```python
from flask import Flask

app = Flask(__name__)

@app.route('/')
def index():
    return '首页'

@app.route('/about')
def about():
    return '关于页面'

@app.route('/user/<username>')
def show_user(username):
    return f'用户: {username}'

@app.route('/post/<int:post_id>')
def show_post(post_id):
    return f'文章ID: {post_id}'
```

### 3.2 HTTP方法

```python
from flask import Flask, request

app = Flask(__name__)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        return '处理登录'
    return '显示登录表单'
```

### 3.3 URL构建

```python
from flask import Flask, url_for

app = Flask(__name__)

@app.route('/')
def index():
    return url_for('show_user', username='john')

@app.route('/user/<username>')
def show_user(username):
    return f'用户: {username}'
```

## 4. 请求和响应

### 4.1 请求对象

```python
from flask import Flask, request

app = Flask(__name__)

@app.route('/login', methods=['POST'])
def login():
    # 获取表单数据
    username = request.form['username']
    password = request.form['password']
    
    # 获取查询参数
    page = request.args.get('page', 1, type=int)
    
    # 获取JSON数据
    data = request.get_json()
    
    # 获取文件
    file = request.files['file']
    
    return '登录成功'
```

### 4.2 响应对象

```python
from flask import Flask, make_response, jsonify, redirect, url_for

app = Flask(__name__)

@app.route('/')
def index():
    # 返回字符串
    return 'Hello, World!'
    
    # 返回JSON
    return jsonify({'message': 'Hello, World!'})
    
    # 返回自定义响应
    response = make_response('Hello, World!')
    response.headers['Content-Type'] = 'text/plain'
    return response
    
    # 重定向
    return redirect(url_for('login'))
```

## 5. 模板

### 5.1 基本使用

```python
from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html', name='John')
```

### 5.2 Jinja2语法

```html
<!-- index.html -->
<!DOCTYPE html>
<html>
<head>
    <title>{{ title }}</title>
</head>
<body>
    <h1>Hello, {{ name }}!</h1>
    
    {% if user %}
        <p>欢迎, {{ user.username }}!</p>
    {% else %}
        <p>请登录</p>
    {% endif %}
    
    <ul>
        {% for item in items %}
            <li>{{ item }}</li>
        {% endfor %}
    </ul>
</body>
</html>
```

### 5.3 模板继承

```html
<!-- base.html -->
<!DOCTYPE html>
<html>
<head>
    <title>{% block title %}{% endblock %}</title>
</head>
<body>
    {% block content %}{% endblock %}
</body>
</html>

<!-- index.html -->
{% extends "base.html" %}

{% block title %}首页{% endblock %}

{% block content %}
    <h1>欢迎</h1>
{% endblock %}
```

## 6. 静态文件

```python
from flask import Flask, url_for

app = Flask(__name__)

# 在模板中使用
# <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
# <img src="{{ url_for('static', filename='logo.png') }}">
```

## 7. 表单处理

### 7.1 使用Flask-WTF

```bash
pip install flask-wtf
```

```python
from flask import Flask, render_template, request, flash, redirect
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'

class LoginForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired()])
    password = StringField('密码', validators=[DataRequired()])
    submit = SubmitField('登录')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash(f'登录成功, {form.username.data}!')
        return redirect('/')
    return render_template('login.html', form=form)
```

## 8. 数据库集成

### 8.1 使用Flask-SQLAlchemy

```bash
pip install flask-sqlalchemy
```

```python
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    
    def __repr__(self):
        return f'<User {self.username}>'

# 创建表
with app.app_context():
    db.create_all()
```

## 9. 会话管理

### 9.1 Session

```python
from flask import Flask, session, redirect, url_for, request

app = Flask(__name__)
app.secret_key = 'your-secret-key'

@app.route('/login', methods=['POST'])
def login():
    session['username'] = request.form['username']
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

@app.route('/')
def index():
    if 'username' in session:
        return f'已登录: {session["username"]}'
    return '未登录'
```

## 10. 蓝图（Blueprint）

```python
from flask import Blueprint

# 创建蓝图
auth = Blueprint('auth', __name__)

@auth.route('/login')
def login():
    return '登录页面'

@auth.route('/logout')
def logout():
    return '登出'

# 注册蓝图
from flask import Flask
app = Flask(__name__)
app.register_blueprint(auth, url_prefix='/auth')
```

## 11. 错误处理

```python
from flask import Flask, render_template

app = Flask(__name__)

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500
```

## 12. 中间件和钩子

```python
from flask import Flask, g

app = Flask(__name__)

@app.before_request
def before_request():
    g.user = get_current_user()

@app.after_request
def after_request(response):
    # 处理响应
    return response

@app.teardown_request
def teardown_request(exception):
    # 清理资源
    pass
```

## 13. RESTful API

```python
from flask import Flask, jsonify, request
from flask.views import MethodView

app = Flask(__name__)

class UserAPI(MethodView):
    def get(self, user_id):
        if user_id is None:
            return jsonify({'users': []})
        return jsonify({'user': {'id': user_id}})
    
    def post(self):
        data = request.get_json()
        return jsonify({'user': data}), 201
    
    def put(self, user_id):
        data = request.get_json()
        return jsonify({'user': {'id': user_id, **data}})
    
    def delete(self, user_id):
        return '', 204

# 注册视图
user_view = UserAPI.as_view('user_api')
app.add_url_rule('/users/', defaults={'user_id': None},
                 view_func=user_view, methods=['GET'])
app.add_url_rule('/users/', view_func=user_view, methods=['POST'])
app.add_url_rule('/users/<int:user_id>', view_func=user_view,
                 methods=['GET', 'PUT', 'DELETE'])
```

## 14. 部署

### 14.1 使用Gunicorn

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

### 14.2 使用uWSGI

```bash
pip install uwsgi
uwsgi --http :8000 --wsgi-file app.py --callable app
```

## 15. 常用扩展

- **Flask-WTF**：表单处理
- **Flask-SQLAlchemy**：数据库ORM
- **Flask-Login**：用户认证
- **Flask-Mail**：邮件发送
- **Flask-Migrate**：数据库迁移
- **Flask-RESTful**：RESTful API

## 16. 最佳实践

1. **项目结构**：合理组织项目目录
2. **配置管理**：使用配置文件管理不同环境
3. **错误处理**：完善的错误处理机制
4. **安全性**：防止SQL注入、XSS等安全问题
5. **测试**：编写单元测试和集成测试

## 17. 总结

Flask是一个轻量级、灵活的Web框架，适合快速开发小型应用和API。通过扩展可以构建功能完整的Web应用。

