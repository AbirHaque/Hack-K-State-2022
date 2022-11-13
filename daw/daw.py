import gi
from parser import Parser
import numpy as np
import simpleaudio as sa
from scipy.io.wavfile import write
import threading
import requests
from appwrite.client import Client
from appwrite.input_file import InputFile
from appwrite.services.storage import Storage

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
        self.samples_per_note=11025#44100/4
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
        self.thread_results=[0,0,0,0]



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
    def signal_computation_thread(self,id,buf,queue):
        parser=Parser()
        final_audio=[0 for x in range(len(buf[0])*self.samples_per_note)] 
        for j in range(len(buf[0])):
            for i in range(len(buf)):
                for t in range(0+j*self.samples_per_note,self.samples_per_note+j*self.samples_per_note):
                    tmp=[token if token!="f" else self.note_frequency_mapping[i][1] for token in queue]#self.note_frequency_mapping[i][1] for token in queue]
                    tmp=[(token if token!='t' else str(t)) for token in tmp]
                    tmp=[(token if token!="a" else str(buf[i][j])) for token in tmp]                    
                    final_audio[t]+=parser.calculate(tmp)
        self.thread_results[id]= final_audio


    def gen_wav_binary(self):
        num_notes=len(self.music_matrix[0])
        num_samples=num_notes*self.samples_per_note
        num_rows=len(self.music_matrix)
        num_chunks=int((num_samples/self.sample_rate)+((num_samples%self.sample_rate)!=0))#Ceiling division
        equation=self.instrument_combo.get_child().get_text()
        parser=Parser()

        final_audio=[]#[0 for x in range(num_samples)] 


        buf=np.array([[0 for y in range(len(self.music_matrix[0]))] for x in range(len(self.music_matrix))])
        for i in range(len(self.music_matrix)):
            for j in range(len(self.music_matrix[i])):
                buf[i][j]=0 if self.music_matrix[i][j].get_text()=="" else float(self.music_matrix[i][j].get_text())
        queue = parser.shunting_yard(equation)
        partitions=np.hsplit(buf, 4)
        t1 = threading.Thread(target=self.signal_computation_thread,args=(0,partitions[0],queue))
        t2 = threading.Thread(target=self.signal_computation_thread,args=(1,partitions[1],queue))
        t3 = threading.Thread(target=self.signal_computation_thread,args=(2,partitions[2],queue))
        t4 = threading.Thread(target=self.signal_computation_thread,args=(3,partitions[3],queue))
        

        # start threads
        t1.start()
        t2.start()
        t3.start()
        t4.start()
    
        # wait until threads finish their job
        t1.join()
        t2.join()
        t3.join()
        t4.join()
        
        for result in self.thread_results:
            final_audio=final_audio+result

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
        client = Client()
        client.set_endpoint('http://10.150.152.83/80/v1').set_project('636f70dd0ab3fd35c183')
        storage = Storage(client)
        result = storage.create_file('636f70ff960601600409', 'sdfiosjdf', InputFile.from_path('tmp.wav'))
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