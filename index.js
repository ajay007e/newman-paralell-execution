
import * as util from './lib/util.js'


const main = async () => {
    util.initializeFileSetups();
    const resultFromPrompt = await util.executePrompt();
    const resultFromSetup = !resultFromPrompt?.status ? console.error(`Prompt execution failed`) : await util.configureSetups(resultFromPrompt?.response);
    !resultFromSetup?.status ? console.error(`Configuring setup failed`) : console.log(resultFromSetup);
}

main()