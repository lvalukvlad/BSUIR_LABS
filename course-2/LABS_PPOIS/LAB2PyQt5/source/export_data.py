def export_to_csv(tournaments, filename):
    """Экспорт в CSV с обработкой ошибок"""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([...])  # Заголовки
            for t in tournaments:
                writer.writerow([...])  # Данные
        return True
    except Exception as e:
        raise ExportError(f"Ошибка экспорта: {str(e)}")