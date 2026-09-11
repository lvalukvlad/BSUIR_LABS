# Сравнение своей реализации и предоставленного варианта

Прогон 10.09.2026. Дампы: `gcore` + `strings`.

| Аспект | Свой (p1, :5070) | Provided (p2, :5071) |
|--------|------------------|----------------------|
| Секрет в ОЗУ | Fernet ciphertext | plaintext `str` |
| Затирание | `bytearray` + zero-fill | нет |

| Сценарий | PUBLIC | SECRET_BRAVO | SECRET_DELTA |
|----------|--------|--------------|--------------|
| Свой after_create | 1 | 3 | 0 |
| Свой after_update | 2 | 1 | 0 |
| Свой after_delete | 1 | 1 | 0 |
| Provided after_create | 2 | 1 | 0 |
| Provided after_update | 1 | 0 | 2 |
| Provided after_delete | 1 | 0 | 1 |

Чек-лист: свой **14/16**, provided **5/16**.
