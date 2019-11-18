from mca.config import config
import gettext
import os

dir_path = os.path.dirname(os.path.realpath(__file__))
if config.config.get('language') == 'en':
    _ = gettext.gettext
elif config.config.get('language') == 'de':
    de = gettext.translation('messages', localedir=dir_path + '/locales', languages=['de'])
    de.install()
    _ = de.gettext
