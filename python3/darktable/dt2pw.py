"""
Module Darktable to Piwigo (dt2pw) connects two open source products: the photo managing and editing software Darktable
and the photo web presentation platform Piwigo. This software allows to create albums with images on Piwigo and update
the image data. In combination with an Excel Power Query file it allows full synchronization of images between Darktable
and Piwigo.
"""
import requests
import string
import random
import json
import csv
import pandas as pd
import os
import PySimpleGUI as Sg
import datetime

logo_data = b'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'


class Piwigo:
    """
    This class would likely not be necessary - only holds a number of common variables and a few static methods we need
    occasionally. Only 'serious' method is the resfresh_data classmethod which reads all information from Piwigo and
    stores it in various files in a selectable folder
    """

    # Main url for Piwigo API calls and a dictionary with the API methods used throughout the module

    url = 'http://myfototours.piwigo.com/ws.php?format=json'
    methods = {'login': 'pwg.session.login',
               'set_info': 'pwg.images.setInfo',
               'add_tag': 'pwg.tags.add',
               'search': 'pwg.images.search',
               'upload': 'pwg.images.addSimple',
               'read_album': 'pwg.categories.getAdminList',
               'read_tags': 'pwg.tags.getAdminList',
               'read_images': 'pwg.categories.getImages',
               'get_info': 'pwg.images.getInfo',
               'add_album': 'pwg.categories.add'
               }

    # Sub paths where the downloaded Piwigo data files are stored. Imgae files go into a separate folder:

    data_store_path = 'piwigo_data/'
    image_folder = 'imagedetails/'

    def __init__(self):
        self.account = Account()
        self.cookies = self.account.login()

    @classmethod
    def refresh_data(cls, main_path, images_included, album_included, tags_included):
        """
        Downloads album details, tags and all image details from Piwigo and stores the information in json file in a
        selectablle folder main_path (the selected folder is amended by data_store_path and for image files additionally
        with image_folder

        :param main_path: the folderpath where Piwigo data is downloaded to
        :type main_path: (str)
        """

        print('Starting download...')

        # Check if folders already exist and create them if not:

        if not os.path.exists(main_path + cls.data_store_path):
            os.mkdir(main_path + cls.data_store_path)

        if not os.path.exists(main_path + cls.data_store_path + cls.image_folder):
            os.mkdir(main_path + cls.data_store_path + cls.image_folder)

        # We need to login to get a valid cookie for download

        acc = Account()
        p_cookies = acc.login()

        # Now we can download the information step-by-step

        if album_included:
            print('Downloading Album data...')
            a = Album()
            albums = a.read_album_data(main_path + cls.data_store_path, 'albuminformation.json', p_cookies)
            del a

        if tags_included:
            print('Downloading Tags...')
            t = Tag()
            t.read_tag_data(main_path + cls.data_store_path, 'tags.json', p_cookies)
            del t

        if images_included:
            print('Start downloading Image data...')
            i = Image()
            i.read_image_data(main_path + cls.data_store_path + cls.image_folder, 'images', albums, p_cookies)
            del i

        print('Piwigo data refreshed - Click OK to continue')

        return 0

    @staticmethod
    def str_pad(integer_number, str_length):
        """
        Rather sure we can get this from a package ;-) - but this pads a string  with leading zeros. And yes we should
        definitely validate string length first or find a smarter way than using a fixed length padding pattern...

        :param integer_number: the number we want to pad with leading zeros
        :type integer_number: (int)
        :param str_length: expected length of the returned string
        :type str_length: (int)
        :return: padded string: (str)
        """

        # We use this padstring to copy a number of 0 into the padded string

        pad_string = '000000000000000'

        # A minimum level of error management

        if len(str(integer_number)) < str_length:
            padded = pad_string[:str_length - len(str(integer_number))] + str(integer_number)
        elif len(str(integer_number)) == str_length:
            padded = str(integer_number)
        else:
            call_error('Could not created padded string - returning original value', '', 'soft')
            padded = str(integer_number)

        return padded

    @staticmethod
    def pw_search_image(dt_id_str, cookies):
        """
        Searches an image on Piwigo platform using the Darktable id - works based on the image title on Piwigo which is
        set to be something like 'Image pw_id_str - dt_id_str'

        :param dt_id_str: the Darktable id including leading zeros
        :type dt_id_str: (str)
        :param cookies: a valid cookie to authenticate against Piwigo
        :type cookies: (dict)
        """

        data = {'query': dt_id_str,
                }

        method = Piwigo.methods['search']

        r = requests.post(Piwigo.url + '&method=' + method, data, cookies=cookies)

        # Piwigo returns a *list* of matching image ids as a result, we can only use this if the result is unique

        if len(r.json()['result']['images']) == 0:
            return 0
        elif len(r.json()['result']['images']) == 1:
            return r.json()['result']['images'][0]['id']
        else:
            return -1

    @staticmethod
    def create_random_string(number_of_characters):
        """
        Creates a random uppercase string (ascii + digits) of a defined length

        :param number_of_characters: length of the returned string
        :type number_of_characters: (int)
        """

        selection_space = string.ascii_uppercase + string.digits  # We want only letters in uppercase and numbers

        random_string = ''.join(random.choice(selection_space) for i in range(number_of_characters))

        return random_string


class Account:
    """
    The Account class does not provide much: only a method to login more or less
    """

    # Account details are stored in system variables, to obfuscate them

    def __init__(self):
        self.username = os.environ.get('PWG_USER_NAME')  # We could have achieved 'pw_data' without stating username
        self.password = os.environ.get('PWG_USER_PWD')  # /password explicitly - but this is hopefully future proof
        self.login_data = {'username': self.username,
                           'password': self.password}

    def login(self):
        """
        Login method, sends a login request to Piwigo and returns a session cookie if successful

        :return cookies: (dict)
        """
        method = Piwigo.methods['login']

        r = requests.post(Piwigo.url + '&method=' + method, self.login_data)

        if r.status_code != 200:
            return call_error('Could not login the provided user...Exiting', json.dumps(r.json()), 'hard')
        else:

            # The required key is returned as part of the 'Set-Cookie' parameter in the response header

            token = r.headers['Set-Cookie']

            # We need to juggle around a bit with the string returned

            token = token[token.find('pwg_id') + 7:token.find(';', token.find('pwg_id'))]

            cookies = {'pwg_id': token}

            return cookies


