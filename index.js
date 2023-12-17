
import * as util from './lib/util.js'


const main = async () => {
    util.initializeFileSetups();
    const resultFromPrompt = await util.executePrompt();
    const resultFromSetup = !resultFromPrompt?.status ? console.error(`Prompt execution failed`) : await util.configureSetups(resultFromPrompt?.response);
    const resultFromTest = !resultFromSetup?.status ? console.error(`Configuring setup failed`) : await util.executeTests(resultFromSetup?.data);
    !resultFromTest.status ? console.error(`Test execution failed`) : console.log(resultFromTest)

}

main()

