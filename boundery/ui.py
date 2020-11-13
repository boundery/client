import toga

class App(toga.App):
    def __init__(self, initial_url):
        self.__initial_url = initial_url
        super().__init__()

    def startup(self):
        self.main_window = toga.MainWindow(title=self.formal_name)

        webview = toga.WebView(url=self.__initial_url)

        self.main_window.content = webview
        self.main_window.show()
