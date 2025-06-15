
"""Run the RecallGuard development server."""
from backend.api.app import create_app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)

"""Example entry point for RecallGuard."""
from backend.api.recalls import fetch_cpsc
from backend.api.alerts import check_user_items, generate_summary, send_email_alert


def main():
    recalls = fetch_cpsc.fetch()
    items = ["Widget"]
    matches = check_user_items.check_user_items(items, recalls)
    for match in matches:
        summary = generate_summary.generate_summary({"title": "Recall", "product": match})
        send_email_alert.send_email_alert("user@example.com", summary)


if __name__ == "__main__":
    main()


