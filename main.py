'''Dit is een app voor het uitlenen van klimschoenben in de klimles zodanig dat we kunnen bijhouden
wie er al allemaal heeft geleend en dus zou moeten betalen ofzoiets, de commetns zijn medemogelijk 
gemaakt door AI omdat ik daar geen zin in had, de code is daarentegen volledig door mij Lenn Lepez gemaakt''' 

import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
import requests

# === VUL HIER JOUW FIREBASE URL IN ===
# Vergeet de '/' aan het einde niet!
FIREBASE_URL = "https://klimschoenleen-default-rtdb.europe-west1.firebasedatabase.app/"

class SchoenenApp(App):
    def build(self):
        layout = BoxLayout(orientation='vertical', padding=25, spacing=12)

        # Titel van de app
        titel = Label(
            text="[b]Klimschoenen Uitleen Systeem[/b]", 
            markup=True,
            font_size='22sp', 
            color=(0.1, 0.5, 0.8, 1),
            size_hint_y=None, 
            height=40
        )
        layout.add_widget(titel)

        # Invoerveld: Naam
        naam_label = Label(text="Naam van het kind:", font_size='16sp', halign='left', size_hint_y=None, height=25)
        naam_label.bind(size=naam_label.setter('text_size'))
        layout.add_widget(naam_label)

        self.naam_input = TextInput(hint_text="Voer naam in", multiline=False, size_hint_y=None, height=45)
        layout.add_widget(self.naam_input)

        # Invoerveld: Groep
        groep_label = Label(text="Groep (Max. 3):", font_size='16sp', halign='left', size_hint_y=None, height=25)
        groep_label.bind(size=groep_label.setter('text_size'))
        layout.add_widget(groep_label)

        self.groep_input = TextInput(hint_text="1, 2 of 3", multiline=False, input_filter='int', size_hint_y=None, height=45)
        layout.add_widget(self.groep_input)

        # Knop: Registreren / Toevoegen
        self.verzend_knop = Button(
            text="Schoen Lenen (+1)", 
            font_size='16sp',
            bold=True,
            size_hint_y=None, 
            height=50,
            background_color=(0.2, 0.7, 0.3, 1)
        )
        self.verzend_knop.bind(on_press=self.verwerk_invoer)
        layout.add_widget(self.verzend_knop)

        # Knop: Bekijk volledige lijst
        self.lijst_knop = Button(
            text="Bekijk Volledige Lijst / Beheren", 
            font_size='16sp',
            bold=True,
            size_hint_y=None, 
            height=50,
            background_color=(0.2, 0.5, 0.9, 1)
        )
        self.lijst_knop.bind(on_press=self.toon_volledige_lijst)
        layout.add_widget(self.lijst_knop)

        # Feedback label
        self.resultaat_label = Label(
            text="Vul de gegevens in en klik op 'Schoen Lenen'.", 
            font_size='15sp', 
            color=(0.3, 0.3, 0.3, 1),
            halign='center',
            valign='middle',
            size_hint_y=1
        )
        self.resultaat_label.bind(size=self.resultaat_label.setter('text_size'))
        layout.add_widget(self.resultaat_label)

        return layout

    def maak_sleutel(self, naam, groep):
        # Maakt een schone sleutel voor Firebase zonder spaties of vreemde tekens
        return f"{naam.replace(' ', '_')}_G{groep}"

    def verwerk_invoer(self, instance):
        naam = self.naam_input.text.strip().title()
        groep_tekst = self.groep_input.text.strip()

        if not naam or not groep_tekst:
            self.resultaat_label.text = "[color=ff3333]FOUT: Vul naam en groep in![/color]"
            self.resultaat_label.markup = True
            return

        try:
            groep = int(groep_tekst)
        except ValueError:
            self.resultaat_label.text = "[color=ff3333]FOUT: Groep moet een getal zijn![/color]"
            self.resultaat_label.markup = True
            return

        if groep < 1 or groep > 3:
            self.resultaat_label.text = "[color=ff3333]FOUT: Kies groep 1, 2 of 3![/color]"
            self.resultaat_label.markup = True
            return

        sleutel = self.maak_sleutel(naam, groep)

        try:
            # 1. Haal de huidige data van deze persoon op uit Firebase
            response = requests.get(f"{FIREBASE_URL}schoenen/{sleutel}.json")
            data = response.json()

            huidig_aantal = 0
            if data and 'aantal_keer' in data:
                huidig_aantal = data['aantal_keer']

            nieuw_aantal = huidig_aantal + 1

            # 2. Update naar Firebase
            payload = {
                "naam": naam,
                "groep": groep,
                "aantal_keer": nieuw_aantal
            }
            requests.put(f"{FIREBASE_URL}schoenen/{sleutel}.json", json=payload)

            # 3. Bereken betalingsstatus voor het scherm
            if nieuw_aantal <= 3:
                betaal_status = "[color=ff8800](Telt nog niet mee voor betaling)[/color]"
            else:
                te_betalen = nieuw_aantal - 3
                betaal_status = f"[color=008800](Telt mee voor betaling: {te_betalen}x te betalen)[/color]"

            self.resultaat_label.markup = True
            self.resultaat_label.text = f"{naam} (Groep {groep}) heeft nu [b]{nieuw_aantal}x[/b] geleend.\n{betaal_status}"

            self.naam_input.text = ""
            self.groep_input.text = ""

        except Exception as e:
            self.resultaat_label.markup = True
            self.resultaat_label.text = "[color=ff3333]FOUT: Kan niet verbinden met de server![/color]"

    def toon_volledige_lijst(self, instance):
        box = BoxLayout(orientation='vertical', padding=15, spacing=10)

        try:
            # Haal alle gegevens live op uit Firebase
            response = requests.get(f"{FIREBASE_URL}schoenen.json")
            schoenen_data = response.json()

            if not schoenen_data:
                info_label = Label(text="Er zijn nog geen klimschoenen uitgeleend.", font_size='15sp')
                box.add_widget(info_label)
            else:
                scroll = ScrollView()
                grid = GridLayout(cols=1, spacing=10, size_hint_y=None)
                grid.bind(minimum_height=grid.setter('height'))

                for sleutel, info in schoenen_data.items():
                    naam = info.get('naam', 'Onbekend')
                    groep = info.get('groep', '-')
                    keer = info.get('aantal_keer', 0)

                    if keer <= 3:
                        status = "[color=ff8800]- nog niet betalen[/color]"
                    else:
                        te_betalen = keer - 3
                        status = f"[color=008800]- te betalen ({te_betalen}x)[/color]"

                    regel_layout = BoxLayout(orientation='horizontal', spacing=10, size_hint_y=None, height=40)

                    item_label = Label(
                        text=f"• [b]{naam}[/b] (Groep {groep}): {keer}x geleend {status}",
                        markup=True,
                        font_size='14sp',
                        halign='left',
                        valign='middle'
                    )
                    item_label.bind(size=item_label.setter('text_size'))
                    regel_layout.add_widget(item_label)

                    # Verwijderknop
                    verwijder_knop = Button(
                        text="X", 
                        size_hint_x=None, 
                        width=40, 
                        background_color=(0.9, 0.2, 0.2, 1),
                        bold=True
                    )
                    verwijder_knop.bind(on_press=lambda btn, s=sleutel, n=naam, g=groep: self.bevestig_verwijderen(s, n, g))
                    regel_layout.add_widget(verwijder_knop)

                    grid.add_widget(regel_layout)

                scroll.add_widget(grid)
                box.add_widget(scroll)

        except Exception as e:
            info_label = Label(text="Fout bij het ophalen van gegevens uit de cloud.", font_size='15sp')
            box.add_widget(info_label)

        sluit_knop = Button(text="Sluiten", size_hint_y=None, height=45, background_color=(0.5, 0.5, 0.5, 1))
        box.add_widget(sluit_knop)

        self.lijst_popup = Popup(
            title="Overzicht & Beheren (Live Cloud)", 
            content=box, 
            size_hint=(0.95, 0.8)
        )
        sluit_knop.bind(on_press=self.lijst_popup.dismiss)
        self.lijst_popup.open()

    def bevestig_verwijderen(self, sleutel, naam, groep):
        bevestig_box = BoxLayout(orientation='vertical', padding=15, spacing=15)
        
        vraag_label = Label(
            text=f"Ben je zeker dat je [b]{naam}[/b] (Groep {groep}) wilt verwijderen?",
            markup=True,
            halign='center',
            valign='middle'
        )
        vraag_label.bind(size=vraag_label.setter('text_size'))
        bevestig_box.add_widget(vraag_label)

        knoppen_layout = BoxLayout(orientation='horizontal', spacing=10, size_hint_y=None, height=45)

        ja_knop = Button(text="Ja, verwijder", background_color=(0.8, 0.2, 0.2, 1))
        nee_knop = Button(text="Nee, annuleren", background_color=(0.4, 0.4, 0.4, 1))

        knoppen_layout.add_widget(ja_knop)
        knoppen_layout.add_widget(nee_knop)
        bevestig_box.add_widget(knoppen_layout)

        bevestig_popup = Popup(
            title="Bevestig Verwijdering",
            content=bevestig_box,
            size_hint=(0.85, 0.4)
        )

        def voer_verwijdering_uit(instance):
            try:
                # Verwijder het record uit Firebase via een DELETE-request
                requests.delete(f"{FIREBASE_URL}schoenen/{sleutel}.json")
            except Exception as e:
                print(f"Fout bij verwijderen: {e}")

            bevestig_popup.dismiss()
            self.lijst_popup.dismiss()
            self.toon_volledige_lijst(None)  # Ververs het overzicht meteen

        ja_knop.bind(on_press=voer_verwijdering_uit)
        nee_knop.bind(on_press=bevestig_popup.dismiss)

        bevestig_popup.open()

if __name__ == '__main__':
    SchoenenApp().run()
