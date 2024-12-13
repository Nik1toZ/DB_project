CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    hashed_password VARCHAR(255) NOT NULL,
    role VARCHAR(20) CHECK (role IN ('client', 'dispatcher', 'admin')),
    created_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE companies (
    company_id SERIAL PRIMARY KEY,
    company_name VARCHAR(255) NOT NULL UNIQUE,
    created_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE company_users (
    company_user_id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    company_id INT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (company_id) REFERENCES companies(company_id) ON DELETE CASCADE
);


CREATE TABLE orders (
    order_id SERIAL PRIMARY KEY,
    order_name VARCHAR(255) NOT NULL,
    status VARCHAR(20) CHECK (status IN ('Новый', 'В пути', 'Доставлен')),
    created_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE company_orders (
    company_order_id SERIAL PRIMARY KEY,
    company_id INT NOT NULL,
    order_id INT NOT NULL,
    FOREIGN KEY (company_id) REFERENCES companies(company_id) ON DELETE CASCADE,
    FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE
);

CREATE TABLE vehicles (
    vehicle_id SERIAL PRIMARY KEY,
    number_plate VARCHAR(50) NOT NULL UNIQUE,
    type VARCHAR(20) CHECK (type IN ('Фура', 'Фургон', 'Пикап')),
    capacity INT,
    status VARCHAR(20) CHECK (status IN ('Доступен', 'Не доступен'))
);

CREATE TABLE routes (
    route_id SERIAL PRIMARY KEY,
    start_point VARCHAR(255) NOT NULL,
    end_point VARCHAR(255) NOT NULL
);

CREATE TABLE order_details (
    ord_det_id SERIAL PRIMARY KEY,
    order_id INT NOT NULL,
    vehicle_id INT,
    route_id INT NOT NULL,
    weight FLOAT,
    FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE,
    FOREIGN KEY (vehicle_id) REFERENCES vehicles(vehicle_id) ON DELETE CASCADE,
    FOREIGN KEY (route_id) REFERENCES routes(route_id) ON DELETE CASCADE
);

CREATE TABLE logs (
    log_id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    action VARCHAR(255) NOT NULL,
    time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- Функция триггера
CREATE OR REPLACE FUNCTION update_order_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_time = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Триггер для обновления updated_time перед обновлением строки
CREATE TRIGGER update_orders_timestamp
BEFORE UPDATE ON orders
FOR EACH ROW
EXECUTE FUNCTION update_order_timestamp();

CREATE OR REPLACE FUNCTION log_user_action()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO logs (user_id, action, time)
    VALUES (NEW.user_id, TG_ARGV[0], CURRENT_TIMESTAMP);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Создание пользователя
CREATE OR REPLACE FUNCTION log_user_creation()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO logs (user_id, action, time)
    VALUES (NEW.user_id, 'Создан пользователь: ' || NEW.username, CURRENT_TIMESTAMP);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER user_creation_trigger
AFTER INSERT ON users
FOR EACH ROW
EXECUTE FUNCTION log_user_creation();

-- Создание заказа Новый
CREATE OR REPLACE FUNCTION log_new_order()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO logs (user_id, action, time)
    VALUES (current_setting('session.user_id')::INT, 'Создан заказ: ' || NEW.order_name, CURRENT_TIMESTAMP);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER new_order_trigger
AFTER INSERT ON orders
FOR EACH ROW
WHEN (NEW.status = 'Новый')
EXECUTE FUNCTION log_new_order();


-- Назначение заказа В пути
CREATE OR REPLACE FUNCTION log_order_in_transit()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO logs (user_id, action, time)
    VALUES (current_setting('session.user_id')::INT, 'Заказ: ' || NEW.order_name || ' назначен', CURRENT_TIMESTAMP);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER order_in_transit_trigger
AFTER UPDATE ON orders
FOR EACH ROW
WHEN (OLD.status = 'Новый' AND NEW.status = 'В пути')
EXECUTE FUNCTION log_order_in_transit();


-- Завершение заказа Доставлен
CREATE OR REPLACE FUNCTION log_order_delivered()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO logs (user_id, action, time)
    VALUES (current_setting('session.user_id')::INT, 'Заказ: ' || NEW.order_name || ' доставлен', CURRENT_TIMESTAMP);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER order_delivered_trigger
AFTER UPDATE ON orders
FOR EACH ROW
WHEN (OLD.status = 'В пути' AND NEW.status = 'Доставлен')
EXECUTE FUNCTION log_order_delivered();


-- Отмена заказа (удаление)
CREATE OR REPLACE FUNCTION log_order_cancellation()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO logs (user_id, action, time)
    VALUES (current_setting('session.user_id')::INT, 'Заказ: ' || OLD.order_name || ' отменен', CURRENT_TIMESTAMP);
    RETURN OLD;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER order_cancellation_trigger
AFTER DELETE ON orders
FOR EACH ROW
EXECUTE FUNCTION log_order_cancellation();


-- Создание транспорта
CREATE OR REPLACE FUNCTION log_vehicle_creation()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO logs (user_id, action, time)
    VALUES (current_setting('session.user_id')::INT, 'Создан транспорт: ' || NEW.number_plate, CURRENT_TIMESTAMP);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER vehicle_creation_trigger
AFTER INSERT ON vehicles
FOR EACH ROW
EXECUTE FUNCTION log_vehicle_creation();


-- Удаление компании
CREATE OR REPLACE FUNCTION log_company_deletion()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO logs (user_id, action, time)
    VALUES (current_setting('session.user_id')::INT, 'Удалена компания: ' || OLD.company_name, CURRENT_TIMESTAMP);
    RETURN OLD;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER company_deletion_trigger
AFTER DELETE ON companies
FOR EACH ROW
EXECUTE FUNCTION log_company_deletion();


-- Удаление пользователя
CREATE OR REPLACE FUNCTION log_user_deletion()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO logs (user_id, action, time)
    VALUES (current_setting('session.user_id')::INT, 'Удален пользователь: ' || OLD.username, CURRENT_TIMESTAMP);
    RETURN OLD;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER user_deletion_trigger
AFTER DELETE ON users
FOR EACH ROW
EXECUTE FUNCTION log_user_deletion();


-- Удаление транспорта
CREATE OR REPLACE FUNCTION log_vehicle_deletion()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO logs (user_id, action, time)
    VALUES (current_setting('session.user_id')::INT, 'Удален транспорт: ' || OLD.number_plate, CURRENT_TIMESTAMP);
    RETURN OLD;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER vehicle_deletion_trigger
AFTER DELETE ON vehicles
FOR EACH ROW
EXECUTE FUNCTION log_vehicle_deletion();