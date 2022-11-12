import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk


class GridWindow(Gtk.Window):
    def __init__(self):

        super().__init__(title="Grid Example")

        self.master_grid = Gtk.Grid()
        self.toolbar_grid= Gtk.Grid()
        self.music_grid=Gtk.Grid()
        self.num_instruments=4
        self.num_columns=4
        self.instrument_inputs = [Gtk.Entry() for x in range (self.num_instruments)]
        self.music_matrix=[[Gtk.Entry() for y in range(self.num_columns)] for x in range (self.num_instruments)]
        
        add_column_button = Gtk.Button(label="Add columns")
        remove_column_button = Gtk.Button(label="Remove columns")
        add_instrument = Gtk.Button(label="Add instrument")
        remove_instrument = Gtk.Button(label="Remove Instrument")


        add_column_button.connect("clicked", self.on_click_add_column_button)
        remove_column_button.connect("clicked", self.on_click_remove_column_button)
        add_instrument.connect("clicked", self.on_click_add_instrument_button)
        remove_instrument.connect("clicked", self.on_click_remove_instrument_button)

        
        self.toolbar_grid.add(add_column_button)
        self.toolbar_grid.attach_next_to(remove_column_button,add_column_button,Gtk.PositionType.RIGHT, 1, 1)
        self.toolbar_grid.attach_next_to(add_instrument,remove_column_button,Gtk.PositionType.RIGHT, 1, 1)
        self.toolbar_grid.attach_next_to(remove_instrument,add_instrument,Gtk.PositionType.RIGHT, 1, 1)

        self.music_grid.add(self.instrument_inputs[0])
        for i in range(1,len(self.instrument_inputs)):
            self.music_grid.attach_next_to(self.instrument_inputs[i], self.instrument_inputs[i-1], Gtk.PositionType.BOTTOM, 1, 1)
        
        for i in range(len(self.music_matrix)):
            for j in range(len(self.music_matrix[i])):
                if j==0:
                    self.music_grid.attach_next_to(self.music_matrix[i][j], self.instrument_inputs[i], Gtk.PositionType.RIGHT, 1, 1)
                else:
                    self.music_grid.attach_next_to(self.music_matrix[i][j], self.music_matrix[i][j-1], Gtk.PositionType.RIGHT, 1, 1)
        self.master_grid.add(self.toolbar_grid)
        self.master_grid.attach_next_to(self.music_grid, self.toolbar_grid, Gtk.PositionType.BOTTOM, 1, 1)
        self.add(self.master_grid)
    
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
        self.num_instruments+=1
        self.instrument_inputs.append(Gtk.Entry())
        self.music_grid.attach_next_to(self.instrument_inputs[self.num_instruments-1], self.instrument_inputs[self.num_instruments-2], Gtk.PositionType.BOTTOM, 1, 1)
        self.instrument_inputs[self.num_instruments-1].show()
        self.music_matrix.append([Gtk.Entry()])
        self.music_grid.attach_next_to(self.music_matrix[self.num_instruments-1][0],self.instrument_inputs[self.num_instruments-1], Gtk.PositionType.RIGHT, 1, 1)
        self.music_matrix[self.num_instruments-1][0].show()
        for j in range(1,self.num_columns):
            self.music_matrix[self.num_instruments-1].append(Gtk.Entry())
            self.music_grid.attach_next_to(self.music_matrix[self.num_instruments-1][j],self.music_matrix[self.num_instruments-1][j-1], Gtk.PositionType.RIGHT, 1, 1)
            self.music_matrix[self.num_instruments-1][j].show()

    def on_click_remove_instrument_button(self, button):
        if self.num_instruments>1:
            self.num_instruments-=1
            self.music_grid.remove(self.instrument_inputs[num_instruments-1])
            self.instrument_inputs.pop()

win = GridWindow()
win.connect("destroy", Gtk.main_quit)
win.show_all()
Gtk.main()