# Ms Launcher
Plugin for game [BombSquad](https://github.com/efroemling/ballistica ),
filters the list of servers, showing only verified servers (can be disabled)
and simplifies & speeds up the connection to them.

[English]() | [Русский](https://github.com/Ms-company-BombSquad/docs/README.ru.md)

![](https://github.com/Ms-company-BombSquad/ms-launcher/actions/workflows/pylint.yml/badge.svg )
## Additional functionality:
- Auto-update (can be disabled in the settings)
- Localization for English and Russian languages

## FAQ
- Where does the plugin get the list of verified servers from?
  - At the moment, the repository stores a list of verified `ip` and plugin just checks
    if the `ip` of a particular server is in this list. A little later we hope to implement
    getting a list of servers from our web server, and in the meantime will update the list regularly
    in the repository.
    > If you are the owner of the server and want your server to be included in the list — write to us
    ivanms.ept@gmail.com
- Why do we need server filtering?
  - A lot of fake copies of the original servers have appeared on the network, which make it very difficult
    access to the original servers. Fake servers can be used by attackers
    to collect your data.
- How does the plugin speed up connection to servers?
  - Disabling the queue. When you click on the server, the plugin immediately tries to connect, unlike
    the standard BombSquad, which first requests a list of players in the queue and only if
    the queue is empty — trying to connect.