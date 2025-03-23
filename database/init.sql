CREATE TABLE transactions (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    amount DECIMAL(15,2) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE OR REPLACE FUNCTION notify_transaction()
RETURNS TRIGGER AS $$
DECLARE
    payload JSONB;
BEGIN
    IF TG_OP = 'UPDATE' THEN
        payload := jsonb_build_object(
            'operation', TG_OP,
            'id', NEW.id,
            'user_id', NEW.user_id,
            'new_amount', NEW.amount,
            'old_amount', OLD.amount,
            'new_status', NEW.status,
            'old_status', OLD.status,
            'timestamp', CURRENT_TIMESTAMP
        );
    ELSE
        payload := jsonb_build_object(
            'operation', TG_OP,
            'id', COALESCE(NEW.id, OLD.id),
            'user_id', COALESCE(NEW.user_id, OLD.user_id),
            'amount', COALESCE(NEW.amount, OLD.amount),
            'status', COALESCE(NEW.status, OLD.status),
            'timestamp', CURRENT_TIMESTAMP
        );
    END IF;

    PERFORM pg_notify('transaction_alert', payload::text);
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER transaction_trigger
AFTER INSERT OR UPDATE OR DELETE ON transactions
FOR EACH ROW EXECUTE FUNCTION notify_transaction();
