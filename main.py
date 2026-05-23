print("Hello, World!")
# print('\a')

import winsound
import time


# Пример использования
# winsound.Beep(1000, 500)  # Частота 1000 Гц, длительность 500 мс


"""  Ре, Ми, До, До, Со (второй До звучит на октаву ниже).
 Длительность: Мелодия звучит с точным ритмическим рисунком. 
 В музыкальной нотации Джона Уильямса первые три ноты (Ре, Ми, До) 
 равны четвертям (относительно быстрый темп), 
 четвертая нота (До) — восьмая, 
 а завершающий тон (Со) — половинная нота. 
 """


# Частоты нот (Гц)
D4 = 294   # Ре
E4 = 330   # Ми
C4 = 262   # До
G4 = 392   # Со

# Длительности (мс): четвертная, восьмая, половинная
duration_quarter = 300
duration_eighth = 150
duration_half = 600
koeff = 3

# Пауза между нотами (в мс)
# Для четвертных — пауза 100 мс, для восьмой — 50 мс, для половинной — 200 мс
pause_quarter = 100
pause_eighth = 50
pause_half = 200
""" 
winsound.Beep(D4, duration_quarter * koeff)  # Ре
winsound.Beep(E4, duration_quarter * koeff)  # Ми
winsound.Beep(C4, duration_quarter * koeff)  # До
winsound.Beep(C4, duration_eighth * koeff)   # До (быстро)
winsound.Beep(G4, duration_half * koeff)     # Со (долго) """


winsound.Beep(D4, duration_quarter * koeff)
time.sleep(pause_quarter * koeff / 1000)

winsound.Beep(E4, duration_quarter * koeff)
time.sleep(pause_quarter * koeff / 1000)

winsound.Beep(C4, duration_quarter * koeff)
time.sleep(pause_quarter * koeff / 1000)

winsound.Beep(C4, duration_eighth * koeff)
time.sleep(pause_eighth * koeff / 1000)