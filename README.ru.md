<p align="center">
  <img src="react_app/public/icon.png" alt="Sooklib" width="120" />
</p>

# Sooklib — Библиотека и управление книгами

**Языки / Languages**:
[简体中文](README.md) | [繁體中文](README.zh-TW.md) | [English](README.en.md) | [日本語](README.ja.md) | [Русский](README.ru.md) | [한국어](README.ko.md)

Sooklib — библиотеко-ориентированный проект в стиле Emby.  
Онлайн-чтение поддерживает **только TXT**, остальные форматы — только скачивание.

## Позиционирование

- **Библиотека прежде всего**: управление и поиск важнее расширения читалки
- **TXT только онлайн**: стабильность и большие файлы — приоритет
- **Остальные форматы — только скачивание**: EPUB / PDF / комиксы
- **AI**: диалоговый поиск, рекомендации, анализ имен файлов

## Основные возможности

- Сканирование, извлечение метаданных, дедупликация, кэш обложек
- Мульти-пути в библиотеке
- Фоновое сканирование с прогрессом
- Расширенный поиск и фильтры
- RBAC + JWT
- Синхронизация прогресса чтения
- OPDS каталог
- Telegram бот (поиск/скачивание/TXT чтение)
- Авто-бэкапы

## Технологии

Backend:
- FastAPI
- SQLAlchemy 2.x + Alembic
- SQLite / aiosqlite
- APScheduler
- python-telegram-bot
- chardet / ebooklib

Frontend:
- React 18 + TypeScript
- Vite
- MUI
- Zustand
- React Router
- Axios

## Образы и версии

- GHCR: `ghcr.io/sooklib/sooklib`
- DockerHub: `haruka041/sooklib`
- Версия: `v1.2.3`
- Каналы: `beta` / `stable`

## Быстрый старт (Docker)

```bash
mkdir sooklib && cd sooklib
curl -O https://raw.githubusercontent.com/sooklib/sooklib/main/docker-compose.yml
docker-compose up -d
```

## OPDS

OPDS использует HTTP Basic Auth:

- URL: `http://your-server:8080/opds/`
- Логин/пароль: учетная запись Sooklib

## Документация

- Docs: https://github.com/sooklib/sooklib-docs
- Getting started: https://github.com/sooklib/sooklib-docs/blob/main/docs/getting-started.md
- Docker deployment: https://github.com/sooklib/sooklib-docs/blob/main/docs/docker-deployment.md

## Лицензия

MIT License
