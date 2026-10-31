import os
import json
from datetime import datetime
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.screenmanager import ScreenManager, Screen

# File to store flashcards locally
DATA_FILE = "flashcards.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    # Default initial data if file doesn't exist
    return {
        "Science": [
            {"q": "Powerhouse of the cell?", "a": "Mitochondria", "date": str(datetime.now().strftime("%Y-%m-%d %H:%M"))}
        ],
        "History": [
            {"q": "In what year did World War II end?", "a": "1945", "date": str(datetime.now().strftime("%Y-%m-%d %H:%M"))}
        ]
    }

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

class StudyScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.data = load_data()
        self.current_subject = list(self.data.keys())[0] if self.data else "General"
        self.current_index = 0
        self.showing_answer = False

        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)

        # Top bar: Subject Selector & Manage Button
        top_layout = BoxLayout(size_hint=(1, 0.1), spacing=10)
        
        subjects = list(self.data.keys()) if self.data else ["General"]
        self.spinner = Spinner(
            text=self.current_subject,
            values=subjects,
            size_hint=(0.7, 1)
        )
        self.spinner.bind(text=self.on_subject_select)
        top_layout.add_widget(self.spinner)

        manage_btn = Button(text="Manage", size_hint=(0.3, 1), background_color=(0.2, 0.6, 0.8, 1))
        manage_btn.bind(on_press=self.go_to_manage)
        top_layout.add_widget(manage_btn)
        
        layout.add_widget(top_layout)

        # Date added label
        self.date_label = Label(text="", font_size=12, size_hint=(1, 0.05), color=(0.7, 0.7, 0.7, 1))
        layout.add_widget(self.date_label)

        # Flashcard Display Area
        self.card_label = Label(
            text="", 
            font_size=18,
            halign='center',
            valign='middle'
        )
        self.card_label.bind(size=self.card_label.setter('text_size'))
        layout.add_widget(self.card_label)

        # Bottom Buttons (Flip & Next)
        btn_layout = BoxLayout(size_hint=(1, 0.2), spacing=10)
        
        self.flip_btn = Button(text="Show Answer", background_color=(0.1, 0.5, 0.8, 1))
        self.flip_btn.bind(on_press=self.flip_card)
        btn_layout.add_widget(self.flip_btn)

        self.next_btn = Button(text="Next Card", background_color=(0.2, 0.7, 0.3, 1))
        self.next_btn.bind(on_press=self.next_card)
        btn_layout.add_widget(self.next_btn)

        layout.add_widget(btn_layout)
        self.add_widget(layout)
        self.update_card()

    def on_enter(self):
        # Refresh data whenever returning to this screen
        self.data = load_data()
        subjects = list(self.data.keys())
        self.spinner.values = subjects
        if self.current_subject not in subjects and subjects:
            self.current_subject = subjects[0]
            self.spinner.text = self.current_subject
        self.current_index = 0
        self.update_card()

    def on_subject_select(self, spinner, text):
        self.current_subject = text
        self.current_index = 0
        self.showing_answer = False
        self.update_card()

    def update_card(self):
        cards = self.data.get(self.current_subject, [])
        if not cards:
            self.card_label.text = "No flashcards in this subject yet!\nClick 'Manage' to add some."
            self.date_label.text = ""
            self.flip_btn.disabled = True
            self.next_btn.disabled = True
        else:
            self.flip_btn.disabled = False
            self.next_btn.disabled = False
            if self.current_index >= len(cards):
                self.current_index = 0
            card = cards[self.current_index]
            self.showing_answer = False
            self.card_label.text = f"Q: {card['q']}"
            self.date_label.text = f"Added: {card.get('date', 'Unknown')}"
            self.flip_btn.text = "Show Answer"

    def flip_card(self, instance):
        cards = self.data.get(self.current_subject, [])
        if not cards:
            return
        card = cards[self.current_index]
        if not self.showing_answer:
            self.card_label.text = f"A: {card['a']}"
            self.flip_btn.text = "Show Question"
            self.showing_answer = True
        else:
            self.card_label.text = f"Q: {card['q']}"
            self.flip_btn.text = "Show Answer"
            self.showing_answer = False

    def next_card(self, instance):
        cards = self.data.get(self.current_subject, [])
        if cards:
            self.current_index = (self.current_index + 1) % len(cards)
            self.update_card()

    def go_to_manage(self, instance):
        self.manager.current = 'manage'

class ManageScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)

        layout.add_widget(Label(text="Add New Flashcard", font_size=20, size_hint=(1, 0.1)))

        # Subject input/selector
        sub_layout = BoxLayout(size_hint=(1, 0.1), spacing=10)
        sub_layout.add_widget(Label(text="Subject:", size_hint=(0.3, 1)))
        self.sub_input = TextInput(text="Science", multiline=False, size_hint=(0.7, 1))
        sub_layout.add_widget(self.sub_input)
        layout.add_widget(sub_layout)

        # Question input
        layout.add_widget(Label(text="Question:", size_hint=(1, 0.05)))
        self.q_input = TextInput(text="", multiline=True, size_hint=(1, 0.25))
        layout.add_widget(self.q_input)

        # Answer input
        layout.add_widget(Label(text="Answer:", size_hint=(1, 0.05)))
        self.a_input = TextInput(text="", multiline=True, size_hint=(1, 0.25))
        layout.add_widget(self.a_input)

        # Action Buttons
        act_layout = BoxLayout(size_hint=(1, 0.15), spacing=10)
        
        save_btn = Button(text="Save Card", background_color=(0.2, 0.7, 0.3, 1))
        save_btn.bind(on_press=self.save_card)
        act_layout.add_widget(save_btn)

        back_btn = Button(text="Back to Study", background_color=(0.8, 0.3, 0.2, 1))
        back_btn.bind(on_press=self.go_back)
        act_layout.add_widget(back_btn)

        layout.add_widget(act_layout)
        self.add_widget(layout)

    def save_card(self, instance):
        subject = self.sub_input.text.strip().capitalize()
        question = self.q_input.text.strip()
        answer = self.a_input.text.strip()

        if not subject or not question or not answer:
            return

        data = load_data()
        if subject not in data:
            data[subject] = []

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        data[subject].append({"q": question, "a": answer, "date": timestamp})
        save_data(data)

        # Clear inputs
        self.q_input.text = ""
        self.a_input.text = ""

    def go_back(self, instance):
        self.manager.current = 'study'

class FlashcardApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(StudyScreen(name='study'))
        sm.add_widget(ManageScreen(name='manage'))
        return sm

if __name__ == '__main__':
    FlashcardApp().run()