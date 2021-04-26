import sqlite3, os, glob, subprocess, shutil, PySimpleGUI as Sg

logo_data = b'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'

safety_path = 'E:\BackupBeforeTagging'

# Next two variables contain the two libraries darktable is using to store its stuff.

data_db = 'C:/OneDrive/OneDrive - 3c/Dokumente/40_Lightroom DB/darktable/data.db'
library_db = 'C:/OneDrive/OneDrive - 3c/Dokumente/40_Lightroom DB/darktable/library.db'


# Some tags we do not want to display, as they are more or less meaningless for a search / part of the hierarchy
# backbone

blacklist = ['1 Was', '2 Wo', '3 Wie', 'Dinge', 'Aktivitäten', 'Orte']


def tags_full(db_fetch):
    """"Function to create a list string of hierarchical tags (in Adobe Lightroom syntax) from the a database
    response. The resulting string will be written to the XMP-lr:Subject tag of the image.

    :param db_fetch: the response from the database (all tags with id, name, synonyms, flags) assigned to an image
    :type db_fetch: (db_fetch)
    :return: tag_list as str
    """

    tag_list = ''

    for row in db_fetch:

        if row[1].find('darktable') == -1:  # We remove the darktable inherent tags, which we don't need
            synonym = ''

            if row[2] is not None:                                  # Check if synonyms exist
                if row[2].find('|en:') != -1:                       # if the synonym includes a translation
                    synonym = row[2][0:row[2].find('|en:')]         # remove the english translation after |en:
                    synonym = synonym.replace(', ', ',').replace(' ,', ',').strip(',')   # Clean synonym
                else:
                    synonym = row[2]                                # if no translation included we take is as it is

            if synonym.find('{') != -1:                             # We do not want to have  the album_id in {}
                synonym = ''

            if synonym != '':                                   # if the synonym isn't empty...
                tag_list = tag_list + row[1][row[1].find('|') + 1:] + synonym + ';'  # Add the synonym to the string
            else:
                tag_list = tag_list + row[1][row[1].find('|') + 1:] + ';'            # if not just take the string

    return tag_list[:-1]


def tags_single(db_fetch):
    """"Function to create a list string of NON-hierarchical tags (in Adobe Lightroom syntax) from the a database
    response. The resulting string will be written to the EXIF:XPKeywords, IPTC:Keywords and XMP:Subject tag of the
    image.

    :param db_fetch: the response from the database (all tags with id, name, synonyms, flags) assigned to an image
    :type db_fetch: (db_fetch)
    :return: tag_list as list of keywords and tag_str as str (concatenates the list elements with ";")
    """

    tag_list = []

    for row in db_fetch:

        if row[1].find('darktable') == -1:      # we do not want to add darktable internal tags
            if row[1].find('Website') != -1:    # we want to see the full hierarchy for website tags
                tag_list = tag_list + [row[1][row[1].find('Website'):]]
            # Next one is a bit more complicated. We want to split the tag in its parts and add the synonym but
            # not the english translation
            else:
                synonym = ''
                if row[2] is not None:                          # if synonyms exist
                    if row[2].find('|en:') != -1:               # if the synonym includes a translation
                        synonym = row[2][0:row[2].find('|en:')]      # remove the english translation after |en:
                        synonym = synonym.replace(', ', ',').replace(' ,', ',').strip(',')   # clean the result string
                    else:                                       # if no translation included we take is as it is
                        synonym = row[2]
                tag_list = tag_list + row[1].split('|')         # split the list in parts
                if synonym != '':                                  # if the synonym isn't empty...
                    tag_list[-1] = tag_list[-1] + ',' + synonym    # we add the synonym to the last element of the tags

    tag_list = set(tag_list)
    tag_list = list(set(tag_list)-set(blacklist))

    tag_str = ''

    for item in tag_list:
        tag_str = tag_str + item + ';'

    return tag_list, tag_str[:-1]


