# python_scrape
Module built to scrape python modules and turn them into Jupyter Notebooks.

## How to use this module
In a bash terminal run:<br>
<code>git clone scrape/scrape_python_modules.py
cd python_scrape
chmod +x install_and_scrape.sh scrape_python_modules.py
./install_and_scrape.sh
</code><br>
* At this point a Jupyter Labs window should pop up. You can go into the modules individually. To run a codeblock, use CTRL+Enter.<br>
* Each Notebook will run in it's own space. Make sure to shut down the kernels once you are complete and ready to move on. <br>
* Now you will have your own space to follow along the class and run the code blocks! PLEASE add your own blocks and play with the code as much as you want.<br>
* Because this is running locally, any changes you make and notes you take will be saved to your notebook (so make sure you don't run this program again!).


## NOTE:
* **Rerunning this program will overwrite your lab notebooks** which may have notes in it. This should only be ran once at the beginning of the Python Course.<br>
* This program is not perfect. The markdown that are inside of code blocks do not differentiate what should have been in an interpretter. **These blocks should not be ran** and are used as examples of what a Python REPL session would look like.