class Album:
    """
    Creates variables and methods required to manage albums (and collections) in Piwigo. An album is has 0...n images
    assigned.  A method to upload an entire album is provided based on reading a folder of jpg files to a single album.
    A collection is defined here as a list of images assigned to 1..n albums - the list of images is provided in a
    single file with and can include multiple attributes for an image.
    """

    id_file_name = 'album_id'         # Filename where the program will find the album_id
    tag_list_file = 'album_tags.csv'  # Filename where the program will find the tags for every image
    image_file_type = 'jpg'           # We build this for jpg files only for now.
    standard_album = 33               # The id of the default album to use (here: Miscellaneous)
    album_string = 'album_id = '       # The string which is used in the album id file as lead into the id itself

    def __init__(self):
        self.directory = Directory(type=Album.image_file_type)
        self.id_file = File(name=Album.id_file_name, extension='')
        self.tag_file = File(name_w_extension=Album.tag_list_file)
        self.id = Album.standard_album
        self.tags = pd.DataFrame

        self.image_collection = pd.DataFrame
        self.data_file = File()

    def read_album_data(self, f_path, f_name_w_ext, cookies):
        """
        Reads all album information from Piwigo (also non-public, but user logged in must have access to the albums
        in scope) and stores it in the specficied location with the specified name in JSON format.

        :param f_path: Full path were the result file is stored
        :type f_path: (str)
        :param f_name_w_ext: Filename under which the album information is stored with its extension
        :type f_name_w_ext: (str)
        :param cookies: Valid cookie to authenticate request against Piwigo
        :type cookies: (dict)
        :return: album_content (in json format): dict
        """

        data = {'recursive': 'true',
                'public': 'false',
                'tree_output': 'false',
                'fullname': 'true'}

        method = Piwigo.methods['read_album']

        r = requests.get(Piwigo.url + '&method=' + method, data, cookies=cookies)

        if r.status_code != 200:
            call_error('Error reading the album data from Piwigo...Skipping', json.dumps(r.json), 'soft')
        else:
            json_string = json.dumps(r.json())
            self.data_file.set_file(path=f_path, name_w_extension=f_name_w_ext)
            self.data_file.save_data(json_string)
            print('Album data downloaded and saved to ' + self.data_file.full_path)

        return r.json()

    def create_new_album(self, cookies, f_path):
        """
        Creates a new, public album on top level in Piwigo. Used if no album id is provided when uploading a new folder
        of images. Also creates the album_id file in the image folder after successful album creation.

        :param cookies: a valid authentication cookie for Piwigo
        :type cookies: (dict)
        :param f_path: the folder path to create the album_id file after successful album creation
        :type f_path: (str)
        """

        # No this isn't very creative, but the album needs a name (which can be changed later)

        data = {'name': datetime.datetime.now().strftime('%Y-%m-%d_%H%M%S'),
                'visible': 'true',
                'status': 'public'
                }

        method = Piwigo.methods['add_album']

        # Creating the new album and assigning the album_id

        r = requests.get(Piwigo.url + '&method=' + method, data, cookies=cookies)

        if r.status_code != 200:
            call_error('Could not create album...Skipping', json.dumps(r.json()), 'soft')
            self.id = Album.standard_album
        else:
            self.id = int(r.json()['result']['id'])

        # We also need to create the album_id file so that we can re-use it later

        f = File(path=f_path, name=Album.id_file_name, extension='')

        content = Album.album_string + str(self.id)

        f.save_data(content)

        del f

        return r.json()

    def read_album_id(self):
        """
        Reads the (Piwigo) id of an album from a file which is located in the album directory and stored under the name
        defined in the class variable id_file_name. The read process starts after a fixed number of characters (we assume
        "album_id = xxx").
        The album must exist in Piwigo before load. If album id is void  uploads are not rejected but images are found
        under "Orphans" in Piwigo

        :return int album_id:
        """

        content = self.id_file.load_file()

        if Album.album_string in content:
            try:
                self.id = int(content[len(Album.album_string)-content.find(Album.album_string):])
            except Exception as e:
                call_error('Could not read album id from existing file...Setting to Miscellaneous', e, 'soft')
                self.id = Album.standard_album

        return self.id

    def upload_album(self, f_path):
        """
        Reads all images from a folder and loads them to a Piwigo Account. An album_id to load to as well as a tags
        for each image is read from fixed files if provided. The Routine detects automatically if an image is already
        existing in the Piwigo Account and updates only if detected. Image filename and title in Piwigo are created /
        updated to contain the dt_id / dt_id & pw_id respectively.

        :param f_path: the fully qualified path where the album to upload can be found
        :type f_path: (str)
        :return: None
        """

        print('Start uploading / updating album in ' + f_path)

        # Set the path for: (1) the album itself, (2) the optional album_id file (3) the optional tag_list file

        self.directory.set_path(f_path)
        self.id_file.set_file(name=Album.id_file_name, extension='', path=f_path)
        self.tag_file.set_file(name_w_extension=Album.tag_list_file, path=f_path)

        # We need to login and provide a cookie to the upload / update methods of image. We need to put this here
        # if we don't want to login for every image instance...

        acc = Account()
        a_cookies = acc.login()

        # Check if album file exists and read if so. If album file does not exist create new public album with current
        # date and time as name. NOTE: If no images are available already only an additional ASSIGNMENT to the new album
        # is UPDATED on the existing images

        if self.directory.check_file_existence(self.id_file.name + self.id_file.extension):
            self.id = self.read_album_id()
        else:
            self.create_new_album(a_cookies, f_path)

        # Check if tag_list exists and read into a pandas dataframe

        if self.directory.check_file_existence(self.tag_file.name + self.tag_file.extension):
            self.tags = self.tag_file.load_file()
            tags = True
        else:
            tags = False

        # Read the file list from the directory

        self.directory.set_file_list()

        # Loop through all files in the directory

        for file in self.directory.file_list:

            # Instantiate the image and set the respective dt_id and pw_id

            image = Image(name_w_extension=file.name, path=self.directory.path, album_id=self.id, cookies=a_cookies)

            image.set_dt_id()
            image.set_pw_id()

            # Only if (1) the image cannot be uniquely identified or (2) doesn't exist on Piwigo we throw an error

            if image.pw_id == -1:
                print('WARNING: Piwigo search returned multiple results for ' + image.dt_id_str + ' ... Skipping')
                continue
            else:
                image.upload_image()  # if pw_id = 0 (new image) case is handled inside the  upload method
                image.set_pw_image_filename()  # we do not need to provide 'extension' here - included in name!
                image.set_pw_imagename()
                if tags:  # If tag_file was loaded AND the dt_id is in the list then only we read the tag
                    if image.dt_id not in self.tags.values:
                        image.set_image_tags(image.default_attribute)
                    else:
                        buffer = self.tags.loc[self.tags['dt_id'] == image.dt_id]
                        image.set_image_tags(buffer.iloc[0]['tagList'])
                        # Alternatively this single line should also work:
                        # image.set_image_tags(self.tags.loc[self.tags['dt_id'] == image.dt_id]['tagList'].values[0])

                image.category_switcher()  # Upload requires 'category' and setInfo requires 'categories' attribute

                # Not sure if this should be the final behavior but for an UPDATE this would REPLACE the existing
                # filename, title and tag list

                image.update_image_data(sv_mode='replace', mv_mode='replace', verbose=False)

        print('Successfully uploaded / updated images...Click OK to continue')

    def update_collection(self, f_full_path, l_mode, l_refresh, **kwargs):
        """
        This function updates a collection of images with attributes provided in the specified load file. Minimum file
        content is the dt_id and the pw_id (with which we can update the filename and the image title if required.
        Additionally, the following attributes can be provided (column names must equal attributes below):
            - tags: comma separated list of tags
            - album_ids: comma separated list of album_ids
            - description: text for the image description

        :param f_full_path: full path (directory and filename) of the loadfile
        :type f_full_path: (str)
        :param l_mode:  a boolean flag indicating the mode for the setInfo method of the Piwigo API; either 'append' or 'replace' (true = do not overwrite, false: do overwrite)
        :type l_mode: (str)
        :param l_refresh: a boolean flag indicating if the filename and imagetitle should be refreshed or not
        :type l_refresh: (bool)
        :param kwargs: takes additional parameters to be passed to the load_file method. 'type' defines the file type as in 'csv' or 'xls', 'sheet' can take an additional sheet name parameter (defaulted to 'Tabelle1')
        :return: None
        """

        print('Start updating collection...')

        # Load the file with the collection data set

        image_file = File(full_path=f_full_path)

        self.image_collection = image_file.load_file(sheet=kwargs.get('sheet', 'Tabelle1'))

        # Validate if content is loadable

        if 'pw_image_id' not in self.image_collection.columns or 'dt_image_id' not in self.image_collection.columns:
            call_error('Could not load file: pw_image_id and dt_image_id must be in file...Exiting', '', 'hard')

        # Following statement can /should be uncommented if we want to make sure that at a minimum album_ids or tags or
        # description is in the file. If we do so however, we cannot update image filename and title on Pw only.

        # if self.image_collection.shape[1] < 3:
        #    call_error('File does not contain enough data, provide at least one more column...Exiting', '', 'hard')

        # Login first:

        acc = Account()
        c_cookies = acc.login()

        for row in self.image_collection.iterrows():

            change_string = ''

            # Create instance of image object:
            image = Image(cookies=c_cookies)

            # Set the ids:
            image.set_pw_id(pw_id=row[1].get('pw_image_id'))
            image.set_dt_id(dt_id=row[1].get('dt_image_id'))

            image.get_pw_image_data()

            # Check if filename and image title should be refreshed:
            if l_refresh:
                image.set_pw_image_filename()
                image.set_pw_imagename()
                change_string = 'filename, title, '

            # Check if we shall append or overwrite existing information
            if not l_mode:
                image.sv_mode = 'fill_if_empty'     # This is actually not really 'append' but...
                image.mv_mode = 'append'
            else:
                image.sv_mode = 'replace'
                image.mv_mode = 'replace'

            # Following three if-statements sets other data elements if they are provided in the loadfile
            if 'tags' in self.image_collection.columns:
                image.set_image_tags(str(row[1].get('tags')))
                if image.tag_ids == 'nan':
                    image.tag_ids = image.default_attribute
                else:
                    change_string = change_string + 'tags, '

            if 'album_ids' in self.image_collection.columns:
                image.album_ids = str(row[1].get('album_ids'))
                if image.album_ids == 'nan':
                    image.album_ids = image.default_attribute
                else:
                    change_string = change_string + 'album_ids, '

            if 'description' in self.image_collection.columns:
                image.pw_image_description = row[1].get('description')
                if image.pw_image_description == 'nan':
                    image.pw_image_description = image.default_attribute
                else:
                    change_string = change_string + 'description '

            # And finally load the image data to Piwigo
            image.update_image_data(sv_mode=image.sv_mode, mv_mode=image.mv_mode, changed=change_string, verbose=True)

            # We delete the instance for memory purposes. Better safe than sorry
            del image

        print('Finished updating collection data - click OK')


