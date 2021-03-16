// pathToData
let
    Quelle = Excel.CurrentWorkbook(){[Name="pathToData"]}[Content],
    changeType = Table.TransformColumnTypes(Quelle,{{"source", type text}, {"path_to_data", type text}})
in
    changeType

// dt_tags
let
    datapath = Table.SelectRows(pathToData, each [source] = "Darktable")[path_to_data]{0},
    Quelle = Odbc.DataSource("database="&datapath&"/data.db;dsn=SQLite3 Datasource", [HierarchicalNavigation=true]),
    tags_Table = Quelle{[Name="tags",Kind="Table"]}[Data],
    changeType = Table.TransformColumnTypes(tags_Table,{{"id", Int64.Type}}),
    removeDarktableTags = Table.SelectRows(changeType, each not Text.StartsWith([name], "darktable")),
    addLevel = Table.AddColumn(removeDarktableTags, "lvl", each List.Count(Text.PositionOf([name],"|",Occurrence.All ))),
    splitOffAlbumId = Table.SplitColumn(addLevel, "synonyms", Splitter.SplitTextByDelimiter("{", QuoteStyle.Csv), {"synonyms", "album_id"}),
    cleanUpAlbumId = Table.ReplaceValue(splitOffAlbumId,"}","",Replacer.ReplaceText,{"album_id"}),
    changeAlbumIdType = Table.TransformColumnTypes(cleanUpAlbumId,{{"album_id", Int64.Type}}),
    splitSynonyms = Table.SplitColumn(changeAlbumIdType, "synonyms", Splitter.SplitTextByEachDelimiter({"|en:"}, QuoteStyle.Csv, false), {"synonymsDe", "englishNameSyn"}),
    splitTranslationEn = Table.SplitColumn(splitSynonyms, "englishNameSyn", Splitter.SplitTextByEachDelimiter({","}, QuoteStyle.Csv, false), {"translationEn", "synonymEn"}),
    replaceComma = Table.ReplaceValue(splitTranslationEn,",","/",Replacer.ReplaceText,{"synonymsDe", "synonymEn"}),
    addGermanName = Table.AddColumn(replaceComma, "nameDe", each if [lvl]=0 then "" else Text.Range(List.Accumulate(List.RemoveFirstN(Text.Split([name],"|"),1),"",(state,current)=>state&"|"&current),1)),
    addNameDeFlat = Table.AddColumn(addGermanName, "nameDeFlat", each if ([synonymsDe] = null or [synonymsDe] = "") then (if Text.Contains([nameDe],"|") then List.Last(Text.Split([nameDe],"|")) else [nameDe]) else (if Text.Contains([nameDe],"|") then List.Last(Text.Split([nameDe],"|"))&"/"&[synonymsDe] else [nameDe]&"/"&[synonymsDe])),
    addNameEnFlat = Table.AddColumn(addNameDeFlat, "nameEnFlat", each if [translationEn] = null or [translationEn] = "" then [nameDeFlat] else if ([synonymEn] = null or [synonymEn] = "") then [translationEn] else [translationEn]&"/"&[synonymEn]),
    removeGarbage = Table.SelectColumns(addNameEnFlat,{"id", "name", "nameDeFlat", "nameEnFlat", "album_id", "lvl"}),
    cleanText1 = Table.TransformColumns(removeGarbage,{{"name", Text.Clean, type text}, {"nameDeFlat", Text.Clean, type text}, {"nameEnFlat", Text.Clean, type text}}),
    cleantext2 = Table.TransformColumns(cleanText1,{{"name", Text.Clean, type text}, {"nameDeFlat", Text.Clean, type text}, {"nameEnFlat", Text.Clean, type text}}),
    #"Umbenannte Spalten" = Table.RenameColumns(cleantext2,{{"id", "dt_tag_id"}, {"name", "dt_tag_name"}})
in
    #"Umbenannte Spalten"

// dt_images
let
    datapath = Table.SelectRows(pathToData, each [source] = "Darktable")[path_to_data]{0},
    connectSqlLiteDb = Odbc.DataSource("database="&datapath&"/library.db;dsn=SQLite3 Datasource", [HierarchicalNavigation=true]),
    images_Table = connectSqlLiteDb{[Name="images",Kind="Table"]}[Data],
    copyFilename = Table.DuplicateColumn(images_Table, "filename", "filename - Kopie"),
    addCreationDate2 = Table.AddColumn(copyFilename, "creationDate", each if ([datetime_taken]= null or [datetime_taken]="" or [datetime_taken]=" ") then "2000/01/01 00:00:00" else Text.Replace(Text.Range([datetime_taken],0,10),":","/")&Text.Range([datetime_taken],10)),
    changeToDateTime = Table.TransformColumnTypes(addCreationDate2,{{"creationDate", type datetime}}),
    renameToStandard = Table.RenameColumns(changeToDateTime,{{"id", "dt_image_id"}})
in
    renameToStandard

// dt_tagged_Images
let
    datapath = Table.SelectRows(pathToData, each [source] = "Darktable")[path_to_data]{0},
    Quelle = Odbc.DataSource("database="&datapath&"/library.db;dsn=SQLite3 Datasource", [HierarchicalNavigation=true]),
    tagged_images_Table = Quelle{[Name="tagged_images",Kind="Table"]}[Data],
    changedTypes = Table.TransformColumnTypes(tagged_images_Table,{{"imgid", Int64.Type}, {"tagid", Int64.Type}}),
    #"Umbenannte Spalten" = Table.RenameColumns(changedTypes,{{"imgid", "dt_image_id"}, {"tagid", "dt_tag_id"}})
in
    #"Umbenannte Spalten"

