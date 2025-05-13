import logging
import html
from telegram import Bot
from telegram.error import TelegramError


class SyncTelegramLoggingHandler(logging.Handler):
    MAX_MESSAGE_LENGTH = 4096
    TRACE_CHUNK_SIZE = 4096

    def __init__(self, bot_token, chat_id):
        super().__init__()
        try:
            self.bot = Bot(token=bot_token)
        except Exception as e:
            self.bot = None
            print(f"Error setting up Telegram logger: {e}")

        self.chat_id = chat_id

    def escape_html(self, text: str) -> str:
        return html.escape(text)

    def escape_md(self, text: str) -> str:
        for c in r"_*[]()~`>#+-=|{}.!":
            text = text.replace(c, f"\\{c}")
        return text

    def split_text(self, text: str, limit: int):
        """Chunk text by lines, then hard-slice if a single line is too long"""
        if len(text) <= limit:
            return [text]
        chunks = []
        for line in text.splitlines(keepends=True):
            if chunks and len(chunks[-1]) + len(line) <= limit:
                chunks[-1] += line
            elif len(line) <= limit:
                chunks.append(line)
            else:
                for i in range(0, len(line), limit):
                    chunks.append(line[i:i + limit])
        return chunks

    def send_one(self, text: str):
        try:
            self.bot.send_message(
                chat_id=self.chat_id,
                text=text,
                parse_mode="MarkdownV2",
                disable_web_page_preview=True,
            )
        except TelegramError as e:
            print(f"Failed to send Telegram message: {e}")

    def emit(self, record: logging.LogRecord):
        if not self.bot or not self.chat_id:
            return
        try:
            raw = self.format(record)
            header = "🐞 Django Exception 🐞" if record.exc_info else ""
            msg = self.escape_md(raw)

            parts = []
            if header:
                parts.append(self.escape_md(header))

            req = getattr(record, "request", None)
            if record.exc_info and req:
                path = getattr(req, "get_full_path", lambda: "<?>")()
                parts.append(f"Route: `{self.escape_md(path)}`")

                try:
                    body = req.body
                except Exception as e:
                    snippet = f"Error accessing request body: {self.escape_md(str(e))}"
                else:
                    if isinstance(body, (bytes, bytearray)):
                        body = body.decode("utf-8", "replace")
                    body_snippet = body.strip()[:self.TRACE_CHUNK_SIZE]
                    escaped_snippet = self.escape_md(body_snippet)
                    if len(body) > self.TRACE_CHUNK_SIZE:
                        escaped_snippet += "…"
                    snippet = f"```\n{escaped_snippet}\n```"

                parts.append(snippet)

            parts.append(msg)
            full = "\n".join(p for p in parts if p)

            for chunk in self.split_text(full, self.MAX_MESSAGE_LENGTH):
                self.send_one(chunk)

        except Exception as e:
            print(f"Error in SyncTelegramHandler: {e}")