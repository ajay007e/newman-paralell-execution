
import fs from 'fs'
import https from 'https'









const TEMPLATE_HTML_URL = 'https://github.com/ajay007e/newman-paralell-execution/blob/main/lib/resources/template.html';
const TEAR_COLLECTION_SCRIPT_URL = 'https://github.com/ajay007e/newman-paralell-execution/blob/main/lib/resources/_tear_collection_script.py';
const GENERATE_REPORTS_SCRIPT_URL = 'https://github.com/ajay007e/newman-paralell-execution/blob/main/lib/resources/_generate_reporsts_script.py';


const createDirIfNotExists = (dir) => !fs.existsSync(dir) ? fs.mkdirSync(dir) : undefined;

const downloadFileIfNotExists = (url, path) => !fs.existsSync(path) ? downloadFileFromRemote(url, path) : undefined;

const downloadFileFromRemote = (url, path) => {
    https.get(url, (res) => {
        const writeStream = fs.createWriteStream(path);
        res.pipe(writeStream);
        writeStream.on("finish", () => {
           writeStream.close();
        })
     })
}



export const initializeFileSetups = () => {

    // create source folder if not exists
    createDirIfNotExists('source')

    // create .tmp, collection, env folders if not exists inside 'source'
    createDirIfNotExists('source/.tmp')
    createDirIfNotExists('source/collection')
    createDirIfNotExists('source/env')

    // create reports, resource folders if not exists inside 'source/.tmp'
    createDirIfNotExists('source/.tmp/reports')
    createDirIfNotExists('source/.tmp/resources')

    // create csv, html, html_color_css folders if not exists inside 'source/.tmp/reports'
    createDirIfNotExists('source/.tmp/reports/csv')
    createDirIfNotExists('source/.tmp/reports/html')
    createDirIfNotExists('source/.tmp/reports/html_color_css')

    // download template.html if not exists inside 'source/.tmp/templates'
    downloadFileIfNotExists(TEMPLATE_HTML_URL, 'source/.tmp/resources/template.html')
    
    // download tearCollection.py, generateReports.py if not exists inside 'source/.tmp/scripts'
    downloadFileIfNotExists(TEAR_COLLECTION_SCRIPT_URL, 'source/.tmp/resources/tearCollection.py')
    downloadFileIfNotExists(GENERATE_REPORTS_SCRIPT_URL, 'source/.tmp/resources/generateReports.py')

}