// piwigo_subpath
let
    Quelle = {"\piwigo_data", "\imagedetails"}
in
    Quelle

// pw_albums
let
    datapath = Table.SelectRows(pathToData, each [source] = "Piwigo")[path_to_data]{0}&piwigo_subpath{0},
    loadJsonFile = Json.Document(File.Contents(datapath&"\albuminformation.json")),
    result = loadJsonFile[result],
    convertToTable = Record.ToTable(result),
    expandList = Table.ExpandListColumn(convertToTable, "Value"),
    expandDetails = Table.ExpandRecordColumn(expandList, "Value", {"id", "name", "comment", "uppercats", "global_rank", "dir", "status", "nb_images", "fullname"}, {"id", "name.1", "comment", "uppercats", "global_rank", "dir", "status", "nb_images", "fullname"}),
    removeGarbage = Table.SelectColumns(expandDetails,{"id", "fullname", "name.1", "comment", "uppercats", "global_rank", "status", "nb_images"}),
    changeTypes = Table.TransformColumnTypes(removeGarbage,{{"id", Int64.Type}, {"nb_images", Int64.Type}, {"fullname", type text}, {"name.1", type text}, {"comment", type text}, {"uppercats", type text}, {"global_rank", type text}, {"status", type text}}),
    renameToStyle = Table.RenameColumns(changeTypes,{{"id", "pw_album_id"}, {"fullname", "pw_album_fullname"}, {"name.1", "album_name"}}),
    sortAscending = Table.Sort(renameToStyle,{{"pw_album_id", Order.Ascending}})
in
    sortAscending

// pw_images
let
    datapath = Table.SelectRows(pathToData, each [source] = "Piwigo")[path_to_data]{0}&piwigo_subpath{0}&piwigo_subpath{1},
    loadInformationFolder = Folder.Files(datapath),
    expandFileSize = Table.ExpandRecordColumn(loadInformationFolder, "Attributes", {"Size"}, {"Size"}),
    removeEmptyAlbum = Table.SelectRows(expandFileSize, each [Size] > 120),
    addContent = Table.AddColumn(removeEmptyAlbum, "GetContent", each loadJsonFile([Folder Path],[Name])),
    removeRest = Table.SelectColumns(addContent,{"GetContent"}),
    expandDetails = Table.ExpandTableColumn(removeRest, "GetContent", {"id", "width", "height", "hit", "file", "name", "comment", "date_creation", "date_available", "page_url", "element_url", "derivatives", "categories"}, {"id", "width", "height", "hit", "file", "name", "comment", "date_creation", "date_available", "page_url", "element_url", "derivatives", "categories"}),
    sortAscencding = Table.Sort(expandDetails,{{"id", Order.Ascending}}),
    expandAlbumData = Table.ExpandListColumn(sortAscencding, "categories"),
    expandAlbumId = Table.ExpandRecordColumn(expandAlbumData, "categories", {"id"}, {"pw_album_id"}),
    copyFilename = Table.DuplicateColumn(expandAlbumId, "file", "file - Kopie"),
    separation1 = Table.SplitColumn(copyFilename, "file - Kopie", Splitter.SplitTextByDelimiter("_", QuoteStyle.Csv), {"file - Kopie.1", "file - Kopie.2"}),
    separation2 = Table.SplitColumn(separation1, "file - Kopie.2", Splitter.SplitTextByDelimiter(".", QuoteStyle.Csv), {"dt_image_id", "file - Kopie.2.2"}),
    removeGarbage = Table.SelectColumns(separation2,{"id", "dt_image_id", "pw_album_id", "file", "name", "comment", "date_creation", "date_available", "page_url", "width", "height", "hit"}),
    changeTypes = Table.TransformColumnTypes(removeGarbage,{{"id", Int64.Type}, {"dt_image_id", Int64.Type}, {"pw_album_id", type number}, {"width", Int64.Type}, {"height", Int64.Type}, {"hit", Int64.Type}, {"file", type text}, {"name", type text}, {"comment", type text}, {"page_url", type text}, {"date_creation", type datetime}, {"date_available", type datetime}}),
    nameToFit = Table.RenameColumns(changeTypes,{{"id", "pw_image_id"}, {"name", "pw_picture_name"}})
in
    nameToFit

// loadJsonFile
let 

    loadJsonImages = (filepath as text, filename as text) =>

let
    loadJsonFile = Json.Document(File.Contents(filepath&filename)),
    getResult = loadJsonFile[result],
    getImagesList = getResult[images],
    convertToTable = Table.FromList(getImagesList, Splitter.SplitByNothing(), null, null, ExtraValues.Error),
    expandImageData = Table.ExpandRecordColumn(convertToTable, "Column1", {"id", "width", "height", "hit", "file", "name", "comment", "date_creation", "date_available", "page_url", "element_url", "derivatives", "categories"}, {"id", "width", "height", "hit", "file", "name", "comment", "date_creation", "date_available", "page_url", "element_url", "derivatives", "categories"})
in
    expandImageData

in
    loadJsonImages

// childrenFinder
let

  childrenFinder = (tag_value as text, inputtable as table, currentLevel as number) =>
let
    filterTable  = Table.SelectRows(inputtable, each Text.Contains([dt_tag_name],tag_value) and [lvl]=currentLevel+1),
    outputList = Table.ToColumns(filterTable){1}
in
    outputList

in

  childrenFinder

// readAlbumIds
let

    extractAlbum = (recordList as list) =>

