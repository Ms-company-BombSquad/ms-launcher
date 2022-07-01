# Ms Launcher
Плагин для игры [BombSquad](https://github.com/efroemling/ballistica),
фильтрует список серверов, показывая только проверенные сервера (можно отключить)
и упрощает & ускоряет подключение к ним.

[English](https://github.com/Ms-company-BombSquad/README.md) | [Русский]()

![](https://github.com/Ms-company-BombSquad/ms-launcher/actions/workflows/pylint.yml/badge.svg)
## Дополнительный функционал:
- Автообновление (можно отключить в настройках)
- Локализация под Английский и Русский языки

## FAQ
- Откуда плагин получает список проверенных серверов?
  - В данный момент репозиторий хранит список проверенных `ip` и плагин просто проверяет
    если ли `ip` конкретного сервера в этом списке. Чуть позже мы надеемся реализовать
    получения списка серверов с нашего веб-сервера, а пока будет регулярно обновлять список
    в репозитории.
    > Если Вы являетесь владельцем сервера и хотите чтобы Ваш сервер попал в список — напишите нам
      ivanms.ept@gmail.com
- Зачем нужна фильтрация серверов?
  - В сети появилось множество поддельных копий оригинальных серверов, которые сильно затрудняют
    доступ к оригинальным серверам. Поддельные сервера могут использоваться злоумышленниками
    для сбора Ваших данных.
- Как плагину получается ускорять подключение к серверам?
  - Отключение очереди. При нажатии на сервер плагин тут же пытается подключиться, в отличие от
    стандартного BombSquad, который сначала запрашивает список игроков в очереди и только если
    очередь пуста — пытается подключиться.