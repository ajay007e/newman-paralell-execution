
import * as util from './lib/util.js'


const exitFails = (message) => {
    throw message;
}

const main = async () => {
    try {
        const resultFromFileSetups = await util.initializeFileSetups();
        const resultFromPrompt = !resultFromFileSetups?.status ? exitFails('Initilization failed') : await util.executePrompt(resultFromFileSetups?.isPatternAvailableInEnv);
        const resultFromSetup = !resultFromPrompt?.status ? exitFails(`Prompt execution failed`) : await util.configureSetups(resultFromPrompt?.response);
        !resultFromSetup?.status ? exitFails(`Configuring setup failed`) : await util.executeTests(resultFromSetup?.data);
    } catch (err){
        console.error(err)
    }
}

main()

