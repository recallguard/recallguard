"""Run the RecallGuard development server."""
from backend.api.app import create_app
from backend.utils.scheduler import init_scheduler


if __name__ == "__main__":
    app = create_app()
    init_scheduler(app)
    app.run(debug=True)
