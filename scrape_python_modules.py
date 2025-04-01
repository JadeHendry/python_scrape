#!/usr/bin/env python3.8

import requests
from bs4 import BeautifulSoup
import re
import os
import json
import copy
from markdownify import markdownify as md
from lxml import etree

NEW_NB_METADATA = {
    'nbformat': 4,
    'nbformat_minor': 2, 
    'cells': [],
    'metadata': {
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python", 
            "name": "python3"}
        }
    }

BASIC_CODE_CELL = {
   "cell_type": "code",
   "metadata": {},
   "outputs": [],
   "source": []
  }

BASIC_MARKDOWN_CELL = {
   "cell_type": "markdown",
   "metadata": {},
   "source": []
  }

urlList = [
    "https://cted.cybbh.io/tech-college/cttsb/PROG/prog/Python/01_Python_Fundamentals/00_intro.html",
    "https://cted.cybbh.io/tech-college/cttsb/PROG/prog/Python/02_Python_Data_Types/00_intro.html",
    "https://cted.cybbh.io/tech-college/cttsb/PROG/prog/Python/03_Python_intermediate_lists_and_strings/00_intro.html",
    "https://cted.cybbh.io/tech-college/cttsb/PROG/prog/Python/04_Python_Functions/00_intro.html",
    "https://cted.cybbh.io/tech-college/cttsb/PROG/prog/Python/05_Python_Conditional_Expressions/00_intro.html",
    "https://cted.cybbh.io/tech-college/cttsb/PROG/prog/Python/06_Slicing_Built-in_Functions_and_Loops/00_intro.html",
    "https://cted.cybbh.io/tech-college/cttsb/PROG/prog/Python/07_Loops/00_intro.html",
    "https://cted.cybbh.io/tech-college/cttsb/PROG/prog/Python/08_Python_File_IO/00_intro.html",
    "https://cted.cybbh.io/tech-college/cttsb/PROG/prog/Python/09_Python_Standard_Libraries/00_intro.html",
    "https://cted.cybbh.io/tech-college/cttsb/PROG/prog/Python/10_Python_Dictionary_Sets/00_intro.html",
    "https://cted.cybbh.io/tech-college/cttsb/PROG/prog/Python/11_args_kwargs/00_intro.html",
    "https://cted.cybbh.io/tech-college/cttsb/PROG/prog/Python/12_Sorting/00_intro.html",
    "https://cted.cybbh.io/tech-college/cttsb/PROG/prog/Python/13_Python_Debugging/00_into.html",
    "https://cted.cybbh.io/tech-college/cttsb/PROG/prog/Python/14_Number_Systems/00_intro.html",
    "https://cted.cybbh.io/tech-college/cttsb/PROG/prog/Python/15_Python_OOP/00_intro.html",
    "https://cted.cybbh.io/tech-college/cttsb/PROG/prog/Python/16_Python_Networking/00_intro.html",
    "https://cted.cybbh.io/tech-college/cttsb/PROG/prog/Python/17_Python_Regexes/00_intro.html"  
]


def get_sublinks(soup):
    list_of_subpages = []
    for a_item in soup.find_all("a"):
        re_mat = re.match('^\d\d_', a_item.get("href"))
        if re_mat:
            list_of_subpages.append(a_item.get("href"))
    return set(list_of_subpages)


# Originally built this funtion when I was html parsing, it will fix some of the elements
# when we pull them in as text. Function is recursive and will handle specific problems one
# at a time (usually the problems are that there are extra html elements or that there isn't
# a closing bracket)

def ensure_code_str(html_str):
    if html_str.find("\n") != -1:
        html_str = " ".join(html_str.split("\n")[:-1])

    try:
        root = etree.fromstring(html_str)
    except etree.XMLSyntaxError as e:
        if str(e).startswith("Extra content at the end of the document"):
            rev_str = html_str[::-1]
            where_to_pop = 0
            for idx, letter in enumerate(rev_str):
                if letter == "<":
                    where_to_pop = idx
                    break
            html_str = ensure_code_str(html_str[0:-(where_to_pop+1)])
        elif str(e).startswith("Premature end of data "):
            idx = html_str.find("<p>")
            html_str = html_str[:idx] + html_str[idx + 3:]

    return html_str