class Image:
    """
    The image class is the core of this module. Includes a number of methods to upload, and update image information
    """
    default_attribute = '&***&'  # Defines default pattern which we remove from data record if not replaced
    image_name_separator = ' - '  # Defines pattern how in pw the image name is separating dt_id#separator#pw_id
    file_name_splitter = '__'  # Defines the pattern which separates dt_id in filename (needs to be set in dt)
    dt_id_std_length = 6  # We assume never more than 1M images in dt
    pw_id_std_length = 5  # We assume never more than 100000 images in pw
    std_filename_length = 10  # Defines the length of the random filename generated for Piwigo

    def __init__(self, **kwargs):
        self.cookies = kwargs.get('cookies', '')
        self.pw_id = 0
        self.dt_id = 0
        self.dt_id_str = '0'
        self.pw_id_str = '0'
        self.content = File(name_w_extension=kwargs.get('name_w_extension', ''), path=kwargs.get('path', ''))
        self.content.type = 'img'
        self.pw_image_filename = self.default_attribute
        self.pw_image_name = self.default_attribute
        self.pw_image_description = self.default_attribute
        self.album_ids = kwargs.get('multiple_album_ids', self.default_attribute)
        self.album_id = kwargs.get('album_id', self.default_attribute)
        self.tag_ids = self.default_attribute
        self.sv_mode = self.default_attribute
        self.mv_mode = self.default_attribute
        self.api_data = {'image_id': self.pw_id,
                         'file': self.pw_image_filename,
                         'name': self.pw_image_name,
                         'comment': self.pw_image_description,
                         'categories': self.album_ids,
                         'category': self.album_id,
                         'tag_ids': self.tag_ids,
                         'single_value_mode': self.sv_mode,
                         'multiple_value': self.mv_mode
                         }

    def read_image_data(self, f_path, f_name, album_list, cookies):
        """
        Reads all image detailed information from Piwigo (also from non-public albums, but user logged in must have
        access to the albums in scope) and stores it in the specficied location with the specified name in JSON format.
        Piwigo does not offer an image oriented API method for download - we have to use the "images per category"
        method and iterate over all albums and create one file per album.

        :param f_path: Full path were the result file is stored
        :type f_path: (str)
        :param f_name: Filename under which the album information is stored
        :type f_name: (str)
        :param album_list: json string with returned by read_album_data() method, containing all album_ids
        :type album_list: (dict)
        :param cookies: Valid cookie to authenticate request against Piwigo
        :type cookies: (dict)
        :return: album_content (in json format): dict
        """

        # Long story short: I like (and half-understand) dataframes...this one contains the album_data

        df = pd.DataFrame.from_dict(album_list['result']['categories'])

        # We need to run through every album and download a file per album with image details

        for value in df['id'].iteritems():

            f = File(path=f_path, name=f_name+'_for_album_id='+str(value[1]), extension='.json')

            data = {'cat_id': value[1],
                    'recursive': 'false',
                    'per_page': '500'               # Limits the number of returned images per page; not allowed: >500
                    }                            # We hope we don't meet this limit for a single album and omit
                                                    # the looping through pages

            method = Piwigo.methods['read_images']

            r = requests.get(Piwigo.url + '&method=' + method, data, cookies=cookies)

            if r.status_code != 200:
                call_error('Image data file download failed...Skipping', json.dumps(r.json()), 'soft')
            else:
                json_string = json.dumps(r.json())
                f.save_data(json_string)
                print('Downloaded image data for album ' + str(value[1]) + ' to ' + f.name)

            del f

        return

    def pop_api_data(self):
        """
        We always start with a default  definition of the API data container to be send to Piwigo. After updating all
        image attributes, we are copying the non-default attributes in the final API data container and remove the rest
        (which is still default)

        :return: the final API data container ready to be send to Piwigo
        """

        # We need to assign all currently available image variables to the api-data block
        # if pw_id is 0 however this means the image doesnt exist yet and we have to remove it

        self.api_data = {'image_id': self.pw_id,
                         'file': self.pw_image_filename,
                         'name': self.pw_image_name,
                         'comment': self.pw_image_description,
                         'category': self.album_id,
                         'categories': self.album_ids,
                         'tag_ids': self.tag_ids,
                         'single_value_mode': self.sv_mode,
                         'multiple_value': self.mv_mode
                         }

        if self.pw_id == 0:
            self.api_data['image_id'] = self.default_attribute

        # And now we remove all items which have default attribute and return the final API data container

        data_final = dict()

        for (k, v) in self.api_data.items():
            if v != self.default_attribute:
                data_final[k] = v

        return data_final

    def set_pw_id(self, **kwargs):
        """
        Sets the Piwigo id of an image in integer and string format (the latter padded to a standard length). We can
        either provide a pw_id in **kwargs or we need a valid dt_id assigned to the image before calling this
        method which is used to search the respective Piwigo id

        :param kwargs: possibility to handover a Piwigo id (as int) in 'pw_id'
        :return: None
        """

        if 'pw_id' in kwargs:
            self.pw_id = kwargs['pw_id']
            self.pw_id_str = Piwigo.str_pad(self.pw_id, self.pw_id_std_length)
        else:
            if self.dt_id == 0:
                call_error('Cannot search for empty dt_id, please set  dt_id first...Exiting', '', 'hard')
            else:
                self.pw_id = Piwigo.pw_search_image(self.dt_id_str, self.cookies)
                self.pw_id_str = Piwigo.str_pad(self.pw_id, self.pw_id_std_length)

    def set_dt_id(self, **kwargs):
        """
        Sets the Darktable id of an image in integer and string format (the latter padded to a standard length). We can
        either provide a dt_id in **kwargs or the filename of a content file is used to extract dt_id

        :param kwargs: possibility to handover a Darktable id (as int) in 'dt_id'
        :return: None
        """
        if 'dt_id' in kwargs:
            self.dt_id = kwargs['dt_id']
            self.dt_id_str = Piwigo.str_pad(self.dt_id, self.dt_id_std_length)
        else:
            self.dt_id = int(self.content.name[self.content.name.find(Image.file_name_splitter) +
                                               len(Image.file_name_splitter):])
            self.dt_id_str = Piwigo.str_pad(self.dt_id, self.dt_id_std_length)

    def set_pw_image_filename(self, **kwargs):
        """
        Sets the image file name (to be used on Piwigo) to a random string + the dt_id
        :param kwargs: offers the possibility to provide a different extension if required in 'extension'
        """
        random_string = Piwigo.create_random_string(self.std_filename_length)

        self.pw_image_filename = random_string + '_' + self.dt_id_str + kwargs.get('extension', self.content.extension)

    def set_pw_imagename(self):
        """
        Sets the image name (field name in Piwigo is 'Title') to a defined string which is (1) bi-lingual, i.e., de-de
        and en-en and (2) makes the Piwigo id and the Darktable id visible for each image
        """
        self.pw_image_name = '[lang=de]Bild ' + self.pw_id_str + self.image_name_separator + self.dt_id_str + \
                             '[/lang][lang=en]Image ' + self.pw_id_str + self.image_name_separator + \
                             self.dt_id_str + '[/lang]'

    def set_image_tags(self, tag_list):
        """
        Sets the image tags of an image (in Piwigo tag ids). In case no tags are provided for a particular image, tags
        are removed from the API data container
        """
        if tag_list == '':
            self.tag_ids = self.default_attribute
        else:
            self.tag_ids = tag_list

    def update_image_data(self, **kwargs):
        """
        Sends an API post request to update image data on Piwigo. Depending on image attributes set these can be: (1)
        image filename (2) image title (3) image tags (4) image album assignments (5) an image description
        :param kwargs: offers the possibility to provide: (i) the override mode for single-value parameters in 'sv_mode'
        (ii) the override mode for multiple value parameters in 'mv_mode' (iii) the attributes changed for a specific
        image in 'changed' and (iv) a flag to omit the display message in 'verbose'
        """

        # We define the final data block to be sent here and remove the  special default pattern to
        # remove the not provided parameters from data. Hence the minimum to be sent will be
        # the ImageID - this cannot do much harm ;-)

        self.sv_mode = kwargs.get('sv_mode', self.default_attribute)
        self.mv_mode = kwargs.get('mv_mode', self.default_attribute)
        self.api_data = self.pop_api_data()

        method = Piwigo.methods['set_info']

        r = requests.post(Piwigo.url + '&method=' + method, self.api_data, cookies=self.cookies)

        if r.status_code != 200:
            call_error('Could not fully update Piwigo image information for ' + self.pw_id_str
                       + ' check album and / or tag ids:\n' + json.dumps(self.api_data) + '\n',
                       json.dumps(r.json()), 'soft')
        else:
            if kwargs.get('changed') != '':
                if kwargs['verbose']:
                    print('Successfully updated ' + kwargs.get('changed', '') + ' of image with pw_id: '
                          + self.pw_id_str)

        return r.json()

    def category_switcher(self):
        """
        Piwigo API uses two different parameters for the album id (category and categories). While uploading new image
        we need to transfer the album id from category to categories and this is accomplished here
        """
        self.album_ids = self.album_id
        self.album_id = self.default_attribute

    def upload_image(self):
        """
        Method to upload (or update if already existing) the binary content of an image file to Piwigo. If succesful
        returns the Piwigo image id.

        :return: pw_id
        """

        # Load the image content

        img_binary = self.content.load_file()

        self.api_data = self.pop_api_data()

        method = Piwigo.methods['upload']

        r = requests.post(Piwigo.url + '&method=' + method, self.api_data, cookies=self.cookies,
                          files={'image': img_binary})

        if r.status_code == 200:

            if self.pw_id == 0:
                self.set_pw_id(pw_id=r.json()['result']['image_id'])
                print('Successfully CREATED new image with pw_id ' + self.pw_id_str)
            else:
                print('Successfully UPDATED existing image with pw_id ' + self.pw_id_str)

        else:
            print(r.json()['message'])
            call_error('Error while uploading image with dt_id ' + self.dt_id_str + '...Skipping',
                       json.dumps((r.json())), 'soft')

        return self.pw_id

    def get_pw_image_data(self):
        """
        This method allows to retrieve the attributes (filename, title, etc) of a particular image  from Piwigo. At
        the moment we only need this to get the filename extension - but is obviousyl useful for more.

        :return: Piwigo attributes of an image
        """
        api_data = {'image_id': self.pw_id}

        method = Piwigo.methods['get_info']

        r = requests.post(Piwigo.url + '&method=' + method, api_data, cookies=self.cookies)

        if r.status_code != 200:
            call_error('Error retrieving image info for ' + self.pw_id_str + '....Skipping',
                       json.dumps(r.json()), 'soft')
        else:
            # We only update the extension here but the json part of the response includes tons of data
            self.content.name, self.content.extension = os.path.splitext(r.json()['result']['file'])

        return r.json()


