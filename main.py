import flet as ft
import yt_dlp
from download_support import DownloadCancelled, DownloadLog, runtime_options
import threading
import queue
import asyncio
import os
import subprocess
import tkinter as tk
from tkinter import filedialog
import pyperclip 
import glob
import ctypes
import locale
import random
import string

# ==========================================
# Localization Data (i18n)
# ==========================================
I18N = {
    '简体中文': {
        'title': 'ParrMotion 下载器', 'paste_hint': '在此粘贴视频链接...',
        'quality_label': '优先下载画质', 'q_auto': '最高画质 (自动)', 'q_audio': '音频 (MP3)',
        'btn_start': '开始下载', 'sidebar_title': ' ParrMotion', 'save_loc': '保存位置',
        'btn_change': '更改', 'q_pref': '画质偏好', 'support_sites': '支持网站',
        'history': '下载记录', 'history_title': '下载记录管理', 'search_title': '支持网站查询',
        'search_hint': '输入网站名称...', 'search_empty': '💡 输入关键词搜索全量支持库 (如: bili)',
        'search_found': '✅ 已找到 {} 个匹配站点：', 'search_not_found': '❌ 列表中暂无 \'{}\'，但仍可尝试',
        'status_paused': '⏸️ 已暂停', 'status_resume': '▶️ 继续下载...', 'status_stop': '🛑 正在清理并停止...',
        'status_parsing': '⏳ 解析中...', 'status_merging': '⏳ 合并中 (较慢)...',
        'status_success': '🎉 下载成功！', 'status_stopped': '已停止', 'speed': '速度',
        'tooltip_clear': '清空', 'tooltip_paste': '粘贴并下载',
        'limit_label': '下载限速 (0或留空为无限制)'
    },
    '繁體中文': {
        'title': 'ParrMotion 下載器', 'paste_hint': '在此貼上影片連結...',
        'quality_label': '優先下載畫質', 'q_auto': '最高畫質 (自動)', 'q_audio': '音訊 (MP3)',
        'btn_start': '開始下載', 'sidebar_title': ' ParrMotion', 'save_loc': '儲存位置',
        'btn_change': '更改', 'q_pref': '畫質偏好', 'support_sites': '支援網站',
        'history': '下載紀錄', 'history_title': '下載紀錄管理', 'search_title': '支援網站查詢',
        'search_hint': '輸入網站名稱...', 'search_empty': '💡 輸入關鍵字搜尋全量支援庫 (如: bili)',
        'search_found': '✅ 已找到 {} 個匹配站點：', 'search_not_found': '❌ 列表中暫無 \'{}\'，但仍可嘗試',
        'status_paused': '⏸️ 已暫停', 'status_resume': '▶️ 繼續下載...', 'status_stop': '🛑 正在清理並停止...',
        'status_parsing': '⏳ 解析中...', 'status_merging': '⏳ 合併中 (較慢)...',
        'status_success': '🎉 下載成功！', 'status_stopped': '已停止', 'speed': '速度',
        'tooltip_clear': '清空', 'tooltip_paste': '貼上並下載',
        'limit_label': '下載限速 (0或留空為無限制)'
    },
    '한국어': {
        'title': 'ParrMotion 다운로더', 'paste_hint': '여기에 비디오 링크를 붙여넣으세요...',
        'quality_label': '우선 다운로드 화질', 'q_auto': '최고 화질 (자동)', 'q_audio': '오디오 (MP3)',
        'btn_start': '다운로드 시작', 'sidebar_title': ' ParrMotion', 'save_loc': '저장 위치',
        'btn_change': '변경', 'q_pref': '화질 선호', 'support_sites': '지원 웹사이트',
        'history': '다운로드 기록', 'history_title': '다운로드 기록 관리', 'search_title': '지원 웹사이트 검색',
        'search_hint': '웹사이트 이름 입력...', 'search_empty': '💡 키워드를 입력하여 지원 사이트 검색 (예: bili)',
        'search_found': '✅ {}개의 일치하는 사이트 찾음:', 'search_not_found': '❌ 목록에 \'{}\'이(가) 없지만 시도 가능',
        'status_paused': '⏸️ 일시 정지됨', 'status_resume': '▶️ 다운로드 재개...', 'status_stop': '🛑 정리 및 중지 중...',
        'status_parsing': '⏳ 분석 중...', 'status_merging': '⏳ 병합 중 (느림)...',
        'status_success': '🎉 다운로드 성공!', 'status_stopped': '중지됨', 'speed': '속도',
        'tooltip_clear': '지우기', 'tooltip_paste': '붙여넣기 및 다운로드',
        'limit_label': '속도 제한 (0/공백: 무제한)'
    },
    '日本語': {
        'title': 'ParrMotion ダウンローダー', 'paste_hint': 'ここに動画のリンクを貼り付けてください...',
        'quality_label': '優先ダウンロード画質', 'q_auto': '最高画質 (自動)', 'q_audio': '音声 (MP3)',
        'btn_start': 'ダウンロード開始', 'sidebar_title': ' ParrMotion', 'save_loc': '保存先',
        'btn_change': '変更', 'q_pref': '画質設定', 'support_sites': '対応サイト',
        'history': 'ダウンロード履歴', 'history_title': '履歴の管理', 'search_title': '対応サイト検索',
        'search_hint': 'サイト名を入力...', 'search_empty': '💡 キーワードを入力して検索 (例: bili)',
        'search_found': '✅ {} 個のサイトが見つかりました：', 'search_not_found': '❌ リストに「{}」はありませんが、試すことは可能です',
        'status_paused': '⏸️ 一時停止中', 'status_resume': '▶️ ダウンロード再開...', 'status_stop': '🛑 クリーンアップと停止中...',
        'status_parsing': '⏳ 解析中...', 'status_merging': '⏳ 結合中 (少し時間がかかります)...',
        'status_success': '🎉 ダウンロード成功！', 'status_stopped': '停止しました', 'speed': '速度',
        'tooltip_clear': 'クリア', 'tooltip_paste': '貼り付けてダウンロード',
        'limit_label': '速度制限 (0 または 空白 で無制限)'
    },
    'English': {
        'title': 'ParrMotion Downloader', 'paste_hint': 'Paste video link here...',
        'quality_label': 'Preferred Quality', 'q_auto': 'Highest Quality (Auto)', 'q_audio': 'Audio (MP3)',
        'btn_start': 'Start Download', 'sidebar_title': ' ParrMotion', 'save_loc': 'Save Location',
        'btn_change': 'Change', 'q_pref': 'Quality Preference', 'support_sites': 'Supported Sites',
        'history': 'Download History', 'history_title': 'History Management', 'search_title': 'Supported Sites',
        'search_hint': 'Enter site name...', 'search_empty': '💡 Enter keyword to search sites (e.g. bili)',
        'search_found': '✅ Found {} matching sites:', 'search_not_found': '❌ \'{}\' not in list, but still tryable',
        'status_paused': '⏸️ Paused', 'status_resume': '▶️ Resuming...', 'status_stop': '🛑 Cleaning and stopping...',
        'status_parsing': '⏳ Parsing...', 'status_merging': '⏳ Merging (slower)...',
        'status_success': '🎉 Download Successful!', 'status_stopped': 'Stopped', 'speed': 'Speed',
        'tooltip_clear': 'Clear', 'tooltip_paste': 'Paste & Download',
        'limit_label': 'Speed Limit (0/blank = unlmt)'
    }
}