let
    listToRecord = [data = recordList],
    convertToTable = Record.ToTable(listToRecord),
    expandList = Table.ExpandListColumn(convertToTable, "Value"),
    expandDetails = Table.ExpandRecordColumn(expandList, "Value", {"id", "url", "page_url"}, {"id", "url", "page_url"}),
    convertIdToString = Table.TransformColumnTypes(expandDetails,{{"id", type text}}),
    toColumns = Table.ToColumns(convertIdToString){0}
in
    toColumns

in
    extractAlbum

// removeAlbums
let
    removeAlbums = {"Unterwegs", "Miscellaneous"}
in
    removeAlbums

// removeTagBranches
let
    removeTagBranches = {"1 Was|Menschen|Kollegen", "1 Was|Menschen|Freunde", "1 Was|Menschen|Familie","3 Wie|Website"}
in
    removeTagBranches

// pw_tags
let
    datapath = Table.SelectRows(pathToData, each [source] = "Piwigo")[path_to_data]{0}&piwigo_subpath{0},
    loadJson = Json.Document(File.Contents(datapath&"\pw_tags.json")),
    readResult = loadJson[result],
    readTags = readResult[tags],
    convertToTable = Table.FromList(readTags, Splitter.SplitByNothing(), null, null, ExtraValues.Error),
    expandTags = Table.ExpandRecordColumn(convertToTable, "Column1", {"id", "name", "url_name", "lastmodified"}, {"pw_tag_id", "pw_tag_name", "url_name", "lastmodified"}),
    changeTypes = Table.TransformColumnTypes(expandTags,{{"pw_tag_id", Int64.Type}, {"pw_tag_name", type text}, {"url_name", type text}, {"lastmodified", type datetime}}),
    sortAscending = Table.Sort(changeTypes,{{"pw_tag_id", Order.Ascending}})
in
    sortAscending

// tag_map
let
    Quelle = Csv.Document(File.Contents("C:\OneDrive\OneDrive - 3c\Daten\DarktableData\tag_map.csv"),[Delimiter=",", Columns=2, Encoding=1252, QuoteStyle=QuoteStyle.None]),
    #"Höher gestufte Header" = Table.PromoteHeaders(Quelle, [PromoteAllScalars=true]),
    #"Geänderter Typ" = Table.TransformColumnTypes(#"Höher gestufte Header",{{"dt_id", Int64.Type}, {"pw_id", Int64.Type}}),
    #"Umbenannte Spalten" = Table.RenameColumns(#"Geänderter Typ",{{"dt_id", "dt_tag_id"}, {"pw_id", "pw_tag_id"}})
in
    #"Umbenannte Spalten"

// tags_w_pw_id
let
    loadTagsRaw = Table.Buffer(dt_tags),
    removeTopLevel = Table.SelectRows(loadTagsRaw, each ([nameDeFlat] <> "")),
    removePrivateTags = Table.SelectRows(removeTopLevel, each not List.Contains(removeTagBranches,[dt_tag_name],(x as text, y as text)=>Text.Contains(y,x))),
    joinTagMap = Table.NestedJoin(removePrivateTags, {"dt_tag_id"}, tag_map, {"dt_tag_id"}, "tag_map", JoinKind.LeftOuter),
    expandPwTagId = Table.ExpandTableColumn(joinTagMap, "tag_map", {"pw_tag_id"}, {"pw_tag_id"}),
    idToFront = Table.ReorderColumns(expandPwTagId,{"dt_tag_id" ,"pw_tag_id", "dt_tag_name", "nameDeFlat", "nameEnFlat", "album_id", "lvl"}),
    sortAscending = Table.Sort(idToFront,{{"pw_tag_id", Order.Ascending}})
in
    sortAscending

// tagsWithParents_pw
let
    loadTags = Table.Buffer(tags_w_pw_id),
    removeGarbage = Table.SelectColumns(loadTags,{"pw_tag_id", "dt_tag_name", "lvl"}),
    addChildrenList = Table.AddColumn(removeGarbage, "children", each childrenFinder([dt_tag_name],tags_w_pw_id,[lvl])),
    expandChildren = Table.ExpandListColumn(addChildrenList, "children"),
    removeGarbage2 = Table.SelectColumns(expandChildren,{"pw_tag_id", "children","lvl"}),
    changeTypes = Table.TransformColumnTypes(removeGarbage2,{{"pw_tag_id", Int64.Type}, {"lvl", Int64.Type}, {"children", Int64.Type}}),
    createFilterColumn = Table.AddColumn(changeTypes, "filterColumn", each if [lvl]=1 and [children] = null then "Keep" else if [children] <> null then "Keep" else "Delete"),
    removeUnprotectedLeaves = Table.SelectRows(createFilterColumn, each ([filterColumn] = "Keep")),
    RemoveFilterColumn = Table.RemoveColumns(removeUnprotectedLeaves,{"filterColumn"}),
    protectId = Table.RenameColumns(RemoveFilterColumn,{{"pw_tag_id", "id_"}}),
    copyChildId = Table.AddColumn(protectId, "pw_tag_id", each if [children] = null then [id_] else [children]),
    copyParentId = Table.AddColumn(copyChildId, "pw_tag_parent_id", each if [children] = null then 0 else [id_]),
    cleanUp = Table.SelectColumns(copyParentId,{"pw_tag_id", "pw_tag_parent_id", "lvl"}),
    sortAscending = Table.Sort(cleanUp,{{"pw_tag_id", Order.Ascending}})
in
    sortAscending

