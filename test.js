import fs from 'fs';
import git from 'simple-git';
import dotenv from 'dotenv';

dotenv.config();

const repositoryUrl = process.env.REPOSITORY_URL; // SSH URL of your Bitbucket repositorygit clone 
const branch = process.env.DEV_BRANCH ? process.env.DEV_BRANCH : 'master';
const files = JSON.parse(process.env.FILES);
console.log(branch)

// Function to download a file

const localRepoPath = 'source/.tmp/temp-repo'; // Local path to clone the repository  

// Function to download a file
async function downloadFile(filePath, saveAs) {
    try {
        const content = await git(localRepoPath).show([branch + ':' + filePath]);
        fs.writeFileSync(saveAs, content);
    } catch (error) {
        console.error(`Error downloading file: ${filePath}`, error);
    }
}
// Function to clone repository and download multiple files
async function downloadFiles() {
    try {
        await git().clone(repositoryUrl, localRepoPath, ['--branch', branch]);

        await git(localRepoPath).fetch('origin', branchName); // Fetch latest changes from the remote branch
        await git(localRepoPath).checkout('master'); // Checkout the master branch
        await git(localRepoPath).pull('origin', 'master'); // Pull latest changes from the master branch
        await git(localRepoPath).checkout(branchName); // Checkout the feature branch again
        await git(localRepoPath).rebase(['master']); // Rebase feature branch with master

        await git(localRepoPath).push('origin', branchName, { '--force': null }); // Push changes to remote repository

        await Promise.all(files.map(({ path, saveAs }) => downloadFile(path, saveAs)));
    } catch (error) {
        console.error('Error:', error);
    } finally {
        fs.rmdirSync(localRepoPath, { recursive: true });
    }
}
// Call the function to download multiple files
// downloadFiles();



// run with existing collection with sequence 1, 2, 3
// run with existing collection with range -- u=10 l=5
// run with latest version

