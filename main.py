from quart import Quart, render_template, request

from simplytranslate_engines.googletranslate import GoogleTranslateEngine
from simplytranslate_engines.libretranslate import LibreTranslateEngine

google_translate_engine = GoogleTranslateEngine()

engines = [google_translate_engine, LibreTranslateEngine()]

app = Quart(__name__)

def to_full_name(lang_code, engine):
    lang_code = lang_code.lower()

    if lang_code == "auto":
        return "Autodetect"

    supported_languages = engine.get_supported_languages()

    for key, value in supported_languages.items():
        if value == lang_code:
            return key

    return None

def to_lang_code(lang, engine):
    lang = lang.lower()

    if lang == "autodetect" or lang == "auto":
        return "auto"

    supported_languages = engine.get_supported_languages()

    for key in supported_languages.keys():
        if key.lower() == lang:
            return supported_languages[key]

    for value in supported_languages.values():
        if value.lower() == lang:
            return value

    return None

@app.route(
    "/translate/<string:from_language>/<string:to_language>/<string:input_text>/"
)
async def translate(from_language, to_language, input_text):
    return google_translate_engine.translate(
        input_text, from_language=from_language, to_language=to_language
    )

@app.route("/", methods=["GET", "POST"])
async def index():
    engine_name = request.args.get("engine")

    engine = next((engine for engine in engines if engine.name == engine_name), google_translate_engine)

    switch_engine = request.args.get("switchengine", False)
    translation = None

    if request.method == "GET":
        # support google format
        inp = request.args.get("text", "")

        from_lang = to_full_name(request.args.get("sl", "auto"), engine)

        to_lang = to_full_name(request.args.get("tl", "en"), engine)
    elif request.method == "POST":
        form = await request.form

        inp = form.get("input", "")

        from_lang = form.get("from_language", "Autodetect")

        to_lang = form.get("to_language", "English")

    if not (inp == "" or inp.isspace()):
        translation = engine.translate(
            inp,
            to_language=to_lang_code(to_lang, engine),
            from_language=to_lang_code(from_lang, engine),
        )

    use_text_fields = request.args.get("typingiscool") == "True"

    return await render_template(
        "index.html",
        inp=inp,
        translation=translation,
        from_l=from_lang,
        to_l=to_lang,
        engine=engine.name,
        supported_languages=engine.get_supported_languages(),
        use_text_fields=use_text_fields
    )

if __name__ == "__main__":
    app.run()
