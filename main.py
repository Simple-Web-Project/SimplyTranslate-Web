from quart import Quart, render_template, request

import simplytranslate_engines.googletranslate as gtranslate
import simplytranslate_engines.libretranslate as libre

app = Quart(__name__)

# TODO: find a better name.
def to_short_name(long_name, supported_languages):
    if long_name == "Autodetect":
        return "auto"

    return supported_languages[long_name]

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

    from_lang = (await request.form).get("from_language", None)

    if from_lang == None:
        from_lang = "Autodetect"

    to_lang = (await request.form).get("to_language", None)

    if to_lang == None:
        to_lang = "English"

    translation = None

    if request.method == "POST" and not switch_engine:
        if translation_engine == "libre":
            translation = libre.translate(
                inp,
                to_language=supported_languages[to_lang],
                from_language=to_short_name(from_lang, supported_languages),
            )
        elif translation_engine == "google":
            translation = gtranslate.translate(
                inp,
                to_language=supported_languages[to_lang],
                from_language=to_short_name(from_lang, supported_languages),
            )

    return await render_template(
        "index.html",
        inp=inp,
        translation=translation,
        from_l=from_lang,
        to_l=to_lang,
        engine=translation_engine,
        supported_languages=supported_languages
    )

if __name__ == "__main__":
    app.run()
