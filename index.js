
import * as util from './lib/util.js'


const exitFails = (message) => {
    throw message;
}

const main = async () => {
    try {
        util.initializeFileSetups();
        const resultFromPrompt = await util.executePrompt();
        const resultFromSetup = !resultFromPrompt?.status ? exitFails(`Prompt execution failed`) : await util.configureSetups(resultFromPrompt?.response);
        const resultFromTest = !resultFromSetup?.status ? exitFails(`Configuring setup failed`) : await util.executeTests(resultFromSetup?.data);
        const resultFromGenerateReport = !resultFromTest?.status ? exitFails(`Test execution failed`) : await util.generateReport(resultFromTest);
        !resultFromGenerateReport?.status ? exitFails(`Report Generation failed`) : util.showGenerateReports();
    } catch (err){
        console.error(err)
    }
}

main()

