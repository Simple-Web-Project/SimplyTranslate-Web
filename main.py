from quart import Quart, render_template, request

import simplytranslate_engines.googletranslate as gtranslate
import simplytranslate_engines.libretranslate as libre

app = Quart(__name__)

def to_full_name(lang_code, supported_languages):
    lang_code = lang_code.lower()

    if lang_code == "auto":
        return "Autodetect"

    for key, value in supported_languages.items():
        if value == lang_code:
            return key

    return None

def to_lang_code(lang, supported_languages):
    lang = lang.lower()

    if lang == "autodetect" or lang == "auto":
        return "auto"

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
    return gtranslate.translate(
        input_text, from_language=from_language, to_language=to_language
    )


@app.route("/", methods=["GET", "POST"])
async def index():
    translation_engine = request.args.get("engine")
    if translation_engine == None or translation_engine != "libre":
        translation_engine = "google"

    if translation_engine == "libre":
        supported_languages = libre.supported_languages
    elif translation_engine == "google":
        supported_languages = gtranslate.supported_languages

    switch_engine = request.args.get("switchengine", False)

    inp = (await request.form).get("input", "")

    from_lang = (await request.form).get("from_language", "Autodetect")

    to_lang = (await request.form).get("to_language", "English")

    translation = None

    if request.method == "GET":
        # support google format
        inp = request.args.get("text", "")
        from_lang = to_full_name(request.args.get("sl", "auto"), supported_languages)
        to_lang = to_full_name(request.args.get("tl", "en"), supported_languages)

    if not (inp == "" or inp.isspace()):
        if translation_engine == "libre":
            translation = libre.translate(
                inp,
                to_language=to_lang_code(to_lang, supported_languages),
                from_language=to_lang_code(from_lang, supported_languages),
            )
        elif translation_engine == "google":
            translation = gtranslate.translate(
                inp,
                to_language=to_lang_code(to_lang, supported_languages),
                from_language=to_lang_code(from_lang, supported_languages),
            )

    use_text_fields = request.args.get("typingiscool") == "True"

    return await render_template(
        "index.html",
        inp=inp,
        translation=translation,
        from_l=from_lang,
        to_l=to_lang,
        engine=translation_engine,
        supported_languages=supported_languages,
        use_text_fields=use_text_fields
    )

if __name__ == "__main__":
    app.run()