// tagsHierarchy_pw
let
    Quelle = Table.Buffer(tagsWithParents_pw),
    joinTags = Table.NestedJoin(Quelle, {"pw_tag_id"}, tags_w_pw_id, {"pw_tag_id"}, "joinedColumn", JoinKind.LeftOuter),
    expandNameFlatEn = Table.ExpandTableColumn(joinTags, "joinedColumn", {"nameEnFlat"}, {"nameEnFlat"}),
    buffer=Table.Buffer(expandNameFlatEn),
    selfJoin1 = Table.NestedJoin(expandNameFlatEn, {"pw_tag_parent_id"},buffer, {"pw_tag_id"}, "joinedColumn", JoinKind.LeftOuter),
    expandParentId1 = Table.ExpandTableColumn(selfJoin1, "joinedColumn", {"pw_tag_parent_id", "nameEnFlat"}, {"pw_tag_parent_id1", "NameEn1"}),
    selfJoin2 = Table.NestedJoin(expandParentId1, {"pw_tag_parent_id1"}, buffer, {"pw_tag_id"}, "joinedColumn", JoinKind.LeftOuter),
    expandParentId2 = Table.ExpandTableColumn(selfJoin2, "joinedColumn", {"pw_tag_parent_id", "nameEnFlat"}, {"pw_tag_parent_id2", "NameEn2"}),
    selfJoin3 = Table.NestedJoin(expandParentId2, {"pw_tag_parent_id"}, buffer, {"pw_tag_id"}, "joinedColumn", JoinKind.LeftOuter),
    expandParentId3 = Table.ExpandTableColumn(selfJoin3, "joinedColumn", {"pw_tag_parent_id", "nameEnFlat"}, {"pw_tag_parent_id3", "NameEn3"}),
    selfJoin4 = Table.NestedJoin(expandParentId3, {"pw_tag_parent_id"}, buffer, {"pw_tag_id"}, "joinedColumn", JoinKind.LeftOuter),
    expandParentId4 = Table.ExpandTableColumn(selfJoin4, "joinedColumn", {"pw_tag_parent_id", "nameEnFlat"}, {"pw_tag_parent_id4", "NameEn4"}),
    selfJoin5 = Table.NestedJoin(expandParentId4, {"pw_tag_parent_id"}, buffer, {"pw_tag_id"}, "joinedColumn", JoinKind.LeftOuter),
    expandParentId5 = Table.ExpandTableColumn(selfJoin5, "joinedColumn", {"pw_tag_parent_id", "nameEnFlat"}, {"pw_tag_parent_id5", "NameEn5"}),
    addParentList = Table.AddColumn(expandParentId5, "allParents", each List.RemoveItems(List.RemoveNulls({[pw_tag_parent_id5],[pw_tag_parent_id4],[pw_tag_parent_id3],[pw_tag_parent_id2],[pw_tag_parent_id1],[pw_tag_parent_id],[pw_tag_id]}),{0})),
    final = Table.SelectColumns(addParentList,{"pw_tag_id", "pw_tag_parent_id", "allParents"}),
    sortAscending = Table.Sort(final,{{"pw_tag_id", Order.Ascending}})
in
    sortAscending

// allDtImagesPwTags
let
    loadTaggedImages = Table.Buffer(dt_tagged_Images),
    loadTagMap = Table.Buffer(tag_map),
    loadPwTags = Table.Buffer(tagsHierarchy_pw),
    joinTagMap = Table.NestedJoin(loadTaggedImages,{"dt_tag_id"},loadTagMap,{"dt_tag_id"}, "joinColumn", JoinKind.LeftOuter),
    expandPwId = Table.ExpandTableColumn(joinTagMap, "joinColumn", {"pw_tag_id"}, {"pw_tag_id"} ),
    removeNullfromPwId = Table.SelectRows(expandPwId, each ([pw_tag_id] <> null)),
    joinTagList = Table.NestedJoin(removeNullfromPwId,{"pw_tag_id"},loadPwTags,{"pw_tag_id"}, "joinColumn", JoinKind.LeftOuter),
    expandTagList = Table.ExpandTableColumn(joinTagList, "joinColumn", {"allParents"}, {"tagList"} ),
    removeNullEntries = Table.SelectRows(expandTagList, each ([pw_tag_id] <> null)),
    createTableColumn = Table.Group(removeNullEntries, {"dt_image_id"}, {{"combine", each _, type table [dt_image_id=nullable number, dt_tag_id=nullable number, position=nullable number, pw_tag_id=nullable number, tagList=list]}}),
    removeNullFromTable = Table.AddColumn(createTableColumn, "removedNullEntries", each Table.SelectRows([combine], each not List.IsEmpty([tagList]))),
    expandValueList = Table.AddColumn(removeNullFromTable, "combinedTagList", each List.Distinct(List.Combine(Table.Column([removedNullEntries],"tagList")))),
    removeGarbage = Table.RemoveColumns(expandValueList,{"combine","removedNullEntries"})
in
    removeGarbage

// imagesToUpdate
let
    loadImages = Table.Buffer(pw_images),
    joinAlbumSelected = Table.NestedJoin(loadImages, {"pw_album_id"}, albumIdList, {"pw_album_id"}, "joinColumn", JoinKind.LeftOuter),
    expandAlbumSelected = Table.ExpandTableColumn(joinAlbumSelected, "joinColumn", {"pw_album_id"}, {"pw_album_id.1"}),
    keepSelected = Table.SelectRows(expandAlbumSelected, each [pw_album_id.1] <> null),
    removeDuplicates = Table.Distinct(keepSelected, {"pw_image_id"}),
    removeUnmatched = Table.SelectRows(removeDuplicates, each [dt_image_id] <> 9000000),
    removeGarbage = Table.SelectColumns(removeUnmatched,{"dt_image_id","pw_image_id"}),
    joinTagInformation = Table.NestedJoin(removeGarbage, {"dt_image_id"}, allDtImagesPwTags, {"dt_image_id"}, "allDtImagesPwTags", JoinKind.LeftOuter),
    expandTagInformation = Table.ExpandTableColumn(joinTagInformation, "allDtImagesPwTags", {"combinedTagList"}, {"tags"}),
    convertToList = Table.TransformColumns(expandTagInformation, {"tags", each Text.Combine(List.Transform(_, Text.From), ","), type text})
