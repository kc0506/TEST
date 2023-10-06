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
        # Enter
        source CSL/bin/activate
        # Leave
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
