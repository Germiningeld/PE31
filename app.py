# app.py
from flask import Flask, render_template, request, jsonify, send_file
import os
from logo_generator import generate_logo
import time

app = Flask(__name__)

os.makedirs('static/logos', exist_ok=True)

# Хранилище статусов операций
operations = {}


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/generate', methods=['POST'])
def generate():
    try:
        data = request.get_json()
        style = data.get('style', '')
        description = data.get('description', '')

        if not style or not description:
            return jsonify({'error': 'Необходимо указать стиль и описание'}), 400

        # Генерируем уникальное имя файла и operation_id
        operation_id = os.urandom(8).hex()
        filename = f"logo_{operation_id}.jpeg"
        filepath = os.path.join('static/logos', filename)

        # Запускаем генерацию и сохраняем статус
        operations[operation_id] = {
            'status': 'processing',
            'filename': filename,
            'filepath': filepath,
            'start_time': time.time(),
            'style': style,
            'description': description
        }

        # Запускаем генерацию в фоновом режиме
        # В реальном приложении здесь лучше использовать Celery или другой механизм фоновых задач
        def generate_in_background():
            try:
                success = generate_logo(style, description, filepath)
                if success:
                    operations[operation_id]['status'] = 'completed'
                else:
                    operations[operation_id]['status'] = 'error'
                    operations[operation_id]['error'] = 'Ошибка при генерации логотипа'
            except Exception as e:
                operations[operation_id]['status'] = 'error'
                operations[operation_id]['error'] = str(e)

        import threading
        thread = threading.Thread(target=generate_in_background)
        thread.start()

        return jsonify({
            'status': 'processing',
            'operation_id': operation_id
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/check_status/<operation_id>')
def check_status(operation_id):
    try:
        if operation_id not in operations:
            return jsonify({'status': 'error', 'error': 'Операция не найдена'})

        operation = operations[operation_id]

        if operation['status'] == 'completed':
            return jsonify({
                'status': 'completed',
                'image_url': f'/static/logos/{operation["filename"]}',
                'filename': operation["filename"]
            })
        elif operation['status'] == 'error':
            return jsonify({
                'status': 'error',
                'error': operation.get('error', 'Неизвестная ошибка')
            })
        else:
            # Проверяем тайм-аут (например, 30 секунд)
            if time.time() - operation['start_time'] > 30:
                operation['status'] = 'error'
                operation['error'] = 'Превышено время ожидания'
                return jsonify({
                    'status': 'error',
                    'error': 'Превышено время ожидания'
                })
            return jsonify({'status': 'processing'})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/download/<filename>')
def download(filename):
    try:
        return send_file(f'static/logos/{filename}', as_attachment=True)
    except Exception as e:
        return jsonify({'error': str(e)}), 404


if __name__ == '__main__':
    app.run(debug=True)