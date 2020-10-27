import gettext
import os

from mca import config

dir_path = os.path.dirname(os.path.realpath(__file__))
try:
    language = gettext.translation('messages', localedir=dir_path + '/locales',
                                   languages=[config.Config().get('language')])
except FileNotFoundError:
    _ = gettext.gettext
else:
    language.install()
    _ = language.gettext
