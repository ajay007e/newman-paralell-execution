
import fs from 'fs'
import https from 'https'
import path from "path";
import enquirer from "enquirer";
import child_process from "child_process";

const { prompt } = enquirer;
const { spawn } = child_process;


const TEMPLATE_HTML_URL = 'https://github.com/ajay007e/newman-paralell-execution/main/lib/resources/template.html';
const TEAR_COLLECTION_SCRIPT_URL = 'https://github.com/ajay007e/newman-paralell-execution/main/lib/resources/_tear_collection_script.py';
const GENERATE_REPORTS_SCRIPT_URL = 'https://github.com/ajay007e/newman-paralell-execution/main/lib/resources/_generate_reporsts_script.py';


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

const getFiles = (url) => {
  return new Promise((resolve, reject) => {
    fs.readdir(url, (err, files) => {
      if (err) {
        reject(err);
      } else {
        resolve(files);
      }
    });
  });
};

const createSelectPrompt = async (url, name, message) => {
    try {
      const content = await getFiles(url);
  
      if (content.length === 0) {
        throw new Error(`No ${name} found in the ${url}`);
      }
  
      const choices = content.map((element) => ({
        message: element,
        value: element,
        name: `${url}/${element}`,
      }));
  
      return {
        type: "select",
        name: name,
        message: message,
        choices: choices,
      };
    } catch (err) {
      throw `Something went wrong while fetching files from ${url} with ${err}`;
    }
};

const runScript = (scriptPath, args) => {
    return new Promise((resolve, reject) => {
      let data = "";
      
      const pyProg = spawn("python3", [scriptPath].concat(args));

      pyProg.stdout.on("data", (stdout) => {
        data += stdout.toString();
      });
      pyProg.stderr.on("data", (stderr) => {
        reject(stderr);
      });
      pyProg.on("close", (code) => {
        resolve({status: true, code, data});
      });
    });
};

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

export const executePrompt = async () => {
    try {
        // create enquirer prompt for postman collection
        const collectionPrompt = await createSelectPrompt(
            path.resolve("./source/collection"),
            "collection",
            "Choose a Collection"
        );
        // create enquirer prompt for postman environment
        const environmentPrompt = await createSelectPrompt(
            path.resolve("./source/env"),
            "environment",
            "Choose a Environment"
        );
        // create enquirer prompt for pattern used for partitioning collection
            // if collection start with 1)request-group to n)request-group then pattern can be 1,...,n+1
            // minimum one request group should be in partitioin, if you want to partition the collection
            //      into two collections, then pattern will be 1,m,n+1 where m<n, which is the  required 
            //      pattern for creation two collections from main collection. 
            //      first collection will contain 1 to m-1 request groups and second one will contain m to n
        const patternPrompt = {
            type: "input",
            name: "pattern",
            message: "Enter your pattern ",
        };

        // execute prompt using the created prompts and return response from user as a key-value pair 
        const response = await prompt([
            collectionPrompt,
            environmentPrompt,
            patternPrompt,
        ])
        return {status: true, response};
    } catch (err) {
        console.debug(err)
        return {status: false};
    }
};

export const configureSetups = async (data) => {
  try {
    // destructuring the input
    const { collection, environment, pattern } = data;
    // running the script to setup the collection and environment with the pattern
    return await runScript(
      path.resolve("./source/.tmp/resources/tearCollection.py"),
      [collection, environment, pattern]
    ).catch((err) => {
      console.debug(err.toString());
      return { status: false };
    });
  } catch (err) {
    console.debug(err);
    return { status: false };
  }
};
