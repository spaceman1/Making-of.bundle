import re

PLUGIN_PREFIX = "/video/MakingOf"
ROOT = "http://www.makingof.com"
VAULT_BASE = ROOT + '/vault/feature'
FILMING_NOW_BASE = ROOT + '/filming_now/feature'

CACHE_TIME = 86400
insiders = [
  ['Actors', 'http://makingof.com/insiders/department/actor/34'],
  ['ADR Supervisors', 'http://makingof.com/insiders/department/adr-supervisor/50'],
  ['Art Directors', 'http://makingof.com/insiders/department/art-director/40'],
  ['Camera/Electrical', 'http://makingof.com/insiders/department/camera-elect-dept/3'],
  ['Casting Directors', 'http://makingof.com/insiders/department/casting-director/46'],
  ['Cinematographers', 'http://makingof.com/insiders/department/cinematographer/37'],
  ['Composers', 'http://makingof.com/insiders/department/composer/43'],
  ['Costume Designers', 'http://makingof.com/insiders/department/costume-designer/44'],
  ['Directors', 'http://makingof.com/insiders/department/director/35'],
  ['Editors', 'http://makingof.com/insiders/department/editor/38'],
  ['Producers', 'http://makingof.com/insiders/department/producer/41'],
  ['Screenwriters', 'http://makingof.com/insiders/department/screenwriter/39'],
  ['Special Effects/vfx', 'http://makingof.com/insiders/department/special-effects-vfx/5'],
  ['Stunts', 'http://makingof.com/insiders/department/stunts/4'] ]

sections = [
  ['Interviews', '/interview/1'],
  ['Movie Clips', '/movie-clip/3'],
  ['On Set', '/on-set/6'],
  ['Trailers', '/trailer/2'] ]
####################################################################################################
def Start():
  Plugin.AddPrefixHandler(PLUGIN_PREFIX, MainMenu, "Making Of", "icon-default.png", "art-default.png")
  Plugin.AddViewGroup("Details", viewMode="InfoList", mediaType="items")
  Plugin.AddViewGroup("List", viewMode="List", mediaType="items")
  MediaContainer.title1 = L('Making Of')
  MediaContainer.viewGroup = 'List'
  MediaContainer.art = R('art-default.png')
  DirectoryItem.thumb = R('icon-default.png')
  HTTP.SetCacheTime(CACHE_TIME)
####################################################################################################
def MainMenu():
  dir = MediaContainer()
  dir.Append(Function(DirectoryItem(SectionMenu, title='Filming Now'), url=FILMING_NOW_BASE))
  dir.Append(Function(DirectoryItem(InsidersMenu, title='Insiders')))
  dir.Append(Function(DirectoryItem(SectionMenu, title='The Vault'), url=VAULT_BASE))
  return dir

def InsidersMenu(sender):
  dir = MediaContainer(title2=sender.itemTitle)
  for (name, link) in insiders:
    dir.Append(Function(DirectoryItem(VideosMenu, title=name), url=link))
  return dir

def SectionMenu(sender, url):
  dir = MediaContainer(title2=sender.itemTitle)
  for (name, link) in sections:
    dir.Append(Function(DirectoryItem(VideosMenu, title=name), url=url + link))
  return dir

def VideosMenu(sender, url):
  dir = MediaContainer(title2=sender.itemTitle, viewGroup='Details')
  page = HTML.ElementFromURL(url)
  try:
    pageCount = int(page.xpath('//span[@class="current"]')[0].text.split(' ')[-1])
  except:
    pageCount = 1
  Log('Page count :' + str(pageCount))
  
  for pageNum in range(1, pageCount + 1):
    if pageNum != 1:
      page = HTML.ElementFromURL(url + '?page=' + str(pageNum))
    for tr in page.xpath('//table[@class="insiders_table table"]/tbody/tr'):
      thumb = ROOT + tr.xpath('child::td[@class="exclusive"]/a/img')[0].get('src')
      link = tr.xpath('child::td[@class="title"]/span[@class="hdr"]/a')[0]
      title = link.text
      href = link.get('href')
      summary = tr.xpath('child::td[@class="title"]/span[2]')[0].text
      subtitle = tr.xpath('child::td[@class="updated"]')[0].text
      dir.Append(Function(DirectoryItem(VideoMenu, title=title, thumb=thumb, summary=summary, subtitle=subtitle), url=href, thumb=thumb, summary=summary, subtitle=subtitle))
  return dir

def VideoMenu(sender, url, thumb, summary, subtitle):
  dir = MediaContainer(title2=sender.itemTitle, viewGroup='Details')
  script = HTML.ElementFromURL(url).xpath('//div[starts-with(@id,"media_viewer")]/script')[0].get('src')
  xmlURL = re.search(r"([^']*\.xml)", script).group(1)
  xmlPage = GetFixedXML(ROOT + xmlURL, False)
  rtmpURL = xmlPage.xpath('/media_post/fms_url')[0].text + '/' + xmlPage.xpath('/media_post/stream_url')[0].text
  Log(rtmpURL)
  dir.Append(VideoItem(rtmpURL, title=sender.itemTitle, thumb=thumb, summary=summary, subtitle=subtitle))
  return dir
