import sqlite3, os, exiftool, glob

f_path = 'C:/OneDrive/OneDrive - 3c/Bilder/Fotos/Online/2021/'
safety_path = 'C:/Users/ThomasRoch(Privat)/Desktop/Backup/'

data_db = 'C:/OneDrive/OneDrive - 3c/Dokumente/40_Lightroom DB/darktable/data.db'
library_db = 'C:/OneDrive/OneDrive - 3c/Dokumente/40_Lightroom DB/darktable/library.db'

blacklist = ['1 Was', '2 Wo', '3 Wie', 'Dinge', 'Aktivitäten', 'Orte']


def tags_full(db_fetch):

    tag_list = ''

    for row in db_fetch:
        if row[1].find('darktable'):
            tag_list = taglist + row[1][row[1].find('|') + 1:] + ';'

    return tag_list[:-1]


def tags_single(db_fetch):

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
                        synonym = synonym.strip(', ').strip(' ,')    # clean the result string
                    else:                                       # if no translation included we take is as it is
                        synonym = row[2]
                tag_list = tag_list + row[1].split('|')         # split the list in parts
                if synonym != '':                                  # if the synonym isn't empty...
                    tag_list[-1] = tag_list[-1] + ',' + synonym    # ...we add the synonym to the last element of the tags

    tag_list = set(tag_list)
    tag_list = list(set(tag_list)-set(blacklist))

    tag_str = ''

    for item in tag_list:
        tag_str = tag_str + item + ';'

    return tag_str[:-1]


conn_db = sqlite3.connect(data_db)
conn_lib = sqlite3.connect(library_db)

d = conn_db.cursor()
l = conn_lib.cursor()

folder_content = []
for filename in glob.iglob(f_path + '**/**', recursive=True):
    folder_content.append(filename)

filtered_content = [x for x in folder_content if x[-3:].lower() in ('jpg', 'cr2', 'tif', 'arw', 'dng')]

with exiftool.ExifTool(executable_='C:/Program Files (x86)/exiftool/exiftool.exe') as et:
    for image_file in filtered_content:
        image_file_name = os.path.split(image_file)[1]
        print(image_file_name)
        q_l = '''SELECT images.id, tagged_images.tagid
          FROM images
        LEFT JOIN tagged_images ON
        images.id = tagged_images.imgid
        where images.filename like '{filename}';'''.format(filename=image_file_name)

        l.execute(q_l)

        rows = l.fetchall()

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

            taglist = ''

            params = map(exiftool.fsencode, ['-exif:XPKeywords={tags}'.format(tags=taglist),
                                                image_file])
            et.execute(*params)

            taglist = tags_single(rows)
            print(taglist)

            params = map(exiftool.fsencode, ['-exif:XPKeywords={tags}'.format(tags=taglist),
                                                image_file])
            et.execute(*params)

            if os.path.isfile(image_file+'_original'):
                os.replace(image_file+'_original', safety_path+image_file_name)