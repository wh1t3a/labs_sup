import csv
import random
import statistics
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor
import os

NUM_FILES = 5
ROWS_PER_FILE = 10_000
VALUE_MIN = 0.0
VALUE_MAX = 1000.0
CATEGORIES = ['А', 'Б', 'В', 'Г', 'Д']
FILE_PREFIX = "data_"


def generate_csv(file_id: int):
    filename = f"{FILE_PREFIX}{file_id}.csv"
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Категория', 'Значение'])  # заголовок

        for _ in range(ROWS_PER_FILE):
            category = random.choice(CATEGORIES)
            value = round(random.uniform(VALUE_MIN, VALUE_MAX), 4)
            writer.writerow([category, value])

    print(f"Сгенерирован файл: {filename} ({ROWS_PER_FILE} строк)")


print("Генерация файлов...")
for i in range(1, NUM_FILES + 1):
    generate_csv(i)

def process_single_file(filename: str) -> dict[str, list[float]]:

    local_data = defaultdict(list)

    with open(filename, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader)

        for row in reader:
            if len(row) >= 2:
                category = row[0].strip()
                if category in CATEGORIES:
                    try:
                        value = float(row[1])
                        local_data[category].append(value)
                    except ValueError:
                        continue
    return local_data

def process_all_files():
    filenames = [f"{FILE_PREFIX}{i}.csv" for i in range(1, NUM_FILES + 1)]

    # Собираем все значения по категориям параллельно
    all_data = defaultdict(list)

    with ProcessPoolExecutor() as executor:
        results = executor.map(process_single_file, filenames)

        for partial_data in results:
            for category, values in partial_data.items():
                all_data[category].extend(values)

    print("\n" + "=" * 60)
    print("Результат по категориям (из всех файлов вместе):")
    print("=" * 60)

    category_stats = {}

    for cat in CATEGORIES:
        values = all_data[cat]
        if not values:
            continue

        median_val = statistics.median(values)

        std_val = statistics.stdev(values) if len(values) > 1 else 0.0

        category_stats[cat] = (median_val, std_val)

        print(f"{cat}, {median_val:.6f}, {std_val:.6f}")


    medians = [median for median, _ in category_stats.values()]

    meta_median = statistics.median(medians)
    meta_std = statistics.stdev(medians) if len(medians) > 1 else 0.0

    print("\n" + "=" * 60)
    print("Итоговый результат (медиана из медиан и СКО из медиан):")
    print("=" * 60)
    print(f"А, {meta_median:.6f}, {meta_std:.6f}")

    # Если хотите по всем категориям — можно раскомментировать:
    # for cat in CATEGORIES:
    #     print(f"{cat}, {meta_median:.6f}, {meta_std:.6f}")


if __name__ == "__main__":

    process_all_files()

    # Удаление файлов после работы (по желанию)
    # for i in range(1, NUM_FILES + 1):
    #     os.remove(f"{FILE_PREFIX}{i}.csv")