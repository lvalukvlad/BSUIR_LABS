from app import create_app

if __name__ == '__main__':
    print("Запуск приложения...")
    try:
        app = create_app()
        print("Приложение создано успешно.")
        print("Список маршрутов:")
        for rule in app.url_map.iter_rules():
            print(f" - {rule.rule} -> {rule.endpoint}")
    except Exception as e:
        print(f"Ошибка при создании приложения: {e}")
        import traceback
        traceback.print_exc()

    app.run(debug=True)