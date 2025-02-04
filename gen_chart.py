import os
import datetime

def read_csv(csv_file):
    if not os.path.exists(csv_file):
        raise FileNotFoundError(f"Plik {csv_file} nie istnieje. Upewnij się, że ścieżka jest poprawna.")
    
    data = []
    with open(csv_file, "r") as file:
        for line in file:
            parts = line.strip().split(",")
            if len(parts) == 2:
                date, trainings = parts
                try:
                    data.append((datetime.datetime.strptime(date, "%Y-%m-%d"), int(trainings)))
                except ValueError:
                    pass
    return data

def linear_regression(dates, trainings):
    try:
        import numpy as np
        x = np.array([(d - min(dates)).days for d in dates])
        y = np.array(trainings)
        slope, intercept = calulate_linear_regression(x, y)

        extended_dates_numeric = np.append(x, x[-1] + np.arange(1, 11))
        extended_dates = [min(dates) + datetime.timedelta(days=int(d)) for d in extended_dates_numeric]
        regression_line = slope * extended_dates_numeric + intercept
        end_of_year = slope * 365 + intercept
        return regression_line, extended_dates, end_of_year
    except ImportError:
            raise RuntimeError("Biblioteka matplotlib nie jest dostępna. Zainstaluj ją za pomocą 'python3 -m  pip install numpy'.")

def calulate_linear_regression(x, y):
    n = len(x)
    sum_x = sum(x)
    sum_y = sum(y)
    sum_xx = sum(x_i ** 2 for x_i in x)
    sum_xy = sum(x_i * y_i for x_i, y_i in zip(x, y))
    
    # Współczynniki prostej regresji
    slope = (n * sum_xy - sum_x * sum_y) / (n * sum_xx - sum_x ** 2)
    intercept = (sum_y - slope * sum_x) / n
    return slope, intercept


def generate_training_plot(data, output_file):
    dates, trainings = zip(*data)
    
    # Tworzenie wykresu
    try:
        import matplotlib.pyplot as plt
        import matplotlib.dates as mdates

        # Obliczenie regresji liniowej
        regression_line, extended_dates, end_of_year = linear_regression(dates, trainings)

        plt.figure(figsize=(12, 6))
        plt.plot(dates, trainings, marker='o', linestyle='-', color='b', alpha=0.7, label="Liczba treningów")
        plt.plot(extended_dates, regression_line, linestyle='--', color='r', label="Regresja liniowa")

        # Formatowanie wykresu
        plt.title("Estymowana ilość treningów na koniec 2025 roku: " + "%.0f" % end_of_year)
        plt.xlabel("Data")
        plt.ylabel("Liczba treningów")
        plt.grid(True, linestyle='--', alpha=0.5)
        plt.gca().xaxis.set_major_locator(mdates.AutoDateLocator())
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
        plt.xticks(rotation=45)
        plt.legend()
        
        # Zapis wykresu do pliku PNG
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()
    except ImportError:
        raise RuntimeError("Biblioteka matplotlib nie jest dostępna. Zainstaluj ją za pomocą 'python3 -m  pip install matplotlib'.")

# Przykład użycia
if __name__ == "__main__":
    input_csv = "2k25.csv"  # Plik wejściowy
    output_png = "training_plot.png"  # Plik wyjściowy
    
    try:
        data = read_csv(input_csv)
        generate_training_plot(data, output_png)
    except (FileNotFoundError, RuntimeError) as e:
        print(e)
