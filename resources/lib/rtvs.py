# -*- coding: UTF-8 -*-
# /*
# *      Copyright (C) 2013 Maros Ondrasek
# *      Update        2022 Jastrab
# *      Update 2026 pre Kodi 22 (Python 3)
# *
# *  This Program is free software; you can redistribute it and/or modify
# *  it under the terms of the GNU General Public License as published by
# *  the Free Software Foundation; either version 2, or (at your option)
# *  any later version.
# *
# *  This Program is distributed in the hope that it will be useful,
# *  but WITHOUT ANY WARRANTY; without even the implied warranty of
# *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# *  GNU General Public License for more details.
# *
# *  You should have received a copy of the GNU General Public License
# *  along with this program; see the file COPYING.  If not, write to
# *  the Free Software Foundation, 675 Mass Ave, Cambridge, MA 02139, USA.
# *  http://www.gnu.org/copyleft/gpl.html
# *
# */

import re
import urllib.parse
import urllib.request
import http.cookiejar
import calendar
from datetime import date
import util
from provider import ContentProvider
import json
import xbmc, xbmcaddon, xbmcgui

# Kompatibilita pre staršie volania v utilitách
urllib2 = urllib.request
cookielib = http.cookiejar

DOMAIN = 'stvr.sk[span_1](start_span)'[span_1](end_span)
HOST = 'https://www.' + DOMAIN[span_2](start_span)[span_2](end_span)
IMAGES = '[span_3](start_span)'[span_3](end_span)

START_AZ = '<div class="row tv__archive">[span_4](start_span)'[span_4](end_span)
END_AZ = '<div class="footer[span_5](start_span)'[span_5](end_span)
AZ_ITER_RE = r'<a title="(?P<title>[^"]+)"(.+?)href="(?P<url>[^"]+)"(.+?)<img src="(?P<img>[^"]+)"(.+?)<span class="date">(?P<date>[^<]+)</span>(.+?)<span class="program time--start">(?P<time>[^<]+)[span_6](start_span)'[span_6](end_span)

START_AZ_RADIO = '<li class="list--radio-series__list list__headers">[span_7](start_span)'[span_7](end_span)
END_AZ_RADIO = '<div class="box box--live">[span_8](start_span)'[span_8](end_span)
AZ_ITER_RE_RADIO = r'title="(?P<title>[^\"]+)" href="(?P<url>[^\"]+)".+?__station[^"]+">(?P<station>[^\t]+).+?__series">(?P<series>[^<]+).+?__date">(?P<date>[^<]+)[span_9](start_span)'[span_9](end_span)

START_DATE = 'class="row tv__archive tv__archive--date">[span_10](start_span)'[span_10](end_span)
END_DATE = '<!-- FOOTER -->[span_11](start_span)'[span_11](end_span)
DATE_ITER_RE = r'<div class="media.+?">\s*<a href="(?P<url>[^\"]+)".+?<img src="(?P<img>[^\"]+)".+?</a>\s*<div class="media__body">.+?<div class="program time--start">(?P<time>[^\<]+)<span>.+?<a class="link".+?title="(?P<title>[^\"]+)">[span_12](start_span)'[span_12](end_span)

START_DATE_RADIO = '<li class="list--radio-series__list list__headers">[span_13](start_span)'[span_13](end_span)
END_DATE_RADIO = '<div class="box box--live">[span_14](start_span)'[span_14](end_span)
DATE_ITER_RE_RADIO = r'title="(?P<title>[^\"]+)" href="(?P<url>[^\"]+)".+?__station">(?P<station>[^\t]+).+?__series">(?P<series>[^<]+).+?__date">(?P<date>[^<]+)[span_15](start_span)'[span_15](end_span)


RADIO_STATION_START = 'class="box box--live">[span_16](start_span)'[span_16](end_span)
RADIO_STATION_END = '<!-- FOOTER -->[span_17](start_span)'[span_17](end_span)
RADIO_STATION_ITER_RE = r'href="(?P<url>[^\"]+)".+?title="(?P<title>[^\"]+)[span_18](start_span)'[span_18](end_span)

RADIO_EXTRA_START = 'class="router--archive-extra">[span_19](start_span)'[span_19](end_span)
RADIO_EXTRA_END = '<!-- ROZHLASOVE STANICE-->[span_20](start_span)'[span_20](end_span)
RADIO_EXTRA_ITER_RE = r'title="(?P<title>[^\"]+).*?href="(?P<url>[^\"]+)".+?subtitle\">(?P<subtitle>[^<]+|)[span_21](start_span)'[span_21](end_span)

RADIO_PLUS_START = '<table width="100%">[span_22](start_span)'[span_22](end_span)
RADIO_PLUS_END = '</table>[span_23](start_span)'[span_23](end_span)
RADIO_PLUS_ITER_RE = r'src="(?P<img>[^\"]+)".*?<a class="a210_page a210_page" title="(?P<title>[^\"]+)" href="(?P<url>[^\"]+)".*?(?:<br \/>|<\/b>)\((?P<popis>[^\)]+)\)[span_24](start_span)'[span_24](end_span)

RADIO_PLUS_START_CAST = '<div class="col-12 col-md-8 article__body">[span_25](start_span)'[span_25](end_span)
RADIO_PLUS_END_CAST = '<!-- ROZHLASOVE STANICE-->[span_26](start_span)'[span_26](end_span)
RADIO_PLUS_ITER_RE_CAST = r'<strong class="player-title">(?P<title>[^\<]+)</strong>.*?loading="lazy" src="(?P<url>[^\"]+)[span_27](start_span)'[span_27](end_span)
RADIO_PLUS_ITER_RE_CAST2 = r'title="(?P<title0>[^"]+)" href="(?P<url>[^"]+)".*?>(?P<title>[^<]+)<[span_28](start_span)'[span_28](end_span)


RADIO_PLUS_START_CAST2 = '<!-- LAVA STRANA -->[span_29](start_span)'[span_29](end_span)
RADIO_PLUS_ITER_RE_CAST22 = r'<picture>.*?source srcset="(?P<img>[^"]+)".*?article__body">(?P<desc>.*?)</p>[span_30](start_span)'[span_30](end_span)

RADIO_PLUS_START_CAST3 = '<!-- CONTENT -->[span_31](start_span)'[span_31](end_span)
RADIO_PLUS_END_CAST3 = '<!-- ROZHLASOVE STANICE-->[span_32](start_span)'[span_32](end_span)
RADIO_PLUS_ITER_RE_CAST3 = r'<picture>.*?source srcset="(?P<img>[^"]+)".*?article__body">(?P<desc>.*?)<strong class="player-title">(?P<title>[^\<]+)</strong>.*?loading="lazy" src="(?P<url>[^\"]+)[span_33](start_span)'[span_33](end_span)

