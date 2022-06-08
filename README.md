# Ms Launcher
## Плагин должен реализовывать следующий функционал:
- В `BombSquad -> Настройки -> Дополнительно` должна быть кнопка "**ms launcher settings**"
- В `BombSquad -> Мультиплеер -> Сервера`, около поля для поиска серверов по их названию должен быть чекбокс (по умолчанию включен). При включенном чекбоксе BombSquad должен получать список серверов не от мастер сервера Эрика, а от нашего сервера `https://servers.ms-bombsquad.com/`. Формат данных нашего сервера от сервера Эрика ничем отличаться не будет, все тот же список серверов с их параметрами.
- По нажатию на "ms launcher settings" должно открываться окно с идентичным названием. В нем должны быть указаны: версия плагина, дата последнего его обновление и текущий язык.
- В `BombSquad -> Мультиплеер -> Сервера` по нажатию на сервер должна быть отключена очередь, т.е. сразу же заход на сервер (Так же как это происходить во вкладке "Избранное")
- Автообновление (из публичного репозитория на `github.com`)
- Локализация под русский и английский языки. Текущий язык плагин должен получать от BombSquad'а.

## Требования:
- Работоспособный плагин, активирующийся в BombSquad. Должен корректно работать на BombSquad 1.7.2
- Без использования сторонних библиотек (обговаривается с нами)
- Использование python 3.10
- Чистый и красивый код
- Успешное прохождение CI
