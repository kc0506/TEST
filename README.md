# 112-1_CSL

112-1_CSL LAB

## Pre-Installation and VE Setup

1. (OPTIONAL) Install Virtual Environment

    ```bash
    pip install virtualenv 
    ```

2. Create virtual environment named "CSL"

    ```bash
    virtualenv CSL
    ```

3. Enter / Leave virtual environment

    ```bash
    # Enter VE
    source CSL/bin/activate
    # Leave VE
    deactivate
    ```

4. Install packages in "./requirements.txt"

    ```bash
    pip install -r requirements.txt
    ```

5. If new packages are added, update the requirements.txt

    ```bash
    pip freeze > requirements.txt
    ```

## Setup the repo

1. Fork this repo

2. Clone the repo you forked to your local computer

    ```bash
    git clone https://github.com/<your-forked-repo>/<your-forked-repo>.git
    ```

3. Add upstream

    ```bash
    git remote add upstream https://github.com/weiiiii0622/112-1_CSL.git
    ```

## If you want to get others new code…

1. Pull from "source repo"

    ```bash
    git pull upstream master
    ```

2. Push to "local repo (your own)"

    ```bash
    git push origin
    ```

## If you want to update your code to others…

1. Add every thing that you modified

    ```bash
    git add .
    ```

2. Commit with "msg"

    ```bash
    git commit -m "msg"
    ```

3. Push back to "local repo (your own)"

    ```bash
    git push -u origin master
    ```

4. Send a pull request to "source repo"

    // Go to github page and press the pull request button
