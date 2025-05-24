#!/bin/bash

# Встановлення інструментів (якщо потрібно)
pip install --upgrade black isort autoflake autopep8 flake8 pyupgrade

echo "==> Форматування коду black"
black .

echo "==> Сортування імпортів isort"
isort .

echo "==> Видалення невикористаних імпортів autoflake"
autoflake --in-place --remove-all-unused-imports --recursive .

echo "==> Автоматичне виправлення стилю autopep8"
autopep8 --in-place --aggressive --aggressive -r .

echo "==> Оновлення синтаксису pyupgrade"
find . -name "*.py" -exec pyupgrade --py311-plus {} +

echo "==> Аналіз flake8"
flake8 . || echo "flake8: знайдено стилістичні або потенційні помилки"

echo "==> Готово! Перевір результати через git diff або git status."