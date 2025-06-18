from __future__ import annotations

import os
from flask import Blueprint, request
from slack_bolt import App
from slack_bolt.adapter.flask import SlackRequestHandler
from sqlalchemy import text

from backend.utils.session import SessionLocal
from backend.db.models import channel_subs, recalls

bot_token = os.getenv("SLACK_BOT_TOKEN")
signing = os.getenv("SLACK_SIGNING_SECRET")
slack_app = App(token=bot_token, signing_secret=signing) if bot_token and signing else None
handler = SlackRequestHandler(slack_app) if slack_app else None

bp = Blueprint("slackbot", __name__)

@bp.route("/slack/events", methods=["POST"])
def slack_events():
    if handler:
        return handler.handle(request)
    return "", 404

if slack_app:

    @slack_app.command("/recallhero")
    def recallhero_cmd(ack, respond, command):
        ack()
        text_arg = command.get("text", "").strip()
        channel_id = command.get("channel_id")
        if not text_arg:
            respond("Try `/recallhero <query>` or `/recallhero subscribe stroller`")
            return
        tokens = text_arg.split()
        action = tokens[0].lower()
        with SessionLocal() as db:
            if action == "subscribe":
                source = "CPSC"
                if len(tokens) >= 3:
                    source = tokens[1].upper()
                    query = " ".join(tokens[2:])
                else:
                    query = " ".join(tokens[1:])
                res = db.execute(
                    channel_subs.insert().values(
                        platform="slack", channel_id=channel_id, query=query, source=source
                    )
                )
                db.commit()
                respond(f"Subscribed `{query}` ({source}) id={res.lastrowid}")
            elif action == "list":
                rows = db.execute(
                    channel_subs.select().where(
                        channel_subs.c.platform == "slack",
                        channel_subs.c.channel_id == channel_id,
                    )
                ).fetchall()
                if not rows:
                    respond("No subscriptions")
                else:
                    msg = "Current subscriptions:\n" + "\n".join(
                        f"{r._mapping['id']}: {r._mapping['source']} {r._mapping['query']}" for r in rows
                    )
                    respond(msg)
            elif action == "unsubscribe" and len(tokens) >= 2:
                sid = int(tokens[1])
                db.execute(
                    channel_subs.delete().where(
                        channel_subs.c.id == sid,
                        channel_subs.c.channel_id == channel_id,
                    )
                )
                db.commit()
                respond(f"Unsubscribed {sid}")
            else:
                query = text_arg
                rows = db.execute(
                    text(
                        "SELECT product, recall_date, source FROM recalls WHERE lower(product) LIKE '%' || lower(:q) || '%' ORDER BY recall_date DESC LIMIT 5"
                    ),
                    {"q": query},
                ).fetchall()
                if not rows:
                    respond(f"No recalls found for {query}")
                else:
                    msg = "\n".join(
                        f"{r._mapping['source']}: {r._mapping['product']} ({r._mapping['recall_date']})" for r in rows
                    )
                    respond(msg)
