from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.engine import Engine


def ensure_blockchain_log_audit(engine: Engine) -> None:
    """
    Creates an audit table + trigger to capture any UPDATEs to `blockchain_log`.

    This is what enables the dashboard to show "what changed from -> to" with timestamps
    even if the change was done directly in Supabase Table Editor (outside the app).
    """
    ddl = """
    -- 1) History table
    CREATE TABLE IF NOT EXISTS blockchain_log_audit (
      audit_id       BIGSERIAL PRIMARY KEY,
      block_index    INTEGER NOT NULL,
      changed_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
      operation      TEXT NOT NULL,
      old_row        JSONB,
      new_row        JSONB
    );

    CREATE INDEX IF NOT EXISTS idx_blockchain_log_audit_block_index_changed_at
      ON blockchain_log_audit (block_index, changed_at DESC);

    -- 2) Trigger function
    CREATE OR REPLACE FUNCTION trg_blockchain_log_audit_fn()
    RETURNS trigger AS $$
    BEGIN
      IF TG_OP = 'UPDATE' THEN
        INSERT INTO blockchain_log_audit (block_index, operation, old_row, new_row)
        VALUES (NEW.block_index, TG_OP, to_jsonb(OLD), to_jsonb(NEW));
        RETURN NEW;
      END IF;
      RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;

    -- 3) Trigger (idempotent)
    DO $$
    BEGIN
      IF NOT EXISTS (
        SELECT 1
        FROM pg_trigger
        WHERE tgname = 'trg_blockchain_log_audit'
      ) THEN
        CREATE TRIGGER trg_blockchain_log_audit
        AFTER UPDATE ON blockchain_log
        FOR EACH ROW
        EXECUTE FUNCTION trg_blockchain_log_audit_fn();
      END IF;
    END;
    $$;
    """
    with engine.begin() as conn:
        conn.execute(text(ddl))
