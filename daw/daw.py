import gi
from parser import Parser
import numpy as np
import simpleaudio as sa
from scipy.io.wavfile import write
import threading
import requests

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk


class GridWindow(Gtk.Window):
    def __init__(self):

        super().__init__(title="Grid Example")

        self.master_grid = Gtk.Grid()
        self.toolbar_grid= Gtk.Grid()
        self.compose_grid=Gtk.Grid()
        self.pitch_grid=Gtk.Grid()
        self.music_grid=Gtk.Grid()
        self.set_default_size(200, 200)
        #self.music_grid.size_allocate(Gdk.Rectangle(0,0,2,2))

        self.num_pitches=13
        self.num_columns=4
        self.sample_rate=44100
        self.note_frequency_mapping=[
            ('C4','261.63'),
            ('C#4',' 277.18'),
            ('D4','293.66'),
            ('D#4','311.13'),
            ('E4','329.63'),
            ('F4','349.23'),
            ('F#4','369.99'),
            ('G4','392.00'),
            ('G#4','415.30'),
            ('A4','440.00'),
            ('A#4','466.16'),
            ('B4','493.88'),
            ('C5','523.25'),
        ]
        self.note_frequency_mapping.reverse()
        self.pitch_entries = [Gtk.Entry(text=str(self.note_frequency_mapping[x][0]),editable=False) for x in range (self.num_pitches)]
        self.music_matrix=[[Gtk.Entry() for y in range(self.num_columns)] for x in range (self.num_pitches)]
        
        self.instrument_store = Gtk.ListStore(str)

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)

        self.instrument_combo = Gtk.ComboBox.new_with_model_and_entry(self.instrument_store)
       
        renderer_text = Gtk.CellRendererText()
        self.instrument_combo.pack_start(renderer_text, True)
        self.instrument_combo.add_attribute(renderer_text, "text", 1)
        self.instrument_combo.connect("changed", self.on_instrument_combo_changed)
        self.instrument_combo.set_entry_text_column(0)
        self.instrument_combo.set_active(0)


        add_instrument_button = Gtk.Button(label="Add Instrument")
        remove_instrument_button = Gtk.Button(label="Remove Instrument")
        add_column_button = Gtk.Button(label="Add columns")
        remove_column_button = Gtk.Button(label="Remove columns")
        play = Gtk.Button(label="Play")
        stop = Gtk.Button(label="Stop")
        load = Gtk.Button(label="Load")
        save = Gtk.Button(label="Save")
        export = Gtk.Button(label="Export")

        add_column_button.connect("clicked", self.on_click_add_column_button)
        remove_column_button.connect("clicked", self.on_click_remove_column_button)
        add_instrument_button.connect("clicked", self.on_click_add_instrument_button)
        remove_instrument_button.connect("clicked", self.on_click_remove_instrument_button)
        play.connect("clicked", self.on_click_play)
        '''
        stop.connect("clicked", self.on_click_remove_instrument_button)
        load.connect("clicked", self.on_click_remove_instrument_button)
        save.connect("clicked", self.on_click_remove_instrument_button)
        '''
        export.connect("clicked", self.on_click_export)
        
        toolbar_elements=[self.instrument_combo,add_instrument_button,remove_instrument_button,play,stop,load,save,export,add_column_button,remove_column_button]
        self.toolbar_grid.add(toolbar_elements[0])
        for i in range(1,len(toolbar_elements)):
            self.toolbar_grid.attach_next_to(toolbar_elements[i],toolbar_elements[i-1],Gtk.PositionType.RIGHT, 1, 1)

        self.pitch_grid.add(self.pitch_entries[0])
        for i in range(1,len(self.pitch_entries)):
            self.pitch_grid.attach_next_to(self.pitch_entries[i], self.pitch_entries[i-1], Gtk.PositionType.BOTTOM, 1, 1)
        
        for i in range(len(self.music_matrix)):
            for j in range(len(self.music_matrix[i])):
                if i == 0 and j == 0: 
                    self.music_grid.add(self.music_matrix[i][j])
                elif i == 0:
                    self.music_grid.attach_next_to(self.music_matrix[i][j], self.music_matrix[i][j-1], Gtk.PositionType.RIGHT, 1, 1)
                else:
                    self.music_grid.attach_next_to(self.music_matrix[i][j], self.music_matrix[i-1][j], Gtk.PositionType.BOTTOM, 1, 1)
        



        self.compose_grid.add(self.pitch_grid)
        self.compose_grid.attach_next_to(self.music_grid, self.pitch_grid, Gtk.PositionType.RIGHT, 1, 1)
        


        self.master_grid.add(self.toolbar_grid)
        self.master_grid.attach_next_to(self.compose_grid, self.toolbar_grid, Gtk.PositionType.BOTTOM, 1, 1)
        self.add(self.master_grid)
    def is_float(self, val):
        try:
            val=float(val)
            return True
        except:
            return False
    def gen_wav_binary(self):
        sample_rate=44100
        num_notes=len(self.music_matrix[0])
        samples_per_note=11025#44100/4
        num_samples=num_notes*samples_per_note
        num_rows=len(self.music_matrix)
        num_chunks=int((num_samples/sample_rate)+((num_samples%sample_rate)!=0))#Ceiling division
        equation=self.instrument_combo.get_child().get_text()
        parser=Parser()

        final_audio=[0 for x in range(num_samples)] 


        buf=[[0 for y in range(len(self.music_matrix[0]))] for x in range(len(self.music_matrix))]
        for i in range(len(self.music_matrix)):
            for j in range(len(self.music_matrix[i])):
                #if j >=1 and self.music_matrix[i][j-1].get_text()!="" and self.music_matrix[i][j].get_text()=="" :
                #    buf[i][j]=buf[i][j-1]#float(self.music_matrix[i][j-1].get_text())
                #else:
                #    buf[i][j]=0 if self.music_matrix[i][j].get_text()=="" else float(self.music_matrix[i][j].get_text())
                buf[i][j]=0 if self.music_matrix[i][j].get_text()=="" else float(self.music_matrix[i][j].get_text())
        for x in buf:
            for y in x:
                print(y,end=", ")
            print("")
        queue = parser.shunting_yard(equation)
        print(queue)
        print(num_samples)
        for j in range(len(buf[0])):
            for i in range(len(buf)):
                for t in range(0+j*samples_per_note,samples_per_note+j*samples_per_note):
                    tmp=[token if token!="f" else self.note_frequency_mapping[i][1] for token in queue]#self.note_frequency_mapping[i][1] for token in queue]
                    tmp=[(token if token!='t' else str(t)) for token in tmp]
                    tmp=[(token if token!="a" else str(buf[i][j])) for token in tmp]                    
                    final_audio[t]+=parser.calculate(tmp)
                
        return final_audio
    def on_click_play(self, button):
        final_audio=self.gen_wav_binary()
                    #print(final_audio[t])
        
        #write("example.wav", sample_rate, np.array(final_audio).astype(np.int16))
        print("Playing")
        play_obj = sa.play_buffer(np.array(final_audio).astype(np.int16), 1, 2, self.sample_rate)
        # wait for playback to finish before exiting
        play_obj.wait_done()
        print("Done.")
        
    def on_click_export(self, button):
        final_audio=self.gen_wav_binary()
        write("tmp.wav", self.sample_rate, np.array(final_audio).astype(np.int16))
        with open('tmp.wav', 'rb') as f:
            r = requests.post('http://10.150.152.83/v1/storage/buckets/636f70ff960601600409/files', files={'tmp.wav': f}, headers= {'X-Appwrite-Project': '636f70dd0ab3fd35c183'})
        print("Done")
    def on_click_add_column_button(self, button):
        self.num_columns+=1
        for i in range(len(self.music_matrix)):
            self.music_matrix[i].append(Gtk.Entry())
            self.music_grid.attach_next_to(self.music_matrix[i][len(self.music_matrix[i])-1], self.music_matrix[i][len(self.music_matrix[i])-2], Gtk.PositionType.RIGHT, 1, 1)
            self.music_matrix[i][len(self.music_matrix[i])-1].show()

    def on_click_remove_column_button(self, button):
        if self.num_columns>1:
            for i in range(len(self.music_matrix)):
                self.music_grid.remove(self.music_matrix[i][self.num_columns-1])
                self.music_matrix[i].pop()
            self.num_columns-=1
            #self.music_grid.remove_column(self.num_columns)



    def on_click_add_instrument_button(self, button):
        print(self.instrument_combo.get_child().get_text())
        self.instrument_store.append([self.instrument_combo.get_child().get_text()])
    def on_click_remove_instrument_button(self, button):
        self.instrument_store.remove(self.instrument_store[-1].iter)




    def on_instrument_combo_changed(self, combo):
        print("X")

win = GridWindow()
win.connect("destroy", Gtk.main_quit)
win.show_all()
Gtk.main()