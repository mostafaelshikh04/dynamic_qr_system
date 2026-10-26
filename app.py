import sqlite3
from flask import Flask, request, redirect, render_template_string

app = Flask(__name__)
DB_FILE = "dynamic_qr.db"

def init_db():
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS qr_codes (
                id TEXT PRIMARY KEY,
                target_url TEXT DEFAULT NULL,
                is_active INTEGER DEFAULT 0
            )
        ''')
    print("قاعدة البيانات جاهزة للعمل.")

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>تفعيل منتجك الذكي</title>
    <style>
        body { font-family: sans-serif; background-color: #f4f6f9; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
        .card { background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); width: 90%; max-width: 400px; text-align: center; }
        h2 { color: #333; margin-bottom: 10px; }
        p { color: #666; font-size: 14px; margin-bottom: 25px; }
        input[type="url"] { width: 100%; padding: 12px; border: 2px solid #ddd; border-radius: 6px; box-sizing: border-box; font-size: 16px; margin-bottom: 20px; transition: 0.3s; }
        input[type="url"]:focus { border-color: #007bff; outline: none; }
        button { background-color: #007bff; color: white; border: none; padding: 12px 25px; font-size: 16px; border-radius: 6px; cursor: pointer; width: 100%; font-weight: bold; }
        button:hover { background-color: #0056b3; }
        .success { color: green; font-weight: bold; }
    </style>
</head>
<body>
    <div class="card">
        {% if success %}
            <h2 class="success">🎉 تم التفعيل بنجاح!</h2>
            <p>سيتم توجيهك إلى رابطك الآن...</p>
            <script>setTimeout(function(){ window.location.href = "{{ target_url }}"; }, 2000);</script>
        {% else %}
            <h2>ربط الـ QR Code بالمنتج</h2>
            <p>هذا الرمز غير مفعّل بعد. يرجى إدخال الرابط (URL) الذي تريد توجيه عملائك إليه مستقبلاً:</p>
            <form method="POST">
                <input type="url" name="target_url" placeholder="https://example.com" required>
                <button type="submit">تفعيل وحفظ الرابط</button>
            </form>
        {% endif %}
    </div>
</body>
</html>
"""

@app.route('/qr/<qr_id>', methods=['GET', 'POST'])
def handle_qr(qr_id):
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT target_url, is_active FROM qr_codes WHERE id = ?", (qr_id,))
        row = cursor.fetchone()
        
        if not row:
            return "عذراً، هذا الرمز غير صالح أو لم يتم إنشاؤه عبر النظام.", 404
            
        target_url, is_active = row
        
        if is_active == 1 and target_url:
            return redirect(target_url)
            
        if request.method == 'POST':
            user_url = request.form.get('target_url')
            if not user_url.startswith(('http://', 'https://')):
                user_url = 'https://' + user_url
                
            cursor.execute("UPDATE qr_codes SET target_url = ?, is_active = 1 WHERE id = ?", (user_url, qr_id))
            conn.commit()
            return render_template_string(HTML_TEMPLATE, success=True, target_url=user_url)
            
        return render_template_string(HTML_TEMPLATE, success=False)

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)
