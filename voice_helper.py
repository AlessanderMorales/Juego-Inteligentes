import threading


class AsistenteVoz:
    def __init__(self):
        self.sr = None
        self.pyttsx3 = None
        self.recognizer = None
        self.engine = None
        self.disponible = False

        try:
            import speech_recognition as sr
            import pyttsx3

            self.sr = sr
            self.pyttsx3 = pyttsx3
            self.recognizer = sr.Recognizer()
            self.engine = pyttsx3.init()
            self.engine.setProperty("rate", 130)
            self.disponible = True
        except Exception:
            self.disponible = False

    def hablar(self, texto):
        if not self.disponible:
            return

        def _speak():
            try:
                self.engine.say(texto)
                self.engine.runAndWait()
            except Exception:
                pass

        hilo = threading.Thread(target=_speak, daemon=True)
        hilo.start()

    def escuchar(self, timeout=4, phrase_time_limit=6):
        if not self.disponible:
            return {
                "ok": False,
                "tipo": "no_disponible",
                "texto": "",
                "mensaje": "No tengo librerías de voz instaladas.",
            }

        try:
            with self.sr.Microphone() as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.6)
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)

            texto = self.recognizer.recognize_google(audio, language="es-ES")
            return {
                "ok": True,
                "tipo": "ok",
                "texto": texto,
                "mensaje": "",
            }
        except self.sr.WaitTimeoutError:
            return {
                "ok": False,
                "tipo": "silencio",
                "texto": "",
                "mensaje": "Presiona el botón cuando quieras hablar.",
            }
        except self.sr.UnknownValueError:
            return {
                "ok": False,
                "tipo": "no_entendido",
                "texto": "",
                "mensaje": "No entendí bien, puedes repetirlo más despacio?",
            }
        except self.sr.RequestError:
            return {
                "ok": False,
                "tipo": "servicio",
                "texto": "",
                "mensaje": "No pude conectarme al servicio de reconocimiento.",
            }
        except OSError:
            return {
                "ok": False,
                "tipo": "microfono",
                "texto": "",
                "mensaje": "No encontré micrófono disponible.",
            }


def interpretar_intencion(texto):
    t = texto.lower().strip()

    if any(p in t for p in ["dfs", "profundidad", "explorar"]):
        return "usar_dfs"
    if any(p in t for p in ["dijkstra", "rapido", "rápido", "mejor ruta"]):
        return "usar_dijkstra"
    if any(p in t for p in ["ucs", "costo uniforme", "costo"]):
        return "usar_ucs"
    if any(p in t for p in ["ayuda", "guiame", "guíame", "ruta", "camino"]):
        return "pedir_ayuda"
    if any(p in t for p in ["si", "sí", "dale", "ok", "quiero"]):
        return "afirmar"
    if any(p in t for p in ["no", "despues", "después", "luego"]):
        return "negar"

    for n in ["1", "2", "3", "4", "5"]:
        if n in t:
            return f"mision_{n}"

    palabras_a_numero = {
        "uno": "1",
        "dos": "2",
        "tres": "3",
        "cuatro": "4",
        "cinco": "5",
    }
    for palabra, numero in palabras_a_numero.items():
        if palabra in t:
            return f"mision_{numero}"

    return "desconocido"