def get_init_lang():
    try:
        lang_id = ctypes.windll.kernel32.GetUserDefaultUILanguage()
        loc = locale.windows_locale.get(lang_id, '').lower()
        if 'zh_cn' in loc: return '简体中文'
        if 'zh_tw' in loc or 'zh_hk' in loc: return '繁體中文'
        if 'ja' in loc: return '日本語'
        if 'ko' in loc: return '한국어'
    except: pass
    return 'English'

def format_bytes(bytes_num):
    if not bytes_num: return "0 B"
    try: bytes_num = float(bytes_num)
    except: return "0 B"
    for x in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_num < 1024.0: return f"{bytes_num:.2f} {x}"
        bytes_num /= 1024.0
    return "0 B"

def main(page: ft.Page):
    download_log = DownloadLog()
    current_lang = get_init_lang()
    t_ptr = [I18N[current_lang]] 

    # --- UI Initialization ---
    page.theme_mode = ft.ThemeMode.LIGHT
    page.title = t_ptr[0]['title']
    page.window_width = 1000
    page.window_height = 750
    page.padding = 0 

    # --- Supported Extractors List ---
    raw_sites = """10play, 17live, 1News, 1tv, 23video, 24tv.ua, 3qsdn, 3sat, 4tube, 56.com, 7plus, 8tracks, 9c9media, 9gag, 9News, 9now.com.au, abc.net.au, abcnews, abcotvs, AbemaTV, AcFunBangumi, AcFunVideo, ADN, ADNSeason, AdobeConnect, adobetv, AdultSwim, aenetworks, AeonCo, agalega, AirTV, AitubeKZVideo, Alibaba, AliExpressLive, AlJazeera, Allocine, Allstar, AllstarProfile, AlphaPorno, Alsace20TV, altcensored, Alura, AmadeusTV, Amara, AmazonMiniTV, AmazonReviews, AmazonStore, AMCNetworks, AmericasTestKitchen, AmHistoryChannel, AnchorFMEpisode, anderetijden, Angel, AnimalPlanet, ant1newsgr, antenna, Anvato, APA, Aparat, apple:music, ApplePodcasts, appletrailers, archive.org, ArcPublishing, ARD, ARDAudiothek, ARDMediathek, Art19, ArteTV, asobichannel, AsobiStage, AtresPlayer, AtScaleConfEvent, ATVAt, AudiMedia, AudioBoom, Audiodraft, audiomack, Audius, AWAAN, axs.tv, AZMedien, BaiduVideo, BanBye, Bandcamp, Bandlab, BannedVideo, bbc, bbc.co.uk, BBVTV, BeaconTv, BeatBump, Beatport, Beeg, BerufeTV, Bet, bfmtv, bibeltv, Bigflix, Bigo, Bild, BiliBili, BilibiliAudio, BiliBiliBangumi, BilibiliCheese, BilibiliCollectionList, BiliBiliDynamic, BilibiliFavoritesList, BiliBiliPlayer, BilibiliPlaylist, BiliBiliSearch, BilibiliSeriesList, BilibiliSpaceAudio, BilibiliSpaceVideo, BilibiliWatchlater, BiliIntl, BiliLive, BioBioChileTV, Biography, BitChute, Bitmovin, BlackboardCollaborate, blerp, Blob, blogger.com, Bloomberg, Bluesky, BokeCC, BongaCams, Boosty, BostonGlobe, Box, BoxCastVideo, Bpb, BrainPOP, BravoTV, BreitBart, brightcove, Brilliantpala, BTVPlus, Bundesliga, Bundestag, BunnyCdn, BusinessInsider, BuzzFeed, CaffeineTV, Callin, Caltrans, CAM4, Camdemy, CamFM, CamModels, Camsoda, CamtasiaEmbed, Canal1, CanalAlpha, canalc2.tv, Canalplus, Canalsurmas, CaracolTvPlay, cbc.ca, CBSLocal, cbsnews, CCMA, CCTV, CDA, CDAFolder, Cellebrite, CeskaTelevize, CGTN, CharlieRose, Chaturbate, Chilloutzone, chzzk, cielotv.it, CinetecaMilano, Cineverse, CiscoLive, ciscowebex, CJSW, Clipchamp, Clippit, CloudflareStream, CloudyCDN, Clyp, CNBCVideo, CNN, CNNIndonesia, ComedyCentral, CommonMistakes, CondeNast, CONtv, CookingChannel, Corus, Coub, CozyTV, cp24, cpac, Cracked, Craftsy, croatian.film, CrooksAndLiars, CrowdBunker, Crtvg, CSpan, CSpanCongress, CtsNews, CTVNews, cu.ntv.co.jp, CultureUnplugged, curiositystream, Cybrary, Dacast, DagelijkseKost, DailyMail, dailymotion, DailyWire, damtomo, dangalplay, daum.net, daystar, DBTV, DctpTv, democraciesnow, DestinationAmerica, DetikEmbed, DeuxM, DigitalConcertHall, DigitallySpeaking, Digiteka, Digiview, DiscogsReleasePlaylist, DiscoveryLife, DiscoveryPlus, DiscoveryPlusIndia, DiscoveryPlusItaly, Disney, dlf, dlive, Douyin, DouyuShow, DouyuTV, DPlay, DRBonanza, DRM, Drooble, Dropbox, Dropout, DrTalks, DrTuber, drtv, duboku, Dumpert, Duoplay, dvtv, dzen.ru, EbaumsWorld, Ebay, egghead, eggs, EinsUndEinsTV, eitb.tv, ElementorEmbed, Elonet, ElPais, ElTreceTV, Embedly, EMPFlix, Epicon, EpidemicSound, eplus, Epoch, Eporner, Erocast, EroProfile, ERRArhiiv, ERRJupiter, ertflix, ESPN, ESPNArticle, ESPNCricInfo, EttuTv, EuroParlWebstream, EuropeanTour, Eurosport, EUScreen, EWETV, Expressen, EyedoTV, facebook, Fathom, Faulio, faz.net, fc2, Fczenit, Fifa, FilmArchiv, filmon, Filmweb, FiveThirtyEight, FiveTV, Flickr, Floatplane, Folketinget, FoodNetwork, FootyRoom, Formula1, FOX, foxnews, FoxSports, fptplay, FrancaisFacile, FranceCulture, franceinfo, FranceInter, francetv, Freesound, freespeech.org, freetv, FreeTvMovies, FrontendMasters, FujiTVFODPlus7, Funk, Funker530, Fux, FuyinTV, Gab, Gaia, GameDevTVDashboard, GameJolt, GameSpot, GameStar, Gaskrank, GBNews, GediDigital, gem.cbc.ca, Genius, Germanupa, GetCourseRu, Gettr, GiantBomb, GlattvisionTV, Glide, GlobalPlayer, Globo, glomex, GMANetworkVideo, Go, GoDiscovery, GodResource, Gofile, Golem, goodgame, GoogleDrive, GoPro, Goshgay, GoToStage, GPUTechConf, Graspop, Gronkh, Groupon, Harpodeon, hbo, HearThisAt, Heise, HellPorno, hetklokhuis, HGTV, HiDive, HistoricFilms, history, HitRecord, hketv, HollywoodReporter, Holodex, hotstar, href.li, hrfernsehen, HRTi, HSEProduct, HSEShow, html5, Huajiao, HuffPost, Hungama, huya, Hypem, Hytale, Icareus, Idagio, IdolPlus, iflix, ign.com, iheartradio, IlPost, Iltalehti, imdb, Imgur, Ina, Inc, InfoQ, Instagram, InstagramIOS, Internazionale, InternetVideoArchive, InvestigationDiscovery, IPrima, iq.com, iqiyi, IslamChannel, IsraelNationalNews, ITProTV, ITV, ivi, ivideon, Ivoox, IVXPlayer, iwara, Ixigua, Izlesene, Jamendo, Joj, Jove, JStream, JTBC, JWPlatform, Kakao, Kaltura, Karaoketv, Kenh14, khanacademy, kick, Kicker, KickStarter, Kika, KinoPoisk, Kommunetv, KompasVideo, KTH, Ku6, KukuluLive, la7.it, laracasts, LastFM, LaXarxaMes, lbry, LCI, Le, LearningOnScreen, Lecturio, LeFigaro, LEGO, Lemonde, LePlaylist, LetvCloud, Libsyn, life, likee, LinkedIn, Liputan6, ListenNotes, LiTV, livestream, Livestreamfails, Lnk, loc, Loco, loom, LoveHomePorn, LRT, LSMLR, LSMReplay, Lumni, lynda, maariv.co.il, MagellanTV, MagentaMusik, mailru, MainStreaming, mangomolo, MangoTV, ManyVids, MaoriTV, massengeschmack.tv, Masters, MatchTV, mave, MBN, MDR, MedalTV, media.ccc.de, Mediaite, MediaKlikk, Medialaan, Mediaset, Mediasite, MediaStream, MediaWorksNZVOD, Medici, megaphone.fm, megatvcom, Meipai, MelonVOD, Metacritic, mewatch, MicrosoftBuild, MicrosoftEmbed, MicrosoftLearn, MicrosoftMedius, microsoftstream, minds, Minoto, mir24.tv, mirrativ, MirrorCoUK, mixch, mixcloud, Mixlr, MLB, MLSSoccer, Mms, MNetTV, MochaVideo, Mojevideo, Mojvideo, Monstercat, monstersiren, Motherless, moviepilot, MoviewPlay, Moviezine, MovingImage, MSN, mtg, mtv, MujRozhlas, Murrtube, MuseAI, MuseScore, MusicdexAlbum, MusicdexArtist, MusicdexPlaylist, MusicdexSong, Mux, Mx3, Mxplayer, MySpace, MySpass, MyVideoGe, MyVidster, Mzaalo, n-tv.de, N1Info, NascarClassics, Nate, natgeo, Naver, navernow, NBC, NBCNews, nbcolympics, NBCStations, ndr, nebula, NekoHacker, NerdCubedFeed, Nest, NetAppCollection, NetAppVideo, netease, NetPlusTV, Netverse, Netzkino, Newgrounds, NewsPicks, Newsy, Nexx, nfb, NFHSNetwork, nfl.com, NhkForSchool, NhkRadioNewsPage, NhkRadiru, NhkVod, nhl.com, nick.com, niconico, NiconicoChannelPlus, NiconicoUser, NinaProtocol, Nintendo, Nitter, njoy, NobelPrize, NoicePodcast, NonkTube, NoodleMagazine, NOSNLArticle, Nova, NowCanal, nowness, npo, Npr, NRK, NRKRadioPodkast, NRKSkole, NRKTV, nts.live, ntv.ru, NubilesPorn, nuum, Nuvid, NYTimes, nzherald, NZOnScreen, NZZ, ocw.mit.edu, Odnoklassniki, OfTV, OktoberfestTV, OlympicsReplay, on24, OnDemandChinaEpisode, OnDemandKorea, OneFootball, OnePlacePodcast, onet.pl, OnetMVP, OnionStudios, onsen, Opencast, openrec, OraTV, orf, OsnatelTV, OutsideTV, OwnCloud, PacktPub, PalcoMP3, PandaTv, Panopto, ParamountPressExpress, Parler, parliamentlive.tv, Parlview, parti, patreon, pbs, PBSKids, PearVideo, PeekVids, peer.tv, PeerTube, peloton, PerformGroup, periscope, PGATour, PhilharmonieDeParis, phoenix.de, Photobucket, PiaLive, Piapro, picarto, Piksel, Pinkbike, Pinterest, Piracy, PiramideTV, PlanetMarathi, Platzi, play.tv, player.sky.it, PlayerFm, playeur, PlayPlusTV, PlaySuisse, Playtvak, PlayVids, Playwire, pluralsight, PlVideo, PlyrEmbed, PodbayFM, Podchaser, PokerGo, PolsatGo, PolskieRadio, Popcorntimes, PopcornTV, Pornbox, PornerBros, PornFlip, PornHub, Pornotube, PornTop, PornTube, Pr0gramm, PrankCast, PremiershipRugby, PressTV, prosiebensat1, PRX, puhutv, Puls4, Pyvideo, QDance, QingTing, qqmusic, QuantumTV, Radiko, Radio1Be, radiocanada, RadioComercial, radiofrance, radiokapital, RadioRadicale, RadioZetPodcast, radlive, Rai, RayWenderlich, RbgTum, RCS, RCTIPlus, RedBull, redcdnlivx, Reddit, RedGifs, RedTube, ReverbNation, RheinMainTV, RideHome, RinseFM, RMCDecouverte, Rokfin, RoosterTeeth, RottenTomatoes, RoyaLive, Rozhlas, RTDocumentry, rte, rtl, rtl2, RTLLu, Rtmp, RTNews, RTP, RTRFM, RTVC, rtve.es, rtvslo.si, RudoVideo, Rule34Video, Rumble, Ruptly, rutube, Ruv, S4C, safari, SAKTV, SaltTV, SampleFocus, Sangiin, Sapo, SaucePlus, SBS, sbs.co.kr, schooltv, ScienceChannel, Screen9, Screencast, ScreenRec, ScrippsNetworks, Scrolller, sejm, Sen, senate.gov, Servus, SeznamZpravy, Shahid, SharePoint, ShareVideosEmbed, ShemarooMe, Shiey, ShowRoomLive, ShugiinItv, SibnetEmbed, simplecast, Sina, Skeb, sky.it, sky:news, sky:sports, SkyNewsAU, Slideshare, SlidesLive, Slutload, smotrim, southpark, SovietsCloset, SpankBang, Spiegel, Sport5, Spreaker, SpringboardPlatform, SproutVideo, sr:mediathek, SRGSSR, Stacommu, StagePlusVODConcert, stanfordoc, startrek, startv, Steam, Stitcher, StoryFire, Streaks, Streamable, StreamCZ, StreetVoice, StretchInternet, Stripchat, stv, stvr, Subsplash, Substack, SunPorno, sverigesradio, svt, SwearnetEpisode, Syfy, SYVDK, SztvHu, TapTapApp, tarangplus, TBS, TBSJP, Teamcoco, TeamTreeHouse, techtv.mit.edu, TedEmbed, TedPlaylist, TedSeries, TedTalk, Tele13, Tele5, TeleBruxelles, TelecaribePlay, Telecinco, Telegraaf, telegram:embed, TeleQuebec, Tempo, TennisTV, TestURL, TF1, theatercomplextown, TheChosen, TheGuardianPodcast, TheHighWire, TheHoleTv, TheIntercept, ThePlatform, TheStar, TheSun, TheWeatherChannel, ThisAmericanLife, ThisOldHouse, ThisVid, ThreeSpeak, TikTok, TLC, TMZ, TNAFlix, toggo, tokfm, ToonGoggles, tou.tv, toutiao, TravelChannel, Triller, Trovo, TrtCocukVideo, TrtWorld, TrueID, TruNews, Truth, ttinglive, TubeTuGraz, tubitv, Tumblr, tunein, tv.dfb.de, TV2, TV2DK, tv2play, TV4, TV5MONDE, tv5unis, tv8.it, TVANouvelles, tvaplus, TVC, TVer, tvigle, TVIPlayer, tvnoe, tvopengr, tvp, TVPlayer, TVPlayHome, tvw, Tweakers, TwitCasting, twitch, twitter, Txxx, udemy, UDNEmbed, UFCArabia, UFCTV, UKTVPlay, Uliza, umg:de, Unistra, UnitedNationsWebTv, uol.com.br, uplynk, URPlay, USANetwork, USAToday, ustream, ustudio, Vbox7, Veo, Vevo, VGTV, vh1.com, vhx, Videa, video.arnes.si, video.google, video.sky.it, VideoDetective, VideoKen, videomore, VideoPress, Vidflex, Vidio, VidLii, Vidly, vids.io, Vidyard, viewlift, Viidea, vimeo, Vimm, ViMP, Viously, Viu, viu:ott, ViuOTTIndonesia, vk, VKPlay, Vocaroo, VODPl, VODPlatform, volejtv, VoxMedia, vpro, vqq, vrsquare, VRT, vrtmax, VTM, VTV, VTVGo, VTXTV, VuClip, VVVVID, Walla, WalyTV, washingtonpost, wat.tv, WatchESPN, WDR, WDRElefant, WDRPage, Webcamerapl, Webcaster, WebOfStories, Weibo, WeVidi, Weyyak, whowatch, Whyp, wikimedia.org, Wimbledon, WimTV, WinSportsVideo, Wistia, wnl, wordpress, WorldStarHipHop, wppilot, WrestleUniverse, WSJ, WWE, wyborcza, WyborczaPodcast, wykop, XboxClips, XHamster, XiaoHongShu, ximalaya, Xinpianchang, XNXX, Xstream, XVideos, XXXYMovies, yahoo, YandexDisk, yandexmusic, YandexVideo, Yappy, yfanefa, YleAreena, YouJizz, youku, YouNow, YouPorn, youtube, Zaiko, Zapiks, Zattoo, zdf, Zee5, ZenPorn, ZetlandDKArticle, Zhihu, zingmp3, zoom, Zype"""
    all_extractors = sorted(list(set([s.strip() for s in raw_sites.replace('\n', '').split(',') if s.strip()])))

    # --- Component Declaration ---
    main_title = ft.Text(size=32, weight="bold")
    side_title = ft.Text(size=24, weight="bold", color=ft.Colors.BLUE_800)
    save_loc_text = ft.Text("")
    
    btn_change = ft.ElevatedButton(content=ft.Text("..."), height=30)
    q_pref_text = ft.Text("")
    
    limit_label_text = ft.Text("")
    limit_input = ft.TextField(value="0", width=80, height=35, text_size=12, content_padding=5)
    limit_row = ft.Row([limit_input, ft.Text("MB/s", size=12)])
    
    url_input = ft.TextField(expand=True, border_radius=12, prefix_icon=ft.Icons.LINK)
    progress_bar = ft.ProgressBar(width=450, value=0, visible=False, color="blue")
    progress_percent = ft.Text("", size=12, weight="bold")
    progress_size = ft.Text("", size=12, color=ft.Colors.BLUE_GREY_400) 
    status_text = ft.Text("", size=14, weight="bold", selectable=True)
    history_list = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True, spacing=10)
    
    quality_dropdown = ft.Dropdown()

    search_title_ui = ft.Text("", weight="bold", size=20)
    search_input_ui = ft.TextField()
    history_title_ui = ft.Text("", weight="bold", size=22)

    search_tile = ft.ListTile(leading=ft.Icon(ft.Icons.SEARCH), title=ft.Text(""))
    history_tile = ft.ListTile(leading=ft.Icon(ft.Icons.HISTORY), title=ft.Text(""))

    clear_btn = ft.IconButton(icon=ft.Icons.DELETE_SWEEP, icon_color="red")
    paste_btn = ft.IconButton(icon=ft.Icons.PASTE_ROUNDED, icon_color="blue", icon_size=30)
    action_btns = ft.Row([clear_btn, paste_btn])

    lang_display = ft.Text(size=13, weight="bold", color=ft.Colors.BLUE_800)

    # --- Theme Toggle ---
    def toggle_theme(e):
        if page.theme_mode == ft.ThemeMode.LIGHT:
            page.theme_mode = ft.ThemeMode.DARK
            theme_btn.icon = ft.Icons.LIGHT_MODE
            sidebar.bgcolor = ft.Colors.BLUE_GREY_900
            lang_overlay.bgcolor = ft.Colors.BLUE_GREY_900
            support_overlay_content.bgcolor = ft.Colors.BLUE_GREY_900
            history_overlay_content.bgcolor = ft.Colors.BLUE_GREY_900
        else:
            page.theme_mode = ft.ThemeMode.LIGHT
            theme_btn.icon = ft.Icons.DARK_MODE
            sidebar.bgcolor = ft.Colors.BLUE_GREY_50
            lang_overlay.bgcolor = ft.Colors.WHITE
            support_overlay_content.bgcolor = ft.Colors.WHITE
            history_overlay_content.bgcolor = ft.Colors.WHITE
        page.update()
    
    theme_btn = ft.IconButton(icon=ft.Icons.DARK_MODE, on_click=toggle_theme, tooltip="Dark/Light Mode")

    def update_ui_text():
        t = t_ptr[0]
        page.title = t['title']
        main_title.value = t['title']
        url_input.label = t['paste_hint']
        
        old_val = quality_dropdown.value
        quality_dropdown.label = t['quality_label']
        quality_dropdown.options = [
            ft.dropdown.Option(key="auto", text=t['q_auto']),
            ft.dropdown.Option(key="4k", text="4K (2160p)"),
            ft.dropdown.Option(key="2k", text="2K (1440p)"),
            ft.dropdown.Option(key="1080p", text="1080p"),
            ft.dropdown.Option(key="720p", text="720p"),
            ft.dropdown.Option(key="480p", text="480p"),
            ft.dropdown.Option(key="360p", text="360p"),
            ft.dropdown.Option(key="240p", text="240p"),
            ft.dropdown.Option(key="144p", text="144p"),
            ft.dropdown.Option(key="audio", text=t['q_audio'])
        ]
        quality_dropdown.value = old_val if old_val else "auto"

        download_btn.content.value = t['btn_start']
        btn_change.content.value = t['btn_change']
        
        side_title.value = t['sidebar_title']
        save_loc_text.value = t['save_loc']
        q_pref_text.value = t['q_pref']
        limit_label_text.value = t['limit_label'] 
        
        search_tile.title.value = t['support_sites']
        history_tile.title.value = t['history']
        
        search_title_ui.value = t['search_title']
        search_input_ui.label = t['search_hint']
        history_title_ui.value = t['history_title']
        
        clear_btn.tooltip = t['tooltip_clear']
        paste_btn.tooltip = t['tooltip_paste']
        
        lang_display.value = f"🌐 {current_lang_ptr[0]}"
        on_search(None) 
        page.update()

    current_lang_ptr = [current_lang]
    def set_lang(lang_str):
        current_lang_ptr[0] = lang_str
        t_ptr[0] = I18N[lang_str]
        lang_overlay.visible = False
        update_ui_text()

    lang_overlay = ft.Container(
        visible=False, bgcolor=ft.Colors.WHITE, border=ft.border.all(1, "black12"), border_radius=10, padding=10,
        content=ft.Column([
            ft.TextButton(content=ft.Text("简体中文"), on_click=lambda _: set_lang("简体中文")),
            ft.TextButton(content=ft.Text("繁體中文"), on_click=lambda _: set_lang("繁體中文")),
            ft.TextButton(content=ft.Text("日本語"), on_click=lambda _: set_lang("日本語")),
            ft.TextButton(content=ft.Text("한국어"), on_click=lambda _: set_lang("한국어")),
            ft.TextButton(content=ft.Text("English"), on_click=lambda _: set_lang("English")),
        ], tight=True),
        left=20, bottom=110
    )

    lang_selector_btn = ft.Container(
        content=ft.Row([lang_display, ft.Icon(ft.Icons.LANGUAGE, size=16, color=ft.Colors.BLUE_800)]),
        on_click=lambda _: [setattr(lang_overlay, 'visible', not lang_overlay.visible), page.update()],
        padding=5, border_radius=5
    )

    # --- Core Download Logic ---
    mailbox = queue.Queue()
    pause_event = threading.Event(); pause_event.set()
    cancel_flag = [False]; is_paused_ui = [False]

    def toggle_pause(e):
        t = t_ptr[0]
        if pause_event.is_set():
            pause_event.clear(); is_paused_ui[0] = True
            pause_btn.icon = ft.Icons.PLAY_CIRCLE_FILLED; pause_btn.icon_color = ft.Colors.ORANGE; status_text.value = t['status_paused']
        else:
            pause_event.set(); is_paused_ui[0] = False
            pause_btn.icon = ft.Icons.PAUSE_CIRCLE_FILLED; pause_btn.icon_color = ft.Colors.BLUE; status_text.value = t['status_resume']
        page.update()

    def stop_download(e):
        t = t_ptr[0]
        cancel_flag[0] = True
        pause_event.set()
        status_text.value = t['status_stop']
        cancel_btn.disabled = True
        page.update()

    pause_btn = ft.IconButton(icon=ft.Icons.PAUSE_CIRCLE_FILLED, icon_size=40, icon_color=ft.Colors.BLUE, visible=False, on_click=toggle_pause)
    cancel_btn = ft.IconButton(icon=ft.Icons.STOP_CIRCLE, icon_size=40, icon_color=ft.Colors.RED, visible=False, on_click=stop_download)
    
    download_btn = ft.FilledButton(content=ft.Text("..."), width=180, height=50, on_click=lambda _: start_download_logic())

    clear_btn.on_click = lambda _: [setattr(url_input, 'value', ""), page.update()]
    paste_btn.on_click = lambda _: [setattr(url_input, 'value', pyperclip.paste().strip()), page.update(), start_download_logic()]

    def start_download_logic():
        t = t_ptr[0]
        if not url_input.value: return
        cancel_flag[0] = False; is_paused_ui[0] = False
        cancel_btn.disabled = False
        download_btn.visible = False; pause_btn.visible = cancel_btn.visible = progress_bar.visible = True
        progress_percent.visible = progress_size.visible = True
        
        status_text.opacity = 1
        status_text.value = t['status_parsing']; page.update() 
        
        limit_val = limit_input.value
        threading.Thread(target=backend_worker, args=(url_input.value, dir_text.value, quality_dropdown.value, limit_val), daemon=True).start()
        page.run_task(ui_updater)

    async def ui_updater():
        t = t_ptr[0]
        while True:
            try:
                msg = mailbox.get_nowait()
                if msg['type'] == 'progress' and not is_paused_ui[0]:
                    progress_bar.value = msg['p']; progress_percent.value = msg['ps']
                    progress_size.value = msg['size_str']
                    status_text.value = msg['ss']; page.update()
                elif msg['type'] == 'merging':
                    progress_bar.value = None
                    status_text.value = t['status_merging']; page.update()
                elif msg['type'] == 'success':
                    progress_bar.visible = progress_percent.visible = progress_size.visible = False
                    download_btn.visible = True; pause_btn.visible = cancel_btn.visible = False
                    status_text.value = t['status_success']
                    if msg.get('info'): history_list.controls.insert(0, create_history_card(msg['info']))
                    page.update(); await asyncio.sleep(2); status_text.opacity = 0; page.update(); break
                elif msg['type'] in ['error', 'cancelled']:
                    progress_bar.visible = progress_percent.visible = progress_size.visible = False
                    download_btn.visible = True; pause_btn.visible = cancel_btn.visible = False
                    
                    err_txt = msg.get('content', t['status_stopped'])
                    # Keep the full error visible and copyable until the next attempt.
                    if msg['type'] == 'error':
                        err_txt += f"\nLog: {download_log.path}"
                    status_text.value = f"❌ {err_txt}"
                    page.update()
                    break
            except queue.Empty: await asyncio.sleep(0.1)

    def backend_worker(link, save_dir, quality_key, limit_val):
        current_file_path = [None]
        
        # Generate random task ID to prevent file overwrite
        task_id = ''.join(random.choices(string.ascii_letters + string.digits, k=4))

        def hook(d):
            current_file_path[0] = d.get('filename') or current_file_path[0]
            if cancel_flag[0]: raise DownloadCancelled()
            if not pause_event.is_set(): pause_event.wait()
            if d['status'] == 'downloading':
                current_file_path[0] = d.get('filename')
                total = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
                downloaded = d.get('downloaded_bytes', 0)
                p = downloaded / total if total > 0 else 0
                size_info = f"{format_bytes(downloaded)} / {format_bytes(total)}"
                mailbox.put({'type': 'progress', 'p': p, 'ps': f"{p:.1%}", 'size_str': size_info, 'ss': f"⬇️ {t_ptr[0]['speed']}: {format_bytes(d.get('speed'))}/s"})
            elif d['status'] == 'finished': mailbox.put({'type': 'merging'})
        try:
            q_map = {
                "auto": "bestvideo+bestaudio/best", "4k": "bestvideo[height<=2160]+bestaudio/best",
                "2k": "bestvideo[height<=1440]+bestaudio/best", "1080p": "bestvideo[height<=1080]+bestaudio/best",
                "720p": "bestvideo[height<=720]+bestaudio/best", "480p": "bestvideo[height<=480]+bestaudio/best",
                "360p": "bestvideo[height<=360]+bestaudio/best", "240p": "bestvideo[height<=240]+bestaudio/best",
                "144p": "bestvideo[height<=144]+bestaudio/best", "audio": "bestaudio/best"
            }
            ydl_opts = {
                'outtmpl': os.path.join(save_dir, f'%(title)s_{task_id}.%(ext)s'), 
                'format': q_map.get(quality_key, "bestvideo+bestaudio/best"), 
                'progress_hooks': [hook],
                'socket_timeout': 15, 
                'retries': 3,
                'noplaylist': True,
                'logger': download_log,
                **runtime_options(),
            }
            if quality_key == "audio": ydl_opts['postprocessors'] = [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'}]
            
            try:
                limit_str = str(limit_val).strip()
                limit_mb = float(limit_str) if limit_str else 0.0
                if limit_mb > 0: ydl_opts['ratelimit'] = int(limit_mb * 1024 * 1024) 
            except Exception: pass 
            
            os.makedirs(save_dir, exist_ok=True)
            download_log.debug(f'Download requested; quality={quality_key}; runtimes={list(ydl_opts.get("js_runtimes", {}))}')
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(link, download=True)
                path = info.get('_filename')
                if info.get('requested_downloads'): path = info['requested_downloads'][0].get('filepath') or path
                
                res_text = next((o.text for o in quality_dropdown.options if o.key == quality_key), quality_key)
                if quality_key == "auto":
                    v_height = info.get('height')
                    real_res = f"{v_height}p" if v_height else info.get('resolution', 'Auto')
                    if real_res and real_res != 'Auto':
                        base_text = res_text.split('(')[0].strip()
                        res_text = f"{base_text} ({real_res})"

                mailbox.put({'type': 'success', 'info': {'title':info['title'],'thumbnail':info.get('thumbnail'),'resolution':res_text,'size':format_bytes(info.get('filesize_approx') or info.get('filesize')),'filepath':str(path)}})
        
        except DownloadCancelled:
            if current_file_path[0]:
                for f in glob.glob(f"{os.path.splitext(current_file_path[0])[0]}*"): 
                    if f.endswith((".part", ".ytdl", ".temp")): os.remove(f)
            mailbox.put({'type': 'cancelled'})
        except Exception as e:
            download_log.error(str(e))
            mailbox.put({'type': 'error', 'content': str(e)}) 

    # --- Overlay UI ---
    def create_history_card(item_data):
        card = ft.Card(content=ft.Container(padding=15, content=ft.Row([
            ft.Image(src=item_data['thumbnail'], width=100, height=56, fit="cover") if item_data['thumbnail'] else ft.Icon(ft.Icons.VIDEO_FILE),
            ft.Column([ft.Text(item_data['title'], weight="bold", width=350, max_lines=1), ft.Text(f"{item_data['size']} | {item_data['resolution']}", size=11)], expand=True),
            ft.Row([ft.IconButton(icon=ft.Icons.FOLDER_OPEN, on_click=lambda _: subprocess.run(['explorer', '/select,', os.path.normpath(str(item_data['filepath']))], shell=True)), 
                    ft.IconButton(icon=ft.Icons.DELETE, on_click=lambda _: [history_list.controls.remove(card), page.update()], icon_color="red")])
        ])))
        return card

    search_results_list = ft.ListView(expand=True, spacing=5)
    def on_search(e):
        q = search_input_ui.value.lower().strip() if search_input_ui.value else ""
        search_results_list.controls.clear()
        if not q: search_results_list.controls.append(ft.Text(t_ptr[0]['search_empty'], color=ft.Colors.GREY_500))
        else:
            matches = [n for n in all_extractors if q in n.lower()]
            if matches:
                search_results_list.controls.append(ft.Text(t_ptr[0]['search_found'].format(len(matches)), weight="bold", color=ft.Colors.GREEN_700))
                for m in matches[:50]: search_results_list.controls.append(ft.Text(f" • {m}"))
            else: search_results_list.controls.append(ft.Text(t_ptr[0]['search_not_found'].format(q), color=ft.Colors.RED_400))
        if e: page.update()

    search_input_ui.on_change = on_search
    
    # Overlays
    support_overlay_content = ft.Container(width=450, height=550, bgcolor=ft.Colors.WHITE, padding=20, border_radius=15, content=ft.Column([ft.Row([search_title_ui, ft.IconButton(icon=ft.Icons.CLOSE, on_click=lambda _: [setattr(support_overlay, 'visible', False), page.update()])], alignment="spaceBetween"), search_input_ui, ft.Divider(), search_results_list]))
    support_overlay = ft.Container(content=support_overlay_content, alignment=ft.Alignment(0,0), bgcolor=ft.Colors.BLACK54, visible=False, left=0, top=0, right=0, bottom=0)
    
    history_overlay_content = ft.Container(width=750, height=500, bgcolor=ft.Colors.WHITE, padding=20, border_radius=15, content=ft.Column([ft.Row([history_title_ui, ft.IconButton(icon=ft.Icons.CLOSE, on_click=lambda _: [setattr(history_overlay, 'visible', False), page.update()])], alignment="spaceBetween"), ft.Divider(), history_list]))
    history_overlay = ft.Container(content=history_overlay_content, alignment=ft.Alignment(0,0), bgcolor=ft.Colors.BLACK54, visible=False, left=0, top=0, right=0, bottom=0)
    
    # --- Layout Connections ---
    dir_text = ft.Text(os.path.join(os.path.expanduser("~"), "Downloads"), size=11, expand=True)
    btn_change.on_click = lambda _: [tk.Tk().withdraw(), setattr(dir_text, 'value', filedialog.askdirectory() or dir_text.value), page.update()]
    
    search_tile.on_click = lambda _: [setattr(support_overlay, 'visible', True), page.update()]
    history_tile.on_click = lambda _: [setattr(history_overlay, 'visible', True), page.update()]

    update_ui_text() 

    sidebar = ft.Container(
        width=260, padding=20, bgcolor=ft.Colors.BLUE_GREY_50, 
        content=ft.Column([
            ft.Row([side_title, theme_btn], alignment="spaceBetween"), ft.Divider(), save_loc_text, ft.Row([btn_change, dir_text]), ft.Divider(),
            q_pref_text, quality_dropdown, ft.Divider(), 
            limit_label_text, limit_row, ft.Divider(), 
            search_tile, history_tile, ft.Container(expand=True),
            lang_selector_btn, 
            ft.Column([
                ft.Text("Version: v1.0.0", size=10, color=ft.Colors.BLUE_GREY_300),
                ft.Text("Author: srlee", size=12, weight="bold", color=ft.Colors.BLUE_GREY_400),
                ft.Text("Contact: srlee717421@gmail.com", size=10, color=ft.Colors.BLUE_GREY_300),
                ft.Text("Powered by yt-dlp", size=10, italic=True, color=ft.Colors.BLUE_GREY_300)
            ], spacing=2)
        ])
    )

    main_content = ft.Column(
        alignment="center", horizontal_alignment="center", expand=True, 
        controls=[
            main_title, ft.Container(height=20), 
            ft.Row([url_input, action_btns], width=550, alignment="center"), 
            ft.Row([download_btn, pause_btn, cancel_btn], alignment="center"), 
            ft.Container(height=10), progress_bar, ft.Row([progress_percent, progress_size], alignment="spaceBetween", width=450), status_text
        ]
    )
    
    page.add(ft.Stack([ft.Row([sidebar, main_content], expand=True), history_overlay, support_overlay, lang_overlay], expand=True))

if __name__ == "__main__":
    ft.run(main)