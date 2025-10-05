import os
import logging
import sqlite3
from ulauncher.api.client.Extension import Extension
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.event import KeywordQueryEvent, ItemEnterEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.action.CopyToClipboardAction import CopyToClipboardAction
from ulauncher.api.shared.action.DoNothingAction import DoNothingAction
from ulauncher.api.shared.action.ExtensionCustomAction import ExtensionCustomAction

logger = logging.getLogger(__name__)
extension_icon = "images/icon.png"
db_path = os.path.join(os.path.dirname(__file__), "kaomojis.sqlite")
conn = sqlite3.connect(db_path, check_same_thread=False)
conn.row_factory = sqlite3.Row

SEARCH_LIMIT_MIN = 2
SEARCH_LIMIT_DEFAULT = 8
SEARCH_LIMIT_MAX = 50

class KaomojiExtension(Extension):

    def __init__(self):
        super(KaomojiExtension, self).__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())
        self.subscribe(ItemEnterEvent, MoreEnterEventListener())


class KeywordQueryEventListener(EventListener):

    def on_event(self, event, extension):
        return search(event, extension)


class MoreEnterEventListener(EventListener):

    def on_event(self, event, extension):
        data = event.get_data()
        return search(
            event, extension, search_term=data["search_term"], offset=data["offset"]
        )


def search(event, extension, search_term=None, offset=0):
    search_limit = extension.preferences["search_limit"]

    try:
        search_limit = search_limit.strip()
        search_limit = int(search_limit)

        if search_limit < SEARCH_LIMIT_MIN:
            search_limit = SEARCH_LIMIT_MIN
        elif search_limit > SEARCH_LIMIT_MAX:
            search_limit = SEARCH_LIMIT_MAX
    except Exception as e:
        search_limit = SEARCH_LIMIT_DEFAULT

    search_term = (
        (event.get_argument().replace("%", "") if event.get_argument() else None)
        if search_term is None
        else search_term
    )

    if search_term:
        search_term = "".join(["%", search_term, "%"])

    query = """
        SELECT kao.kaomoji, kao.keywords
        FROM Kaomojis AS kao
        WHERE kao.keywords LIKE ?
        ORDER BY
            CASE
                WHEN kao.keywords LIKE ? THEN 0
            END
        LIMIT ?;
        """
    sql_args = [
        search_term,
        search_term,
        SEARCH_LIMIT_MAX,
    ]

    # Display blank prompt if user hasn't typed anything
    if not search_term:
        search_icon = "images/icon.png"
        return RenderResultListAction(
            [
                ExtensionResultItem(
                    icon=search_icon,
                    name="Type in kaomoji name...",
                    on_enter=DoNothingAction(),
                )
            ]
        )

    # Get list of results from sqlite DB
    items = []
    i = 0
    displayed = 0
    for row in conn.execute(query, sql_args):
        i += 1
        if offset > 0 and i <= offset:
            continue

        icon = extension_icon
        name = row["kaomoji"].capitalize()
        keywords = row["keywords"]

        items.append(
            ExtensionResultItem(
                icon=icon, name=name, description=keywords, on_enter=CopyToClipboardAction(name)
            )
        )

        displayed += 1
        if displayed >= search_limit:
            # Add "MORE" result item with a custom action 
            items.append(
                ExtensionResultItem(
                    icon="images/more.png",
                    name="View more",
                    description=f"You are viewing results from {offset + 1} to {offset + displayed}. Click for more",
                    on_enter=ExtensionCustomAction(
                        data={"offset": i, "search_term": search_term},
                        keep_app_open=True,
                    ),
                )
            )
            break

    return RenderResultListAction(items)


if __name__ == "__main__":
    KaomojiExtension().run()
