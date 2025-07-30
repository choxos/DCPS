I want to create a web app for our study on dental caries prevalence in Canada 1990-2025 with projection to 2050. We are still in the data extraction phase but I thought it would be good to have the web app prepared to some extent as well. The preliminary protocol is available in protocol_dmft_canada.md for your information. In summary, we conducted a systematic review to identify all the studies that have assessed dental caries in a population in Canada. You can find the extraction sheet in dmft_canada_DET.xlsx which its first sheet is the extracted data from primary studies and the third sheet is the description of the columns in the first sheet.

I want to create a web app named DCPS (Dental Caries in Population Study). This is a part of Xera DB. Xera DB projects use a same theme and a same structure. You can find the specifics of the theme and the structure in this folder: ~/Documents/Github/xeradb/shared_theme. The specifics for DCPS are in css/themes/dcps-theme.css. You can find the structure of other projects in ~/Documents/Github/OpenScienceTracker for OST project, ~/Documents/GitHub/CitingRetracted for PRCT project, and ~/Documents/GitHub/CIHRPT for CIHRPT project. Read each one carefully to understand the structure.

Please note that we started from Canada and we may expand to other countries.

Please create a web app 


Then, give me a .md file to deploy the project to my VPS (dcps.xeradb.com). The folder is in /var/www/html/ttedb and postgres database is ttedb_production with user name ttedb_user.

Let's GO!