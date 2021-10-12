# SimplyTranslate Web

This is a simple web interface for SimplyTranslate

## List of Instances
You can find a list of instances here: [SimplyTranslate Project Page](https://simple-web.org/projects/simplytranslate.html)

If you want to integrate a list of instances in your project, you can use this endpoint to always have an up-to-date list of all instances known to us: [https://simple-web.org/instances/simplytranslate](https://simple-web.org/instances/simplytranslate)
If you want to add your own instance here, please either send me an email directly to metalune@mailbox.org or tell us about it in our IRC channel #simple-web on [Libera.Chat](https://libera.chat)

## How to install/use
### Clone simplytranslate_engines repository and install it
```sh
git clone https://git.sr.ht/~metalune/simplytranslate_engines
cd simplytranslate_engines
sudo python3 setup.py install
cd ..
```

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

### Other projects like this
[gtranslate](https://git.sr.ht/~yerinalexey/gtranslate)
[lingva translate](https://github.com/TheDavidDelta/lingva-translate)

### Contact
To get in contact with the developers, visit us on the #simple-web IRC channel on [Libera.Chat](https://libera.chat)