def extract_code_elements(html_str):
    ret_str_list = []
    for line in html_str.split("\n"):
        line_to_add = ""
        if "codelineno" in line:
            regex_match = re.findall(">(.*?)<", line)
            if regex_match:
                line_to_add = ("".join(regex_match))

            if not line.endswith(">"):
                idx = line.rfind(">")
                line_to_add += line[idx + 1:]
            ret_str_list.append(line_to_add)

    if len(ret_str_list) // 2 >= 9:
        ret_str_list[len(ret_str_list) // 2] = ret_str_list[len(ret_str_list) // 2][2:]
    else:
        if ret_str_list:
            ret_str_list[len(ret_str_list) // 2] = ret_str_list[len(ret_str_list) // 2][1:]

    # Originally wanted to use lxml to extract these, but the markdown uses whitespace between html elements
    # This will get the elements, but it isn't great. The solution above is also not great persay because SOEMTIMES
    # the lines include markdown. IDK if there is a good way around this, but for now it works. 
    # I could look for the specific lines of text and do text replacement, but I'm not sure that it would
    # be beneficial as when there is markdown in a code element it is meant to demonstrate that code is
    # being executed in REPL. 

    # root = etree.fromstring(html_str)
    # code_str_list = []
    # for span_elem in root.iter("span"):
    #     try:
    #         #print(span_elem.attrib["id"])
    #         code_text = []
    #         if span_elem.attrib["id"].startswith("__span"):
    #             if_span = bool(span_elem.iter("span"))
    #             for child_elem in span_elem.iter("span"):
    #                 code_text += [get_text(child_elem)]
    #         if code_text:
    #             print(code_text)
    #             code_str_list.append("".join(code_text))
    #     except Exception as e:
    #         continue


    return ret_str_list[len(ret_str_list) // 2:]


def get_text(node):
    try:
        return node.text
    except Exception as e:
        return ""


def get_page_json(html_lines, mkdwn_only=False):
    page_json = copy.deepcopy(NEW_NB_METADATA)
    curr_cell = copy.deepcopy(BASIC_MARKDOWN_CELL)
    mkdown_str = ""
    block_is_mkdown = True
    code_str = ""
    div_count = 0
    for idx,line in enumerate(html_lines[1:-2]):
        if not mkdwn_only:
            if line.find("<div") != -1 and div_count != 0:
                div_count += line.count("<div")
            if line.find("<div") != -1 and div_count == 0:
                block_is_mkdown = False
                div_count += line.count("<div")
                curr_cell["source"].append(md(mkdown_str) + "\n")
                page_json['cells'].append(curr_cell)
                curr_cell = copy.deepcopy(BASIC_CODE_CELL)
                mkdown_str = ""
        
        if block_is_mkdown:
            mkdown_str += line + "\n"
        else:
            code_str += line + "\n"
        
        if not mkdwn_only:
            if line.find("</div") != -1:
                div_count -= line.count("</div")
            if line.find("</div") != -1 and div_count == 0:

                if code_str:
                    #code_str = ensure_code_str(code_str) <-- used this when parsing html elements
                    code_str = extract_code_elements(code_str)
                    for elem in code_str:
                        curr_cell["source"].append(elem + "\n")
                page_json['cells'].append(curr_cell)
                code_str = ""
                curr_cell = copy.deepcopy(BASIC_MARKDOWN_CELL)
                block_is_mkdown = True

    if mkdown_str:
        curr_cell["source"].append(md(mkdown_str) + "\n")
        page_json['cells'].append(curr_cell)
    # if code_str:
    #     #code_str = ensure_code_str(code_str) <-- used this when parsing html elements
    #     code_str = extract_code_elements(code_str)
    #     for elem in code_str:
    #         curr_cell["source"].append(elem + "\n")
    
    return(page_json)


if __name__ == "__main__":

    dict_of_links = {}
    for url in urlList:
        dict_of_links["/".join(url.split("/")[:-1])] = []
        response = requests.get(url)
        soup = BeautifulSoup(response.content, "html.parser")
        sublinks = get_sublinks(soup)
        for link in sublinks:
            dict_of_links["/".join(url.split("/")[:-1])].append(link)


    for url in dict_of_links:
        python_module = url.split("/")[-1]
        print(python_module)
        try:
            os.mkdir(python_module)
        except:
            pass
        for page in dict_of_links[url]:
            print(url + "/" + page)
            response = requests.get(url + "/" + page)
            
            #If the page is check on learning, just add everything as markdown
            check_on_learning = False
            if "check_on_learning" in page.lower():
                check_on_learning = True

            soup = BeautifulSoup(response.content, "html.parser")
            nbfile = url.split("/")[-1]
            article = soup.find_all("article")
            htmlstr = str(article[0])
            lines = htmlstr.split("\n")
            
            #get rid of first couple lines that look bad
            htmlstr = ""
            for i in range(len(lines)):
                if i not in range(1,7):
                    htmlstr += lines[i] + "\n"

            # Will save off the file html elements. This is useful for comparing to the data in case 
            # there are unexpected html elements

            # try:
            #     f = open(python_module + "/" + page, "x")
            # except:
            #     f = open(python_module + "/" + page, "w")
            # f.write(str(htmlstr))
            # f.close()

            try:
                f = open(python_module + "/" + page + ".ipynb", "x")
            except:
                f = open(python_module + "/" + page + ".ipynb", "w")
            
            
            f.write(json.dumps(get_page_json(htmlstr.split("\n"), check_on_learning)))