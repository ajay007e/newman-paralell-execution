
import * as util from './lib/util.js'


const main = async () => {
    util.initializeFileSetups();
    const result = await util.executePrompt();
    !result?.status ? console.error(`Prompt execution failed`) : console.log(result?.response)
}

main()