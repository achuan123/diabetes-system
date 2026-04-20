import os

from app import create_app

os.environ.setdefault('MEDICAL_ENCRYPTION_KEY', 'BhwDGcyDHdoH0VwXP53dBB_QrmrvF-Gu2bCE1LfhRNM=')
app = create_app()

if __name__ == '__main__':
    debug = os.getenv('FLASK_DEBUG', '').lower() in {'1', 'true', 'yes'}
    app.run(host='0.0.0.0', port=5000, debug=debug)
