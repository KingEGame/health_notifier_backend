# 🔄 Руководство по миграции - Обновление полей пациентов

## Обзор изменений

Модель `Patient` была обновлена для поддержки более детальных медицинских данных в соответствии с CSV файлом `synthetic_pregnant_patients_1000.csv`.

### Новые поля

| Поле | Тип | Описание |
|------|-----|----------|
| `pregnancy_icd10` | VARCHAR(20) | ICD-10 код беременности |
| `pregnancy_description` | TEXT | Описание состояния беременности |
| `comorbidity_icd10` | VARCHAR(20) | ICD-10 код сопутствующих заболеваний |
| `comorbidity_description` | TEXT | Описание сопутствующих заболеваний |
| `weeks_pregnant` | INT | Недели беременности (1-42) |
| `address` | TEXT | Адрес пациента |

### Удаленные поля

| Поле | Замена |
|------|--------|
| `geo_location` | `address` |
| `conditions_icd10` | `pregnancy_icd10` + `comorbidity_icd10` |
| `trimester` | Автоматически рассчитывается из `weeks_pregnant` |

## Миграция существующих данных

### 1. Автоматическая миграция схемы

```bash
# Запустите скрипт миграции
python migrate_patient_schema.py
```

Этот скрипт:
- Добавит новые колонки в таблицу `patients`
- Создаст необходимые индексы
- Сохранит существующие данные

### 2. Ручная миграция данных

Если у вас есть существующие данные, которые нужно перенести:

```python
# Пример скрипта для переноса данных
from app import create_app, db
from app.models.patient import Patient

app = create_app()
with app.app_context():
    patients = Patient.query.all()
    
    for patient in patients:
        # Переносим geo_location в address
        if hasattr(patient, 'geo_location') and patient.geo_location:
            patient.address = patient.geo_location
        
        # Переносим conditions_icd10
        if hasattr(patient, 'conditions_icd10') and patient.conditions_icd10:
            conditions = patient.get_conditions()
            if conditions:
                patient.pregnancy_icd10 = conditions[0] if len(conditions) > 0 else None
                patient.comorbidity_icd10 = conditions[1] if len(conditions) > 1 else None
        
        # Рассчитываем weeks_pregnant из trimester
        if hasattr(patient, 'trimester') and patient.trimester:
            if patient.trimester == 1:
                patient.weeks_pregnant = 8  # Среднее значение для 1 триместра
            elif patient.trimester == 2:
                patient.weeks_pregnant = 18  # Среднее значение для 2 триместра
            elif patient.trimester == 3:
                patient.weeks_pregnant = 32  # Среднее значение для 3 триместра
    
    db.session.commit()
```

## Импорт новых данных

### 1. Импорт из CSV файла

```bash
# Импорт 1000 пациентов из CSV
python import_patients.py

# Или с указанием файла
python import_patients.py synthetic_pregnant_patients_1000.csv
```

### 2. Создание новых пациентов через API

```bash
# Новый формат
curl -X POST http://localhost:5000/api/patients \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Анна Петрова",
    "age": 28,
    "pregnancy_icd10": "O24.4",
    "pregnancy_description": "Gestational diabetes mellitus",
    "comorbidity_icd10": "I10",
    "comorbidity_description": "Essential hypertension",
    "weeks_pregnant": 20,
    "address": "123 Main St, Moscow",
    "zip_code": "101000"
  }'
```

## Обратная совместимость

Система поддерживает старые поля для обратной совместимости:

### API Endpoints

- `conditions_icd10` - автоматически преобразуется в `pregnancy_icd10` + `comorbidity_icd10`
- `trimester` - автоматически рассчитывается из `weeks_pregnant`

### Примеры

```bash
# Старый формат (все еще работает)
curl -X POST http://localhost:5000/api/patients \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Елена Смирнова",
    "age": 32,
    "zip_code": "190000",
    "conditions_icd10": ["O13", "I10"],
    "trimester": 3
  }'
```

## Тестирование

### 1. Тест новых полей

```bash
python test_new_patient_fields.py
```

### 2. Тест обратной совместимости

```bash
python test_simple.py
```

## Обновление кода

### 1. Модель Patient

```python
# Новые методы
patient.get_trimester()  # Рассчитывает триместр из weeks_pregnant
patient.get_conditions()  # Возвращает массив всех ICD-10 кодов
```

### 2. API Responses

```json
{
  "id": 1,
  "name": "Анна Петрова",
  "age": 28,
  "pregnancy_icd10": "O24.4",
  "pregnancy_description": "Gestational diabetes mellitus",
  "comorbidity_icd10": "I10",
  "comorbidity_description": "Essential hypertension",
  "weeks_pregnant": 20,
  "address": "123 Main St, Moscow",
  "zip_code": "101000",
  "trimester": 2,  // Автоматически рассчитывается
  "conditions_icd10": ["O24.4", "I10"]  // Для обратной совместимости
}
```

## Проверка миграции

### 1. Проверка схемы базы данных

```sql
DESCRIBE patients;
```

### 2. Проверка данных

```python
from app import create_app, db
from app.models.patient import Patient

app = create_app()
with app.app_context():
    patients = Patient.query.limit(5).all()
    for patient in patients:
        print(f"Patient: {patient.name}")
        print(f"  Pregnancy: {patient.pregnancy_icd10} - {patient.pregnancy_description}")
        print(f"  Comorbidity: {patient.comorbidity_icd10} - {patient.comorbidity_description}")
        print(f"  Weeks: {patient.weeks_pregnant}, Trimester: {patient.get_trimester()}")
        print()
```

## Откат изменений

Если нужно откатить изменения:

```sql
-- Удалить новые колонки
ALTER TABLE patients DROP COLUMN pregnancy_icd10;
ALTER TABLE patients DROP COLUMN pregnancy_description;
ALTER TABLE patients DROP COLUMN comorbidity_icd10;
ALTER TABLE patients DROP COLUMN comorbidity_description;
ALTER TABLE patients DROP COLUMN weeks_pregnant;
ALTER TABLE patients DROP COLUMN address;

-- Восстановить старые колонки
ALTER TABLE patients ADD COLUMN geo_location VARCHAR(100);
ALTER TABLE patients ADD COLUMN conditions_icd10 TEXT;
ALTER TABLE patients ADD COLUMN trimester INT;
```

## Поддержка

Если у вас возникли проблемы с миграцией:

1. Проверьте логи приложения
2. Убедитесь, что база данных доступна
3. Проверьте права доступа к базе данных
4. Создайте issue в репозитории проекта

---

**Важно**: Сделайте резервную копию базы данных перед миграцией!
