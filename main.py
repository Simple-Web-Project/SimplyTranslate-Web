from quart import (
    Quart,
    render_template,
    request,
    redirect,
    make_response,
    send_file,
    Response,
)
from configparser import ConfigParser
from urllib.parse import urlencode
from wsgiref.util import FileWrapper
from io import BytesIO

from simplytranslate_engines.googletranslate import GoogleTranslateEngine
from simplytranslate_engines.libretranslate import LibreTranslateEngine
from simplytranslate_engines.deepl import DeeplEngine
from simplytranslate_engines.icibatranslate import IcibaTranslateEngine
from simplytranslate_engines.utils import *

import requests

config = ConfigParser()

config.read(["/etc/simplytranslate/shared.conf", "/etc/simplytranslate/web.conf"])

engines = []

if config.getboolean("google", "Enabled", fallback=True):
    engines.append(GoogleTranslateEngine())

if config.getboolean("deepl", "Enabled", fallback=False):
    engines.append(DeeplEngine())

if config.getboolean("iciba", "Enabled", fallback=False):
    engines.append(IcibaTranslateEngine())

libretranslate_enabled = config.getboolean("libre", "Enabled", fallback=None)

if libretranslate_enabled is None:
    print(
        "LibreTranslate is disabled by default; please edit the config file to explicitly state whether it is enabled or not"
    )

if libretranslate_enabled:
    engines.append(
        LibreTranslateEngine(
            config["libre"]["Instance"],
            # `ApiKey` is not required, so use `get` to get `None` as fallback.
            config["libre"].get("ApiKey"),
        )
    )

if not engines:
    raise Exception("All translation engines are disabled")

app = Quart(__name__)

app.url_map.strict_slashes = False

# NOTE: Legacy Endpoint. Use "/api"
@app.route(
    "/translate/<string:from_language>/<string:to_language>/<string:input_text>/",
)
async def translate(from_language, to_language, input_text):
    return engines[0].translate(
        input_text, from_language=from_language, to_language=to_language
    )


@app.route("/api/translate/")
async def api_translate():
    engine_name = request.args.get("engine")
    text = request.args.get("text")
    from_language = request.args.get("from")
    to_language = request.args.get("to")

    engine = get_engine(engine_name, engines, engines[0])

    from_language = to_lang_code(from_language, engine)
    to_language = to_lang_code(to_language, engine)

    return engine.translate(text, from_language=from_language, to_language=to_language)


@app.route("/api/get_languages/")
async def api_get_languages():
    engine_name = request.args.get("engine")
    engine = get_engine(engine_name, engines, engines[0])

    return engine.get_supported_languages()


@app.route("/api/tts/")
async def api_tts():
    engine_name = request.args.get("engine")
    text = request.args.get("text")
    language = request.args.get("lang")

    engine = get_engine(engine_name, engines, engines[0])

    language = to_lang_code(language, engine)

    url = engine.get_tts(text, language)

    USER_AGENT = "Mozilla/5.0 (Android 4.4; Mobile; rv:41.0) Gecko/41.0 Firefox/41.0"

    if url != None:
        b = BytesIO(
            requests.get(
                url, headers={"Referrer": None, "User-Agent": USER_AGENT}
            ).content
        )
        w = FileWrapper(b)
        return Response(w, mimetype="audio/mpeg")

    abort(404)


@app.route("/switchlanguages/", methods=["POST"])
async def switchlanguages():
    form = await request.form

    engine_name = request.args.get("engine")

    engine = get_engine(engine_name, engines, engines[0])

    text = form.get("input", "")
    from_lang = to_lang_code(form.get("from_language", "Autodetect"), engine)
    to_lang = to_lang_code(form.get("to_language", "English"), engine)

    if from_lang == "auto":
        detected_lang = engine.detect_language(text)

        if detected_lang is not None:
            from_lang = detected_lang

    if from_lang != "auto":
        from_lang, to_lang = to_lang, from_lang

    use_text_fields = request.args.get("typingiscool") == "True"

    """
    In case we ever want to also switch the translated text with the to-be-translated text, this is a good start.

    translation = engine.translate(
        text,
        to_language=to_lang,
        from_language=from_lang,
    )
    """

    redirect_params = {
        "engine": engine_name,
        "typingiscool": use_text_fields,
        "sl": from_lang,
        "tl": to_lang,
        "text": text,
        "could_not_switch_languages": from_lang == "auto",
    }

    response = await make_response(
        redirect(
            f"/?{urlencode(redirect_params)}",
            code=302,
        ),
    )

    response.set_cookie("from_lang", to_lang)
    response.set_cookie("to_lang", from_lang)

    return response


@app.route("/typingiscool/", methods=["POST"])
async def typingiscool():
    form = await request.form

    engine_name = request.args.get("engine")

    engine = get_engine(engine_name, engines, engines[0])

    text = form.get("input", "")
    from_lang = to_lang_code(form.get("from_language", "Autodetect"), engine)
    to_lang = to_lang_code(form.get("to_language", "English"), engine)

    use_text_fields = request.args.get("typingiscool") == "True"
    use_text_fields = not use_text_fields

    redirect_params = {
        "engine": engine_name,
        "typingiscool": use_text_fields,
        "sl": from_lang,
        "tl": to_lang,
        "text": text,
    }

    return redirect(
        f"/?{urlencode(redirect_params)}",
        code=302,
    )


@app.route("/", methods=["GET", "POST"])
async def index():
    engine_name = request.args.get("engine")

    engine = get_engine(engine_name, engines, engines[0])

    from_lang, to_lang, inp, translation = "", "", "", None

    # This is `True` when the language switch button is pressed, `from_lang` is
    # "auto", and the engine doesn't support language detection.
    could_not_switch_languages = False

    if request.method == "GET":
        # support google format
        inp = request.args.get("text", "")

        from_lang = to_full_name(
            request.args.get("sl") or request.cookies.get("from_lang") or "auto", engine
        )

        to_lang = to_full_name(
            request.args.get("tl") or request.cookies.get("to_lang") or "en", engine
        )

        could_not_switch_languages = (
            request.args.get("could_not_switch_languages") == "True"
        )
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

    # TTS
    tts_from = None
    tts_to = None
    # check if the engine even supports TTS
    if engine.get_tts("auto", "test") != None:
        if len(inp) > 0:
            params = {"engine": engine_name, "lang": from_l_code, "text": inp}
            tts_from = f"/api/tts/?{urlencode(params)}"
        if translation != None:
            if len(translation) > 0:
                params = {"engine": engine_name, "lang": to_l_code, "text": translation}
                tts_to = f"/api/tts/?{urlencode(params)}"

    response = await make_response(
        await render_template(
            "index.html",
            inp=inp,
            translation=translation,
            from_l=from_lang,
            from_l_code=from_l_code,
            tts_from=tts_from,
            tts_to=tts_to,
            to_l=to_lang,
            to_l_code=to_l_code,
            engine=engine.name,
            #engines=[engine.name for engine in engines],
            engines=engines,
            
            supported_languages=engine.get_supported_languages(),
            use_text_fields=use_text_fields,
            could_not_switch_languages=could_not_switch_languages,
        )
    )

    if request.method == "POST":
        response.set_cookie("from_lang", to_lang_code(from_lang, engine))
        response.set_cookie("to_lang", to_lang_code(to_lang, engine))

    return response


if __name__ == "__main__":
    app.run(port=config.getint("network", "port", fallback=5000), host=str(config.get("network", "host", fallback="0.0.0.0"))) 
