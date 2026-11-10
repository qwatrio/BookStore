import time

text = 'Загрузка'
point = '.'
while True:
    for i in range(0,4,1):
        print(f'\r{text} {point * i}', end='', flush=True)
        time.sleep(0.333)
