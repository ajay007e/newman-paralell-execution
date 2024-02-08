

# Newman Parallel Execution

This repository will help to run Postman collection parallelly using the Newman


## Run Locally

Clone the project

```bash
  git clone https://github.com/ajay007e/newman-paralell-execution.git
```

Go to the project directory

```bash
  cd newman-paralell-execution
```

Install dependencies

```bash
  npm install --legacy-peer-deps  
```

Start the execution

```bash
  node index.js
```

> [!WARNING]
> If any error occurs related to the missing collection or environment while executing the above command, ensure that the collection and environment are present in the respective folders in the source directory
