# Установка

- [Windows](#windows)
- [Linux](#linux)

## Windows

- Устанавливаем на устройство Python 3.11 (Другие версии не проверялись, можно выше, но ниже не стоит).
- Скачиваем архив и распаковываем его в удобное место.
- Заходим в папку и открываем PowerShell (Shift + Правая кнопка мыши -> Открыть окно PowerShell здесь).
- Пишем:

 ```powershell
python -m pip install -r requements.txt
 ```

Или

```powershell
pip install -r requements.txt
 ```

Для настройки используется файл main_site/settings.py, настройка режима отладки и ключа шифрования вынесена в переменные окружения, чтобы их изменить, создайте файл в корне каталога '.env', и впишите туда:

```env
DEBUG=True 
SECRET_KEY='=@=qfzxp#+r(i8713(htg)vg!khac%e+9m$nhs*t966^f&ab#m'
```

DEBUG - Режим отладки, включен, чтобы видеть различные предупреждения и чтобы не указывать ALLOWED_HOSTS в settings.py.
SECRET_KEY - Секретный ключ, должен быть уникальный для каждого сервера, для генерации рекомендую использовать [этот генератор](https://djecrety.ir/).

Также необходимо подготовить базу данных, для этого введите:

```powershell
python manage.py makemigrations
python manage.py migrate --run-syncdb
```

После всего, для запуска сервера пишем:

```powershell
python manage.py runserver
```

Сервер будет запущен на адресе <http://127.0.0.1:8000>

## Linux