in
    convertToList

// albumIdList
let
    load_pw_albums = Table.Buffer(pw_albums),
    filterAlbumForTarget =  Table.SelectRows(load_pw_albums, each List.Contains(Table.ToColumns(albumToTag){0},[pw_album_fullname],(x as text, y as text)=>Text.Contains(y,x)))
in
    filterAlbumForTarget

// albumToTag
let
    Quelle = Excel.CurrentWorkbook(){[Name="albumToTag"]}[Content],
    #"Geänderter Typ" = Table.TransformColumnTypes(Quelle,{{"albumToTag", type text}}),
    #"Gefilterte Zeilen" = Table.SelectRows(#"Geänderter Typ", each ([albumToTag] <> null))
in
    #"Gefilterte Zeilen"

// tagsToCreate
let
    Quelle = tags_w_pw_id,
    #"Gefilterte Zeilen" = Table.SelectRows(Quelle, each ([pw_tag_id] = null)),
    #"Hinzugefügte benutzerdefinierte Spalte" = Table.AddColumn(#"Gefilterte Zeilen", "tag", each "|[lang=de]"&[nameDeFlat]&"[/lang][lang=en]"&[nameEnFlat]&"[/lang]"),
    #"Andere entfernte Spalten1" = Table.SelectColumns(#"Hinzugefügte benutzerdefinierte Spalte",{"dt_tag_id", "tag"})
in
    #"Andere entfernte Spalten1"

// dt_tagged_website
let
    load_dt_tags = dt_tags,
    filterforAlbums = Table.SelectRows(load_dt_tags, each ([album_id] <> null)),
    join_dt_tagged_images = Table.NestedJoin(filterforAlbums, {"dt_tag_id"}, dt_tagged_Images, {"dt_tag_id"}, "tagged_Images", JoinKind.LeftOuter),
    expand_dt_tagged_images = Table.ExpandTableColumn(join_dt_tagged_images, "tagged_Images", {"dt_image_id"}, {"dt_image_id"}),
    removeImagesNotInAlbum = Table.SelectRows(expand_dt_tagged_images, each [dt_image_id] <> null),
    removeGarbage = Table.RemoveColumns(removeImagesNotInAlbum,{"nameDeFlat", "nameEnFlat", "lvl"}),
    join_dt_images = Table.NestedJoin(removeGarbage, {"dt_image_id"}, dt_images, {"dt_image_id"}, "images", JoinKind.LeftOuter),
    expand_dt_images = Table.ExpandTableColumn(join_dt_images, "images", {"filename", "maker", "model", "lens", "exposure", "aperture", "iso", "focal_length", "focus_distance", "datetime_taken"}, {"filename", "maker", "model", "lens", "exposure", "aperture", "iso", "focal_length", "focus_distance", "datetime_taken"})
    
in
    expand_dt_images

// pw_not_matched_w_dt
let
    load_pw_images = pw_images,
    filterAlbumUnterwegs = Table.SelectRows(load_pw_images, each ([pw_album_id] = 172)),
    addFilterColumn = Table.AddColumn(filterAlbumUnterwegs, "filter", each if [dt_image_id] = null or [dt_image_id] = 9000000 or [pw_image_id]=[dt_image_id] then "count" else "no count"),
    filterUnmatched = Table.SelectRows(addFilterColumn, each ([filter] = "count")),
    removeFilterColumn = Table.RemoveColumns(filterUnmatched,{"filter"})
in
    removeFilterColumn

// album_comparer_overview
let
    load_dt_tagged_website = dt_tagged_website,
    dt_groupByAlbum = Table.Group(load_dt_tagged_website, {"album_id", "dt_tag_name"}, {{"dt_album_images", each Table.RowCount(_), Int64.Type}, {"dt_groupedAlbum", each _, type table [dt_tag_id=nullable number, dt_tag_name=text, nameDeFlat=text, nameEnFlat=text, album_id=nullable number, lvl=number, dt_image_id=nullable number, filename=nullable text, maker=nullable text, model=nullable text, lens=nullable text, exposure=nullable number, aperture=nullable number, iso=nullable number, focal_length=nullable number, focus_distance=nullable number, datetime_taken=nullable text]}}),
    prettyAlbumName = Table.ReplaceValue(dt_groupByAlbum,"3 Wie|Website|","",Replacer.ReplaceText,{"dt_tag_name"}),
    load_pw_images = pw_images,
    removeUnmatched = Table.SelectRows(load_pw_images, each [dt_image_id] <> null),
    pw_groupByAlbum = Table.Group(removeUnmatched, {"pw_album_id"}, {{"pw_album_images", each Table.RowCount(_), Int64.Type}, {"pw_groupedAlbum", each _, type table [pw_image_id=nullable number, dt_image_id=nullable number, pw_album_id=nullable number, file=nullable text, pw_picture_name=nullable text, comment=nullable text, date_creation=nullable datetime, date_available=nullable datetime, page_url=nullable text, width=nullable number, height=nullable number, hit=nullable number]}}),
    joinTables = Table.NestedJoin(pw_groupByAlbum, {"pw_album_id"}, prettyAlbumName, {"album_id"}, "work", JoinKind.LeftOuter),
    expand_dt_details = Table.ExpandTableColumn(joinTables, "work", {"dt_album_images", "dt_groupedAlbum", "dt_tag_name"}, {"dt_album_images", "dt_groupedAlbum", "dt_tag_name"}),
    calculateDelta = Table.AddColumn(expand_dt_details, "delta", each [pw_album_images] - [dt_album_images]),
    sortAscending = Table.Sort(calculateDelta,{{"pw_album_id", Order.Ascending}})
