# SimplyTranslate Web

This is a simple web interface for SimplyTranslate

## List of Instances
You can find a list of instances here: [SimplyTranslate Project Page](https://simple-web.org/projects/simplytranslate.html)

If you want to integrate a list of instances in your project, you can use this endpoint to always have an up-to-date list of all instances known to us: [https://simple-web.org/instances/simplytranslate](https://simple-web.org/instances/simplytranslate)


If you want to add your own instance here, please either send me an email directly to simpleweb@metalune.xyz or tell us about it in our IRC channel #simple-web on [Libera.Chat](https://libera.chat)

## How to install/use

### Clone the repository
```sh
git clone https://git.sr.ht/~metalune/simplytranslate_web
cd simplytranslate_web
``` 

### Install the dependencies
```sh
pip install -r requirements.txt
```

### Run the main.py
```sh
# Directly
python3 main.py
# Using uvicorn
uvicorn main:app --port 5000
```

## How to contribute
1. Setup git-email: https://git-send-email.io
2. Clone the repo you want: `git clone https://git.sr.ht/~metalune/simplytranslate_web`
3. Branch it: `git checkout -b my-cool-changes`
4. Add your changes: `git add .` and commit them `git commit -m "My Cool Changes"`
5. Set mail-to: `git config sendemail.to '~metalune/simplytranslate-devel@lists.sr.ht'`
6. Send your commit: `git send-email master`

## API
[Documentation](./api.md)

## Other projects like this
* [gtranslate](https://git.sr.ht/~yerinalexey/gtranslate)
* [lingva translate](https://github.com/TheDavidDelta/lingva-translate)

## Contact

To get in contact with the developers, visit us on the #simple-web IRC channel on [Libera.Chat](https://libera.chat)

## License

simplytranslate_web is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

simplytranslate_web is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.
