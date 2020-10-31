# Swaipe

Swaipe is a dating app bot with automatic swiping and customizable behavior.

![Swaipe GUI screenshot image](https://raw.githubusercontent.com/thomanq/swaipe/master/assets/swaipe_GUI.png)

Current functionality includes:
- Automatic swiping on Tinder and Badoo
- Random swiping with customizable:
    - like/dislike ratio
    - min/max swiping speed 
    - (optional) swiping limit

It is designed to be extensible, so that you can add support for:
- additional dating platforms (extend the `DatingProvider` class in `providers.py`)
- additional automators (extend the `Automator` class in `automator.py`) with Machine Learning capabilities for example.

# Keyboard shortcuts

The default keyboard shortcuts can be customized by editing the `settings.cfg` file.

The default ones are:

| Keyboard shortcut | Corresponding action |
| ----------------- | ---------------------|
| `d` | Like the picture  |
| `a` | Dislike the picture |
| `e` | Like the profile |
| `q` | Dislike the profile |
| `b` | Select the Badoo provider |
| `shift+b` | Go to Badoo website |
| `t` | Select the Tinder provider |
| `shift+t` | Go to the Tinder website |
| `x` | Start / stop automator |
| `ctrl+x` | Choose next automator |
| `shift+x` | Choose previous automator |
| `+` | Automator: +1 to max limit |
| `shift++` | Automator: +10 to max limit |
| `-` | Automator: -1 to max limit |
| `shift+-` | Automator: -10 to max limit |
| `alt++` | Automator: +1% to yes percentage |
| `alt+-` | Automator: -1% to yes percentage |

# Supported dating platforms

Swaipe currently supports **Tinder** and **Badoo**.

If you wish to add a platform, extend the `DatingProvider` class in `providers.py`.

# Supported operating systems

So far, only **Windows 10** and **Ubuntu Linux** have been tested. Any PRs to support other platforms are welcome.