import sys
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtGui import QIcon
from PyQt5.QtNetwork import QNetworkProxy, QNetworkProxyFactory


class SezBrowser(QMainWindow):
    def __init__(self, is_tor_mode=False, is_private_mode=False):
        super(SezBrowser, self).__init__()
        self.is_tor_mode = is_tor_mode
        self.is_private_mode = is_private_mode
        
        # Pencere başlığını ayarla
        if is_tor_mode:
            self.setWindowTitle("SezBrowser - Tor Modu")
        elif is_private_mode:
            self.setWindowTitle("SezBrowser - Gizli Pencere")
        else:
            self.setWindowTitle("SezBrowser - Open Source Web Browser")
        
        self.setWindowIcon(QIcon("icon.png"))
        
        # Ana widget ve layout
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.setCentralWidget(self.tabs)
        
        # Tor modunda proxy ayarlarını yap
        if is_tor_mode:
            self.setup_tor_proxy()
        
        # Yeni sekme ekle
        self.add_new_tab(QUrl("https://www.startpage.com/"))
        
        # Siber Navigasyon Çubuğu
        navbar = QToolBar()
        navbar.setMovable(False)
        self.addToolBar(navbar)

        # Geri Butonu
        back_btn = QAction('◀ Geri', self)
        back_btn.triggered.connect(self.navigate_back)
        navbar.addAction(back_btn)

        # İleri Butonu
        forward_btn = QAction('İleri ▶', self)
        forward_btn.triggered.connect(self.navigate_forward)
        navbar.addAction(forward_btn)

        # Yenile Butonu
        reload_btn = QAction('🔄 Yenile', self)
        reload_btn.triggered.connect(self.navigate_reload)
        navbar.addAction(reload_btn)

        # Ana Sayfa Butonu
        home_btn = QAction('🏠 Ana Sayfa', self)
        home_btn.triggered.connect(self.navigate_home)
        navbar.addAction(home_btn)

        # Tor Modu Butonu
        tor_btn = QAction('🔒 Tor Penceresi Aç', self)
        tor_btn.triggered.connect(self.open_tor_window)
        navbar.addAction(tor_btn)

        # Gizli Pencere Butonu
        private_btn = QAction('🕵️ Gizli Pencere', self)
        private_btn.triggered.connect(self.open_private_window)
        navbar.addAction(private_btn)

        # Hızlı Erişim Butonları
        tagvids_btn = QAction('🎥 TagVids', self)
        tagvids_btn.triggered.connect(lambda: self.navigate_to_url(QUrl("https://tagvids.web.app")))
        navbar.addAction(tagvids_btn)

        seztalk_btn = QAction('💬 SezTalk', self)
        seztalk_btn.triggered.connect(lambda: self.navigate_to_url(QUrl("https://seztalkforchat.web.app")))
        navbar.addAction(seztalk_btn)

        acrox_btn = QAction('⚡ Acrox', self)
        acrox_btn.triggered.connect(lambda: self.navigate_to_url(QUrl("https://vip-naber.github.io/acrox-systems/")))
        navbar.addAction(acrox_btn)

        # Yeni Sekme Butonu
        new_tab_btn = QAction('➕ Yeni Sekme', self)
        new_tab_btn.triggered.connect(lambda: self.add_new_tab(QUrl("https://www.startpage.com/")))
        navbar.addAction(new_tab_btn)

        # Adres Çubuğu
        self.url_bar = QLineEdit()
        self.url_bar.setPlaceholderText("Arama yapın veya URL girin...")
        self.url_bar.returnPressed.connect(self.navigate_to_url_from_bar)
        navbar.addWidget(self.url_bar)

        # Geçmişi sakla
        self.history = []

        # Sekme değiştiğinde URL'yi güncelle
        self.tabs.currentChanged.connect(self.update_url_from_tab)
        
        # uBlock Origin Lite kuralları
        self.setup_ublock_rules()
        
        # Gizli modda 3. taraf çerezlerini engelle
        if is_private_mode:
            self.setup_private_mode()

    def setup_tor_proxy(self):
        # Tor proxy ayarları (127.0.0.1:9050)
        proxy = QNetworkProxy(QNetworkProxy.Socks5Proxy, "127.0.0.1", 9050)
        QNetworkProxyFactory.setUseProxyDefaults(False)
        QNetworkProxyFactory.setApplicationProxy(proxy)

    def setup_ublock_rules(self):
        # uBlock Origin Lite kuralları (basit engelleme kuralları)
        # Bu, QtWebEngine'in yerel engelleme özelliği kullanılarak yapılır
        profile = QWebEngineProfile.defaultProfile()
        profile.setUrlRequestInterceptor(AdBlocker(profile))

    def setup_private_mode(self):
        # Gizli modda 3. taraf çerezlerini engelle
        profile = QWebEngineProfile.defaultProfile()
        profile.setPersistentCookiesPolicy(QWebEngineProfile.NoPersistentCookies)
        profile.setHttpCacheType(QWebEngineProfile.NoCache)

    def add_new_tab(self, url=None):
        if url is None:
            url = QUrl("https://www.startpage.com/")
        
        browser = QWebEngineView()
        browser.setUrl(url)
        
        # Sekme başlığını ayarla
        index = self.tabs.addTab(browser, "Yeni Sekme")
        self.tabs.setCurrentIndex(index)
        
        # URL değiştiğinde başlığı güncelle
        browser.urlChanged.connect(lambda q, i=index: self.update_tab_title(i, q))
        browser.titleChanged.connect(lambda title, i=index: self.update_tab_title(i, title))

    def close_tab(self, index):
        if self.tabs.count() > 1:
            self.tabs.removeTab(index)
        else:
            self.close()

    def update_tab_title(self, index, title):
        if isinstance(title, str):
            self.tabs.setTabText(index, title[:15] + "..." if len(title) > 15 else title)
        else:
            self.tabs.setTabText(index, title.toString()[:15] + "..." if len(title.toString()) > 15 else title.toString())

    def navigate_back(self):
        current_browser = self.tabs.currentWidget()
        current_browser.back()

    def navigate_forward(self):
        current_browser = self.tabs.currentWidget()
        current_browser.forward()

    def navigate_reload(self):
        current_browser = self.tabs.currentWidget()
        current_browser.reload()

    def navigate_home(self):
        current_browser = self.tabs.currentWidget()
        current_browser.setUrl(QUrl("https://www.startpage.com/"))

    def navigate_to_url(self, url):
        current_browser = self.tabs.currentWidget()
        current_browser.setUrl(url)
        self.history.append(url.toString())

    def navigate_to_url_from_bar(self):
        url = self.url_bar.text().strip()
        if not url:
            return

        # Eğer URL geçerli bir web adresi değilse, Startpage arama yap
        if not url.startswith(('http://', 'https://')):
            url = f"https://www.startpage.com/do/dsearch?query={url}"
        else:
            # Eğer http/https ile başlıyorsa, URL'yi doğrudan aç
            if not url.startswith('http'):
                url = 'https://' + url

        self.navigate_to_url(QUrl(url))

    def update_url_from_tab(self):
        current_browser = self.tabs.currentWidget()
        self.url_bar.setText(current_browser.url().toString())

    def open_tor_window(self):
        # Tor penceresi aç
        self.tor_window = SezBrowser(is_tor_mode=True)
        self.tor_window.show()

    def open_private_window(self):
        # Gizli pencere aç
        self.private_window = SezBrowser(is_private_mode=True)
        self.private_window.show()


# uBlock Origin Lite engelleme kuralları
class AdBlocker(QWebEngineUrlRequestInterceptor):
    def __init__(self, profile):
        super().__init__()
        self.blocked_domains = [
            "google-analytics.com",
            "doubleclick.net",
            "facebook.com",
            "twitter.com",
            "adservice.google.com",
            "googlesyndication.com",
            "adserver.com",
            "tracker.com"
        ]

    def interceptRequest(self, info):
        url = info.requestUrl().toString()
        for domain in self.blocked_domains:
            if domain in url:
                info.block(True)
                return
        
        # HTTPS zorlaması
        if url.startswith("http://"):
            new_url = url.replace("http://", "https://")
            info.redirect(QUrl(new_url))


app = QApplication(sys.argv)
QApplication.setApplicationName('SezBrowser - Open Source Web Browser')
window = SezBrowser()
window.showMaximized()
app.exec_()