from flask import Flask, request, render_template_string
import os

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # Создаём папку, если её нет

# HTML-шаблон страницы загрузки
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Загрузка XML</title>
</head>
<body>
    <h2>Загрузка XML-файла</h2>
    <form action="/upload" method="post" enctype="multipart/form-data">
        <input type="file" name="xml_file" accept=".xml" required>
        <button type="submit">Загрузить</button>
    </form>
    <p>{{ message }}</p>
</body>
</html>
"""

@app.route("/", methods=["GET"])
def index():
    return render_template_string(HTML_TEMPLATE, message="")

@app.route("/upload", methods=["POST"])
def upload_file():
    if "xml_file" not in request.files:
        return render_template_string(HTML_TEMPLATE, message="Файл не выбран!")

    file = request.files["xml_file"]

    if file.filename == "":
        return render_template_string(HTML_TEMPLATE, message="Файл не выбран!")

    if file and file.filename.endswith(".xml"):
        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(file_path)
        return render_template_string(HTML_TEMPLATE, message=f"Файл {file.filename} успешно загружен!")

    return render_template_string(HTML_TEMPLATE, message="Ошибка! Только файлы .xml")

if __name__ == "__main__":
    app.run(debug=True)
