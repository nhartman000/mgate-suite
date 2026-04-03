#!/usr/bin/env python3
"""
Nych Android Application Entry Point
"""

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView

import sys
sys.path.insert(0, '/data/data/org.mgate.nych/files/app')

from nych import Nych


class NychApp(App):
    def build(self):
        self.nych = Nych()
        
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        self.input = TextInput(
            hint_text='Enter word to process...',
            size_hint_y=0.15,
            font_size=18
        )
        layout.add_widget(self.input)
        
        process_btn = Button(
            text='PROCESS WORD',
            size_hint_y=0.1,
            background_color=(0.2, 0.6, 0.9, 1),
            font_size=16
        )
        process_btn.bind(on_press=self.process_word)
        layout.add_widget(process_btn)
        
        self.result_label = Label(
            text='Nych Subsystem Ready\n\nEnter a word above and tap PROCESS',
            size_hint_y=0.75,
            font_size=16,
            text_size=(None, None)
        )
        
        scroll = ScrollView()
        scroll.add_widget(self.result_label)
        layout.add_widget(scroll)
        
        return layout
    
    def process_word(self, instance):
        word = self.input.text.strip()
        if not word:
            return
        
        result = self.nych.process(word)
        
        output = f"INPUT: {word}\n\n"
        output += f"EMOJI: {result.emoji}\n"
        output += f"SIGNATURE: {result.phonetic_signature}\n"
        output += f"MODALITY: {result.modality_match.name}\n"
        output += f"SCORE: {result.gestalt_score:.3f}\n\n"
        output += "FEATURES:\n"
        for k, v in result.metadata['gestalt_features'].items():
            output += f"  {k}: {v:.2f}\n"
        
        self.result_label.text = output


if __name__ == "__main__":
    NychApp().run()
