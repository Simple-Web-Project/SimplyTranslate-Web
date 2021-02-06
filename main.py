from quart import Quart, render_template, request

import simplytranslate_engines.googletranslate as gtranslate
import simplytranslate_engines.libretranslate as libre

app = Quart(__name__)


@app.route(
    "/translate/<string:from_language>/<string:to_language>/<string:input_text>/"
)
async def translate(from_language, to_language, input_text):
    return await gtranslate.translate(
        input_text, from_language=from_language.lower(), to_language=to_language.lower()
    )


@app.route("/", methods=["GET", "POST"])
async def index():
    translation_engine = "google"

    if request.method == "POST":
        translation_engine = (await request.form).get("engine")
        if translation_engine == None or translation_engine != "libre":
            translation_engine = "google"

        inp = (await request.form)["input"]
        from_lang = (await request.form)["from_language"].lower()
        to_lang = (await request.form)["to_language"].lower()

        if translation_engine == "libre":
            translation = libre.translate(
                inp, to_language=to_lang, from_language=from_lang
            )
        elif translation_engine == "google":
            translation = gtranslate.translate(
                inp, to_language=to_lang, from_language=from_lang
            )


        return await render_template(
            "index.html",
            inp=inp,
            translation=translation,
            from_l=from_lang,
            to_l=to_lang,
            engine=translation_engine
        )

    return await render_template("index.html", to_l="en", from_l="auto", engine=translation_engine)


if __name__ == "__main__":
    app.run()