def main_program(f_path, root_path_split_point):
    """Main unit  of dt_win_tagger. Reads all files in a specified folder (recursively), looks them up in the
    darktable database and reads the related tags. Calls then a subprocess with Phil Harveys exiftool.exe and
    writes the hierarchical and non-hierarchical tags to various places in the image metadata structure. A backup of
    each file is stored in the safety_path folder (retaining sub-folder structure) and a log file is written to
    safety_path\Foldername.log

    :param f_path: the folder with should be updated with tags
    :param root_path_split_point: the level after which the initial folder path is cut-off to create the backup folder
    in the backup destination
    :type f_path: (str)
    :type root_path_split_point: (int)"""

    # Connect the two darktable databases; we need both as tags table is in data.db, whereas tagged_images
    # is in library.db

    conn_db = sqlite3.connect(data_db)
    conn_lib = sqlite3.connect(library_db)

    d = conn_db.cursor()
    l = conn_lib.cursor()

    # Read the complete content of the folder to be tagged (all levels of folder hierarchy)

    f_path = f_path.replace('/', '\\')
    folder_content = []
    for filename in glob.iglob(f_path + '**/**', recursive=True):
        folder_content.append(filename)

    # Filter the file list for image files only - just to dave time / effort for looking into unnecessary files

    filtered_content = [x for x in folder_content if x[-3:].lower() in ('jpg', 'cr2', 'tif', 'arw', 'dng', 'orf')]

    # We want to give the user some information how fare we are in the process,
    # need to know how many files we have to tag

    total_files = len(filtered_content)
    counter = 0

    # Create the filename and open the logfile for writing

    log_filename = '-'.join(f_path.split(os.sep)[root_path_split_point:])+'.log'

    log_file = open('E:\\BackupBeforeTagging\\logfiles\\'+log_filename, 'a')

    # Now we run through all image file in the content list

    for image_file in filtered_content:

        counter += 1    # Increment  the "current state" image counter

        # We split of the image name and search for it in the database to get the image id and all the tag_ids assigned
        # to the image. This results in a data set with 0..n entries

        image_file_name = os.path.split(image_file)[1]
        original_path = os.path.split(image_file)[0]
        original_path = original_path.replace('/', '\\')
        # We do only want to retain a certain level of the folder structure when backing up the original files
        # Splitting the path into a list and concatenating if at a certain level with the safety_path

        folders = original_path.split(os.sep)
        backup_path = os.path.join(safety_path, os.sep.join(folders[root_path_split_point:]))

        if not os.path.exists(backup_path):
            os.makedirs(backup_path)

        # First db-query: we select all entries from tagged_images where the filename is equal to the one under
        # examination

        q_l = '''SELECT images.id, tagged_images.tagid
          FROM images
        LEFT JOIN tagged_images ON
        images.id = tagged_images.imgid
        where images.filename like '{filename}';'''.format(filename=image_file_name)

        l.execute(q_l)

        rows = l.fetchall()

        # If the data sets of tag_ids is not empty we lookup the tag names for all of them

        if rows:

            tags = '('

            for row in rows:
                tags = tags + str(row[1]) + ','

            tags = tags[:-1] + ')'

            q_d = '''SELECT id,
                   name,
                   synonyms,
                   flags
              FROM tags where id in {tags};'''.format(tags=tags)

            d.execute(q_d)

            rows = d.fetchall()

            # We have now a data set with all tags/keywords. We want two types of keywords: a list of the hierarchical
            # keywords broken down into its pieces (and blacklist removed), i.e., flat keywords and the hierarchical
            # keywords. For both we remove the darktable created tags, add the synonyms and remove the album_ids.
            # I will perhaps regret that once: but for now this will consider German language only

            # Create the tag strings for flat and hierarchical keywords

            taglist_hier = tags_full(rows)
            taglist, tag_str = tags_single(rows)

            # Print the status information for the end user

            print('Updating Imagefile {current}/{total}: {filename}'.format(current=counter,
                                                                            total=total_files, filename=image_file))

            # Create the list of input arguments for the subprocess.run function we are going to use.
            # NB: ran into a problem with the XMP:Subject and IPTC:Keywords when trying this with the pyExifTool module;
            # the logic as for EXIF:XPKeywords=A;B;C does not work (or better I cannot make it work) with the other two;
            # whatever I tried, I get a SINGLE tag in both which is a the input string with splitting it as indicated
            # by -sep ";". This works fine though in the ExifToolGUI... ;-(.

            exiftool_arguments_list = ['exiftool.exe',
                                       '-L',                               # Use Windows Latin1
                                       '-w EXT',
                                       '-sep ";"',                         # Use ; as a separator for the list of keywords
                                       '-EXIF:XPKeywords="'+tag_str+'"',   # Write EXIF Keywords (works for all file tpyes)
                                       '-XMP:Subject="'+tag_str+'"',       # Write XMP Keywords, works for JPG, TIF , DNG
                                       '-IPTC:Keywords="'+tag_str+'"',     # Write IPTC  Keywords, works for JPG, TIF , DNG
                                       '-XMP-lr:HierarchicalSubject="'+taglist_hier+'"', # Write hierarchical Keywords in Lightroom logic
                                       '"'+image_file+'"']

            # Now we run the subprocess with the arguments

            try:
                process_result = subprocess.run(" ".join(exiftool_arguments_list), capture_output=True)
            except Exception as e:
                print(e)

            # If we are successful with the transformation exiftool retains the original file which we write to the
            # backup directory

            if os.path.isfile(image_file+'_original'):
                shutil.move(image_file+'_original', backup_path)

            # We append the collected process output to the logfile

            log_file.write(image_file+';'+process_result.stdout.decode('utf-8').replace('\r\n', ';')
                           +process_result.stderr.decode('utf-8').replace('\r\n', ';')+'\n')

    "Successfully tagged all images - please click OK to return..."
    log_file.close()
    return