in
    sortAscending

// album_comparer_detail
let 

    album_comparer_detail = (album_id_input as number) =>

let
    load_dt_tagged_website = Table.Buffer(dt_tagged_website),
    dt_groupByAlbum = Table.Group(load_dt_tagged_website, {"album_id", "dt_tag_name"}, {{"dt_album_images", each Table.RowCount(_), Int64.Type}, {"dt_groupedAlbum", each _, type table [dt_tag_id=nullable number, dt_tag_name=text, nameDeFlat=text, nameEnFlat=text, album_id=nullable number, lvl=number, dt_image_id=nullable number, filename=nullable text, maker=nullable text, model=nullable text, lens=nullable text, exposure=nullable number, aperture=nullable number, iso=nullable number, focal_length=nullable number, focus_distance=nullable number, datetime_taken=nullable text]}}),
    prettyAlbumName = Table.ReplaceValue(dt_groupByAlbum,"3 Wie|Website|","",Replacer.ReplaceText,{"dt_tag_name"}),
    load_pw_images = Table.Buffer(pw_images),
    removeUnmatched = Table.SelectRows(load_pw_images, each [dt_image_id] <> null),
    pw_groupByAlbum = Table.Group(removeUnmatched, {"pw_album_id"}, {{"pw_album_images", each Table.RowCount(_), Int64.Type}, {"pw_groupedAlbum", each _, type table [pw_image_id=nullable number, dt_image_id=nullable number, pw_album_id=nullable number, file=nullable text, pw_picture_name=nullable text, comment=nullable text, date_creation=nullable datetime, date_available=nullable datetime, page_url=nullable text, width=nullable number, height=nullable number, hit=nullable number]}}),
    joinTables = Table.NestedJoin(pw_groupByAlbum, {"pw_album_id"}, prettyAlbumName, {"album_id"}, "work", JoinKind.LeftOuter),
    expand_dt_details = Table.ExpandTableColumn(joinTables, "work", {"dt_album_images", "dt_groupedAlbum", "dt_tag_name"}, {"dt_album_images", "dt_groupedAlbum", "dt_tag_name"}),
    calculateDelta = Table.AddColumn(expand_dt_details, "delta", each [pw_album_images] - [dt_album_images]),
    sortAscending = Table.Sort(calculateDelta,{{"pw_album_id", Order.Ascending}}),
    filterAlbum = Table.SelectRows(sortAscending, each [pw_album_id] = album_id_input),
    addJoinedTableColumn = Table.AddColumn(filterAlbum, "joinTables", each Table.NestedJoin([pw_groupedAlbum], {"dt_image_id"}, [dt_groupedAlbum], {"dt_image_id"}, "joinedTables", JoinKind.FullOuter)),
    removeGarbage = Table.SelectColumns(addJoinedTableColumn,{"joinTables"}),
    expandJoinedTables = Table.ExpandTableColumn(removeGarbage, "joinTables", {"pw_image_id", "dt_image_id", "pw_picture_name", "page_url", "joinedTables"}, {"pw_pw_image_id", "pw_dt_image_id", "pw_pw_picture_name", "pw_pw_page_url", "joinedTables"}),
    expandJoin = Table.ExpandTableColumn(expandJoinedTables, "joinedTables", {"dt_tag_id", "dt_tag_name", "dt_image_id", "dt_album_id", "filename"}, {"dt_dt_tag_id", "dt_dt_tag_name","dt_dt_album_id", "dt_dt_image_id", "dt_dt_filename"}),
    addFlag = Table.AddColumn(expandJoin, "comparer", each if [pw_dt_image_id] = null then "Flagged in dt but not in pw" else if [dt_dt_image_id] = null then "In pw but not flagged in dt" else "Full match" ),
    dt_tag_id_calc = Table.ToColumns(Table.SelectRows(dt_tags, each[album_id] = album_id_input)){0}{0},
    // This is complicated - we have the complete information only for full matches; for Dt images which are tagged but not in Pw we are missing the pw information and 
    // for images in an album in Pw but not tagged in Dt we are missing the Dt information - we need to join BOTH again.
     // 1. Join Pw data for images tagged in Dt 
    pw_images_in_album  = Table.SelectRows(load_pw_images, each [pw_album_id] = album_id_input),
    joinPwImages = Table.NestedJoin(addFlag, {"dt_dt_image_id"}, pw_images_in_album, {"dt_image_id"}, "pw_images", JoinKind.LeftOuter),
    expandPwData = Table.ExpandTableColumn(joinPwImages, "pw_images", {"pw_image_id", "page_url"}, {"dt_pw_image_id", "dt_pw_page_url"}),
    addSqlCode = Table.AddColumn(expandPwData, "correction_code", each if [comparer] = "Flagged in dt but not in pw" then "DELETE FROM tagged_images
      WHERE imgid = '"&Number.ToText([dt_dt_image_id])&"' AND 
            tagid = '"&Number.ToText([dt_dt_tag_id])&"';"
        else if [comparer] = "In pw but not flagged in dt" then "('"&Number.ToText([pw_dt_image_id])&"', '"&Number.ToText([dt_dt_tag_id])&"', '2147483647'),"
        else ""),
    addApiContent = Table.AddColumn(addSqlCode, "pw_id|album_id", each Number.ToText([dt_pw_image_id])&"|"&Number.ToText([dt_dt_album_id]))

