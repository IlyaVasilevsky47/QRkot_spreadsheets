# QRKot

[![CI](https://github.com/IlyaVasilevsky47/service_home_bookkeeping/actions/workflows/main.yml/badge.svg?branch=main)](https://github.com/IlyaVasilevsky47/service_home_bookkeeping/actions/workflows/main.yml)

Приложение QRKot — это API для Благотворительного фонда поддержки котиков.

Фонд собирает пожертвования на различные проекты, включая медицинское обслуживание, обустройство колоний в подвалах, корм для кошек, оставшихся без опеки, и любые другие цели, связанные с поддержанием популяции кошек.

## Основные возможности:
- В Фонде могут быть запущены несколько проектов, каждый из которых имеет название, описание и сумму сбора. Когда сумма собрана, проект закрывается.
- Пользователи могут делать пожертвования на любую сумму, добавляя при желании комментарий. Пожертвования идут в общий фонд и распределяются по проектам до сбора полной суммы. Если пожертвовано больше, чем требуется, остаток сохраняется для следующего проекта. Новые средства автоматически инвестируются в новый проект при его запуске.
- Администраторы сайта создают проекты и управляют ими. Пользователи видят полный список проектов и их статус. Зарегистрированные пользователи также могут отправлять пожертвования и отслеживать свои предыдущие взносы.

## Дополнительная возможность:
- Возможность создавать отчеты о скорости закрытия проектов в Google Таблицах.

## Запуск проекта:
1. Клонируем проект.
```bash
    git clone git@github.com:IlyaVasilevsky47/cat_charity_fund.git
```

2. Создаем и активируем виртуальное окружение.
```bash
    python -m venv venv
    source venv/scripts/activate
```

3. Обновляем менеджер пакетов pip и устанавливаем зависимости из файла requirements.txt.
```bash
    python -m pip install --upgrade pip
    pip install -r requirements.txt
```

APP_TITLE=QRKot
DATABASE_URL=sqlite+aiosqlite:///./cat-foundation.db

4. Создаем базу данных. 
```bash
    alembic upgrade head
```

5. Запускаем проект.
```bash
    uvicorn app.main:app --reload
```

## Автор:
- Василевский И.А.
- [GitHub](https://github.com/IlyaVasilevsky47)
- [Почта](vasilevskijila047@gmail.com)
- [Вконтакте](https://vk.com/ilya.vasilevskiy47)

## Технический стек
- Python 3.9.0
- sqlalchemy 1.4.36
- FastAPI 0.78.0
- FastAPI-Users 10.0.4
- Uvicorn 0.17.6
- aiosqlite 0.17.0
- Aiogoogle 5.5.0
- google-auth 2.23.2
