import cv2
import numpy as np


def create_test_images():
    try:
        map_img = np.ones((400, 600, 3), dtype=np.uint8) * 200

        # Рисуем дорожки
        cv2.rectangle(map_img, (0, 180), (600, 220), (150, 150, 150), -1)
        cv2.rectangle(map_img, (280, 0), (320, 400), (150, 150, 150), -1)

        # Рисуем деревья (объекты для поиска)
        trees_positions = [(100, 100), (500, 100), (100, 300), (500, 300), (300, 200)]

        for x, y in trees_positions:
            cv2.circle(map_img, (x, y), 25, (0, 100, 0), -1)
            cv2.rectangle(map_img, (x - 5, y + 25), (x + 5, y + 50), (100, 50, 0), -1)


        cv2.rectangle(map_img, (200, 350), (250, 360), (100, 50, 0), -1)
        cv2.rectangle(map_img, (200, 360), (210, 370), (100, 50, 0), -1)
        cv2.rectangle(map_img, (240, 360), (250, 370), (100, 50, 0), -1)

        # Фонтан
        cv2.circle(map_img, (400, 350), 20, (0, 150, 200), -1)

        cv2.imwrite('map.jpg', map_img)
        print("Создана карта: map.jpg")

        # Создаем шаблон дерева
        template = np.ones((80, 60, 3), dtype=np.uint8) * 200
        cv2.circle(template, (30, 30), 25, (0, 100, 0), -1)
        cv2.rectangle(template, (25, 55), (35, 75), (100, 50, 0), -1)

        cv2.imwrite('template.jpg', template)
        print("Создан шаблон: template.jpg")

        bench = np.ones((40, 60, 3), dtype=np.uint8) * 200
        cv2.rectangle(bench, (5, 15), (55, 20), (100, 50, 0), -1)  # Сиденье
        cv2.rectangle(bench, (10, 20), (15, 35), (100, 50, 0), -1)  # Ножка левая
        cv2.rectangle(bench, (45, 20), (50, 35), (100, 50, 0), -1)  # Ножка правая

        cv2.imwrite('bench.jpg', bench)
        print("Создан объект для замены: bench.jpg")

        return True

    except Exception as e:
        print(f"Ошибка создания изображений: {e}")
        return False


def replace_objects(map_img, template, replacement_obj, threshold=0.7):

    map_gray = cv2.cvtColor(map_img, cv2.COLOR_BGR2GRAY)
    template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)

    h_template, w_template = template_gray.shape
    h_replace, w_replace = replacement_obj.shape[:2]

    result = cv2.matchTemplate(map_gray, template_gray, cv2.TM_CCOEFF_NORMED)

    locations = np.where(result >= threshold)

    modified_map = map_img.copy()
    detection_map = map_img.copy()

    rectangles = []
    for pt in zip(*locations[::-1]):  # Переключаем x и y
        rectangles.append([pt[0], pt[1], w_template, h_template])

    filtered_rectangles = []
    for rect in rectangles:
        x, y, w, h = rect
        overlap = False
        for existing in filtered_rectangles:
            ex, ey, ew, eh = existing
            # Проверяем пересечение
            if (x < ex + ew and x + w > ex and
                    y < ey + eh and y + h > ey):
                overlap = True
                break
        if not overlap:
            filtered_rectangles.append(rect)

    replacement_count = 0
    for (x, y, w, h) in filtered_rectangles:
        cv2.rectangle(modified_map, (x, y), (x + w, y + h), (200, 200, 200), -1)

        center_x = x + w // 2
        center_y = y + h // 2
        new_x = center_x - w_replace // 2
        new_y = center_y - h_replace // 2

        new_x = max(0, min(new_x, modified_map.shape[1] - w_replace))
        new_y = max(0, min(new_y, modified_map.shape[0] - h_replace))

        modified_map[new_y:new_y + h_replace, new_x:new_x + w_replace] = replacement_obj

        cv2.rectangle(detection_map, (x, y), (x + w, y + h), (0, 0, 255), 2)
        cv2.putText(detection_map, f'Tree', (x, y - 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 255), 1)

        replacement_count += 1

    return modified_map, detection_map, replacement_count


def object_replacement_demo():
    create_test_images()

    map_img = cv2.imread('map.jpg')
    template = cv2.imread('template.jpg')
    replacement = cv2.imread('bench.jpg')

    if map_img is None or template is None or replacement is None:
        print("Ошибка загрузки изображений!")
        return

    print("=== ДЕМОНСТРАЦИЯ ЗАМЕНЫ ОБЪЕКТОВ ===")
    print("Ищем: деревья")
    print("Заменяем на: скамейки")

    thresholds = [0.6, 0.7, 0.8]

    for threshold in thresholds:
        print(f"\n--- Порог обнаружения: {threshold} ---")

        modified_map, detection_map, count = replace_objects(
            map_img, template, replacement, threshold
        )

        print(f"Найдено и заменено объектов: {count}")

        cv2.imshow(f'Detection (threshold={threshold})', detection_map)
        cv2.imshow(f'After Replacement (threshold={threshold})', modified_map)

        if threshold == 0.7:
            cv2.imwrite('detection_result.jpg', detection_map)
            cv2.imwrite('replacement_result.jpg', modified_map)
            print("Результаты сохранены в detection_result.jpg и replacement_result.jpg")

    cv2.imshow('Original Map', map_img)
    cv2.imshow('Template (Tree)', template)
    cv2.imshow('Replacement (Bench)', replacement)

    print("\nНажмите любую клавишу для выхода...")
    cv2.waitKey(0)
    cv2.destroyAllWindows()


if __name__ == "__main__":
    object_replacement_demo()