class Tag:
    """
    Tags are keywords which can be assigned to an image. This class provides methods to create and retrieve tags from
    Piwigo. In order to synchronize with darktable we also need to persist a map of dt_tag_ids to pw_tag_ids
    """
    tag_map_file = 'tag_map.csv'
    tag_map_path = 'C:/OneDrive/OneDrive - 3c/Daten/DarktableData/'

    def __init__(self, **kwargs):
        self.cookies = kwargs.get('cookies')
        self.pw_tag_id = 0
        self.dt_tag_id = 0
        self.tag_name = ''
        self.tag_file = File()
        self.tag_map = File(name_w_extension=self.tag_map_file, path=self.tag_map_path)
        self.tag_data_file = File()

    def read_tag_data(self, f_path, f_name, cookies):
        """
        Reads all tags from Piwigo (also non-public, but user logged in must have access) and stores them in the
        specficied location with the specified name in JSON format.

        :param f_path: Full path were the result file is stored
        :type f_path: (str)
        :param f_name: Filename under which the album information is stored
        :type f_name: (str)
        :param cookies: Valid cookie to authenticate request against Piwigo
        :type cookies: (dict)
        :return: tags (in json format): (dict)
        """

        method = Piwigo.methods['read_tags']

        r = requests.get(Piwigo.url + '&method=' + method, cookies=cookies)

        if r.status_code != 200:
            call_error('Could not read the tags from Piwigo...Skipping', json.dumps(r.json()), 'soft')
        else:
            json_string = json.dumps(r.json())
            self.tag_data_file.set_file(path=f_path, name_w_extension=f_name)
            self.tag_data_file.save_data(json_string)
            print('Tag information downloaded and saved to ' + self.tag_data_file.full_path)

        return r.json()

    def set_name(self, name):
        """
        Set the name of a tag
        """
        self.tag_name = name

    def get_tag_id(self):
        """
        Get the Piwigo id of a tag
        """
        return self.pw_tag_id

    def create_tag(self):
        """
        Creates a single tag on Piwigo and returns it's id if successful. If a tag already exists Piwigo rejects
        creation and display a warning

        :return: Piwigo tag id
        """
        data = {'name': self.tag_name
                }

        method = Piwigo.methods['add_tag']

        r = requests.post(Piwigo.url + '&method=' + method, data, cookies=self.cookies)

        if r.status_code != 200:
            print('Tag creation failed for tag ' + self.tag_name + ' Piwigo Answer: ' + json.dumps(r.json()['message']))
            self.pw_tag_id = 0
        else:
            self.pw_tag_id = r.json()['result']['id']
            print('Created tag ' + self.tag_name + ' with pw_tag_id ' + str(self.pw_tag_id))

        return self.pw_tag_id

    def mass_load_tags(self, f_full_path, **kwargs):
        """
        In order to create multiple tags in  a batch, this method reads a tag file (from csv or xlsx) and creates all
        tags included in there. After creation also the tag map (dt_tag_id -> pw_tag_id) is updated

        :param (str) f_full_path:  the full path of the tag  upload file
        :param kwargs: allows to provide a sheet name if upload file is xlsx format in 'sheet'
        :return: None
        """
        print('Start uploading new tags...')

        # Loggin in first
        acc = Account()
        t_cookies = acc.login()

        # Setting & reading the tag file into a dataframe
        self.tag_file.set_file(full_path=f_full_path)

        tag_list = self.tag_file.load_file(sheet=kwargs['sheet'])

        # Checking if all required columns are included
        if 'dt_tag_id' not in tag_list.columns or 'tag' not in tag_list.columns:
            call_error('Could not load file: dt_tag_id and tag column must be in file...Exiting', '', 'hard')

        # Initializing the temporary dataframe for the tag map
        new_tags = pd.DataFrame()

        for tl in tag_list.itertuples():
            # Tags don't have a sequence etc - we only need to iterate over all rows
            tag = Tag(cookies=t_cookies)
            tag.dt_tag_id = tl[1]
            tag.set_name(tl[2])
            tag.create_tag()
            if tag.pw_tag_id == 0:           # We don't want to write something to the file if tag could not be created
                del tag
                continue
            else:
                new_tags = new_tags.append({'dt_id': int(tag.dt_tag_id),
                                            'pw_id': int(tag.pw_tag_id)}, ignore_index=True)
                del tag

        # Now we update the tag map with the new tags stored in new_tags
        if not new_tags.empty:
            new_tags = new_tags.astype({'dt_id': 'int32', 'pw_id': 'int32'})  # Make sure id's are in  int format
            self.tag_map.save_tag_map(new_tags)

        print('Finished uploading tags from file...Click OK to continue')


