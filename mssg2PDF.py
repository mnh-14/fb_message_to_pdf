from ast import Tuple
import fpdf
import os, json, sys
import contextlib, datetime
from tkinter import Tk
from tkinter.filedialog import askdirectory, asksaveasfilename


CONSTANTS = {
    'font style': "BI",
    'text color': (20, 20, 20),
    'gray': (128, 128, 128),
    'light blue': (100, 100, 200),
    'max celllength': 135,
    'default font size': 26,
    "default fillcolor": (50,50,50),
    'fontB size': 14,
    'fontA size': 26,
    'minute gap': datetime.timedelta(minutes=15),
    'date gap': datetime.timedelta(minutes=30),
    # 'newdir': r"E:\fb massages\JSON version",
    # 'file path': "messages\\inbox\\",
    # 'own info': "messages\\autofill_information.json",
    'img width': 75,
    'img margin gap': 10
}

@contextlib.contextmanager
def fontsize(pdf: fpdf.FPDF, size):
    pdf.set_font_size(size)
    yield
    pdf.set_font_size(CONSTANTS['fontA size'])

@contextlib.contextmanager
def fillcolor(pdf: fpdf.FPDF, color: tuple):
    pdf.set_fill_color(*color)
    yield
    pdf.set_fill_color(*CONSTANTS['default fillcolor'])


def pick_correct_file() -> dict:
    """From user input, finds the accurate message.json file\n
    Returns the whole dictionarey"""
    with open(CONSTANTS['own info']) as own_info:
        own_data = json.load(own_info)
    while True:
        req_name = input("Enter the id name of the person you're looking: ")
        for folder in os.listdir(CONSTANTS['file path']):
            file_path = os.getcwd()+'\\'+ CONSTANTS['file path'] + folder + '\\message_1.json'
            with open(file_path) as json_file:
                message_dict = json.load(json_file)
                if req_name == message_dict['title']:
                    return message_dict, own_data['autofill_information_v2']
        else:
            print('Not Found .  .  .  !')
                    

def pick_user_file() -> dict:
    source_dir = askdirectory(title="Pick the unzipped 'Your facebook activity' folder")
    source_dir = source_dir.replace("your_facebook_activity", '')
    folder = askdirectory(title="Pick the message folder of your desired user")
    folder.replace('/', '\\')
    file_path = folder + "\\message_1.json"
    if os.path.isfile(file_path) == False:
        print("This folder doesn't have required files")
        return pick_user_file()
    with open(file_path) as json_file:
        message_dict = json.load(json_file)
        message_dict['source folder'] = source_dir
        return message_dict


def save_pdf(pdf: fpdf.FPDF):
    filepath = asksaveasfilename(
            title="Set file location and name",
            initialfile="something.pdf",
            filetypes=(("PDF files", "*.pdf"),))
    pdf.output(name=filepath)
    


# def create_nicknames_2(whole_data: dict)->str:
def set_name_nicknames(whole_data: dict)->str:
    """Creates a new dict of nicknames in main data(dict)\n
    Nicknames holds user name, user nickname and other participants nicknames"""
    own_name = ""
    for i, participant in enumerate(whole_data['participants']):
        print(str(i+1)+'. '+participant['name'])
    choice = int(input("Pick your name: (index)\n\t-> "))
    if choice <= 0 and choice > len(whole_data[participant]):
        print("Wrong choice !! Pick again")
        return set_name_nicknames(whole_data)
    own_name = whole_data["participants"][choice-1]['name']

    whole_data['nicknames'] = {}
    print("Give the nicknames for the participants. Give nothing if no nicknames are needed, in this case the full name will be added")
    for person in whole_data['participants']:
        whole_data['nicknames'][person['name']] = input(person['name']+"'s nickname: ") or person['name']
    # Show the data
    print("%25s %15s"%('Names :', 'Nicknames'))
    for key in whole_data['nicknames']:
        if key == own_name:
            print("<myself>", end=' ')
        print("%30s : %s"%(key, whole_data['nicknames'][key]))

    if (x:=input("are those data okk ? (yes/no) ").lower()) != 'yes' and (x != ''):
        set_name_nicknames(whole_data)
    
    return own_name


def mainfunc():
    """Handles everything"""
    # change current directory and get the messages
    # os.chdir(CONSTANTS['newdir'])
    # main_dict, own_info = pick_correct_file()
    main_dict = pick_user_file()
    main_dict['messages'].reverse()
    messages:list[dict] = main_dict['messages']
    own_name = set_name_nicknames(main_dict)
    
    #final confirmation
    proceed = input("Do you want to proceed (yes/no)?\n =>> ")
    if proceed.lower() == 'no':
        return 0

    # create the pdf object and get it ready to be written
    pdf = fpdf.FPDF('portrait', 'mm', 'letter')
    pdf.add_page()
    pdf.set_font('times', CONSTANTS['font style'], CONSTANTS['fontA size'])
    pdf.set_text_color(*CONSTANTS['text color'])
    pdf.set_fill_color(*CONSTANTS['gray'])
    pdf.set_auto_page_break(auto=True, margin=15)

    # get into the main loop
    prev_message = {'nickname': None, 'datetime': datetime.datetime.fromtimestamp(100000000)}
    text_count = 0
    for message in messages:
        #if text_count == 250:
        #    break
    
        # set nicknames, and datetimes
        message['nickname'] = main_dict['nicknames'][message['sender_name']]
        message['datetime'] = datetime.datetime.fromtimestamp(message['timestamp_ms']/1000)

        #write all the informations
        write_prev_timestamp(pdf, prev_message, message, own_name)
        write_nameplate(pdf, prev_message, message, own_name)
        write_messages(pdf, message, own_name)
        print_pictures(pdf, message, own_name, main_dict['source folder'])

        # update prev message and message number
        prev_message = message
        text_count += 1

    print("done. Total:", text_count, 'messages')
    # pdf.output(input('Enter you output file name: ') + '.pdf')
    save_pdf(pdf);



