# Wikipedia Analysis Tool #

## Building the database ## 

To run the tool localy you first need to build the sql database on your computer. This requiers a postgresql server to be running on the computer. To build the database run the `build_db.sh` file in the `builddb` directory. You need to specify a language code for the wikipedia to be downloaded. You may also specify a date of the dump to use. If no date is specifyed then the latest dump is used. To download the latest english wikipedia run:

    $ ./build_db.sh en

### In case of fire ###

If the script at some point would crash or stop before it's done, you may run the scrips individually to recover the progress. The scripts and their order of execution are as follows:

- `dowload_db.sh`: Downloads all the requierd files or just one if specified. Use `./download_db.sh <lang-code> [date]` to download all requierd fiels or `./download_db.sh <lang-code> <date> <file name>` to download one specific file.
- `filter_sql.sh`: Removes unnesesary data from the sql files. Pass the language code and a date to it to start it. The date can be found in the file name of the downloaded files in the database directory. To run it use `./filter_sql.sh <lang-code> <date>`
- `sort_pagelinks.sh`: Sorts the pagelinks. This is requierd for the insertion into the sql table. Give it the language code and date to run it: `./sort_pagelinks.sh <lang-code> <date>`
- `build_sql.sh`: This builds the actual sql table in postgres and inserts all the values. As with the other scripts; pass it the language code and the date and it'll be happy (`./build_sql.sh <lang-code> <date>`).

Once the sql table is fully built the `database/` folder is no longer requierd and can safely be deleated.
