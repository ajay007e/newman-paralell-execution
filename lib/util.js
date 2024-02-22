
import fs from 'fs'
import https from 'https'
import path from "path";
import enquirer from "enquirer";
import child_process from "child_process";
import * as multi_progress_bars from "multi-progress-bars";
import async from "async";
import newman from "newman";
import chalk from "chalk";
import table from "cli-table3";

const { prompt } = enquirer;
const { spawn } = child_process;
const { MultiProgressBars } = multi_progress_bars;

const TEAR_COLLECTION_SCRIPT_URL = 'https://raw.githubusercontent.com/ajay007e/newman-paralell-execution/main/lib/resources/_tear_collection_script.py';


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
    .on("error",(err) => {
      throw err;
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
      throw err;
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
        reject(stderr.toString());
      });
      pyProg.on("close", (code) => {
        resolve({status: true, code, data});
      });
    });
};

const printReport = (allFailures) => {
  let failtureTable = new table({
    colWidths: [5, 35, 100],
    chars: {
      top: " ",
      "top-mid": " ",
      "top-left": " ",
      "top-right": " ",
      bottom: " ",
      "bottom-mid": " ",
      "bottom-left": " ",
      "bottom-right": " ",
      left: " ",
      "left-mid": " ",
      mid: " ",
      "mid-mid": " ",
      right: " ",
      "right-mid": " ",
      middle: " ",
    },
    head: ["#", "failture", "detail"],
  });

  const addToTable = (element, index, arr) => {
    const { message, test, name } = element.error;
    failtureTable.push(
      [index + 1, name, test],
      ["", "", `${chalk.grey(message)}`],
      ["", "", `${chalk.grey(element.at)}`],
      [
        "",
        "",
        `${chalk.grey(
          `inside ${element.parent.name} / ${element.source.name}`
        )}`,
      ]
    );
  };
  allFailures.forEach(addToTable);

  return allFailures.length!=0? console.log(failtureTable.toString()) : undefined;
};

