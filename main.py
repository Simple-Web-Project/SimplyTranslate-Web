from quart import Quart, render_template, request, redirect

from simplytranslate_engines.googletranslate import GoogleTranslateEngine
from simplytranslate_engines.libretranslate import LibreTranslateEngine
from simplytranslate_engines.utils import *

google_translate_engine = GoogleTranslateEngine()

engines = [google_translate_engine, LibreTranslateEngine()]

app = Quart(__name__)

@app.route(
    "/translate/<string:from_language>/<string:to_language>/<string:input_text>/"
)
async def translate(from_language, to_language, input_text):
    return google_translate_engine.translate(
        input_text, from_language=from_language, to_language=to_language
    )


@app.route("/switchlanguages/", methods=["POST"])
async def switchlanguages():
    form = await request.form

    engine_name = request.args.get("engine")

    engine = get_engine(engine_name, engines, google_translate_engine)

    text = form.get("input", "")
    from_lang = to_lang_code(form.get("from_language", "Autodetect"), engine)
    to_lang = to_lang_code(form.get("to_language", "English"), engine)

    # if the from_lang is not auto,
    if from_lang != "auto":
        tmp_from_lang = from_lang
        from_lang = to_lang
        to_lang = tmp_from_lang

    use_text_fields = request.args.get("typingiscool") == "True"

    """
    In case we ever want to also switch the translated text with the to-be-translated text, this is a good start.

    translation = engine.translate(
        text,
        to_language=to_lang,
        from_language=from_lang,
    )
    """

    return redirect(
        "/?engine={0}&typingiscool={1}&sl={2}&tl={3}&text={4}".format(
            engine_name, use_text_fields, from_lang, to_lang, text
        ),
        code=302,
    )

@app.route("/typingiscool/", methods=["POST"])
async def typingiscool():
    form = await request.form

    engine_name = request.args.get("engine")

    engine = get_engine(engine_name, engines, google_translate_engine)

    text = form.get("input", "")
    from_lang = to_lang_code(form.get("from_language", "Autodetect"), engine)
    to_lang = to_lang_code(form.get("to_language", "English"), engine)

    use_text_fields = request.args.get("typingiscool") == "True"
    use_text_fields = not use_text_fields

    return redirect(
        "/?engine={0}&typingiscool={1}&sl={2}&tl={3}&text={4}".format(
            engine_name, use_text_fields, from_lang, to_lang, text
        ),
        code=302,
    )

@app.route("/", methods=["GET", "POST"])
async def index():
    engine_name = request.args.get("engine")

    engine = get_engine(engine_name, engines, google_translate_engine)

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

    from_l_code = None
    to_l_code = None

    if not (inp == "" or inp.isspace()):
        from_l_code = to_lang_code(from_lang, engine)
        to_l_code = to_lang_code(to_lang, engine)
        translation = engine.translate(
            inp,
            to_language=to_l_code,
            from_language=from_l_code,
        )

    use_text_fields = request.args.get("typingiscool") == "True"

    return await render_template(
        "index.html",
        inp=inp,
        translation=translation,
        from_l=from_lang,
        from_l_code=from_l_code,
        to_l=to_lang,
        to_l_code=to_l_code,
        engine=engine.name,
        supported_languages=engine.get_supported_languages(),
        use_text_fields=use_text_fields,
    )


@app.route("/about", methods=["GET"])
async def about():
    return await render_template("about.html")


if __name__ == "__main__":
    app.run(port=5000, host='0.0.0.0')
