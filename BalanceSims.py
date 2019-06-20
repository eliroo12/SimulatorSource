import BRDgui as brd
import DNCgui as dnc
import PySimpleGUI as sg


def main():
    layout = [[sg.Button('Dancer',size=(10,2)),sg.Button('Bard',size=(10,2))]]
    window = sg.Window("Simulator",icon='graphics\\DRK.png').Layout(layout)

    while True:
        button, values = window.Read(timeout=100)

        if button is None:
            break

        if button == 'Dancer':
            dnc.main()
        if button == 'Bard':
            brd.main()


main()