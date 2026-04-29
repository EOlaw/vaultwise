from sqlalchemy import inspect, text
from sqlalchemy.engine import Engine


def ensure_sqlite_development_schema(engine: Engine) -> None:
    if engine.url.get_backend_name() != "sqlite":
        return
    with engine.begin() as connection:
        inspector = inspect(connection)
        if "accounts" not in inspector.get_table_names():
            return
        account_columns = {column["name"] for column in inspector.get_columns("accounts")}
        if "organization_id" not in account_columns:
            connection.execute(text("ALTER TABLE accounts ADD COLUMN organization_id INTEGER"))
        if "account_holds" in inspector.get_table_names():
            hold_columns = {column["name"] for column in inspector.get_columns("account_holds")}
            if "card_authorization_id" not in hold_columns:
                connection.execute(text("ALTER TABLE account_holds ADD COLUMN card_authorization_id INTEGER"))
        if "cards" in inspector.get_table_names():
            card_columns = {column["name"] for column in inspector.get_columns("cards")}
            if "card_token_hash" not in card_columns:
                connection.execute(text("ALTER TABLE cards ADD COLUMN card_token_hash VARCHAR(128)"))
                connection.execute(text("UPDATE cards SET card_token_hash = 'legacy-' || id || '-' || last4 WHERE card_token_hash IS NULL"))
        if "card_controls" in inspector.get_table_names():
            control_columns = {column["name"] for column in inspector.get_columns("card_controls")}
            if "allow_card_present" not in control_columns:
                connection.execute(text("ALTER TABLE card_controls ADD COLUMN allow_card_present BOOLEAN DEFAULT 1 NOT NULL"))
            if "allow_contactless" not in control_columns:
                connection.execute(text("ALTER TABLE card_controls ADD COLUMN allow_contactless BOOLEAN DEFAULT 1 NOT NULL"))
            if "require_pin" not in control_columns:
                connection.execute(text("ALTER TABLE card_controls ADD COLUMN require_pin BOOLEAN DEFAULT 0 NOT NULL"))
            if "max_transaction_amount" not in control_columns:
                connection.execute(text("ALTER TABLE card_controls ADD COLUMN max_transaction_amount NUMERIC(14, 2)"))
        if "card_authorizations" in inspector.get_table_names():
            authorization_columns = {column["name"] for column in inspector.get_columns("card_authorizations")}
            if "channel" not in authorization_columns:
                connection.execute(text("ALTER TABLE card_authorizations ADD COLUMN channel VARCHAR(12) DEFAULT 'online' NOT NULL"))
        if "user_sessions" in inspector.get_table_names():
            session_columns = {column["name"] for column in inspector.get_columns("user_sessions")}
            if "device_fingerprint_hash" not in session_columns:
                connection.execute(text("ALTER TABLE user_sessions ADD COLUMN device_fingerprint_hash VARCHAR(128)"))
            if "trusted_device" not in session_columns:
                connection.execute(text("ALTER TABLE user_sessions ADD COLUMN trusted_device BOOLEAN DEFAULT 0 NOT NULL"))
            if "mfa_authenticated_at" not in session_columns:
                connection.execute(text("ALTER TABLE user_sessions ADD COLUMN mfa_authenticated_at DATETIME"))
            if "step_up_expires_at" not in session_columns:
                connection.execute(text("ALTER TABLE user_sessions ADD COLUMN step_up_expires_at DATETIME"))
