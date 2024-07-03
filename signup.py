from app import app, db
from app.models import Admin, Stdntinfo, Events, stdntevents

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'Admin': Admin}

if __name__ == "__main__":
    db.create_all()
    db.session.commit()
    app.run(debug=True)