def write_prev_timestamp(pdf: fpdf.FPDF, prev_text:dict , cur_text:dict, own_name:str):
    """Checks if current message is a photo collection or text.\n
    If photo collection then just writes the timestamp \n
    If text, then defines the timestamp position and writes it to the PDF page """

    if prev_text.get('nickname') is None:   # Confirms weather it's the 1st message or not
        pass
    else:
        if 'photos' in prev_text:
            with fontsize(pdf, 13):
                pdf.cell(CONSTANTS['img width'], 6, prev_text['datetime'].strftime("  (%I:%M %p)"), ln=True, align='C')
        else:
            with fontsize(pdf, 13):
                if prev_text['sender_name'] == own_name:
                    pdf.cell((pdf.w-15-prev_text['cell_length']), 6, "")  # positioning timestamp for own texts
                    pdf.cell(prev_text['cell_length'], 6, prev_text['datetime'].strftime("(%I:%M %p)"), ln=True)
                else:
                    pdf.cell(prev_text['cell_length'], 6, prev_text['datetime'].strftime("(%I:%M %p)"), ln=True, align='R')


def write_nameplate(pdf: fpdf.FPDF, prev_text:dict , cur_text:dict, own_name:str):
    """Checks if time gap of two texts are big enough and writes name \n
    Then, checks if sender is changed and writes line break\n
    And finally, after any kind of line break, writes the current sender's name(Nickname) """

    is_line_break = False   # meaning no line break is written yet
    dt= prev_text.get('datetime')
    if (cur_text['datetime'] - dt) >= CONSTANTS['date gap']:
        pdf.ln()
        pdf.ln()
        is_line_break = True
        with fontsize(pdf, 18):
            pdf.cell(pdf.w-15, 9, cur_text['datetime'].strftime("%d-%m-%Y, %A"), align='C', ln=True)
            pdf.cell(0, 5, "", ln=True) # give a gap before next cell
    elif (cur_text['datetime'] - dt) >= CONSTANTS['minute gap']:
        pdf.ln()
        is_line_break = True
    elif cur_text['nickname'] != prev_text['nickname']:
        pdf.cell(0, 4, "", ln=True) # give a small line gap before next cell
        is_line_break = True
    # write the nickname of sender if needed
    if is_line_break:
        alingment = 'R' if cur_text['sender_name'] == own_name else 'L'
        with fontsize(pdf, CONSTANTS['fontB size']):
            pdf.cell(pdf.w-15, 7, cur_text['nickname'], ln=True, align=alingment)



def write_messages(pdf:fpdf.FPDF, cur_text:dict, own_name):
    """Skips photo collections\n
    Writes the messages after positioning them according to sender\n
    Writes removed message if no text is found"""

    if 'photos' in cur_text:
        return None
    removed_txt = "!!! Message Removed !!!"
    main_text = cur_text.get('content', removed_txt)
    cur_text['cell_length'] = get_cell_length(pdf, main_text)
    # align the cells and write those texts
    if cur_text['sender_name'] != own_name:
        with fillcolor(pdf, CONSTANTS['light blue']):
            pdf.multi_cell(cur_text['cell_length'], 13, main_text, border=True, align='L', fill=True, ln=True)
    else:
        with fillcolor(pdf, CONSTANTS['gray']):
            pdf.cell((pdf.w-15-cur_text['cell_length']), 13, '')
            pdf.multi_cell(cur_text['cell_length'], 13, main_text, border=True, align='L', fill=True, ln=True)



def get_cell_length(pdf:fpdf.FPDF, text:str):
    """Finds the longest line, and returns cell length based on it\n
    If exceeds max cell length, returns max cell length"""
    lines = text.split('\n')
    line_lengths = [len(line) for line in lines]
    i = max(line_lengths)
    cell_length = i*14 if i<=4 else i*6+10 if i<=8 else i*5  # function to get the cell length for different line length
    return cell_length if cell_length < CONSTANTS['max celllength'] else CONSTANTS['max celllength']



def print_pictures(pdf:fpdf.FPDF, curr_text:dict, own_name:str, source:str):
    """Works only if current text is a photo collection\n
    Iterates over the photo collection and prints them on sender align"""
    if (pictures:= curr_text.get('photos')) is None:
        return None
    else:
        left_margin = pdf.w-CONSTANTS['img margin gap']-15-CONSTANTS['img width']
        back_cell_length = CONSTANTS['img margin gap'] if curr_text['sender_name'] != own_name else left_margin
        pdf.cell(back_cell_length, 5, '')
        for a_photo in pictures:
            pdf.image(source+a_photo['uri'], None, None, CONSTANTS['img width'])



if __name__ == "__main__":
    tk_root = Tk()
    tk_root.withdraw()
    mainfunc()
