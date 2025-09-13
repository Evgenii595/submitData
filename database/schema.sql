-- Улучшенная схема базы данных для ФСТР
-- Добавлено поле status для модерации и улучшена структура

-- Создание последовательностей
CREATE SEQUENCE IF NOT EXISTS pereval_id_seq;
CREATE SEQUENCE IF NOT EXISTS pereval_areas_id_seq;
CREATE SEQUENCE IF NOT EXISTS pereval_images_id_seq;
CREATE SEQUENCE IF NOT EXISTS pereval_users_id_seq;
CREATE SEQUENCE IF NOT EXISTS activities_types_id_seq;

-- Создание ENUM для статуса модерации
CREATE TYPE pereval_status AS ENUM ('new', 'pending', 'accepted', 'rejected');

-- Таблица пользователей (нормализация данных пользователя)
CREATE TABLE "public"."pereval_users" (
    "id" int4 NOT NULL DEFAULT nextval('pereval_users_id_seq'::regclass),
    "email" varchar(255) NOT NULL UNIQUE,
    "phone" varchar(20) NOT NULL,
    "fam" varchar(100) NOT NULL,
    "name" varchar(100) NOT NULL,
    "otc" varchar(100),
    "created_at" timestamp DEFAULT now(),
    PRIMARY KEY ("id")
);

-- Таблица перевалов (основная таблица)
CREATE TABLE "public"."pereval_added" (
    "id" int4 NOT NULL DEFAULT nextval('pereval_id_seq'::regclass),
    "date_added" timestamp DEFAULT now(),
    "beauty_title" varchar(255),
    "title" varchar(255) NOT NULL,
    "other_titles" varchar(255),
    "connect" text,
    "add_time" timestamp,
    "user_id" int4 NOT NULL,
    "latitude" decimal(10, 7) NOT NULL,
    "longitude" decimal(10, 7) NOT NULL,
    "height" int4 NOT NULL,
    "level_winter" varchar(10),
    "level_summer" varchar(10),
    "level_autumn" varchar(10),
    "level_spring" varchar(10),
    "status" pereval_status DEFAULT 'new',
    "raw_data" json, -- оставляем для совместимости
    "images" json,   -- оставляем для совместимости
    PRIMARY KEY ("id"),
    FOREIGN KEY ("user_id") REFERENCES "public"."pereval_users"("id") ON DELETE CASCADE
);

-- Таблица изображений (улучшенная структура)
CREATE TABLE "public"."pereval_images" (
    "id" int4 NOT NULL DEFAULT nextval('pereval_images_id_seq'::regclass),
    "pereval_id" int4 NOT NULL,
    "date_added" timestamp DEFAULT now(),
    "img" bytea NOT NULL,
    "title" varchar(255),
    "img_path" varchar(500), -- путь к файлу изображения
    PRIMARY KEY ("id"),
    FOREIGN KEY ("pereval_id") REFERENCES "public"."pereval_added"("id") ON DELETE CASCADE
);

-- Таблица географических областей (без изменений)
CREATE TABLE "public"."pereval_areas" (
    "id" int8 NOT NULL DEFAULT nextval('pereval_areas_id_seq'::regclass),
    "id_parent" int8 NOT NULL,
    "title" text,
    PRIMARY KEY ("id")
);

-- Таблица типов активности (без изменений)
CREATE TABLE "public"."spr_activities_types" (
    "id" int4 NOT NULL DEFAULT nextval('activities_types_id_seq'::regclass),
    "title" text,
    PRIMARY KEY ("id")
);

-- Создание индексов для улучшения производительности
CREATE INDEX idx_pereval_added_status ON "public"."pereval_added"("status");
CREATE INDEX idx_pereval_added_user_id ON "public"."pereval_added"("user_id");
CREATE INDEX idx_pereval_added_date_added ON "public"."pereval_added"("date_added");
CREATE INDEX idx_pereval_images_pereval_id ON "public"."pereval_images"("pereval_id");
CREATE INDEX idx_pereval_users_email ON "public"."pereval_users"("email");

-- Вставка тестовых данных
INSERT INTO "public"."pereval_areas" ("id", "id_parent", "title") VALUES
(0, 0, 'Планета Земля'),
(1, 0, 'Памиро-Алай'),
(65, 0, 'Алтай'),
(66, 65, 'Северо-Чуйский хребет'),
(88, 65, 'Южно-Чуйский хребет'),
(92, 65, 'Катунский хребет'),
(105, 1, 'Фанские горы'),
(106, 1, 'Гиссарский хребет (участок западнее перевала Анзоб)'),
(131, 1, 'Матчинский горный узел'),
(133, 1, 'Горный узел Такали, Туркестанский хребет'),
(137, 1, 'Высокий Алай'),
(147, 1, 'Кичик-Алай и Восточный Алай'),
(367, 375, 'Аладаглар'),
(375, 0, 'Тавр'),
(384, 0, 'Саяны'),
(386, 65, 'Хребет Листвяга'),
(387, 65, 'Ивановский хребет'),
(388, 65, 'Массив Мунгун-Тайга'),
(389, 65, 'Хребет Цаган-Шибэту'),
(390, 65, 'Хребет Чихачева (Сайлюгем)'),
(391, 65, 'Шапшальский хребет'),
(392, 65, 'Хребет Южный Алтай'),
(393, 65, 'Хребет Монгольский Алтай'),
(398, 384, 'Западный Саян'),
(399, 384, 'Восточный Саян'),
(402, 384, 'Кузнецкий Алатау'),
(459, 65, 'Курайский хребет');