in
    addApiContent

in
    album_comparer_detail

// analyzedAlbum
let
    load_Album_id = Excel.CurrentWorkbook(){[Name="albumToAnalyze"]}[Content],
    analyzeAlbum = album_comparer_detail_next(load_Album_id[album_id]{0})
in
    analyzeAlbum

// album_comparer_detail_next
let 

    /* This function analyses the differences between 
        (1) Photos tagged in Darktable (_dt_) to be in a specific webiste album and (each Piwigo album has a corresponding flag in _dt_)
        (2) The photos which are in reality in the respective Piwigo (_pw_) album on the website. 
    
    We can have  the following cases:
        (1) A photo is tagged in _dt_ but does not display in the album in _pw_ because (dt_dt_image_id is not null and pw_image_id is null)
            (a) the photo is available in _pw_ but is not assigned to the album under consideration (c1_pw_image_id is not null)
            (b) the photo is not yet available in _pw_ (c1_pw_image_id is null)
            (c) the photo is wrongly flagged in _dt_ (c1_pw_image_id is null or not null)
        (2) A photo is assigned to a specific album in _pw_ but not flagged accordingly in _dt_ because (dt_dt_image_id is null and pw_image_id is not null)
            (a) the tag is not set correctly in _dt_ (c2_pw_image_id is not null)
            (b) the photo is not matched (i.e. it is available in _pw_ but does not have a corresponding photo in _pw_ (c2_pw_image_id is not null and dt_dt_image_id is null or '9000000')
            (c) the photo is wrongly assigned to the album in _pw_ (
    
    We can solve the cases by: 
        (1)(a) assign the photo in _pw_ to the respective album (add album_id to photo using setInfo method of _pw_ API)
        (1)(b) upload the photo to the respective album in _pw_ (upload photo with album_id using the simpleAdd method of _pw_ API)
        (1)(c) remove the _dt_ tag using an Sql DELETE from tagged images 
        (2)(a) add the _dt_ tag using an Sql INSERT to tagged_images
        (2)(b) do nothing
        (2)(c) remove the photo from the respective album (delete the album_id from _pw_... how?)
    */

    album_comparer_detail = (album_id_input as number) =>

