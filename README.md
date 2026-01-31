# النظام المحاسبي - Accounting System

نظام محاسبي خفيف يعمل محلياً على Windows باستخدام Django و PostgreSQL.

## المميزات

- ✅ واجهة عربية بالكامل (RTL)
- ✅ إدارة الأطراف (العملاء والموردين)
- ✅ إدارة الفواتير (بيع وشراء)
- ✅ تسجيل الدفعات
- ✅ دفتر الأستاذ الآلي
- ✅ تقارير الأرصدة والملخصات
- ✅ لوحة إدارة Django

## المتطلبات

- Python 3.12
- PostgreSQL (localhost:5432)
- pgAdmin (للإدارة)

## خطوات الإعداد

### 1. إنشاء قاعدة البيانات

افتح psql أو pgAdmin ونفذ:

```sql
CREATE DATABASE accounting_db;
```

### 2. إنشاء البيئة الافتراضية

```powershell
cd "c:\Users\Haitham\Desktop\AI projects\مشروع محاسبي خفيف"
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. تثبيت المتطلبات

```powershell
pip install -r requirements.txt
```

### 4. إعداد ملف البيئة

```powershell
Copy-Item .env.example .env
```

ثم عدّل ملف `.env` وأدخل بيانات قاعدة البيانات:

```
DB_NAME=accounting_db
DB_USER=postgres
DB_PASSWORD=your_actual_password
DB_HOST=localhost
DB_PORT=5432
SECRET_KEY=your-secret-key-change-this
DEBUG=True
```

### 5. تشغيل الهجرات

```powershell
python manage.py makemigrations parties invoices payments ledger
python manage.py migrate
```

### 6. إنشاء مستخدم مدير

```powershell
python manage.py createsuperuser
```

أدخل اسم المستخدم وكلمة المرور والبريد الإلكتروني.

### 7. تشغيل الخادم

```powershell
python manage.py runserver
```

افتح المتصفح على: http://localhost:8000

## الروابط

| الصفحة | الرابط |
|--------|--------|
| الصفحة الرئيسية | http://localhost:8000/ |
| الأطراف | http://localhost:8000/parties/ |
| الفواتير | http://localhost:8000/invoices/ |
| ملخص الفترة | http://localhost:8000/reports/summary/ |
| لوحة الإدارة | http://localhost:8000/admin/ |
| فحص الصحة | http://localhost:8000/health |

## هيكل المشروع

```
مشروع محاسبي خفيف/
├── core/               # إعدادات Django الرئيسية
├── parties/            # تطبيق الأطراف
├── invoices/           # تطبيق الفواتير
├── payments/           # تطبيق الدفعات
├── ledger/             # تطبيق دفتر الأستاذ
├── reports/            # تطبيق التقارير
├── templates/          # القوالب العامة
├── static/             # الملفات الثابتة
├── requirements.txt    # المتطلبات
├── manage.py          # ملف الإدارة
├── .env.example       # مثال ملف البيئة
└── README.md          # هذا الملف
```

## القواعد المحاسبية

### الفواتير
- فاتورة بيع للعميل = قيد مدين على العميل
- فاتورة شراء من مورد = قيد دائن على المورد

### الدفعات
- دفعة من عميل = قيد دائن (تخفيض الرصيد المدين)
- دفعة لمورد = قيد مدين (تخفيض الرصيد الدائن)

### الرصيد
- الرصيد = مجموع المدين - مجموع الدائن
- رصيد موجب = له علينا
- رصيد سالب = لنا عليه

## فحص الصحة

```powershell
Invoke-RestMethod -Uri http://localhost:8000/health
```

النتيجة المتوقعة:
```json
{
    "status": "ok",
    "database": "connected"
}
```

## الترخيص

جميع الحقوق محفوظة © 2026