const formatBytes = (bytes, decimals = 2) => {
  if (!+bytes) return "0B";

  const k = 1024;
  const dm = decimals < 0 ? 0 : decimals;
  const sizes = ["B", "kB", "mB", "gB", "tB", "pB", "eB", "zB", "yB"];

  const i = Math.floor(Math.log(bytes) / Math.log(k));

  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(dm))}${sizes[i]}`;
};

const formatTime = (ms, decimals = 1) => {
  let milliseconds = ms.toFixed(0);
  let seconds = (ms / 1000).toFixed(decimals);
  let minutes = (ms / (1000 * 60)).toFixed(decimals);
  let hours = (ms / (1000 * 60 * 60)).toFixed(decimals);
  let days = (ms / (1000 * 60 * 60 * 24)).toFixed(decimals);
  if (milliseconds < 10000) return milliseconds + "ms";
  else if (seconds < 60) return seconds + "s";
  else if (minutes < 60) return minutes + "m";
  else if (hours < 24) return hours + "h";
  else return days + " Days";
};

const formatMetricTime = (ms, decimals = 0) => {
  let milliseconds = ms.toFixed(decimals);
  let seconds = (ms / 1000).toFixed(decimals);
  let minutes = (ms / (1000 * 60)).toFixed(decimals);
  let hours = (ms / (1000 * 60 * 60)).toFixed(decimals);
  let days = (ms / (1000 * 60 * 60 * 24)).toFixed(decimals);
  if (milliseconds < 1000) return milliseconds + "ms";
  if (seconds < 60) return seconds + "s";
  else if (minutes < 60) return minutes + "m " + seconds%60 + "s";
  else if (hours < 24) return hours + "h " + minutes%60 + "m " + seconds%60 + "s";
  else return days + "d " + hours%24 + "h " + minutes%60 + "m " + seconds%60 + "s";
};

const parallelCollectionRun = (collectionName, allFailures, mpb, counter, done) => {

  let statsForProgressBar = {};
  let requestLogMessage = {};
  let testResultMessageForRequest = [];

  const parametersForTestRun = {
    collection: path.resolve(
      `./source/.tmp/${collectionName}-group-${counter}.postman_collection.json`
    ),
    environment: path.resolve(`./source/.tmp/${collectionName}-env.json`),
    reporters: ["cli"],
    reporter: {
      cli: {
        silent: true
      },
    },
  };

  newman
    .run(parametersForTestRun)
    
    .on("start", function (err, args) {
      statsForProgressBar[`collection-${counter}`] = { totalTest: 0, failed: 0 };

      mpb.addTask(`collection ${counter}`, {
        type: "percentage",
        barColorFn: chalk.bgGray,
        message: `${chalk.dim(
          statsForProgressBar[`collection-${counter}`].totalTest
        )} | ${chalk.dim(
            statsForProgressBar[`collection-${counter}`].totalTest -
              statsForProgressBar[`collection-${counter}`].failed
        )} | ${chalk.dim(
          statsForProgressBar[`collection-${counter}`].failed
        )}`,
      });
    })
    .on("assertion", function (err, args) {
      if (args.error != null) {
        testResultMessageForRequest.push({ msg: chalk.red(args.assertion), flag: false });
        statsForProgressBar[`collection-${counter}`] = { ...statsForProgressBar[`collection-${counter}`], failed: statsForProgressBar[`collection-${counter}`].failed + 1};
      } else {
        testResultMessageForRequest.push({ msg: chalk.green(args.assertion), flag: true });
      }
      statsForProgressBar[`collection-${counter}`] = { ...statsForProgressBar[`collection-${counter}`], totalTest: statsForProgressBar[`collection-${counter}`].totalTest + 1};
    })

    .on("test", function (err, args) {
      let { protocol, host, port, path } = {};
      let { code, status, responseSize, responseTime }= {};

      try {
        ({ protocol, host, port, path } = args.executions[0].result.request.url);
        ({ code, status, responseSize, responseTime } = args.executions[0].result.response);
        responseSize = formatBytes(responseSize);
        responseTime = formatTime(responseTime);
      } catch {
        code = false;
      }

      const name = args.executions[0].result.legacy._itemName;
      const method = args.executions[0].result.request.method;
      const queries = args.executions[0].result.request.url.query.members;

      const query = queries.reduce(
        (acc, param) => `${acc}${param.key}=${param.value}&`,
        "?"
      );

      const url = `${method} ${protocol}://${host.join(".")}${port ? ":" + port : ""}/${path.join("/")}`;
      const params = `${queries.length != 0 ? query.slice(0, query.length - 1) : ""}`
      const response = `${code?`[${code} ${status}, ${responseSize}, ${responseTime}]`:chalk.red(`[error]`)}`

      const logMessage = `↳ ${name}\n` + chalk.dim(`  ${url.concat(params)}`) +  ` ${response}`;

      requestLogMessage = {...requestLogMessage, currentRequest:logMessage};
    })

    .on("item", function (err, args) {
      let msg = "\n";
      Object.values(requestLogMessage).forEach(value => {
        msg += `${value}\n`;
      });

      let tst = "\n";
      testResultMessageForRequest.forEach((res) => {
        tst += `  ${res.flag ? "✔" : "✘"} ${res.msg}\n`;
      });

      requestLogMessage = {};
      testResultMessageForRequest = [];
      console.log(msg);
      console.log(tst);

      mpb.updateTask(`collection ${counter}`, {
        percentage: args.cursor.position / args.cursor.length,
        message: `${chalk.dim(
          statsForProgressBar[`collection-${counter}`].totalTest
        )} | ${chalk.dim(
            statsForProgressBar[`collection-${counter}`].totalTest -
              statsForProgressBar[`collection-${counter}`].failed
        )} | ${chalk.dim(
          statsForProgressBar[`collection-${counter}`].failed
        )}`,
      });
    })

    .on("done", (err, summary) => {
      if (err || summary.error) {
        console.error("collection run encountered an error.");
        console.error(err);
      } else {
        const { failures, timings } = summary.run;
        allFailures.push(...failures);
        const { completed, started} = timings;

        mpb.done(`collection ${counter}`, {
          message: `${chalk.dim(
            statsForProgressBar[`collection-${counter}`].totalTest
          )} | ${chalk.dim(
              statsForProgressBar[`collection-${counter}`].totalTest -
                statsForProgressBar[`collection-${counter}`].failed
          )} | ${chalk.dim(
            statsForProgressBar[`collection-${counter}`].failed
          )}`,
        });
        done()
      }
    });
};


export const initializeFileSetups = () => {

    // create source folder if not exists
    createDirIfNotExists('source')

    // create .tmp, collection, env folders if not exists inside 'source'
    createDirIfNotExists('source/.tmp')
    createDirIfNotExists('source/collection')
    createDirIfNotExists('source/env')

    // create resource folders if not exists inside 'source/.tmp'
    createDirIfNotExists('source/.tmp/resources')
    
    // download tearCollection.py if not exists inside 'source/.tmp/scripts'
    downloadFileIfNotExists(TEAR_COLLECTION_SCRIPT_URL, 'source/.tmp/resources/tearCollection.py')

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
        throw err;
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
      throw err;
    });
  } catch (err) {
    throw err;
  }
};

export const executeTests =  (stringData) => {
  return new Promise( async (resolve, reject) => {
    
    // extracting collectionName and collectionSize form input
    const [collectionName, collectionSizeStr] = stringData.replace(/[\[\]'\n]/g, '').split(',');
    const collectionSize =  parseInt(collectionSizeStr, 10)

    let allFailures = [];

    const mpb = new MultiProgressBars({
      initMessage: `${collectionName} Test Suite`,
      anchor: "bottom",
      persist: true,
      border: true,
    });

    let commands = [];

    // adding newman jobs into the array
    for (let index = 1; index <= collectionSize; index++) {
      commands.push((done) => parallelCollectionRun(collectionName, allFailures, mpb, index, done));
    }

    // executing newman jobs parallelly using 'async.parallel'
    async.parallel(commands, (err, results) => {
      err && console.error(err);
      printReport(allFailures);
      resolve({status:true, collectionName, collectionSize });
    });
  });
};