CREATE OR REPLACE FUNCTION update_last_purchase()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE parts
    SET last_id_purchase = NEW.purchase_id
    WHERE part_id = NEW.part_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_update_last_purchase
AFTER INSERT ON purchases
FOR EACH ROW
EXECUTE FUNCTION update_last_purchase();