START_LISTING = "<div class='calendar modal-body'>[span_34](start_span)"[span_34](end_span)
END_LISTING = '</table>[span_35](start_span)'[span_35](end_span)
LISTING_PAGER_RE = "<a class='prev calendarRoller' href='(?P<prevurl>[^\']+)\'.+?<a class='next calendarRoller\' href='(?P<nexturl>[^\']+)[span_36](start_span)"[span_36](end_span)
LISTING_DATE_RE = r"<div class='calendar-header'>\s+.*?<h6>(?P<date>[^<]+)</h6>[span_37](start_span)"[span_37](end_span)
LISTING_ITER_RE = r'<td class=(\"day\"|\"active day\")>\s+<a href=[\'\"](?P<url>[^\"^\']+)[\"\'].*?>(?P<daynum>[\d]+)</a>\s+</td>[span_38](start_span)'[span_38](end_span)

EPISODE_RE = r'<div class="article__header">.?<h2 class="page__title">(?P<title>[^<]+)</h2>.?<div class="article__date-name(?: article__date-name--valid)?">.*?(?P<plot>\d{1,2}.\d{1,2}.\d{4})[span_39](start_span)'[span_39](end_span)

COLOR_START = '[COLOR FFB2D4F5][span_40](start_span)'[span_40](end_span)
COLOR_END = '[/COLOR][span_41](start_span)'[span_41](end_span)

def to_unicode(text, encoding='utf-8'):
    if isinstance(text, bytes):
        return text.decode(encoding, errors='replace')
    return str(text)

def get_streams_from_manifest_url(url):
    result = []
    manifest = util.request(url)
    for m in re.finditer(r'^#EXT-X-STREAM-INF:(?P<info>.+)\n(?P<chunk>.+)', manifest, re.MULTILINE):
        stream = {}
        stream['quality'] = '???'
        stream['bandwidth'] = 0
        for info in re.split(r''',(?=(?:[^'"]|'[^']*'|"[^"]*")*$)''', m.group('info')):
            key, val = info.split('=', 1)
            if key == "BANDWIDTH":
                stream['bandwidth'] = int(val)
            if key == "RESOLUTION":
                stream['quality'] = val.split("x")[1] + "p"
        stream['url'] = url[url.find(':')+1:url.find('/')] + m.group('chunk')
        result.append(stream)
    result.sort(key=lambda x:x['bandwidth'], reverse=True)
    return result

def _fix_date(date):
    print(date)
    if date[0] == ' ':
        date = date[1:]
    brb = date.split(' ')
    d, m, y = brb[0].split('.')
    if len(d) == 1: d = '0' + d
    if len(m) == 1: m = '0' + m
    if len(brb) > 1:
        return '{}.{}.{} {} '.format(d, m, y, brb[1])
    else:
        return '{}.{}.{}'.format(d, m, y)

def _fix_space(text):
    text = re.sub('^[ \t\r\n]{1,}|[ \t\r\n]{1,}$', '', text)
    return text

def _fix_chars(text):
    text = re.sub('<br ?/>|<br ?>', '\n', text)
    text = re.sub('<.*?>', '', text)
    return text