class Directory:
    """
    We need a lot of directory and file management. This class establishes what we need from a directory
    """
    def __init__(self, **kwargs):
        self.path = kwargs.get('path', '')
        self.file_list = []
        self.content_type = kwargs.get('type', 'all')  # Sets the directory type for file_list, can be 'all' or 'jpg'

    def set_path(self, path):
        """
        Sets the path of the directory
        """
        self.path = path

    def set_file_list(self):
        """
        Reads the files (of a specified type defined in content_type if required) from the directory and updates the
        respective instance attribute

        :return: a list of files in the directory in self.file_list
        """

        from pathlib import Path

        if self.content_type == 'all':

            self.file_list = os.listdir(self.path)

        elif self.content_type == 'jpg':

            self.file_list = Path(self.path[:-1]).glob('*.jpg')  # Path does NOT like the / at the end of the path

        return self.file_list

    def check_file_existence(self, file_name):
        """
        Checks if a specific file exists in the directory.

        :param (str) file_name: name of the file whose existence should be validated
        :return: file existence
        """
        if os.path.isfile(self.path + file_name):
            return True
        else:
            return False

    def get_path(self):
        """
        Get the path of a directory instance
        """
        return self.path


class File(Directory):
    """
    A class containing all messages to manage our file access, read, write etc.
    """

    # Registering two csv dialects here, as we cannot always use a | as separator
    csv.register_dialect('withPipe', delimiter='|', quoting=csv.QUOTE_NONE)
    csv.register_dialect('withSemi', delimiter=';', quoting=csv.QUOTE_NONE)

    def __init__(self, **kwargs):
        """
        The init-method of File sets filename, path and extension depending on the available information provided and
        can deal with all attributes in individual variables or combinations of them. Hopefully ones and for all takes
        care of the '/' at the end of a path

        :param kwargs: container for different input attributes: (1) filename in 'name' (2) filepath in 'path' (3)
        fileextension in 'extension' (4) the filename with extension in 'name_w_extension' and (5) the full path in
        'full_path'
        """
        if kwargs.keys() == {'path', 'name', 'extension'}:
            self.name = kwargs['name']
            self.path = kwargs['path']
            self.extension = kwargs['extension']

        elif 'name_w_extension' in kwargs:
            self.name, self.extension = os.path.splitext(kwargs['name_w_extension'])
            self.path = kwargs.get('path', '')

        elif 'full_path' in kwargs:
            path_splitter = os.path.split(kwargs['full_path'])
            self.path = path_splitter[0] + '/'
            self.name, self.extension = os.path.splitext(path_splitter[1])

        else:
            self.path = ''
            self.name = ''
            self.extension = ''

        if self.path == '' or self.path[-1] != '/':
            self.path = self.path + '/'

        self.full_path = self.path + self.name + self.extension

    def set_file(self, **kwargs):
        """
        Mimics the init-method of File and  sets filename, path and extension depending on the available information
        provided and can deal with all attributes in individual variables or combinations of them. Hopefully ones and
        for all takes care of the '/' at the end of a path

        :param kwargs: container for different input attributes: (1) filename in 'name' (2) filepath in 'path' (3)
        fileextension in 'extension' (4) the filename with extension in 'name_w_extension' and (5) the full path in
        'full_path'
        """
        if kwargs.keys() == {'path', 'name', 'extension'}:
            self.name = kwargs['name']
            self.path = kwargs['path']
            self.extension = kwargs['extension']

        elif 'name_w_extension' in kwargs:
            self.name, self.extension = os.path.splitext(kwargs['name_w_extension'])
            self.path = kwargs.get('path', '')

        elif 'full_path' in kwargs:
            path_splitter = os.path.split(kwargs['full_path'])
            self.path = path_splitter[0] + '/'
            self.name, self.extension = os.path.splitext(path_splitter[1])

        else:
            self.path = ''
            self.name = ''
            self.extension = ''

        if self.path == '' or self.path[-1] != '/':
            self.path = self.path + '/'

        self.full_path = self.path + self.name + self.extension

    def load_file(self, **kwargs):
        """
        Loads different types of files (txt, csv, xlsx, jgp) and provide their content in the required format for
        further usage

        :param kwargs: allows to handover a sheet name for xslx format in 'sheet'
        """
        csv.register_dialect('withPipe', delimiter='|', quoting=csv.QUOTE_NONE)
        csv.register_dialect('withSemi', delimiter=';', quoting=csv.QUOTE_NONE)

        if self.extension == '.txt' or self.extension == '':

            try:
                file = open(self.full_path, 'r')
                content = file.read()
                return content
            except Exception as e:
                call_error('Could not open / read file...Exiting', e, 'hard')
                return ''

        elif self.extension == '.csv':

            try:
                content = pd.read_csv(self.full_path, '|')               # content is now a pd.dataframe!!
                return content

            except Exception as e:
                call_error('Could not open / read file...Exiting', e, 'hard')
                return pd.DataFrame

        elif self.extension == '.jpg' or self.extension == '.png' or self.extension == '.tif':

            try:
                content = open(self.full_path, 'rb')
                return content

            except Exception as e:
                call_error('Could not open / read file...Exiting', e, 'hard')
                return ''

        elif self.extension == '.xls' or self.extension == '.xlsx':

            # Careful with the formats here. A string with two numbers separated by comma is easily converted to a.b and
            # a number format. It seems, that we can prevent this by creating the information in PowerQuery and format
            # them - in PQ! - as text.

            try:
                content = pd.read_excel(self.full_path, engine='openpyxl',
                                        sheet_name=kwargs.get('sheet', 'Tabelle1'), dtype='string')
                return content

            except PermissionError:
                call_error('Please close the xlsx loadfile and restart...', '', 'hard')
                return pd.DataFrame
            except Exception as e:
                call_error('Could not open / read file...Exiting', e, 'hard')
                return pd.DataFrame

    def save_data(self, f_content):
        """
        Saves data in a defined format (depending on the extension provided by the file object) to disk

        :param (any) f_content: the content which should be saved to disk
        :return: None
        """
        if self.extension == '.json':
            json_file = open(self.full_path, 'w')
            json_file.write(f_content)
            json_file.close()

        if self.extension == '' or self.extension == '.txt':
            txt_file = open(self.full_path, 'w')
            txt_file.write(f_content)
            txt_file.close()

        else:
            pass

    def save_tag_map(self, new_tags):
        """
        A specific method to store the tag map - we need to iterate over the dataframe and append to the csv file.

        :param (dataframe) new_tags: Pandas dataframe with the new tags to be added to the tap map csv file
        """
        tag_map_file = open(self.full_path, 'a')

        # itertuples() returns each row as tuple with the index at row[0], we have dt_id at row[1] and pw_id at row[2}

        for tag in new_tags.itertuples():
            tag_map_file.write(str(tag[1]) + ',' + str(tag[2]) + '\n')

        tag_map_file.close()


