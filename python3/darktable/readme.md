# Introduction
This Python code connects two well known Open Source products for Photographers, namely the Photo editing software [Darktable](https://www.darktable.org/) and the photo gallery software for the web [Piwigo](https://piwigo.org/). 

The piece of python code connects the images and the image data in the Sqlite3 database of Darktable with the albums (Ids) and images (Ids) stored on Piwigo - and hence indirectly with the underlying MySQL database. In addition it allows to create bi-lingual content using the [Extended Descriptions plugin](https://piwigo.org/ext/extension_view.php?eid=175) for Piwigo. The functionality includes: 

- **Download the Piwigo data**: Download all album information, image information and tags from Piwigo and store it in a specified folder structure to be used with Power Query
- **Create new tags on Piwigo**: Using a number of Excel Power Queries a worksheet with tags can be created using the Darktable tags as input. The tags are bi-lingual and can be loaded to and created in Piwigo directly using this functionality. The functionality also maintains a mapping file which connect the Darktable Tag Id to the Piwigo Tag Id.
- **Upload a new album to Piwigo**: After exporting edited images from Darktable (including their Darktable Image Id in the filename) into a folder, a new album is created on Piwigo from this folder and the images are uploaded. A random filename is created for the Piwigo image (including the Darktable Image Id) so that the sequence of pictures while displayed on Piwigo is either stochastic (if filename is chosen as sort criteria) or ordered (if e.g. [date taken] is used as sort criteria). Addtionally, the image title on Piwigo is set to include the Piwigo Image Id and the Darktable Image Id (in two languages). This functionality allows also to update images (i.e., their binary content): during upload it is validated if the image (identified by its Darktable Image Id) already exists on Piwigo and the Piwigo image is updated only in this case. If a file with tags per image exits in the respective folder tags are assigend to the uploaded / updated image on Piwigo
- **Upload collection**: This functionality allows to update the metadata (filename, image title, tags, description, and album assignments) on Piwigo for an arbitrary collection of images. The image information can be provided in Excel or CSV file format

The following archtecture overview shows how the different components interact with each other

![Architectural Overview](https://github.com/not1q84-1/homeserver/blob/master/source3/misc/ArchitectureOverview.png)

# Components
## Darktable
Darktable persists all relevant data in two - simply structured - Sqlite3 databases in the main folder of the Darktable install. In library.db all image related information is stored (including the connection to tags); data.db stores main metadata including tags. 

With he exception of tag management their is no differnce / specialities of Darktable usage in terms of the objectives described above. The tag management however needs to be adjusted to include (i) the english translation of a tag (ii) the album id of an album, if the webgallery assignment of an image should be visble in Darktable. 

- **Tag translation**: Darktable allows to create synonmys for every tag. This is not directly visible during tagging and is hence used to also store translations of a tag. The translation of a tag is entered in the synonym field of a tag **after the real synonmys in the original language** separated by _|en_. The Excel Power Query logic will read the tags from the database and abstract the translation as well as the synonyms in both languages.

![Editing Tags with translations](https://github.com/not1q84-1/homeserver/blob/master/source3/misc/DT_EditTag.jpg)

- **Album information**: It is desirable to know which of the images in Darktable are also publish on Piwigo. A branch of tags is created which mimics the album structure on Piwigo. The album ids are stored in the synonym field of the respective tag in curly braces _{album_id}_.

![Piwigo Album structure in Darktable tags](https://github.com/not1q84-1/homeserver/blob/master/source3/misc/DT_WebsiteTags.jpg)
![Album id stored in synonyms](https://github.com/not1q84-1/homeserver/blob/master/source3/misc/DT_EditTag_albumid.jpg)

## Excel Power Query
## Piwigo
## Python
### Screenshots
### UML Diagrams
#### Use Case Diagram
![Use Case Diagram](https://github.com/not1q84-1/homeserver/blob/master/source3/misc/UseCaseDiagramm.jpg)
#### Class Diagram
![Class Diagram](https://github.com/not1q84-1/homeserver/blob/master/source3/misc/class_diagramm.jpg)
#### Activity Diagram
![Activity Diagramm](https://github.com/not1q84-1/homeserver/blob/master/source3/misc/activity%20diagram.jpg)