def create_gui():

    Sg.LOOK_AND_FEEL_TABLE['MyFototours'] = {'BACKGROUND': '#EEEEEE',
                                                     'TEXT': '#898989',
                                                     'INPUT': 'white',
                                                     'TEXT_INPUT': '#898989',
                                                     'SCROLL': '#c7e78b',
                                                     'BUTTON': ('white', '#C5241C'),
                                                     'PROGRESS': ('#01826B', '#D0D0D0'),
                                                     'BORDER': 2, 'SLIDER_DEPTH': 0, 'PROGRESS_DEPTH': 0,
                                                 }

    gui_theme = 'MyFototours'

    Sg.ChangeLookAndFeel(gui_theme)

    initial_dir = os.path.dirname(os.path.realpath(__file__))

    def win_main():

        layout = [[Sg.Image(data=logo_data, pad=((10, 0),(5, 0))), Sg.Text('Darktable Windows Tagger',
                            size=(30, 1), justification='right', font=("Helvetica", 17, 'bold'))],
            [Sg.Text('')],
            [Sg.Frame(layout=[
                [Sg.Text("Select a folder to tag       :"), Sg.Input(default_text=initial_dir, key="-DATA_FOLDER-", change_submits=True, size=(60, 1)),
                 Sg.FolderBrowse(key="-B_DATA_FOLDER-", initial_folder=initial_dir)],
                [Sg.Text('Level of directory to retain:'),Sg.Input(default_text=2, key="-ROOT-LEVEL-", change_submits=True, size=(1, 1))],
                [Sg.Button("Start", key="-TAG-START-", pad=((20, 10), (10, 10)))]
            ], title='Tag images on harddrive', font=("Helvetica", 12, 'bold'), title_color='#C5241C', relief=Sg.RELIEF_RAISED,
                tooltip='Use this to tag all images in the folder you select (including ALL subfolders). The second \n'
                        'parameter identifies the number of folder levels to be retained for backup folders \n')],
            [Sg.CloseButton(button_text='Close Program', key='-CLOSE-', pad=((200, 10), (10, 10)))]
        ]
        return Sg.Window('myFototours - Darktable2Piwigo', layout, grab_anywhere=True, default_element_size=(40, 1), finalize=True)

    def win_info():

        layout_info = [[Sg.Output(key='-ML2-' + Sg.WRITE_ONLY_KEY, size=(100, 20))],
                       [Sg.Button('OK')]]

        return Sg.Window('Information', layout_info, finalize=True)

    window1, window2 = win_main(), None

    while True:                                                             # The Event Loop
        window, event, values = Sg.read_all_windows()
        if event == Sg.WIN_CLOSED or event == 'Exit':
            window.close()
            if window == window2:  # if closing win 2, mark as closed and continue execution
                continue
            elif window == window1:  # if closing win 1, exit program
                break
        if event == 'OK':
            window.close()
            # if OK is clicked close the information window and continue
            continue
        if event == '-TAG-START-':
            if values['-B_DATA_FOLDER-'] == '':
                Sg.popup_ok('You did not edit the data folder. Continuing with:\n' +
                            values['-DATA_FOLDER-'])
            if values['-ROOT-LEVEL-'].isnumeric():
                window2 = win_info()
                main_program(values['-DATA_FOLDER-'], int(values['-ROOT-LEVEL-']))
            else:
                Sg.popup_ok('Please enter a number for Level of directory!')

    window.close()
    return


if __name__ == '__main__':

    create_gui()
