# FastAPI Announcement API

Bu proje, duyuru yönetimi ve kullanıcı kimlik doğrulaması sağlayan, sürdürülebilir mimari prensipleriyle geliştirilmiş bir FastAPI backend uygulamasıdır. Temiz hata mesajları, sade Swagger arayüzü ve frontend ile tam entegrasyon hedeflenmiştir.

## 🚀 Kurulum

1. Gerekli bağımlılıkları yükleyin:
   ```bash
   pip install pipenv
   pipenv install
   ```

2. Ortam değişkenlerini `.env` dosyasında tanımlayın:
   ```
   DATABASE_URL=postgresql://<kullanıcı>:<şifre>@localhost:5432/announcement_db
   ADMIN_EMAIL=admin@example.com
   ADMIN_PASSWORD=SuperSecure123
   ```

3. Veritabanı migrasyonlarını uygulayın:
   ```bash
   pipenv run alembic upgrade head
   ```

4. Uygulamayı başlatın:
   ```bash
   uvicorn main:app --reload
   ```

## 📁 Proje Yapısı

- `main.py` : Uygulama giriş noktası, middleware ve router tanımları
- `auth.py` : Kimlik doğrulama ve kullanıcı kayıt/giriş işlemleri
- `users.py` : Kullanıcı profili ve şifre işlemleri
- `announcement_router.py` : Duyuru CRUD ve kullanıcıya özel duyurular
- `sector_router.py` : Sektör listesini dönen endpoint
- `models/` : SQLAlchemy modelleri
- `schemas.py` : Pydantic şemaları (request/response)
- `database.py` : Veritabanı bağlantısı ve session yönetimi
- `exceptions.py` : Global hata yönetimi
- `middlewares/` : Özel middleware’ler
- `alembic/` : Veritabanı migrasyon dosyaları
- `static/` : Statik dosyalar

## 🛡️ Özellikler

- JWT tabanlı kimlik doğrulama
- Kullanıcı ve admin rolleri
- Duyuru ekleme, güncelleme, silme (admin)
- Duyuru listeleme, kaydetme, kayıttan çıkarma (kullanıcı)
- Sektör bazlı duyuru filtreleme
- Hız limitleme (rate limiting)
- Gelişmiş hata mesajları ve validation
- CORS ve güvenlik için özel middleware’ler

## 🧪 Test

API endpointlerini test etmek için [Swagger UI](http://localhost:8000/docs) veya Postman kullanabilirsiniz.