class Gui:
    """
    The class to manage the (limited number) of Gui elements
    """
    # def __init__(self):
    #    self.directory_path = ''
    #    self.file_name = ''

    @classmethod
    def new_theme(cls):
        """
        Defines the "myfototours" style theme in grey and red
        """
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

    def main_window(self):
        """
        Defines the main window and the message window shown when a batch is executed
        """
        Sg.ChangeLookAndFeel(self.gui_theme)

        initial_dir = os.path.dirname(os.path.realpath(__file__))

        def win_main():

            layout = [[Sg.Image(data=logo_data, pad=((10, 0),(5, 0))), Sg.Text('Darktable to Piwigo Connector',
                                size=(30, 1), justification='right', font=("Helvetica", 17, 'bold'))],
                [Sg.Text('')],
                [Sg.Frame(layout=[
                    [Sg.Text("Select a folder to download to: "), Sg.Input(default_text=initial_dir, key="-DATA_FOLDER-", change_submits=True, size=(60, 1)),
                     Sg.FolderBrowse(key="-B_DATA_FOLDER-", initial_folder=initial_dir)],
                    [Sg.Checkbox('Albumdetails:', default=True, key='-ALBUM_INCLUDED-'),
                     Sg.Checkbox('Tags:', default=True, key='-TAGS_INCLUDED-'),
                     Sg.Checkbox('Imagedetails:', default=True, key='-IMAGE_INCLUDED-')],
                    [Sg.Button("Start", key="-DATA_DOWNLOAD-", pad=((20, 10), (10, 10)))]
                ], title='Download / Refresh Piwigo Data', font=("Helvetica", 12, 'bold'), title_color='#C5241C', relief=Sg.RELIEF_RAISED,
                    tooltip='Use this to download a full set of Piwigo data. This includes all album information, all \n'
                            'Piwigo tags and a file with image information for each album. The image information will be\n'
                            'stored in a sub folder to keep things tidy.')],
                [Sg.Text('')],
                [Sg.Frame(layout=[
                    [Sg.Text("Select a folder to upload: "), Sg.Input(default_text=initial_dir, key="-ALBUM_FOLDER-", change_submits=True, size=(63, 1)),
                     Sg.FolderBrowse(key="-B_ALBUM_FOLDER-", initial_folder=initial_dir)],
                    [Sg.Button("Start", key='-ALBUM_UPLOAD-', pad=((20, 10), (10, 10)))]
                ],  title='Upload / Update Image Album', font=("Helvetica", 12, 'bold'), title_color='#C5241C', relief=Sg.RELIEF_RAISED,
                    tooltip='Use this to upload or update a complete album to Piwigo. The programm will read the album_id\n'
                            'from a file with the identical name if provided. If not provided album_id will be set to \n'
                            'Miscellaneous. If a file album_tags.csv (dt_id, tagList) is provided the provided tags will \n'
                            'assigned to the images automatically')],
                [Sg.Text('')],
                [Sg.Frame(layout=[
                      [Sg.Text("Select a file to upload: "), Sg.Input(key="-COLL_FILE-", change_submits=True, size=(65, 1)),
                       Sg.FileBrowse(key="-B_COLL_FILE-", initial_folder=initial_dir)],
                     [Sg.Text("Worksheet name:       "), Sg.Input(key='-COLL_TAB-', default_text='imagesToUpdate', change_submits=True, size=(20, 1))],
                     [Sg.Checkbox('Replace existing data', size=(15, 1,), key='-REPLACE-'),
                     Sg.Checkbox('Update Piwigo filename / title', default=True, key='-NAMETITLE-')],
                    [Sg.Button("Start", key='-COLL_UPDATE-', pad=((20, 10), (10, 10)))]
                        ], title='Upload Image Collection',  font=("Helvetica", 12, 'bold'), title_color='#C5241C', relief=Sg.RELIEF_RAISED,
                    tooltip='Use this to upload an image collection. You can decide if all existing data will be replaced\n'
                            ' (careful!) and if you want to re-create and load the image filename and title on Piwigo. The\n'
                            'load file must contain at least the dt_id and pw_id and can additionally have the columns\n'
                            ' album_ids, tags and description')],
                [Sg.Text('')],
                [Sg.Frame(layout=[
                    [Sg.Text("Select a file to upload: "), Sg.Input(key="-TAG_FILE-", change_submits=True, size=(65, 1)),
                     Sg.FileBrowse(key="-B_TAG_FILE-", initial_folder=initial_dir)],
                    [Sg.Text("Worksheet name:       "),
                     Sg.Input(key='-TAG_TAB-', default_text='tagsToCreate', change_submits=True, size=(20, 1))],
                    [Sg.Button("Start", key='-TAG_UPLOAD-', pad=((20, 10), (10, 10)))]
                ], title='Upload new Tags', font=("Helvetica", 12, 'bold'), title_color='#C5241C', relief=Sg.RELIEF_RAISED,
                    tooltip='Use this to upload new tags to Piwigo. The programm will automatically update the tag_map file\n'
                            'The file must contain the columns dt_id and tag')],
                [Sg.Text('')],
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
            if event == '-DATA_DOWNLOAD-':
                if values['-B_DATA_FOLDER-'] == '':
                    Sg.popup_ok('You did not edit the data folder. Continuing with:\n' +
                                values['-DATA_FOLDER-'])

                window2 = win_info()
                Piwigo.refresh_data(values['-DATA_FOLDER-'] + '/', values['-IMAGE_INCLUDED-'],
                                    values['-ALBUM_INCLUDED-'], values['-TAGS_INCLUDED-'])

            if event == '-ALBUM_UPLOAD-':
                if values['-B_ALBUM_FOLDER-'] == '':
                    Sg.popup_ok('You did not edit the data folder. Continuing with:\n' +
                                values['-ALBUM_FOLDER-'])

                window2 = win_info()
                a = Album()
                a.upload_album(values['-B_ALBUM_FOLDER-'] + '/')

            if event == '-COLL_UPDATE-':
                if values['-B_COLL_FILE-'] == '':
                    Sg.popup_ok('Please select an upload file first!')
                else:
                    window2 = win_info()
                    a = Album()
                    a.update_collection(values["-B_COLL_FILE-"], values['-REPLACE-'], values['-NAMETITLE-'],
                                        sheet=values['-COLL_TAB-'])

            if event == '-TAG_UPLOAD-':
                if values['-B_TAG_FILE-'] == '':
                    Sg.popup_ok('Please select an upload file first!')
                else:
                    window2 = win_info()
                    t = Tag()
                    t.mass_load_tags(values["-B_TAG_FILE-"], sheet=values['-TAG_TAB-'])

        window.close()


# No, this should not be a function but a method but... ;-)
def call_error(message, error, error_type):
    """
    Defines a function (sic!) which display an error message

    :param (str) message: a error specific message
    :param (str) error: additional information about the error
    :param (str) error_type: defines if the execution should break ('hard') or only skip the step where the error occured
    :return: None
    """
    if error == '':
        Sg.popup_ok(message, title='ERROR', background_color='red', text_color='white', auto_close=False)
        if error_type == 'hard':
            quit()
        elif error_type == 'soft':
            pass
    else:
        Sg.popup_ok(message + '\nError Message: ' + error, title='ERROR', background_color='red', text_color='white',
                    auto_close=False)
        if error_type == 'hard':
            quit()
        elif error_type == 'soft':
            pass

    pass


if __name__ == '__main__':

    g = Gui()
    Gui.new_theme()
    g.main_window()