let
    dt_album_tag = Table.SelectRows(dt_tags, each [album_id] = album_id_input)[dt_tag_id]{0}, 
    load_dt_tagged_website = Table.Buffer(dt_tagged_website),
    dt_groupByAlbum = Table.Group(load_dt_tagged_website, {"album_id"}, {{"dt_groupedAlbum", each _, type table [dt_tag_id=nullable number, dt_tag_name=text, nameDeFlat=text, nameEnFlat=text, album_id=nullable number, lvl=number, dt_image_id=nullable number, filename=nullable text, maker=nullable text, model=nullable text, lens=nullable text, exposure=nullable number, aperture=nullable number, iso=nullable number, focal_length=nullable number, focus_distance=nullable number, datetime_taken=nullable text]}}),
    load_pw_images = Table.Buffer(pw_images),
    //removeUnmatched = Table.SelectRows(load_pw_images, each [dt_image_id] <> null),
    pw_groupByAlbum = Table.Group(load_pw_images, {"pw_album_id"}, {{"pw_groupedAlbum", each _, type table [pw_image_id=nullable number, dt_image_id=nullable number, pw_album_id=nullable number, file=nullable text, pw_picture_name=nullable text, comment=nullable text, date_creation=nullable datetime, date_available=nullable datetime, page_url=nullable text, width=nullable number, height=nullable number, hit=nullable number]}}),
    joinTables = Table.NestedJoin(pw_groupByAlbum, {"pw_album_id"}, dt_groupByAlbum, {"album_id"}, "work", JoinKind.LeftOuter),
    expand_dt_details = Table.ExpandTableColumn(joinTables, "work", {"dt_groupedAlbum"}, {"dt_groupedAlbum"}),
    filterAlbum = Table.SelectRows(expand_dt_details, each [pw_album_id] = album_id_input),
    addJoinedTableColumn = Table.AddColumn(filterAlbum, "joinTables", each Table.NestedJoin([pw_groupedAlbum], {"dt_image_id"}, [dt_groupedAlbum], {"dt_image_id"}, "joinedTables", JoinKind.FullOuter)),
    removeGarbage = Table.SelectColumns(addJoinedTableColumn,{"joinTables"}),
    expandJoinedTables = Table.ExpandTableColumn(removeGarbage, "joinTables", {"pw_image_id", "dt_image_id", "pw_picture_name", "page_url", "joinedTables"}, {"pw_pw_image_id", "pw_dt_image_id", "pw_pw_image_name", "pw_pw_page_url", "joinedTables"}),
    expandJoin = Table.ExpandTableColumn(expandJoinedTables, "joinedTables", {"dt_image_id", "filename"}, {"dt_dt_image_id", "dt_filename"}),
    addFlag = Table.AddColumn(expandJoin, "comparer", each if ([pw_dt_image_id] = null and [pw_pw_image_id] = null) then "flagged in dt but not in pw album" else if [dt_dt_image_id] = null then "in pw album but not flagged in dt" else "full match" ),
    filterMismatchesOnly = Table.SelectRows(addFlag, each [comparer] <> "full match"),
    dt_tag_id_calc = Table.ToColumns(Table.SelectRows(dt_tags, each[album_id] = album_id_input)){0}{0},
    // From now on it gets complicated - we have the detailed information only for full matches (which we are not interested in); for Dt images which are tagged but not in Pw we are missing the Pw information and 
    // for images in an album in Pw but not tagged in Dt we are missing the Dt information - we need to join BOTH again.
     // 1. Join Pw data for images tagged in Dt (and NO we cannot filter for album before because they are not in ;-) ): 
    case1_all = Table.SelectColumns(Table.SelectRows(filterMismatchesOnly, each [pw_pw_image_id] = null and [pw_dt_image_id] = null), {"dt_dt_image_id", "dt_filename", "comparer"}),
    case2_b = Table.SelectRows(filterMismatchesOnly, each [pw_pw_image_id] <> null and [pw_dt_image_id] = null),
    case2_other = Table.SelectColumns(Table.SelectRows(filterMismatchesOnly, each [pw_pw_image_id] <> null and [pw_dt_image_id] <> null),{"pw_pw_image_id", "pw_dt_image_id", "pw_pw_image_name", "comparer" }),

    pw_images_unique = Table.Distinct(load_pw_images,{"pw_image_id"}),

    joinCase1_all = Table.NestedJoin(case1_all, {"dt_dt_image_id"}, pw_images_unique, {"dt_image_id"}, "image_info", JoinKind.LeftOuter),
    expandCase1_all = Table.ExpandTableColumn(joinCase1_all, "image_info", {"pw_image_id", "dt_image_id", "pw_picture name", "page_url"}, {"pw_pw_image_id", "pw_dt_image_id", "pw_pw_image_name", "pw_pw_page_url"}),

    joinCase2_other = Table.NestedJoin(case2_other, {"pw_dt_image_id"}, dt_images, {"dt_image_id"}, "image_info", JoinKind.LeftOuter),
    expandCase2_other = Table.ExpandTableColumn(joinCase2_other, "image_info", {"dt_image_id","filename"},{"dt_dt_image_id", "dt_filename"}),

    uniteThemAll = Table.Combine({expandCase1_all, expandCase2_other, case2_b}),


    addComparerDetail = Table.AddColumn(uniteThemAll, "comparer_detail", each if [comparer] = "flagged in dt but not in pw album" and [pw_pw_image_id] = null then "Image not loaded to Piwigo yet, please load or remove wrong flag in Darktable" 
        else if [comparer] = "flagged in dt but not in pw album" and [pw_pw_image_id] <> null then "Assign image to album in Piwigo or remove wrong flag in Darktable" 
        else if [comparer] = "in pw album but not flagged in dt" and [dt_dt_image_id] = null then "Unmatched photo, do nothing or match photo"
        else "Remove image from album in Piwigo or add Album flag in Darktable" ),
        
    addSqlCode = Table.AddColumn(addComparerDetail, "Sql_code", each if [comparer] = "flagged in dt but not in pw album" then "DELETE FROM tagged_images
      WHERE imgid = '"&Number.ToText([dt_dt_image_id])&"' AND 
            tagid = '"&Number.ToText(dt_tag_id_calc)&"';"
        else if [comparer] = "in pw album but not flagged in dt" then "('"&Number.ToText([pw_dt_image_id])&"', '"&Number.ToText(dt_tag_id_calc)&"', '2147483647'),"
        else ""),
    addApiContent = Table.AddColumn(addSqlCode, "pw_id|album_id", each Number.ToText([pw_pw_image_id])&"|"&Number.ToText(album_id_input)),
    finalOrder = Table.ReorderColumns(addApiContent,{"comparer", "comparer_detail", "dt_dt_image_id", "dt_filename", "pw_pw_image_id", "pw_dt_image_id", "pw_pw_image_name", "pw_pw_page_url", "Sql_code", "pw_id|album_id"})
 
in
    finalOrder

in
    album_comparer_detail

// pw_image_dt_merge
let
    Quelle = pw_images,
    #"Gefilterte Zeilen" = Table.SelectRows(Quelle, each [dt_image_id] <> null or [dt_image_id] <> 9000000),
    #"Zusammengeführte Abfragen" = Table.NestedJoin(#"Gefilterte Zeilen", {"dt_image_id"}, dt_images, {"dt_image_id"}, "dt_images", JoinKind.LeftOuter),
    #"Erweiterte dt_images" = Table.ExpandTableColumn(#"Zusammengeführte Abfragen", "dt_images", {"dt_image_id", "group_id", "film_id", "width", "height", "filename", "maker", "model", "lens", "exposure", "aperture", "iso", "focal_length", "focus_distance", "datetime_taken", "flags", "output_width", "output_height", "crop", "raw_parameters", "raw_denoise_threshold", "raw_auto_bright_threshold", "raw_black", "raw_maximum", "license", "sha1sum", "orientation", "histogram", "lightmap", "longitude", "latitude", "altitude", "color_matrix", "colorspace", "version", "max_version", "write_timestamp", "history_end", "position", "aspect_ratio", "exposure_bias", "import_timestamp", "change_timestamp", "export_timestamp", "print_timestamp", "filename - Kopie", "creationDate"}, {"dt_image_id.1", "group_id", "film_id", "width.1", "height.1", "filename", "maker", "model", "lens", "exposure", "aperture", "iso", "focal_length", "focus_distance", "datetime_taken", "flags", "output_width", "output_height", "crop", "raw_parameters", "raw_denoise_threshold", "raw_auto_bright_threshold", "raw_black", "raw_maximum", "license", "sha1sum", "orientation", "histogram", "lightmap", "longitude", "latitude", "altitude", "color_matrix", "colorspace", "version", "max_version", "write_timestamp", "history_end", "position", "aspect_ratio", "exposure_bias", "import_timestamp", "change_timestamp", "export_timestamp", "print_timestamp", "filename - Kopie", "creationDate"})
in
    #"Erweiterte dt_images"