CREATE TABLE transactions (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    amount DECIMAL(15,2) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE OR REPLACE FUNCTION notify_transaction()
RETURNS TRIGGER AS $$
BEGIN
    PERFORM pg_notify('transaction_alert', json_build_object(
        'operation', TG_OP,
        'id', COALESCE(NEW.id, OLD.id),
        'user_id', COALESCE(NEW.user_id, OLD.user_id),
        'amount', CASE WHEN TG_OP = 'UPDATE' THEN json_build_object('old', OLD.amount, 'new', NEW.amount) ELSE COALESCE(NEW.amount, OLD.amount) END,
        'status', CASE WHEN TG_OP = 'UPDATE' THEN json_build_object('old', OLD.status, 'new', NEW.status) ELSE COALESCE(NEW.status, OLD.status) END,
        'timestamp', CURRENT_TIMESTAMP
    )::text);
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER transaction_trigger
AFTER INSERT OR UPDATE OR DELETE ON transactions
FOR EACH ROW EXECUTE FUNCTION notify_transaction();
