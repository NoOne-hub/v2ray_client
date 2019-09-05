from app import app, db
from app.models import v2rayConfig


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'v2rayConfig': v2rayConfig}
