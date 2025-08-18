from better5e.UI.pages.homebrew_editor_page import HomebrewEditorPage


class CreateItemPage(HomebrewEditorPage):
    def __init__(self, app) -> None:
        super().__init__(app, "Create Item")