class RtvsContentProvider(ContentProvider):

    data_json = None

    def __init__(self, username=None, password=None, filter=None, tmp_dir='/tmp'):
        ContentProvider.__init__(self, DOMAIN, f'{HOST}/televizia/archiv', username, password, filter, tmp_dir)[span_42](start_span)[span_42](end_span)
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookielib.LWPCookieJar()))[span_43](start_span)[span_43](end_span)
        urllib2.install_opener(opener)[span_44](start_span)[span_44](end_span)

    def _fix_url(self, url):
        if url.startswith('/json/') or url.startswith('/televizia/archiv/'):[span_45](start_span)[span_45](end_span)
            return HOST + url[span_46](start_span)[span_46](end_span)
        return self._url(url)[span_47](start_span)[span_47](end_span)

    def _fix_url_radio(self, url):
        if url.startswith('/json/') or url.startswith('/radio/archiv/'):[span_48](start_span)[span_48](end_span)
            return HOST + url[span_49](start_span)[span_49](end_span)
        return self._url(url)[span_50](start_span)[span_50](end_span)

    def _get_url(self, radio=False):
        url = f'{HOST}/televizia/archiv[span_51](start_span)'[span_51](end_span)
        if radio:
            url = f'{HOST}/radio/archiv[span_52](start_span)'[span_52](end_span)
        return url[span_53](start_span)[span_53](end_span)

    def capabilities(self):
        return ['categories', 'resolve', '!download'][span_54](start_span)[span_54](end_span)

    def list(self, url):
        self.info('== list ==')[span_55](start_span)[span_55](end_span)
        self.info('url=' + url )[span_56](start_span)[span_56](end_span)
        self.info('base_url=' + self.base_url)[span_57](start_span)[span_57](end_span)

        if url.find('#az#') == 0:[span_58](start_span)[span_58](end_span)
            return self.az()[span_59](start_span)[span_59](end_span)

        elif url.find('#az_radio#') == 0:[span_60](start_span)[span_60](end_span)
            return self.az_radio()[span_61](start_span)[span_61](end_span)

        elif url.find('#live#') == 0:[span_62](start_span)[span_62](end_span)
            return self.live()[span_63](start_span)[span_63](end_span)

        elif url.find("#date_radio#") == 0 or (url.find("radio=1") != -1 and url.find('ord=dt') == -1):[span_64](start_span)[span_64](end_span)
            d = re.search('#date(?:_radio|)#(?P<month>[\d]{1,2})\.(?P<year>[\d]{4})', url)[span_65](start_span)[span_65](end_span)
            month = d.group('month')[span_66](start_span)[span_66](end_span)
            year = d.group('year')[span_67](start_span)[span_67](end_span)
            self.base_url = self._get_url(True)[span_68](start_span)[span_68](end_span)
            return self.date_radio(int(year), int(month))[span_69](start_span)[span_69](end_span)

        elif url.find("#date#") == 0:[span_70](start_span)[span_70](end_span)
            month, year = url.split('#')[-1].split('.')[span_71](start_span)[span_71](end_span)
            self.base_url = self._get_url()[span_72](start_span)[span_72](end_span)
            return self.date(int(year), int(month))[span_73](start_span)[span_73](end_span)
        

        elif url.find("/archiv/extra/vzdelavanie") != -1:[span_74](start_span)[span_74](end_span)
            self.base_url = self._get_url(True)[span_75](start_span)[span_75](end_span)
            return self.get_radio_archiv_plus()[span_76](start_span)[span_76](end_span)

        elif url.find("?radio=plus") != -1:[span_77](start_span)[span_77](end_span)
            self.base_url = self._get_url(True)[span_78](start_span)[span_78](end_span)
            return self.get_radio_archiv_plus_cast(url)[span_79](start_span)[span_79](end_span)

        elif url.find("?radio=vzdelanie_plus") != -1:[span_80](start_span)[span_80](end_span)
            self.base_url = self._get_url(True)[span_81](start_span)[span_81](end_span)
            return self.get_radio_archiv_plus_cast2(url)[span_82](start_span)[span_82](end_span)


        elif url.find("#extra_radio#") == 0:[span_83](start_span)[span_83](end_span)
            self.base_url = self._get_url(True)[span_84](start_span)[span_84](end_span)
            return self.get_radio_archiv_extra()[span_85](start_span)[span_85](end_span)

        elif url.find('ord=az') != -1 and url.find('l=') != -1:[span_86](start_span)[span_86](end_span)
            self.info('AZ listing: %s' % url)[span_87](start_span)[span_87](end_span)
            if url.find('&radio=1') == -1:[span_88](start_span)[span_88](end_span)
                return self.list_az(util.request(self._fix_url(url)))[span_89](start_span)[span_89](end_span)
            else:
                self.base_url = self._get_url(True)[span_90](start_span)[span_90](end_span)
                return self.list_az_radio(util.request(self._fix_url_radio(url)))[span_91](start_span)[span_91](end_span)
            
        elif url.find('/archiv/extra/') != -1:[span_92](start_span)[span_92](end_span)
            self.base_url = self._get_url(True)[span_93](start_span)[span_93](end_span)
            return self.list_date_radio(util.request(self._fix_url_radio(url)))[span_94](start_span)[span_94](end_span)

        elif url.find('ord=dt') != -1 and url.find('date=') != -1:[span_95](start_span)[span_95](end_span)
            self.info('DATE listing: %s' % url)[span_96](start_span)[span_96](end_span)
            if url.find('&radio=1') == -1:[span_97](start_span)[span_97](end_span)
                return self.list_date(util.request(self._fix_url(url)))[span_98](start_span)[span_98](end_span)
            else:
                self.base_url = self._get_url(True)[span_99](start_span)[span_99](end_span)
                return self.list_date_radio(util.request(self._fix_url_radio(url)))[span_100](start_span)[span_100](end_span)
        
        elif url.find('/json/') != -1:[span_101](start_span)[span_101](end_span)
            if url.find('snippet_archive_series_calendar.json'):[span_102](start_span)[span_102](end_span)
                if url.find('/radio/') == -1:[span_103](start_span)[span_103](end_span)
                    return self.list_episodes(util.json.loads(util.request(self._fix_url(url)))['snippets']['snippet-calendar-calendar'])[span_104](start_span)[span_104](end_span)
                else:
                    self.base_url = self._get_url(True)[span_105](start_span)[span_105](end_span)
                    return self.list_episodes(util.json.loads(util.request(self._fix_url_radio(url)))['snippets']['snippet-calendar-calendar'])[span_106](start_span)[span_106](end_span)

            else:
                self.error("unknown JSON listing request: %s"% url)[span_107](start_span)[span_107](end_span)
        else:
            self.info("EPISODE listing: %s" % url)[span_108](start_span)[span_108](end_span)
            if url.find('/radio/') == -1:[span_109](start_span)[span_109](end_span)
                page = util.request(self._fix_url(url))[span_110](start_span)[span_110](end_span)
                self.data_web(page)[span_111](start_span)[span_111](end_span)
                return self.list_episodes(page)[span_112](start_span)[span_112](end_span)
            else:
                return self.list_episodes(util.request(self._fix_url_radio(url)))[span_113](start_span)[span_113](end_span)


    def data_web(self, page):
        data_json = None[span_114](start_span)[span_114](end_span)
        fa = re.finditer(r'<script type="application\/ld\+json">(?P<data>.*?)<\/script>', page, re.IGNORECASE | re.DOTALL)[span_115](start_span)[span_115](end_span)
        for f in fa:[span_116](start_span)[span_116](end_span)
            self.info(f)[span_117](start_span)[span_117](end_span)
            try:
                data_json = json.loads(f.group('data'))[span_118](start_span)[span_118](end_span)
                self.info(data_json)[span_119](start_span)[span_119](end_span)
                if 'description' in data_json:[span_120](start_span)[span_120](end_span)
                    break
            except:
                self.info('preskakujem')[span_121](start_span)[span_121](end_span)
        return data_json[span_122](start_span)[span_122](end_span)

    def categories(self):
        result = [][span_123](start_span)[span_123](end_span)
        
        item = self.dir_item()[span_124](start_span)[span_124](end_span)
        item['title'] = '[B]Živé vysielanie[/B][span_125](start_span)'[span_125](end_span)
        item['url'] = "#live#[span_126](start_span)"[span_126](end_span)
        result.append(item)[span_127](start_span)[span_127](end_span)

        item = self.dir_item()[span_128](start_span)[span_128](end_span)
        item['title'] = '[B][COLOR FFB2D4F5]TV:[/COLOR] A-Z[/B][span_129](start_span)'[span_129](end_span)
        item['url'] = "#az#[span_130](start_span)"[span_130](end_span)
        result.append(item)[span_131](start_span)[span_131](end_span)
        
        item = self.dir_item()[span_132](start_span)[span_132](end_span)
        item['title'] = '[B][COLOR FFB2D4F5]TV:[/COLOR] Podľa dátumu[/B][span_133](start_span)'[span_133](end_span)
        d = date.today()[span_134](start_span)[span_134](end_span)
        item['url'] = "#date#%d.%d" % (d.month, d.year)[span_135](start_span)[span_135](end_span)
        result.append(item)[span_136](start_span)[span_136](end_span)
 
        item = self.dir_item()[span_137](start_span)[span_137](end_span)
        item['title'] = '[B][COLOR FFB2D4F5]Rádio:[/COLOR] A-Z [/B][span_138](start_span)'[span_138](end_span)
        item['url'] = "#az_radio#[span_139](start_span)"[span_139](end_span)
        result.append(item)[span_140](start_span)[span_140](end_span)

        item = self.dir_item()[span_141](start_span)[span_141](end_span)
        item['title'] = '[B][COLOR FFB2D4F5]Rádio:[/COLOR] Podľa dátumu[/B][span_142](start_span)'[span_142](end_span)
        item['url'] = "#date_radio#%d.%d" % (d.month, d.year)[span_143](start_span)[span_143](end_span)
        result.append(item)[span_144](start_span)[span_144](end_span)

        item = self.dir_item()[span_145](start_span)[span_145](end_span)
        item['title'] = '[B][COLOR FFB2D4F5]Rádio:[/COLOR] Extra[/B][span_146](start_span)'[span_146](end_span)
        item['url'] = "#extra_radio#%d.%d" % (d.month, d.year)[span_147](start_span)[span_147](end_span)
        result.append(item)[span_148](start_span)[span_148](end_span)
        
        return result[span_149](start_span)[span_149](end_span)

    def getInfoFromWeb(self, item):
        channel_id = item['url'].split('.')[1][span_150](start_span)[span_150](end_span)
        data = util.request(HOST + "/json/live5f.json?c=%s&b=mozilla&p=linux&v=47&f=1&d=1"%(channel_id))[span_151](start_span)[span_151](end_span)
        videodata = util.json.loads(data)['clip'][span_152](start_span)[span_152](end_span)
        url = videodata['sources'][0]['src'][span_153](start_span)[span_153](end_span)
        url = ''.join(url.split())[span_154](start_span)[span_154](end_span)
        title = videodata.get('title','')[span_155](start_span)[span_155](end_span)
        if title != '':[span_156](start_span)[span_156](end_span)
            item['title'] += ':  ' + title[span_157](start_span)[span_157](end_span)
        item['plot'] = videodata.get('description','')[span_158](start_span)[span_158](end_span)
        item['img'] = videodata.get('image','')[span_159](start_span)[span_159](end_span)
        return item[span_160](start_span)[span_160](end_span)

    def get_list_radios(self):
        result = [][span_161](start_span)[span_161](end_span)
        self.info ('== get_list_radios ==')[span_162](start_span)[span_162](end_span)
        page = util.request(f'{HOST}/radio/radia')[span_163](start_span)[span_163](end_span)
        page = util.substr(page, RADIO_STATION_START, RADIO_STATION_END)[span_164](start_span)[span_164](end_span)
        for m in re.finditer(RADIO_STATION_ITER_RE, page, re.IGNORECASE | re.DOTALL):[span_165](start_span)[span_165](end_span)
            item = self.video_item()[span_166](start_span)[span_166](end_span)
            item['title'] = m.group('title')[span_167](start_span)[span_167](end_span)
            item['url'] = m.group('url')[span_168](start_span)[span_168](end_span)
            item['menu'] = {'$30070':{'list':item['url'], 'action-type':'list'}}[spa    urllib2 = urllib.request


import calendar
from datetime import date
import util
from provider import ContentProvider
import json
import xbmc, xbmcaddon, xbmcgui

DOMAIN = 'stvr.sk'
HOST = 'https://www.' + DOMAIN
IMAGES = ''

START_AZ = '<div class=\"row tv__archive\">'
END_AZ = '<div class="footer'
AZ_ITER_RE = r'<a title=\"(?P<title>[^"]+)\"(.+?)href=\"(?P<url>[^"]+)\"(.+?)<img src=\"(?P<img>[^"]+)\"(.+?)<span class=\"date\">(?P<date>[^<]+)<\/span>(.+?)<span class=\"program time--start\">(?P<time>[^<]+)'

START_AZ_RADIO = '<li class=\"list--radio-series__list list__headers\">'
END_AZ_RADIO = '<div class=\"box box--live\">'
AZ_ITER_RE_RADIO = r'title=\"(?P<title>[^\"]+)\" href=\"(?P<url>[^\"]+)\".+?__station[^"]+">(?P<station>[^\t]+).+?__series">(?P<series>[^<]+).+?__date">(?P<date>[^<]+)'

START_DATE = 'class=\"row tv__archive tv__archive--date\">'
END_DATE = '<!-- FOOTER -->'
DATE_ITER_RE = r'<div class=\"media.+?\">\s*<a href=\"(?P<url>[^\"]+)\".+?<img src=\"(?P<img>[^\"]+)\".+?<\/a>\s*<div class=\"media__body\">.+?<div class=\"program time--start\">(?P<time>[^\<]+)<span>.+?<a class=\"link\".+?title=\"(?P<title>[^\"]+)\">'

START_DATE_RADIO = '<li class=\"list--radio-series__list list__headers\">'
END_DATE_RADIO = '<div class=\"box box--live\">'
DATE_ITER_RE_RADIO = r'title=\"(?P<title>[^\"]+)\" href=\"(?P<url>[^\"]+)\".+?__station">(?P<station>[^\t]+).+?__series">(?P<series>[^<]+).+?__date">(?P<date>[^<]+)'


RADIO_STATION_START = 'class=\"box box--live\">'
RADIO_STATION_END = '<!-- FOOTER -->'
RADIO_STATION_ITER_RE = r'href=\"(?P<url>[^\"]+)\".+?title=\"(?P<title>[^\"]+)'

RADIO_EXTRA_START = 'class=\"router--archive-extra\">'
RADIO_EXTRA_END = '<!-- ROZHLASOVE STANICE-->'
RADIO_EXTRA_ITER_RE = r'title=\"(?P<title>[^\"]+).*?href=\"(?P<url>[^\"]+)\".+?subtitle\">(?P<subtitle>[^<]+|)'

RADIO_PLUS_START = '<table width=\"100%\">'
RADIO_PLUS_END = '</table>'
RADIO_PLUS_ITER_RE = r'src=\"(?P<img>[^\"]+)\".*?<a class=\"a210_page a210_page\" title=\"(?P<title>[^\"]+)\" href=\"(?P<url>[^\"]+)\".*?(?:<br \/>|<\/b>)\((?P<popis>[^\)]+)\)'

RADIO_PLUS_START_CAST = '<div class=\"col-12 col-md-8 article__body\">'
RADIO_PLUS_END_CAST = '<!-- ROZHLASOVE STANICE-->'
RADIO_PLUS_ITER_RE_CAST = r'<strong class="player-title">(?P<title>[^\<]+)<\/strong>.*?loading="lazy" src="(?P<url>[^\"]+)'
RADIO_PLUS_ITER_RE_CAST2 = r'title="(?P<title0>[^"]+)" href="(?P<url>[^"]+)".*?>(?P<title>[^<]+)<'


RADIO_PLUS_START_CAST2 = '<!-- LAVA STRANA -->'
RADIO_PLUS_ITER_RE_CAST22 = r'<picture>.*?source srcset="(?P<img>[^"]+)".*?article__body">(?P<desc>.*?)<\/p>'

RADIO_PLUS_START_CAST3 = '<!-- CONTENT -->'
RADIO_PLUS_END_CAST3 = '<!-- ROZHLASOVE STANICE-->'
RADIO_PLUS_ITER_RE_CAST3 = r'<picture>.*?source srcset="(?P<img>[^"]+)".*?article__body">(?P<desc>.*?)<strong class="player-title">(?P<title>[^\<]+)<\/strong>.*?loading="lazy" src="(?P<url>[^\"]+)'

START_LISTING = '<div class=\'calendar modal-body\'>'
END_LISTING = '</table>'
LISTING_PAGER_RE = '<a class=\'prev calendarRoller\' href=\'(?P<prevurl>[^\']+)\'.+?<a class=\'next calendarRoller\' href=\'(?P<nexturl>[^\']+)'
LISTING_DATE_RE = r'<div class=\'calendar-header\'>\s+.*?<h6>(?P<date>[^<]+)</h6>'
LISTING_ITER_RE = r'<td class=(\"day\"|\"active day\")>\s+<a href=[\'\"](?P<url>[^\"^\']+)[\"\'].*?>(?P<daynum>[\d]+)</a>\s+</td>'

EPISODE_RE = r'<div class="article__header">.?<h2 class="page__title">(?P<title>[^<]+)</h2>.?<div class="article__date-name(?: article__date-name--valid)?">.*?(?P<plot>\d{1,2}.\d{1,2}.\d{4})'

COLOR_START = '[COLOR FFB2D4F5]'
COLOR_END = '[/COLOR]'

def to_unicode(text, encoding='utf-8'):
    return text

def get_streams_from_manifest_url(url):
    result = []
    manifest = util.request(url)
    for m in re.finditer(r'^#EXT-X-STREAM-INF:(?P<info>.+)\n(?P<chunk>.+)', manifest, re.MULTILINE):
        stream = {}
        stream['quality'] = '???'
        stream['bandwidth'] = 0
        for info in re.split(r''',(?=(?:[^'"]|'[^']*'|"[^"]*")*$)''', m.group('info')):
            key, val = info.split('=', 1)
            if key == "BANDWIDTH":
                stream['bandwidth'] = int(val)
            if key == "RESOLUTION":
                stream['quality'] = val.split("x")[1] + "p"
        stream['url'] = url[url.find(':')+1:url.find('/')] + m.group('chunk')
        result.append(stream)
    result.sort(key=lambda x:x['bandwidth'], reverse=True)
    return result

def _fix_date(date):
    print (date)
    # return date
    if date[0] == ' ':
        date = date[1:]
    brb = date.split(' ')
    d, m, y = brb[0].split('.')
    if len(d) == 1: d = '0' + d
    if len(m) == 1: m = '0' + m
    if len(brb) > 1:
        return '{}.{}.{} {} '.format(d, m, y, brb[1])
    else:
        return '{}.{}.{}'.format(d, m, y)

def _fix_space(text):
    # text = re.sub('^[ \t]{1,}|[ \t]{1,}$', '', text)
    text = re.sub('^[ \t\r\n]{1,}|[ \t\r\n]{1,}$', '', text)
    return text

def _fix_chars(text):
    text = re.sub('<br ?/>|<br ?>', '\n', text)
    text = re.sub('<.*?>', '', text)
    return text

class RtvsContentProvider(ContentProvider):

    data_json = None

    def __init__(self, username=None, password=None, filter=None, tmp_dir='/tmp'):
        ContentProvider.__init__(self, DOMAIN, f'{HOST}/televizia/archiv', username, password, filter, tmp_dir)
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookielib.LWPCookieJar()))
        urllib2.install_opener(opener)

    def _fix_url(self, url):
        if url.startswith('/json/') or url.startswith('/televizia/archiv/'):
            return HOST + url
        return self._url(url)

    def _fix_url_radio(self, url):
        # self.info('_fix_url_radio url=' + url)
        if url.startswith('/json/') or url.startswith('/radio/archiv/'):
            return HOST + url
        return self._url(url)

    def _get_url(self, radio=False):
        url = f'{HOST}/televizia/archiv'
        if radio:
            url = f'{HOST}/radio/archiv'
        return url

    def capabilities(self):
        return ['categories', 'resolve', '!download']

    def list(self, url):
        self.info('== list ==')
        self.info('url=' + url )
        self.info('base_url=' + self.base_url)

        if url.find('#az#') == 0:
            return self.az()

        elif url.find('#az_radio#') == 0:
            return self.az_radio()

        elif url.find('#live#') == 0:
            return self.live()

        elif url.find("#date_radio#") == 0 or (url.find("radio=1") != -1 and url.find('ord=dt') == -1):
            d = re.search('#date(?:_radio|)#(?P<month>[\d]{1,2})\.(?P<year>[\d]{4})', url)
            month = d.group('month')
            year = d.group('year')
            self.base_url = self._get_url(True)
            return self.date_radio(int(year), int(month))

        elif url.find("#date#") == 0:
            month, year = url.split('#')[-1].split('.')
            self.base_url = self._get_url()
            return self.date(int(year), int(month))
        

        elif url.find("/archiv/extra/vzdelavanie") != -1:
            self.base_url = self._get_url(True)
            return self.get_radio_archiv_plus()

        elif url.find("?radio=plus") != -1:
            self.base_url = self._get_url(True)
            return self.get_radio_archiv_plus_cast(url)

        elif url.find("?radio=vzdelanie_plus") != -1:
            self.base_url = self._get_url(True)
            return self.get_radio_archiv_plus_cast2(url)


        elif url.find("#extra_radio#") == 0:
            self.base_url = self._get_url(True)
            return self.get_radio_archiv_extra()

        elif url.find('ord=az') != -1 and url.find('l=') != -1:
            self.info('AZ listing: %s' % url)
            if url.find('&radio=1') == -1:
                return self.list_az(util.request(self._fix_url(url)))
            else:
                self.base_url = self._get_url(True)
                return self.list_az_radio(util.request(self._fix_url_radio(url)))
            
        elif url.find('/archiv/extra/') != -1:
            self.base_url = self._get_url(True)
            return self.list_date_radio(util.request(self._fix_url_radio(url)))

        elif url.find('ord=dt') != -1 and url.find('date=') != -1:
            self.info('DATE listing: %s' % url)
            if url.find('&radio=1') == -1:
                return self.list_date(util.request(self._fix_url(url)))
            else:
                self.base_url = self._get_url(True)
                return self.list_date_radio(util.request(self._fix_url_radio(url)))
        
        elif url.find('/json/') != -1:
            if url.find('snippet_archive_series_calendar.json'):
                if url.find('/radio/') == -1:
                    return self.list_episodes(util.json.loads(util.request(self._fix_url(url)))['snippets']['snippet-calendar-calendar'])
                else:
                    self.base_url = self._get_url(True)
                    return self.list_episodes(util.json.loads(util.request(self._fix_url_radio(url)))['snippets']['snippet-calendar-calendar'])

            else:
                self.error("unknown JSON listing request: %s"% url)
        else:
            self.info("EPISODE listing: %s" % url)
            if url.find('/radio/') == -1:
                page = util.request(self._fix_url(url))
                self.data_web(page)
                return self.list_episodes(page)
            else:
                return self.list_episodes(util.request(self._fix_url_radio(url)))


    def data_web(self, page):
        data_json = None
        fa = re.finditer(r'<script type="application\/ld\+json">(?P<data>.*?)<\/script>', page, re.IGNORECASE | re.DOTALL)
        for f in fa:
            self.info(f)
            try:
                data_json = json.loads(f['data'])
                self.info(data_json)
                if 'description' in data_json:
                    break
            except:
                self.info('preskakujem')
        return data_json

    def categories(self):
        result = []
        # self.info ('== categories ==')
        
        item = self.dir_item()
        item['title'] = '[B]Živé vysielanie[/B]'
        item['url'] = "#live#"
        result.append(item)

        item = self.dir_item()
        item['title'] = '[B][COLOR FFB2D4F5]TV:[/COLOR] A-Z[/B]'
        item['url'] = "#az#"
        result.append(item)
        
        item = self.dir_item()
        item['title'] = '[B][COLOR FFB2D4F5]TV:[/COLOR] Podľa dátumu[/B]'
        d = date.today()
        item['url'] = "#date#%d.%d" % (d.month, d.year)
        result.append(item)
 
        item = self.dir_item()
        item['title'] = '[B][COLOR FFB2D4F5]Rádio:[/COLOR] A-Z [/B]'
        item['url'] = "#az_radio#"
        result.append(item)

        item = self.dir_item()
        item['title'] = '[B][COLOR FFB2D4F5]Rádio:[/COLOR] Podľa dátumu[/B]'
        item['url'] = "#date_radio#%d.%d" % (d.month, d.year)
        result.append(item)

        item = self.dir_item()
        item['title'] = '[B][COLOR FFB2D4F5]Rádio:[/COLOR] Extra[/B]'
        item['url'] = "#extra_radio#%d.%d" % (d.month, d.year)
        result.append(item)
        
        return result

    def getInfoFromWeb(self, item):
        channel_id = item['url'].split('.')[1]
        data = util.request(HOST + "/json/live5f.json?c=%s&b=mozilla&p=linux&v=47&f=1&d=1"%(channel_id))
        videodata = util.json.loads(data)['clip']
        url = videodata['sources'][0]['src']
        url = ''.join(url.split())
        # item['plot'] = videodata.get('title','')
        title = videodata.get('title','')
        if title != '':
            item['title'] += ':  ' + title
        item['plot'] = videodata.get('description','')
        item['img'] = videodata.get('image','')
        return item

    def get_list_radios(self):
        result = []
        self.info ('== get_list_radios ==')
        page = util.request(f'{HOST}/radio/radia')
        page = util.substr(page, RADIO_STATION_START, RADIO_STATION_END)
        for m in re.finditer(RADIO_STATION_ITER_RE, page, re.IGNORECASE | re.DOTALL):
            item = self.video_item()
            item['title'] = m.group('title')
            item['url'] = m.group('url')
            # item['img'] = IMAGES + "rtvs_24.png"
            item['menu'] = {'$30070':{'list':item['url'], 'action-type':'list'}}
            # self.info(item)
            self._filter(result, item)
        return result

    def get_radio_archiv_extra(self):
        result = []
        self.info ('== get_radio_archiv_extra ==')
        # self.info(page)
        page = util.request(f'{HOST}/radio/archiv/extra')
        page = util.substr(page, RADIO_EXTRA_START, RADIO_EXTRA_END)
        # self.info(page)
        for m in re.finditer(RADIO_EXTRA_ITER_RE, page, re.IGNORECASE | re.DOTALL):
            # item = self.video_item()
            item = self.dir_item()  
            item['title'] = m.group('title')
            item['url'] = HOST + m.group('url')
            item['plot'] = m.group('subtitle')
            item['menu'] = {'$30070':{'list':item['url'], 'action-type':'list'}}
            # self.info(item)
            self._filter(result, item)
        return result

    def get_radio_archiv_plus(self):
        result = []
        # self.info ('== get_radio_archiv_plus ==')
        # self.info(page)
        page = util.request(f'{HOST}/radio/archiv-plus')
        page = util.substr(page, RADIO_PLUS_START, RADIO_PLUS_END)
        # self.info(page)
        for m in re.finditer(RADIO_PLUS_ITER_RE, page, re.IGNORECASE | re.DOTALL):
            # item = self.video_item()
            item = self.dir_item()  
            item['title'] = m.group('title')
            item['url'] = HOST + m.group('url') + '?radio=plus'
            item['plot'] = m.group('popis')
            item['img'] = m.group('img')
            item['menu'] = {'$30070':{'list':item['url'], 'action-type':'list'}}
            # self.info(item)
            self._filter(result, item)
        return result

    def get_radio_archiv_plus_cast(self, url):
        result = []
        # self.info ('== get_radio_archiv_plus_cast ==')
        page = util.request(url)
        page2 = util.substr(page, RADIO_PLUS_START_CAST, RADIO_PLUS_END_CAST)
        if re.search(RADIO_PLUS_ITER_RE_CAST, page, re.IGNORECASE | re.DOTALL):
            for m in re.finditer(RADIO_PLUS_ITER_RE_CAST, page2, re.IGNORECASE | re.DOTALL):
                item = self.video_item()
                item['title'] = _fix_space(m.group('title'))
                item['url'] = m.group('url')                
                self._filter(result, item)
        else:
            page3 = util.substr(page, RADIO_PLUS_START_CAST2, RADIO_PLUS_END_CAST3)
            m = re.search(RADIO_PLUS_ITER_RE_CAST22, page3, re.IGNORECASE | re.DOTALL)
            _desc = None
            _img = None
            if m:
                _desc = _fix_chars(m.group('desc'))
                _img = m.group('img')

            for m in re.finditer(RADIO_PLUS_ITER_RE_CAST2, page2, re.IGNORECASE | re.DOTALL):
                item = self.dir_item()  
                if len(_fix_space(m.group('title'))) > len(m.group('title0')):
                    item['title'] = _fix_space(m.group('title'))
                else:
                    item['title'] = _fix_space(m.group('title0'))

                item['plot'] = _desc
                item['img'] = _img
                item['url'] = HOST + m.group('url')  + '?radio=vzdelanie_plus'
                self.info(item)
                self._filter(result, item)
        return result

    def get_radio_archiv_plus_cast2(self, url):
        result = []
        page = util.request(url)
        page = util.substr(page, RADIO_PLUS_START_CAST3, RADIO_PLUS_END_CAST3)
        for m in re.finditer(RADIO_PLUS_ITER_RE_CAST3, page, re.IGNORECASE | re.DOTALL):
            item = self.video_item()
            item['title'] = _fix_space(m.group('title'))
            item['plot'] = _fix_chars(m.group('desc'))
            item['img'] = m.group('img')
            item['url'] = m.group('url')
            self._filter(result, item)
        return result

    def live(self):
        result = []
        # self.info ('== live ==')

        item = self.video_item("live.1")
        item['title'] = "STV 1"
        item = self.getInfoFromWeb(item)
        result.append(item)

        item = self.video_item("live.2")
        item['title'] = "STV 2"
        item = self.getInfoFromWeb(item)
        result.append(item)

        item = self.video_item("live.3")
        item['title'] = "STV 24"
        # item['img'] = IMAGES + "rtvs_24.png"
        item = self.getInfoFromWeb(item)
        result.append(item)

        item = self.video_item("live.15")
        item['title'] = "STV Šport"
        item = self.getInfoFromWeb(item)
        result.append(item)        

        item = self.video_item("live.4")
        item['title'] = "STV Online"
        item = self.getInfoFromWeb(item)
        result.append(item)

        item = self.video_item("live.5")
        item['title'] = "STV NRSR"
        item = self.getInfoFromWeb(item)
        result.append(item)

        item = self.video_item("live.6")
        item['title'] = "LIVE STVR"
        item = self.getInfoFromWeb(item)
        result.append(item)

        # item = self.video_item("live.3")
        # item['title'] = "STV 3"
        # item = self.getInfoFromWeb(item)
        # result.append(item)

        result += self.get_list_radios()
        
        return result

    def az(self):
        # self.info ('== az ==')
        result = []
        item = self.dir_item()
        item['title'] = '0-9'
        item['url'] = '?l=9&ord=az'
        self._filter(result, item)
        for c in range(65, 91, 1):
            uchr = str(chr(c))
            item = self.dir_item()
            item['title'] = uchr
            item['url'] = '?l=%s&ord=az' % uchr.lower()
            self._filter(result, item)
        return result

    def az_radio(self):
        # self.info ('== az_radio ==')
        result = []
        item = self.dir_item()
        item['title'] = '0-9'
        item['url'] = '?l=9&ord=az&radio=1'
        self._filter(result, item)
        for c in range(65, 91, 1):
            uchr = str(chr(c))
            item = self.dir_item()
            item['title'] = uchr
            item['url'] = '?l=%s&ord=az&radio=1' % uchr.lower()
            self._filter(result, item)
        return result

    def date(self, year, month):
        # self.info ('== date ==')
        result = []
        today = date.today()
        prev_month = month > 0 and month - 1 or 12
        prev_year = prev_month == 12 and year - 1 or year
        item = self.dir_item()
        item['type'] = 'prev'
        item['url'] = "#date#%d.%d" % (prev_month, prev_year)
        result.append(item)
        for d in calendar.LocaleTextCalendar().itermonthdates(year, month):
            if d.month != month:
                continue
            if d > today:
                break
            item = self.dir_item()
            #item['title'] = "%d.%d %d" % (d.day, d.month, d.year)
            item['title'] = _fix_date ("%d.%d.%d" % (d.day, d.month, d.year))
            item['url'] = "?date=%d-%02d-%02d&ord=dt" % (d.year, d.month, d.day)
            self._filter(result, item)
        result.reverse()
        # self.info(result)
        return result

    def date_radio(self, year, month):
        # self.info ('== date_radio ==')
        result = []
        today = date.today()
        prev_month = month > 0 and month - 1 or 12
        prev_year = prev_month == 12 and year - 1 or year
        item = self.dir_item()
        item['type'] = 'prev'
        item['url'] = "#date#%d.%d&radio=1" % (prev_month, prev_year)
        result.append(item)
        for d in calendar.LocaleTextCalendar().itermonthdates(year, month):
            if d.month != month:
                continue
            if d > today:
                break
            item = self.dir_item()
            # item['title'] = "%d.%d %d" % (d.day, d.month, d.year)
            item['title'] = _fix_date ("%d.%d.%d" % (d.day, d.month, d.year))
            item['url'] = "?date=%d-%02d-%02d&ord=dt&radio=1" % (d.year, d.month, d.day)
            self._filter(result, item)
        result.reverse()
        # self.info(result)
        return result

    def list_az(self, page):
        self.info ('== list_az ==')
        # self.info(page)
        result = []
        page = util.substr(page, START_AZ, END_AZ)
        for m in re.finditer(AZ_ITER_RE, page, re.IGNORECASE | re.DOTALL):
            item = self.dir_item()
            semicolon = m.group('title').find(':')
            if semicolon != -1:
                item['title'] = m.group('title')[:semicolon].strip()
            else:
                item['title'] = m.group('title')
            item['img'] = self._fix_url(m.group('img'))
            item['url'] = m.group('url')
            self._filter(result, item)
        _next = re.search(r'href="([^"]+)"[^>]*aria-label="Nasledujúca"', page)
        if _next:
            item = self.dir_item()
            item['type'] = 'next'
            item['url'] = urllib.parse.urljoin(HOST, _next.group(1).replace("&amp;", "&"))
            self._filter(result, item)
        return result

    def list_az_radio(self, page):
        # self.info ('== list_az_radio ==')
        result = []
        page = util.substr(page, START_AZ_RADIO, END_AZ_RADIO)
        for m in re.finditer(AZ_ITER_RE_RADIO, page, re.IGNORECASE | re.DOTALL):
            item = self.dir_item()
           # self.info(m.group())
            semicolon = m.group('title').find(':')
            if semicolon != -1:
                item['title'] = m.group('title')[:semicolon].strip()
            else:
                item['title'] = m.group('title')
           # item['img'] = self._fix_url_radio(m.group('img'))
            item['url'] = m.group('url')
            self._filter(result, item)
        return result

    def list_date(self, page):
        result = []
        # self.info ('== list_date ==')
        page = util.substr(page, START_DATE, END_DATE)
        page = re.sub('<p class=\"perex\"></p>', '<p class=\"perex\">&nbsp;</p>', page)
        # self.info(page)
        for m in re.finditer(DATE_ITER_RE, page, re.IGNORECASE | re.DOTALL):
            item = self.video_item()
            item['title'] = "%s (%s)" % (m.group('title'), m.group('time'))
            item['img'] = self._fix_url(m.group('img'))
            item['url'] = m.group('url')
            if 'plot' in m.groups():
                item['plot'] = m.group('plot')
            item['menu'] = {'$30070':{'list':item['url'], 'action-type':'list'}}
            # self.info(item)
            self._filter(result, item)
        return result


    def list_date_radio(self, page):
        result = []
        # self.info ('== list_date_radio ==')
        # self.info(page)
        page2 = util.substr(page, '<li class=\"page-item active\">', '</nav>')
        page = util.substr(page, START_DATE_RADIO, END_DATE_RADIO)
        for m in re.finditer(DATE_ITER_RE_RADIO, page, re.IGNORECASE | re.DOTALL):
            item = self.video_item()
            #item['title'] = "%s (%s)" % (m.group('title'), m.group('date'))
            item['title'] = "%s%s%s %s" % (COLOR_START, _fix_date(m.group('date')), COLOR_END, m.group('title'))
            #item['img'] = self._fix_url_radio(m.group('img'))
            item['url'] = m.group('url') #+ '?radio=1'
            item['plot'] = m.group('series')
            item['menu'] = {'$30070':{'list':item['url'], 'action-type':'list'}}
            self._filter(result, item)
        if page2:
            prev_url = re.search('page-item active">.+?href=\"(?P<url>\/[^\"]+)\".+?title=\"(?P<title>[^\"]+)\"', page, re.IGNORECASE | re.DOTALL).group('url')
            
            # self.info('prev_url = ' + prev_url)
            item = self.dir_item()
            item['type'] = 'next'
            item['url'] = HOST + prev_url
            result.append(item)
        return result

    def list_episodes(self, page):
        result = []
        episodes = []
        # self.info ('== list_episodes ==')

        data_json = None
        page = util.substr(page, START_LISTING, END_LISTING)
        current_date = to_unicode(re.search(LISTING_DATE_RE, page, re.IGNORECASE | re.DOTALL).group('date'))
        self.info("<list_episodes> current_date: %s" % current_date)
        prev_url = re.search(LISTING_PAGER_RE, page, re.IGNORECASE | re.DOTALL).group('prevurl')
        prev_url = re.sub('&amp;', '&', prev_url)
        self.info("<list_episodes> prev_url: %s" % prev_url)
        if prev_url.find('_radio_') == -1:
            for m in re.finditer(LISTING_ITER_RE, page, re.IGNORECASE | re.DOTALL):
                episodes.append([self._fix_url(re.sub('&amp;', '&', m.group('url'))), m])
        else:
             for m in re.finditer(LISTING_ITER_RE, page, re.IGNORECASE | re.DOTALL):
                episodes.append([self._fix_url_radio(re.sub('&amp;', '&', m.group('url'))), m])

        self.info("<list_episodes> found %d episodes" % len(episodes))
        res = self._request_parallel(episodes)
        for p, m in res:
            m = m[0]
            dnum = to_unicode(m.group('daynum'))
            item = self.list_episode(p)
            item['url'] = re.sub('&amp;', '&', m.group('url'))
            if not data_json:
                data_json = self.data_web(util.request(self._fix_url(item['url'])))
            
            if data_json:
                item['title'] = "%s (%s. %s)" % (item['title'] or data_json['name'], dnum, current_date)
            else:
                item['title'] = "%s (%s. %s)" % (item['title'], dnum, current_date)
            item['date'] = dnum

            if data_json:
                item['img'] = data_json.get('thumbnailUrl', '')
                item['plot'] = data_json.   get('description', '')
            self._filter(result, item)
        result.sort(key=lambda x:int(x['date']), reverse=True)
        item = self.dir_item()
        item['type'] = 'prev'
        item['url'] = prev_url
        self._filter(result, item)
        return result

    def list_episode(self, page):
        item = self.video_item()
        episode = re.search(EPISODE_RE, page, re.DOTALL)
        if episode:
            item['title'] = to_unicode(episode.group('title').strip())
            if episode.group('plot'):
                item['plot'] = to_unicode(episode.group('plot').strip())
        return item

    def resolve(self, item, captcha_cb=None, select_cb=None):
        result = []
        self.info(' == resolve ==')
        self.info ( item )

        _item = item
        item = item.copy()
        if item['url'].startswith('live.'):
            channel_id = item['url'].split('.')[1]
            data = util.request(f"{HOST}/json/live5f.json?c=%s&b=mozilla&p=linux&v=47&f=1&d=1"%(channel_id))
            videodata = util.json.loads(data)['clip']
            url = videodata['sources'][0]['src']
            url = ''.join(url.split()) # remove whitespace \n from URL
            #process m3u8 playlist
            for stream in get_streams_from_manifest_url(url):
                item = self.video_item()
                item['title'] = videodata.get('title','')
                item['url'] = stream['url']
                item['quality'] = stream['quality']
                # item['img'] = videodata.get('image','')
                item['img'] = videodata.get('image', _item.get('img', ''))
                result.append(item)

        elif item['url'].find('/player/') != -1:
            if '/' == item['url'][-1]:
                _url = item['url'][:-1]
            else:
                _url = item['url']
            _url = _url.replace('.rtvs', '.stvr')
            data = util.request('https:' + _url)
            url = re.search('src: "(?P<url>[^\"]+)', data, re.IGNORECASE | re.DOTALL).group('url')
            item['url'] = url
            item['type'] = 'audio/mp3'
            result.append(item)
        
        elif item['url'].find('/embed/audio/') != -1:
                audio_id = item['url'].split('/')[-1]
                # item['url'] = 'http://www.rtvs.sk/json/audio5f.json?id=' + url
                audiodata = util.json.loads(util.request(f"{HOST}/json/audio5f.json?id=" + audio_id))
                for v in audiodata['playlist'][0]['sources']:
                    url =  v['src']
                    if '.mp3' in url:                    
                        item['title'] = audiodata.get('title','')
                        item['surl'] = item['title']
                        item['url'] = url
                        item['type'] = v['type']
                        result.append(item)


        elif item['url'].find('/radio/') != -1:
            audio_id = item['url'].split('/')[-1]
            audio_id0 = item['url'].split('/')[-2]
            self.info("<resolve> audioid: %s" % audio_id)
            embed_data = util.request(f"{HOST}/embed/radio/archive/%s/%s"%(audio_id0, audio_id))
            audio_id = re.search('audio5f\.json\?id=(?P<id>[^\"]+)', embed_data, re.IGNORECASE | re.DOTALL).group('id')
            audiodata = util.json.loads(util.request(f"{HOST}/json/audio5f.json?id=" + audio_id))
            for v in audiodata['playlist'][0]['sources']:
                url =  v['src']
                if '.mp3' in url:                    
                    item['title'] = audiodata.get('title','')
                    item['surl'] = item['title']
                    item['url'] = url
                    item['type'] = v['type']
                    result.append(item)
                    # self.info(item)
        else:
            video_id = item['url'].split('/')[-1]
            self.info("<resolve> videoid: %s" % video_id)
            videodata = util.json.loads(util.request(f"{HOST}/json/archive5f.json?id=" + video_id))
            for v in videodata['clip']['sources']:
                url =  v['src']
                if '.m3u8' in url:
                    #process m3u8 playlist
                    for stream in get_streams_from_manifest_url(url):
                        item = self.video_item()
                        item['title'] = videodata.get('title','')
                        item['surl'] = item['title']
                        item['url'] = stream['url']
                        item['quality'] = stream['quality']
                        result.append(item)

        self.info("<resolve> playlist: %d items" % len(result))
        map(self.info, ["<resolve> item(%d): title= '%s', url= '%s'" % (i, it['title'], it['url']) for i, it in enumerate(result)])
        if len(result) > 0 and select_cb:
            return select_cb(result)
        return result

    def _request_parallel(self, requests):
        def fetch(req, *args):
            return util.request(req), args
        pages = []
        q = util.run_parallel_in_threads(fetch, requests)
        while True:
            try:
                page, args = q.get_nowait()
            except:
                break
            pages.append([page, args])
        return pages

  
