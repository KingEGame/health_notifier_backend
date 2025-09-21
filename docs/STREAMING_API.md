# Streaming API для пациентов

## Обзор

Streaming API позволяет получать данные о всех пациентах в реальном времени, обрабатывая их пакетами. Это особенно полезно для больших объемов данных, когда нужно начать обработку до завершения загрузки всех данных.

## Endpoints

### `/api/patients/with-risks/stream`

Получает поток данных о всех пациентах с оценками рисков и рекомендациями.

#### Параметры запроса

- `risk_level` (optional): Фильтр по уровню риска (`low`, `medium`, `high`)
- `location` (optional): Фильтр по почтовому индексу
- `batch_size` (optional): Размер пакета (по умолчанию 10)
- `include_ai_suggestions` (optional): Включить AI рекомендации (по умолчанию `true`)
- `include_notifications` (optional): Включить уведомления (по умолчанию `true`)

#### Формат ответа

API возвращает данные в формате NDJSON (newline-delimited JSON), где каждая строка - отдельный JSON объект.

#### Типы сообщений

1. **metadata** - Метаданные о потоке
2. **batch** - Пакет пациентов
3. **summary** - Итоговая сводка
4. **error** - Сообщение об ошибке

## Примеры использования

### Базовый запрос

```bash
curl "http://localhost:5000/api/patients/with-risks/stream"
```

### С фильтрами

```bash
# Только высокорисковые пациенты
curl "http://localhost:5000/api/patients/with-risks/stream?risk_level=high"

# Пациенты из определенного региона
curl "http://localhost:5000/api/patients/with-risks/stream?location=10001"

# Большие пакеты для быстрой обработки
curl "http://localhost:5000/api/patients/with-risks/stream?batch_size=50"
```

### Без AI рекомендаций (быстрее)

```bash
curl "http://localhost:5000/api/patients/with-risks/stream?include_ai_suggestions=false&batch_size=25"
```

## Примеры ответов

### Метаданные

```json
{
  "type": "metadata",
  "total_patients": 1000,
  "batch_size": 10,
  "filters_applied": {
    "risk_level": null,
    "location": null,
    "include_ai_suggestions": true,
    "include_notifications": true
  }
}
```

### Пакет пациентов

```json
{
  "type": "batch",
  "patients": [
    {
      "patient_id": 1,
      "name": "Jane Doe",
      "age": 28,
      "risk_level": "medium",
      "risk_score": 6.5,
      "ai_suggestions": {
        "recommendations": ["Monitor blood sugar levels"]
      }
    }
  ],
  "processed_count": 10,
  "total_patients": 1000
}
```

### Итоговая сводка

```json
{
  "type": "summary",
  "total_processed": 1000,
  "total_available_patients": 1000,
  "risk_distribution": {
    "low": 300,
    "medium": 500,
    "high": 200
  },
  "patients_at_risk": 700,
  "filters_applied": {
    "risk_level": null,
    "location": null,
    "include_ai_suggestions": true,
    "include_notifications": true
  }
}
```

## Клиентский код

### Python пример

```python
import requests
import json

def stream_patients():
    url = "http://localhost:5000/api/patients/with-risks/stream"
    response = requests.get(url, stream=True)
    
    for line in response.iter_lines(decode_unicode=True):
        if line:
            data = json.loads(line)
            
            if data['type'] == 'metadata':
                print(f"Processing {data['total_patients']} patients")
                
            elif data['type'] == 'batch':
                for patient in data['patients']:
                    print(f"Patient {patient['name']}: {patient['risk_level']} risk")
                    
            elif data['type'] == 'summary':
                print(f"Completed: {data['total_processed']} patients")

stream_patients()
```

### JavaScript пример

```javascript
async function streamPatients() {
    const response = await fetch('/api/patients/with-risks/stream');
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    
    while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        
        const chunk = decoder.decode(value);
        const lines = chunk.split('\n');
        
        for (const line of lines) {
            if (line.trim()) {
                const data = JSON.parse(line);
                
                if (data.type === 'metadata') {
                    console.log(`Processing ${data.total_patients} patients`);
                } else if (data.type === 'batch') {
                    data.patients.forEach(patient => {
                        console.log(`Patient ${patient.name}: ${patient.risk_level} risk`);
                    });
                } else if (data.type === 'summary') {
                    console.log(`Completed: ${data.total_processed} patients`);
                }
            }
        }
    }
}

streamPatients();
```

## Преимущества Streaming API

1. **Память**: Не загружает все данные в память одновременно
2. **Время отклика**: Начинает возвращать данные сразу
3. **Прогресс**: Показывает прогресс обработки в реальном времени
4. **Масштабируемость**: Работает с любым количеством пациентов
5. **Гибкость**: Настраиваемый размер пакетов

## Рекомендации

- Используйте `batch_size=10-50` для оптимальной производительности
- Отключите AI рекомендации (`include_ai_suggestions=false`) для максимальной скорости
- Обрабатывайте ошибки в каждом пакете
- Используйте фильтры для уменьшения объема данных
