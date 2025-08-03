from kivy.app import App
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout

class AutoCompleteTextInput(TextInput):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._pairs = {
            '*': '**',
            '"': '""',
            '(': '()',
            '[': '[]',
            '{': '{}',
            '_': '__'
        }
        self._start_with = {
            '[ ': '[ ] ',
            '-[': '- [ ] ',
            '- [': '- [ ] ',
            '-x': '- [x] ',
            '[>': '[>] ',
            '[<': '[>] ',
            '[o': '[o] ',
            '[0': '[o] ',
            '[O': '[o] ',
            '[x': '[x] ',
            '[-': '[-] '
        }

    def insert_text(self, substring, from_undo=False):
        cc = self.cursor_col-1
        # Reemplaza los inicios
        if -1< cc < 2: # menos de 4 caracteres
            autext = self.text[:cc+1] + substring
            if autext in self._start_with:
                new_txt = self._start_with[autext]
                if len(self.text) >= len(new_txt):
                    if self.text[:len(new_txt)] != new_txt:
                        self.do_replace_start(new_txt, autext)
                    else:
                        return super().insert_text(substring, from_undo=from_undo)
                else:
                    self.do_replace_start(new_txt, autext)
            else:
                return super().insert_text(substring, from_undo=from_undo)
        # Reemplaza los caracteres de par
        elif substring in self._pairs:
            pair = self._pairs[substring]
            self.do_insert_pair(pair, len(substring))
        else:
            return super().insert_text(substring, from_undo=from_undo)

    def do_insert_pair(self, pair, offset):
        # Insert the pair and move cursor to middle
        cursor_pos = self.cursor_index()
        self.text = self.text[:cursor_pos] + pair + self.text[cursor_pos:]
        self.cursor = (cursor_pos + offset, 0)

    def do_replace_start(self, new_txt, old_txt):
        if new_txt[0] in self._pairs:
            cc = len(old_txt)
        else:
            cc = len(old_txt)-1
        self.text = new_txt + self.text[cc:]




class MyApp(App):
    def build(self):
        layout = BoxLayout(orientation='vertical')
        autocomplete_input = AutoCompleteTextInput()
        layout.add_widget(autocomplete_input)
        return layout

if __name__ == '__main__':
    MyApp().run()
