INSERT INTO users (username, hashed_password, role)
VALUES
    ('admin', '$2b$12$WA4C8g5qCgLipQxpFmHshOAzEkwvt6Ku6VYSFJIv0WSL78gmJtt2G', 'admin'),
    ('dpt', '$2b$12$TyHx7WZwgEUQ/4VkfadXVOoAdrxi8j5f94DLQmrfbPDd2vRnkY2SS', 'dispatcher');

INSERT INTO vehicles (number_plate, type, capacity, status)
VALUES
	('A123BC77', 'Фура', 20000, 'Доступен'),
	('A654BC52', 'Фура', 23500, 'Доступен'),
	('E232PC78', 'Пикап', 950, 'Доступен'),
	('X432CO123', 'Фургон', 4500, 'Доступен'),
	('H017MT177', 'Фургон', 3000, 'Доступен'),
	('A321BC77', 'Фура', 24000, 'Доступен'),
	('A604BC52', 'Фура', 23500, 'Доступен'),
	('E872PC78', 'Пикап', 950, 'Доступен'),
	('X109CO123', 'Фургон', 2500, 'Доступен'),
	('H876MT177', 'Фургон', 5000, 'Доступен');
