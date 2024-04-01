# Instructions

## frontend

Change directory into frontend

```shell
cd /frontend
```

Install packages

```shell
yarn --exact
```

Build application

```shell
yarn build
```

Start server in dev mode

```shell
yarn dev
```

You can check your dev server is working by going to:

```plain
http://localhost:5173/health
```

or alternatively in live mode:

```shell
yarn start
```

You can check your live server is working by going to:

```plain
http://localhost:4173/health
```

## backend
### Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

#### Configure AWS boto
```bash
pip install boto
```
* To sign up for an AWS account
* Open https://portal.aws.amazon.com/billing/signup.
* Follow the online instructions.
* Create an administrative user by following instructions. https://docs.aws.amazon.com/polly/latest/dg/prerequisites.html
* Get your Access Key
* Install AWS CLI: https://aws.amazon.com/cli/
* configure the AWS profile on the AWS CLI as follows:
```bash
aws configure
```
* Alternatively, you can input your access_key in `~/.aws/credentials`
  * `vi ~/.aws/credentials`
  * ```text
    [default]
    aws_access_key_id = YOUR_ACCESS_KEY
    aws_secret_access_key = YOUR_SECRET_KEY
    [adminuser]
    aws_access_key_id = YOUR_ACCESS_KEY
    aws_secret_access_key = YOUR_SECRET_KEY
    ```
* create a profile called `adminuser` 
#### Configure OpenAI Client
```bash
pip install --upgrade openai
```
* Set up your API key: https://platform.openai.com/docs/quickstart?context=python
* On Mac: 

  * **Open Terminal**: You can find it in the Applications folder or search for it using Spotlight (Command + Space).
  * **Edit Bash Profile**: Use the command `nano ~/.bash_profile` or `nano ~/.zshrc` (for newer MacOS versions) to open the profile file in a text editor.
  * **Add Environment Variable**: In the editor, add the line below, replacing `your-api-key-here` with your actual API key:

  ```text
  export OPENAI_API_KEY='your-api-key-here'
  ```

  * **Save and Exit**: Press Ctrl+O to write the changes, followed by Ctrl+X to close the editor.
  * **Load Your Profile**: Use the command `source ~/.bash_profile` or `source ~/.zshrc`to load the updated profile.
  * **Verification**: Verify the setup by typing `echo $OPENAI_API_KEY` in the terminal. It should display your API key.

* On Windows:

  * **Open Command Prompt**: You can find it by searching "cmd" in the start menu.

  * **Set environment variable in the current session**: To set the environment variable in the current session, use the command below, replacing `your-api-key-here` with your actual API key:

    ```text
    setx OPENAI_API_KEY "your-api-key-here"
    ```

    This command will set the OPENAI_API_KEY environment variable for the current session.

  * **Permanent setup**: To make the setup permanent, add the variable through the system properties as follows:

    - Right-click on 'This PC' or 'My Computer' and select 'Properties'.
    - Click on 'Advanced system settings'.
    - Click the 'Environment Variables' button.
    - In the 'System variables' section, click 'New...' and enter OPENAI_API_KEY as the variable name and your API key as the variable value.

  * **Verification**: To verify the setup, reopen the command prompt and type the command below. It should display your API key: `echo %OPENAI_API_KEY%`


### Start your backend server

Start your backend server

```shell
uvicorn main:app
```

Alternatively, you can ensure your server resets every time you make a change by typing:

```shell
uvicorn main:app -- reload
```

